import random
import os
import itertools
import signal
import sys

# ==============================
# Configuración inicial
# ==============================

RANKS = '23456789TJQKA'
SUITS = ['♠', '♥', '♦', '♣']
RANK_VALUES = {r: i for i, r in enumerate(RANKS, start=2)}

# Ranking con ejemplos
HAND_ORDER_EXAMPLES = [
    ("Carta Alta (High Card)", "A♣ J♦ 8♠ 6♥ 3♠"),
    ("Pareja (One Pair)", "5♠ 5♦ K♣ 9♠ 2♥"),
    ("Doble Pareja (Two Pair)", "Q♣ Q♦ 9♥ 9♠ 4♣"),
    ("Trío (Three of a Kind)", "J♠ J♥ J♦ 7♣ 2♠"),
    ("Escalera (Straight)", "8♣ 7♦ 6♠ 5♣ 4♥"),
    ("Color (Flush)", "A♦ Q♦ 9♦ 6♦ 3♦"),
    ("Full House", "T♠ T♦ T♣ 6♥ 6♦"),
    ("Póker (Four of a Kind)", "K♦ K♣ K♥ K♠ 3♣"),
    ("Escalera de Color (Straight Flush)", "9♥ 8♥ 7♥ 6♥ 5♥"),
    ("Escalera Real (Royal Flush)", "A♠ K♠ Q♠ J♠ T♠")
]

# ==============================
# Utilidades
# ==============================

def clear():
    os.system("clear")

def color_carta(carta):
    if carta[1] in ['♥', '♦']:
        return f"\033[91m{carta}\033[0m"  # rojo
    else:
        return f"\033[97m{carta}\033[0m"  # blanco

def formatear_cartas(cartas):
    return " ".join(color_carta(c) for c in cartas)

def mostrar_orden_manos():
    print("\n=== Orden de manos en el Póker (de menor a mayor) ===")
    for i, (mano, ejemplo) in enumerate(HAND_ORDER_EXAMPLES, 1):
        print(f"{i}. {mano} -> Ejemplo: {formatear_cartas(ejemplo.split())}")
    print("")

def crear_baraja():
    return [r + s for r in RANKS for s in SUITS]

def describir_mano(cartas):
    """Describe qué 5 cartas forman la mano ganadora"""
    mejor_combo = None
    mejor_valor = (-1, [])
    
    for combo in itertools.combinations(cartas, 5):
        valor = mano_valor(combo)
        if valor > mejor_valor:
            mejor_valor = valor
            mejor_combo = combo
    
    return mejor_combo, mejor_valor

def signal_handler(sig, frame):
    """Maneja la señal de interrupción (Ctrl+C)"""
    print('\n\n¡Hasta la próxima! Usa "Q" para salir elegantemente.')
    sys.exit(0)

# ==============================
# Evaluador de manos (CORREGIDO)
# ==============================

def mano_valor(cartas):
    """Evalúa una mano de exactamente 5 cartas y devuelve (ranking, tiebreakers)"""
    ranks = [RANK_VALUES[c[0]] for c in cartas]
    suits = [c[1] for c in cartas]
    
    # Contar frecuencias de cada rank
    rank_counts = {}
    for rank in ranks:
        rank_counts[rank] = rank_counts.get(rank, 0) + 1
    
    # Ordenar ranks por frecuencia y luego por valor
    sorted_by_count = sorted(rank_counts.items(), key=lambda x: (x[1], x[0]), reverse=True)
    counts = [count for rank, count in sorted_by_count]
    rank_values = [rank for rank, count in sorted_by_count]
    
    # Verificar si es escalera
    sorted_ranks = sorted(ranks)
    is_straight = False
    straight_high = 0
    
    # Escalera normal
    if sorted_ranks == list(range(sorted_ranks[0], sorted_ranks[0] + 5)):
        is_straight = True
        straight_high = sorted_ranks[4]  # La carta más alta
    
    # Escalera A-2-3-4-5 (As bajo)
    elif sorted_ranks == [2, 3, 4, 5, 14]:
        is_straight = True
        straight_high = 5  # En escalera baja, el 5 es la carta "alta"
    
    # Verificar si es color
    is_flush = len(set(suits)) == 1
    
    # Escalera real (A-K-Q-J-10 del mismo palo)
    if is_straight and is_flush and straight_high == 14:
        return (9, [14])
    
    # Escalera de color
    elif is_straight and is_flush:
        return (8, [straight_high])
    
    # Póker
    elif counts == [4, 1]:
        return (7, [rank_values[0], rank_values[1]])  # [cuatro_iguales, kicker]
    
    # Full house
    elif counts == [3, 2]:
        return (6, [rank_values[0], rank_values[1]])  # [trio, pareja]
    
    # Color
    elif is_flush:
        return (5, sorted(ranks, reverse=True))
    
    # Escalera
    elif is_straight:
        return (4, [straight_high])
    
    # Trío
    elif counts == [3, 1, 1]:
        return (3, [rank_values[0]] + sorted(rank_values[1:], reverse=True))
    
    # Doble pareja
    elif counts == [2, 2, 1]:
        pairs = sorted(rank_values[:2], reverse=True)
        return (2, pairs + [rank_values[2]])
    
    # Pareja
    elif counts == [2, 1, 1, 1]:
        return (1, [rank_values[0]] + sorted(rank_values[1:], reverse=True))
    
    # Carta alta
    else:
        return (0, sorted(ranks, reverse=True))

def mejor_mano(cartas):
    """Encuentra la mejor mano de 5 cartas posible con las cartas dadas"""
    if len(cartas) < 5:
        return (0, [0])
    
    mejor = (-1, [0])
    mejor_combo = None
    
    for combo in itertools.combinations(cartas, 5):
        valor = mano_valor(combo)
        if valor > mejor:
            mejor = valor
            mejor_combo = combo
    
    return mejor, mejor_combo

# ==============================
# IA de los Bots
# ==============================

def evaluar_fuerza_mano(cartas_privadas, cartas_mesa):
    """Evalúa la fuerza de una mano en una escala de 0-100"""
    total_cartas = cartas_privadas + cartas_mesa
    
    if len(total_cartas) < 5:
        # Pre-flop: evaluar solo cartas privadas
        return evaluar_preflop(cartas_privadas)
    
    # Post-flop: evaluar mejor mano posible
    valor, _ = mejor_mano(total_cartas)
    ranking, tiebreakers = valor
    
    # Convertir ranking a puntuación base
    puntuacion_base = {
        0: 10,   # Carta alta
        1: 25,   # Pareja
        2: 45,   # Doble pareja
        3: 60,   # Trío
        4: 75,   # Escalera
        5: 80,   # Color
        6: 90,   # Full house
        7: 95,   # Póker
        8: 98,   # Escalera de color
        9: 100   # Escalera real
    }
    
    puntuacion = puntuacion_base[ranking]
    
    # Ajustar por la altura de las cartas
    if ranking == 0:  # Carta alta
        puntuacion += min(15, tiebreakers[0] - 10)
    elif ranking == 1:  # Pareja
        puntuacion += min(10, (tiebreakers[0] - 8) * 2)
    elif ranking in [2, 3]:  # Doble pareja, trío
        puntuacion += min(8, (tiebreakers[0] - 10))
    
    return max(0, min(100, puntuacion))

def evaluar_preflop(cartas_privadas):
    """Evalúa la fuerza de las cartas iniciales (pre-flop)"""
    carta1, carta2 = cartas_privadas
    valor1, valor2 = RANK_VALUES[carta1[0]], RANK_VALUES[carta2[0]]
    palo1, palo2 = carta1[1], carta2[1]
    
    # Pareja
    if valor1 == valor2:
        if valor1 >= 10:  # Pareja alta (10, J, Q, K, A)
            return 85 + (valor1 - 10) * 3
        elif valor1 >= 7:  # Pareja media
            return 65 + (valor1 - 7) * 5
        else:  # Pareja baja
            return 45 + (valor1 - 2) * 4
    
    # Cartas del mismo palo (suited)
    suited_bonus = 15 if palo1 == palo2 else 0
    
    # Cartas consecutivas o casi consecutivas
    diferencia = abs(valor1 - valor2)
    if diferencia <= 4:
        conectadas_bonus = 10 - diferencia * 2
    else:
        conectadas_bonus = 0
    
    # Valor base por cartas altas
    valor_alto = max(valor1, valor2)
    valor_bajo = min(valor1, valor2)
    
    if valor_alto == 14:  # As
        if valor_bajo >= 10:  # A-K, A-Q, A-J, A-10
            puntuacion = 70 + (valor_bajo - 10) * 5
        else:
            puntuacion = 35 + (valor_bajo - 2) * 3
    elif valor_alto >= 11:  # Rey o Reina alta
        puntuacion = 25 + (valor_alto - 11) * 10 + (valor_bajo - 2) * 2
    else:
        puntuacion = 15 + (valor_alto - 2) * 2 + (valor_bajo - 2)
    
    return min(85, puntuacion + suited_bonus + conectadas_bonus)

def evaluar_pot_odds(pozo, costo_igualar):
    """Calcula las pot odds como porcentaje"""
    if costo_igualar == 0:
        return 100
    return (costo_igualar / (pozo + costo_igualar)) * 100

def decision_bot(nombre_bot, cartas_privadas, cartas_mesa, fichas_bot, apuesta_actual, pozo):
    """Toma una decisión inteligente para el bot"""
    if fichas_bot <= 0:
        return "retirado", 0
    
    fuerza_mano = evaluar_fuerza_mano(cartas_privadas, cartas_mesa)
    pot_odds = evaluar_pot_odds(pozo, apuesta_actual)
    
    # Personalidades de los bots
    personalidades = {
        "Bot1": {"agresividad": 1.1, "conservador": 0.9, "bluff": 0.05},    # Agresivo
        "Bot2": {"agresividad": 0.8, "conservador": 1.2, "bluff": 0.02},    # Conservador
        "Bot3": {"agresividad": 1.0, "conservador": 1.0, "bluff": 0.08},    # Balanced con bluffs
        "Bot4": {"agresividad": 0.9, "conservador": 1.1, "bluff": 0.03},    # Ligeramente conservador
    }
    
    personalidad = personalidades.get(nombre_bot, personalidades["Bot1"])
    fuerza_ajustada = fuerza_mano * personalidad["agresividad"]
    
    # Decisión de retirarse
    umbral_retiro = 25 * personalidad["conservador"]
    if apuesta_actual > fichas_bot * 0.3:  # Si la apuesta es muy alta
        umbral_retiro += 15
    
    if fuerza_ajustada < umbral_retiro and apuesta_actual > 0:
        if random.random() < 0.8:  # 80% probabilidad de retirarse con mano débil
            return "retirarse", 0
    
    # Bluff ocasional
    if random.random() < personalidad["bluff"] and len(cartas_mesa) >= 3:
        fuerza_ajustada += random.randint(20, 40)
    
    # Decisiones basadas en la fuerza de la mano
    if fuerza_ajustada >= 80:  # Mano muy fuerte
        if random.random() < 0.7:  # 70% subir fuerte
            if apuesta_actual == 0:
                # Sin apuesta previa, apostar entre 3-8 fichas
                subida = random.randint(3, min(8, fichas_bot // 4))
            else:
                # Con apuesta previa, subir entre 1x y 3x la apuesta actual
                max_subida = min(fichas_bot - apuesta_actual, apuesta_actual * 3)
                min_subida = max(2, apuesta_actual // 2)
                if max_subida >= min_subida:
                    subida = random.randint(min_subida, max_subida)
                else:
                    subida = 2
            return "subir", max(2, subida)
        else:
            return "igualar", 0
    
    elif fuerza_ajustada >= 60:  # Mano fuerte
        if random.random() < 0.4:  # 40% subir moderado
            if apuesta_actual == 0:
                # Sin apuesta previa, apostar pequeño
                subida = random.randint(2, min(5, fichas_bot // 6))
            else:
                # Con apuesta previa, subir moderadamente
                max_subida = min(fichas_bot - apuesta_actual, apuesta_actual * 2)
                min_subida = 2
                if max_subida >= min_subida:
                    subida = random.randint(min_subida, max_subida)
                else:
                    subida = 2
            return "subir", max(2, subida)
        else:
            return "igualar", 0
    
    elif fuerza_ajustada >= 35:  # Mano decente
        if apuesta_actual == 0:  # Sin apuesta que igualar
            if random.random() < 0.2:  # 20% apostar pequeño
                subida = random.randint(2, min(3, fichas_bot // 10))
                return "subir", subida
            else:
                return "igualar", 0
        elif pot_odds < 30:  # Buenas pot odds
            return "igualar", 0
        else:
            if random.random() < 0.3:
                return "retirarse", 0
            else:
                return "igualar", 0
    
    else:  # Mano débil
        if apuesta_actual == 0:  # Check gratis
            return "igualar", 0
        elif pot_odds < 20:  # Pot odds excelentes
            return "igualar", 0
        else:
            return "retirarse", 0

# ==============================
# Análisis educativo
# ==============================

def analizar_jugada_educativo(accion_jugador, fuerza_mano, pot_odds, fase, cartas_privadas, mesa, apuesta_actual, pozo):
    """Proporciona análisis educativo de la jugada del jugador"""
    analisis = []
    
    # Análisis de la fuerza de la mano
    if fuerza_mano >= 80:
        fortaleza = "muy fuerte"
        color_fortaleza = "\033[92m"  # Verde
    elif fuerza_mano >= 60:
        fortaleza = "fuerte"
        color_fortaleza = "\033[93m"  # Amarillo
    elif fuerza_mano >= 35:
        fortaleza = "decente"
        color_fortaleza = "\033[96m"  # Cian
    else:
        fortaleza = "débil"
        color_fortaleza = "\033[91m"  # Rojo
    
    analisis.append(f"📊 Fuerza de tu mano: {color_fortaleza}{fuerza_mano:.0f}/100 ({fortaleza})\033[0m")
    
    # Análisis de pot odds si hay apuesta
    if apuesta_actual > 0:
        analisis.append(f"💰 Pot odds: {pot_odds:.1f}% (necesitas ganar 1 de cada {100/pot_odds:.1f} veces para ser rentable)")
    
    # Análisis específico por acción
    if "subir" in accion_jugador.lower() or "subió" in accion_jugador.lower():
        if fuerza_mano >= 70:
            analisis.append("✅ Buena subida con mano fuerte - construyes el pozo con ventaja")
        elif fuerza_mano >= 50:
            analisis.append("⚠️  Subida arriesgada - considera si tus oponentes pueden tener mejor mano")
        else:
            analisis.append("🎯 ¿Bluff? Con mano débil, solo funciona si los oponentes se retiran")
    
    elif "igualar" in accion_jugador.lower() or "igualó" in accion_jugador.lower():
        if apuesta_actual == 0:
            analisis.append("✅ Check correcto - ver la siguiente carta gratis es siempre bueno")
        elif pot_odds < 25 and fuerza_mano >= 30:
            analisis.append("✅ Call correcto - buenas pot odds justifican el riesgo")
        elif fuerza_mano < 25:
            analisis.append("⚠️  Call arriesgado con mano débil - considera retirarte")
        else:
            analisis.append("✅ Call razonable - tienes chances de mejorar o ganar")
    
    elif "retirar" in accion_jugador.lower() or "retiró" in accion_jugador.lower():
        if fuerza_mano < 30 and apuesta_actual > 0:
            analisis.append("✅ Retiro inteligente - conservas fichas para mejores oportunidades")
        elif fuerza_mano >= 50:
            analisis.append("⚠️  Retiro conservador - quizás podrías haber competido")
        else:
            analisis.append("✅ Retiro prudente - evitas perder más fichas")
    
    # Consejos específicos por fase del juego
    if fase == "pre-flop":
        if len(set([c[0] for c in cartas_privadas])) == 1:  # Pareja
            analisis.append("💡 Consejo: Las parejas son manos premium en pre-flop")
        elif cartas_privadas[0][1] == cartas_privadas[1][1]:  # Suited
            analisis.append("💡 Consejo: Cartas del mismo palo tienen más potencial de color")
    elif fase == "flop":
        analisis.append("💡 Consejo: El flop define gran parte de tu mano - evalúa tus draws")
    elif fase == "turn":
        analisis.append("💡 Consejo: Solo una carta más por venir - calcula tus 'outs'")
    elif fase == "river":
        analisis.append("💡 Consejo: Tu mano ya está definida - evalúa solo su fuerza actual")
    
    return analisis

def mostrar_analisis_final_mano(acciones_jugador, fuerza_final, resultado, fichas_ganadas_perdidas):
    """Muestra un análisis completo al final de cada mano"""
    print("\n" + "="*60)
    print("📚 ANÁLISIS EDUCATIVO DE LA MANO")
    print("="*60)
    
    # Resumen de acciones
    print(f"📋 Tus acciones en esta mano:")
    for fase, accion in acciones_jugador.items():
        print(f"   {fase}: {accion}")
    
    print(f"\n🎯 Fuerza final de tu mano: {fuerza_final:.0f}/100")
    
    # Resultado
    if fichas_ganadas_perdidas > 0:
        print(f"💰 Resultado: +{fichas_ganadas_perdidas} fichas - ¡Bien jugado!")
    elif fichas_ganadas_perdidas < 0:
        print(f"💸 Resultado: {fichas_ganadas_perdidas} fichas")
    else:
        print("🤝 Resultado: Empate - No perdiste ni ganaste fichas")
    
    # Lecciones aprendidas
    print(f"\n📖 LECCIONES DE ESTA MANO:")
    
    if resultado == "ganaste":
        if fuerza_final >= 70:
            print("   ✅ Excelente - Ganaste con una mano fuerte como debía ser")
        elif fuerza_final >= 40:
            print("   🎲 Interesante - Ganaste con mano decente, ¿fue suerte o buen juego?")
        else:
            print("   🎯 ¡Bluff exitoso! - Ganaste con mano débil, pero no abuses de esta táctica")
    
    elif resultado == "perdiste":
        if fuerza_final < 30:
            print("   💡 Normal - Con mano débil es difícil ganar, considera retirarte antes")
        elif fuerza_final >= 60:
            print("   🎲 Mala suerte - Tenías buena mano pero el oponente tenía mejor")
        else:
            print("   ⚖️  Situación límite - Con mano decente a veces se gana, a veces se pierde")
    
    elif resultado == "se_retiraron":
        print("   🏆 ¡Éxito! - Los oponentes se retiraron, no importa qué mano tenías")
    
    elif resultado == "te_retiraste":
        if fuerza_final < 25:
            print("   ✅ Decisión correcta - Con mano muy débil, retirarse ahorra fichas")
        elif fuerza_final >= 50:
            print("   ⚠️  Quizás muy conservador - Tenías una mano competitiva")
        else:
            print("   🤔 Decisión borderline - Con mano decente puedes jugar o retirarte")
    
    print("="*60)
    input("Presiona Enter para continuar...")

# ==============================
# Sistema de dealer y blinds
# ==============================

def determinar_posiciones(jugadores_activos, dealer_pos):
    """Determina las posiciones de small blind y big blind"""
    num_jugadores = len(jugadores_activos)
    if num_jugadores < 2:
        return None, None
    
    small_blind_pos = (dealer_pos + 1) % num_jugadores
    big_blind_pos = (dealer_pos + 2) % num_jugadores if num_jugadores > 2 else (dealer_pos + 1) % num_jugadores
    
    return small_blind_pos, big_blind_pos

def mostrar_posiciones(jugadores_activos, dealer_pos, small_blind_pos, big_blind_pos):
    """Muestra las posiciones en la mesa"""
    print("🎯 Posiciones en la mesa:")
    for i, jugador in enumerate(jugadores_activos):
        emblemas = []
        if i == dealer_pos:
            emblemas.append("🔘 DEALER")
        if i == small_blind_pos:
            emblemas.append("💰 SB")
        if i == big_blind_pos:
            emblemas.append("💰💰 BB")
        
        emblema_str = " " + " ".join(emblemas) if emblemas else ""
        print(f"   {jugador}{emblema_str}")
    print()

# ==============================
# Juego
# ==============================

def ronda_apuestas(jugadores, fichas, apuesta_actual, pozo, jugadores_retirados, manos, mesa, fase="", acciones_jugador=None):
    """Maneja una ronda de apuestas"""
    acciones = {}
    jugadores_activos = [j for j in jugadores if j not in jugadores_retirados and fichas[j] > 0]
    
    for jugador in jugadores_activos:
        if jugador == "Tú":
            # Mostrar información útil para el jugador humano
            if mesa:
                tu_fuerza = evaluar_fuerza_mano(manos["Tú"], mesa)
                pot_odds = evaluar_pot_odds(pozo, apuesta_actual) if apuesta_actual > 0 else 0
                print(f"\nFuerza de tu mano: {tu_fuerza:.0f}/100")
                if apuesta_actual > 0:
                    print(f"Pot odds: {pot_odds:.1f}%")
            
            print(f"Tu turno - Fichas: {fichas['Tú']} | Apuesta a igualar: {apuesta_actual} | Pozo: {pozo}")
            while True:
                accion = input("[C]allar/Igualar / [S]ubir / [R]etirarse / [Q]uit: ").strip().lower()
                if accion == 'q':
                    print("\n¡Hasta la próxima!")
                    sys.exit(0)
                elif accion == 's':
                    try:
                        subida = int(input("¿Cuánto quieres subir?: "))
                        if subida > fichas["Tú"] - apuesta_actual:
                            print("No tienes suficientes fichas!")
                            continue
                        total_apuesta = apuesta_actual + subida
                        fichas["Tú"] -= total_apuesta
                        pozo += total_apuesta
                        apuesta_actual += subida
                        accion_desc = f"subió {subida}"
                        acciones[jugador] = accion_desc
                        
                        # Guardar para análisis
                        if acciones_jugador is not None:
                            acciones_jugador[fase] = accion_desc
                        break
                    except ValueError:
                        print("Por favor ingresa un número válido.")
                elif accion == 'c':
                    if apuesta_actual > fichas["Tú"]:
                        print("No tienes suficientes fichas para igualar!")
                        continue
                    fichas["Tú"] -= apuesta_actual
                    pozo += apuesta_actual
                    accion_desc = "igualó" if apuesta_actual > 0 else "pasó"
                    acciones[jugador] = accion_desc
                    
                    # Guardar para análisis
                    if acciones_jugador is not None:
                        acciones_jugador[fase] = accion_desc
                    break
                elif accion == 'r':
                    jugadores_retirados.add(jugador)
                    accion_desc = "se retiró"
                    acciones[jugador] = accion_desc
                    
                    # Guardar para análisis
                    if acciones_jugador is not None:
                        acciones_jugador[fase] = accion_desc
                    break
                else:
                    print("Acción no válida. Usa C, S, R o Q.")
        else:
            # IA mejorada para los bots
            decision, cantidad = decision_bot(jugador, manos[jugador], mesa, fichas[jugador], apuesta_actual, pozo)
            
            if decision == "retirarse":
                jugadores_retirados.add(jugador)
                acciones[jugador] = "se retiró"
            elif decision == "subir":
                if fichas[jugador] >= apuesta_actual + cantidad:
                    total_apuesta = apuesta_actual + cantidad
                    fichas[jugador] -= total_apuesta
                    pozo += total_apuesta
                    apuesta_actual += cantidad
                    acciones[jugador] = f"subió {cantidad}"
                else:
                    # No tiene suficientes fichas para subir, iguala o se retira
                    if fichas[jugador] >= apuesta_actual:
                        fichas[jugador] -= apuesta_actual
                        pozo += apuesta_actual
                        acciones[jugador] = "igualó" if apuesta_actual > 0 else "pasó"
                    else:
                        jugadores_retirados.add(jugador)
                        acciones[jugador] = "se retiró (sin fichas)"
            else:  # igualar
                if fichas[jugador] >= apuesta_actual:
                    fichas[jugador] -= apuesta_actual
                    pozo += apuesta_actual
                    acciones[jugador] = "igualó" if apuesta_actual > 0 else "pasó"
                else:
                    jugadores_retirados.add(jugador)
                    acciones[jugador] = "se retiró (sin fichas)"
    
    return apuesta_actual, pozo, acciones

def mostrar_resultados_finales(jugadores_activos, manos, mesa, resultados):
    """Muestra los resultados finales con detalles de las manos"""
    print("=== SHOWDOWN ===")
    print(f"Cartas de la mesa: {formatear_cartas(mesa)}")
    print()
    
    for jugador in jugadores_activos:
        valor, mejor_combo = resultados[jugador]
        tipo_mano = HAND_ORDER_EXAMPLES[valor[0]][0]
        
        # Mostrar información detallada de tiebreakers
        tiebreaker_info = ""
        if valor[0] == 1:  # Pareja
            tiebreaker_info = f" (Pareja de {RANKS[valor[1][0]-2]}s, kickers: {', '.join([RANKS[k-2] for k in valor[1][1:]])})"
        elif valor[0] == 2:  # Doble pareja
            tiebreaker_info = f" (Parejas de {RANKS[valor[1][0]-2]}s y {RANKS[valor[1][1]-2]}s, kicker: {RANKS[valor[1][2]-2]})"
        elif valor[0] == 3:  # Trío
            tiebreaker_info = f" (Trío de {RANKS[valor[1][0]-2]}s, kickers: {', '.join([RANKS[k-2] for k in valor[1][1:]])})"
        elif valor[0] == 0:  # Carta alta
            tiebreaker_info = f" ({RANKS[valor[1][0]-2]} alta)"
        elif valor[0] in [4, 8]:  # Escalera o escalera de color
            high_card = "5" if valor[1][0] == 5 else RANKS[valor[1][0]-2]
            tiebreaker_info = f" (hasta {high_card})"
        elif valor[0] == 5:  # Color
            tiebreaker_info = f" ({RANKS[valor[1][0]-2]} alta)"
        elif valor[0] == 6:  # Full house
            tiebreaker_info = f" ({RANKS[valor[1][0]-2]}s llenos de {RANKS[valor[1][1]-2]}s)"
        elif valor[0] == 7:  # Póker
            tiebreaker_info = f" (Cuatro {RANKS[valor[1][0]-2]}s)"
        
        print(f"{jugador}:")
        print(f"  Cartas privadas: {formatear_cartas(manos[jugador])}")
        print(f"  Mejor mano: {formatear_cartas(mejor_combo)} -> {tipo_mano}{tiebreaker_info}")
        print()

def determinar_ganadores(jugadores_activos, resultados):
    """Determina los ganadores manejando empates correctamente"""
    # Encontrar el mejor valor de mano
    mejor_valor = max(resultados.values(), key=lambda x: x[0])
    
    # Encontrar todos los jugadores con el mejor tipo de mano
    candidatos = [j for j in jugadores_activos if resultados[j][0][0] == mejor_valor[0][0]]
    
    if len(candidatos) == 1:
        return candidatos
    
    # Si hay múltiples candidatos, comparar tiebreakers
    mejor_tiebreakers = mejor_valor[0][1]
    ganadores_finales = []
    
    for jugador in candidatos:
        tiebreakers = resultados[jugador][0][1]
        if tiebreakers == mejor_tiebreakers:
            ganadores_finales.append(jugador)
    
    return ganadores_finales if ganadores_finales else candidatos

def jugar():
    # Configurar el manejador de señales para Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    clear()
    print("=== Póker Texas Hold'em ===")
    mostrar_orden_manos()
    input("Presiona Enter para comenzar...")

    # Orden aleatorio de jugadores
    jugadores_base = ["Tú", "Bot1", "Bot2", "Bot3", "Bot4"]
    random.shuffle(jugadores_base)
    jugadores = jugadores_base
    
    fichas = {j: 100 for j in jugadores}
    mano_numero = 1
    
    # Posición inicial del dealer (aleatoria)
    dealer_pos = random.randint(0, len(jugadores) - 1)
    
    print(f"\n🎲 Orden aleatorio de jugadores: {' -> '.join(jugadores)}")
    input("Presiona Enter para continuar...")

    while fichas["Tú"] > 0:
        clear()
        print(f"=== MANO #{mano_numero} ===")
        
        # Determinar jugadores activos (con fichas)
        jugadores_activos = [j for j in jugadores if fichas[j] > 0]
        if len(jugadores_activos) < 2:
            print("No hay suficientes jugadores activos para continuar.")
            break
        
        # Ajustar posición del dealer si es necesario
        if dealer_pos >= len(jugadores_activos):
            dealer_pos = 0
        
        # Determinar posiciones de blinds
        small_blind_pos, big_blind_pos = determinar_posiciones(jugadores_activos, dealer_pos)
        
        print("Fichas actuales:")
        for j in jugadores_activos:
            print(f"  {j}: {fichas[j]} fichas")
        print()
        
        # Mostrar posiciones
        mostrar_posiciones(jugadores_activos, dealer_pos, small_blind_pos, big_blind_pos)
        
        baraja = crear_baraja()
        random.shuffle(baraja)

        # Repartir cartas
        manos = {}
        for j in jugadores_activos:
            manos[j] = [baraja.pop(), baraja.pop()]
        
        mesa = []
        pozo = 0
        jugadores_retirados = set()
        
        # Cobrar blinds
        small_blind = 1
        big_blind = 2
        
        sb_jugador = jugadores_activos[small_blind_pos]
        bb_jugador = jugadores_activos[big_blind_pos]
        
        # Cobrar small blind
        sb_amount = min(small_blind, fichas[sb_jugador])
        fichas[sb_jugador] -= sb_amount
        pozo += sb_amount
        
        # Cobrar big blind
        bb_amount = min(big_blind, fichas[bb_jugador])
        fichas[bb_jugador] -= bb_amount
        pozo += bb_amount
        
        apuesta_actual = big_blind
        
        print(f"💰 {sb_jugador} paga small blind: {sb_amount}")
        print(f"💰💰 {bb_jugador} paga big blind: {bb_amount}")
        print()
        
        # Tracking para análisis educativo
        acciones_jugador = {}
        fichas_iniciales_tu = fichas["Tú"]

        # PRE-FLOP
        clear()
        print("=== PRE-FLOP ===")
        print(f"Tus cartas: {formatear_cartas(manos['Tú'])}")
        apuesta_actual, pozo, acciones = ronda_apuestas(jugadores_activos, fichas, apuesta_actual, pozo, jugadores_retirados, manos, mesa, "PRE-FLOP", acciones_jugador)
        for j, acc in acciones.items():
            if j != "Tú":
                print(f"{j} {acc}")
        
        # Mostrar análisis si el jugador humano participó
        if "Tú" in acciones and "Tú" not in jugadores_retirados:
            fuerza_preflop = evaluar_fuerza_mano(manos['Tú'], mesa)
            pot_odds = evaluar_pot_odds(pozo, apuesta_actual) if apuesta_actual > 0 else 0
            analisis = analizar_jugada_educativo(acciones["Tú"], fuerza_preflop, pot_odds, "pre-flop", manos['Tú'], mesa, apuesta_actual, pozo)
            print(f"\n📊 ANÁLISIS DE TU JUGADA:")
            for punto in analisis:
                print(f"   {punto}")
        
        jugadores_activos = [j for j in jugadores_activos if j not in jugadores_retirados and fichas[j] >= 0]
        if len(jugadores_activos) <= 1:
            if jugadores_activos:
                ganador = jugadores_activos[0]
                fichas[ganador] += pozo
                print(f"\n🏆 {ganador} gana por retiro de todos los demás - Pozo: {pozo} fichas")
                
                # Análisis educativo para el jugador
                if "Tú" in jugadores_retirados:
                    resultado_tipo = "te_retiraste"
                elif ganador == "Tú":
                    resultado_tipo = "se_retiraron"
                else:
                    resultado_tipo = "perdiste"
                    
                fichas_ganadas_perdidas = fichas["Tú"] - fichas_iniciales_tu
                fuerza_final = evaluar_fuerza_mano(manos['Tú'], mesa) if mesa else evaluar_preflop(manos['Tú'])
                mostrar_analisis_final_mano(acciones_jugador, fuerza_final, resultado_tipo, fichas_ganadas_perdidas)
            
            input("Enter para continuar...")
            mano_numero += 1
            dealer_pos = (dealer_pos + 1) % len([j for j in jugadores if fichas[j] > 0])
            continue
            
        input("Enter para continuar...")

        # FLOP
        mesa.extend([baraja.pop() for _ in range(3)])
        clear()
        print("=== FLOP ===")
        print(f"Mesa: {formatear_cartas(mesa)}")
        print(f"Tus cartas: {formatear_cartas(manos['Tú'])}")
        apuesta_actual = 0  # Reset apuesta para nueva ronda
        apuesta_actual, pozo, acciones = ronda_apuestas(jugadores_activos, fichas, apuesta_actual, pozo, jugadores_retirados, manos, mesa, "FLOP", acciones_jugador)
        for j, acc in acciones.items():
            if j != "Tú":
                print(f"{j} {acc}")
        
        # Análisis del flop
        if "Tú" in acciones and "Tú" not in jugadores_retirados:
            fuerza_flop = evaluar_fuerza_mano(manos['Tú'], mesa)
            pot_odds = evaluar_pot_odds(pozo, apuesta_actual) if apuesta_actual > 0 else 0
            analisis = analizar_jugada_educativo(acciones["Tú"], fuerza_flop, pot_odds, "flop", manos['Tú'], mesa, apuesta_actual, pozo)
            print(f"\n📊 ANÁLISIS DE TU JUGADA:")
            for punto in analisis:
                print(f"   {punto}")
        
        jugadores_activos = [j for j in jugadores_activos if j not in jugadores_retirados]
        if len(jugadores_activos) <= 1:
            if jugadores_activos:
                ganador = jugadores_activos[0]
                fichas[ganador] += pozo
                print(f"\n🏆 {ganador} gana por retiro - Pozo: {pozo} fichas")
                
                # Análisis educativo
                if "Tú" in jugadores_retirados:
                    resultado_tipo = "te_retiraste"
                elif ganador == "Tú":
                    resultado_tipo = "se_retiraron"
                else:
                    resultado_tipo = "perdiste"
                    
                fichas_ganadas_perdidas = fichas["Tú"] - fichas_iniciales_tu
                fuerza_final = evaluar_fuerza_mano(manos['Tú'], mesa)
                mostrar_analisis_final_mano(acciones_jugador, fuerza_final, resultado_tipo, fichas_ganadas_perdidas)
            
            input("Enter para continuar...")
            mano_numero += 1
            dealer_pos = (dealer_pos + 1) % len([j for j in jugadores if fichas[j] > 0])
            continue
            
        input("Enter para continuar...")

        # TURN
        mesa.append(baraja.pop())
        clear()
        print("=== TURN ===")
        print(f"Mesa: {formatear_cartas(mesa)}")
        print(f"Tus cartas: {formatear_cartas(manos['Tú'])}")
        apuesta_actual = 0
        apuesta_actual, pozo, acciones = ronda_apuestas(jugadores_activos, fichas, apuesta_actual, pozo, jugadores_retirados, manos, mesa, "TURN", acciones_jugador)
        for j, acc in acciones.items():
            if j != "Tú":
                print(f"{j} {acc}")
        
        # Análisis del turn
        if "Tú" in acciones and "Tú" not in jugadores_retirados:
            fuerza_turn = evaluar_fuerza_mano(manos['Tú'], mesa)
            pot_odds = evaluar_pot_odds(pozo, apuesta_actual) if apuesta_actual > 0 else 0
            analisis = analizar_jugada_educativo(acciones["Tú"], fuerza_turn, pot_odds, "turn", manos['Tú'], mesa, apuesta_actual, pozo)
            print(f"\n📊 ANÁLISIS DE TU JUGADA:")
            for punto in analisis:
                print(f"   {punto}")
        
        jugadores_activos = [j for j in jugadores_activos if j not in jugadores_retirados]
        if len(jugadores_activos) <= 1:
            if jugadores_activos:
                ganador = jugadores_activos[0]
                fichas[ganador] += pozo
                print(f"\n🏆 {ganador} gana por retiro - Pozo: {pozo} fichas")
                
                # Análisis educativo
                if "Tú" in jugadores_retirados:
                    resultado_tipo = "te_retiraste"
                elif ganador == "Tú":
                    resultado_tipo = "se_retiraron"
                else:
                    resultado_tipo = "perdiste"
                    
                fichas_ganadas_perdidas = fichas["Tú"] - fichas_iniciales_tu
                fuerza_final = evaluar_fuerza_mano(manos['Tú'], mesa)
                mostrar_analisis_final_mano(acciones_jugador, fuerza_final, resultado_tipo, fichas_ganadas_perdidas)
            
            input("Enter para continuar...")
            mano_numero += 1
            dealer_pos = (dealer_pos + 1) % len([j for j in jugadores if fichas[j] > 0])
            continue
            
        input("Enter para continuar...")

        # RIVER
        mesa.append(baraja.pop())
        clear()
        print("=== RIVER ===")
        print(f"Mesa: {formatear_cartas(mesa)}")
        print(f"Tus cartas: {formatear_cartas(manos['Tú'])}")
        apuesta_actual = 0
        apuesta_actual, pozo, acciones = ronda_apuestas(jugadores_activos, fichas, apuesta_actual, pozo, jugadores_retirados, manos, mesa, "RIVER", acciones_jugador)
        for j, acc in acciones.items():
            if j != "Tú":
                print(f"{j} {acc}")
        
        # Análisis del river
        if "Tú" in acciones and "Tú" not in jugadores_retirados:
            fuerza_river = evaluar_fuerza_mano(manos['Tú'], mesa)
            pot_odds = evaluar_pot_odds(pozo, apuesta_actual) if apuesta_actual > 0 else 0
            analisis = analizar_jugada_educativo(acciones["Tú"], fuerza_river, pot_odds, "river", manos['Tú'], mesa, apuesta_actual, pozo)
            print(f"\n📊 ANÁLISIS DE TU JUGADA:")
            for punto in analisis:
                print(f"   {punto}")
        
        jugadores_activos = [j for j in jugadores_activos if j not in jugadores_retirados]
        if len(jugadores_activos) <= 1:
            if jugadores_activos:
                ganador = jugadores_activos[0]
                fichas[ganador] += pozo
                print(f"\n🏆 {ganador} gana por retiro - Pozo: {pozo} fichas")
                
                # Análisis educativo
                if "Tú" in jugadores_retirados:
                    resultado_tipo = "te_retiraste"
                elif ganador == "Tú":
                    resultado_tipo = "se_retiraron"
                else:
                    resultado_tipo = "perdiste"
                    
                fichas_ganadas_perdidas = fichas["Tú"] - fichas_iniciales_tu
                fuerza_final = evaluar_fuerza_mano(manos['Tú'], mesa)
                mostrar_analisis_final_mano(acciones_jugador, fuerza_final, resultado_tipo, fichas_ganadas_perdidas)
            
            input("Enter para continuar...")
            mano_numero += 1
            dealer_pos = (dealer_pos + 1) % len([j for j in jugadores if fichas[j] > 0])
            continue
            
        input("Enter para continuar...")

        # SHOWDOWN
        if len(jugadores_activos) > 1:
            clear()
            resultados = {}
            for j in jugadores_activos:
                total_cartas = manos[j] + mesa
                valor, combo = mejor_mano(total_cartas)
                resultados[j] = (valor, combo)

            mostrar_resultados_finales(jugadores_activos, manos, mesa, resultados)
            
            ganadores = determinar_ganadores(jugadores_activos, resultados)
            
            if len(ganadores) == 1:
                ganador = ganadores[0]
                fichas[ganador] += pozo
                valor = resultados[ganador][0]
                tipo_mano = HAND_ORDER_EXAMPLES[valor[0]][0]
                print(f"🏆 Ganador: {ganador} con {tipo_mano}")
                print(f"💰 Pozo ganado: {pozo} fichas")
                
                # Determinar resultado para análisis
                if ganador == "Tú":
                    resultado_tipo = "ganaste"
                else:
                    resultado_tipo = "perdiste"
            else:
                # Empate - dividir el pozo
                pozo_por_ganador = pozo // len(ganadores)
                resto = pozo % len(ganadores)
                
                print(f"🤝 EMPATE entre: {', '.join(ganadores)}")
                valor = resultados[ganadores[0]][0]
                tipo_mano = HAND_ORDER_EXAMPLES[valor[0]][0]
                print(f"Todos con: {tipo_mano}")
                
                if resto == 0:
                    # División exacta
                    for ganador in ganadores:
                        fichas[ganador] += pozo_por_ganador
                    print(f"💰 Pozo dividido equitativamente: {pozo} fichas ({pozo_por_ganador} cada uno)")
                else:
                    # División con resto - las fichas extra van a los primeros jugadores alfabéticamente
                    ganadores_ordenados = sorted(ganadores)
                    for i, ganador in enumerate(ganadores_ordenados):
                        fichas_ganadas = pozo_por_ganador + (1 if i < resto else 0)
                        fichas[ganador] += fichas_ganadas
                    
                    print(f"💰 Pozo dividido: {pozo} fichas")
                    for i, ganador in enumerate(ganadores_ordenados):
                        fichas_extra = pozo_por_ganador + (1 if i < resto else 0)
                        extra_msg = " (+1 ficha extra)" if i < resto else ""
                        print(f"   {ganador}: {fichas_extra} fichas{extra_msg}")
                    
                    if resto > 0:
                        print(f"   (Las {resto} fichas de redondeo van a los primeros {resto} jugadores alfabéticamente)")
                
                # Determinar resultado para análisis
                if "Tú" in ganadores:
                    resultado_tipo = "empate"
                else:
                    resultado_tipo = "perdiste"

            # Análisis educativo final
            fichas_ganadas_perdidas = fichas["Tú"] - fichas_iniciales_tu
            fuerza_final = evaluar_fuerza_mano(manos['Tú'], mesa)
            mostrar_analisis_final_mano(acciones_jugador, fuerza_final, resultado_tipo, fichas_ganadas_perdidas)

        mano_numero += 1
        dealer_pos = (dealer_pos + 1) % len([j for j in jugadores if fichas[j] > 0])
        print(f"\nTus fichas restantes: {fichas['Tú']}")
        
        if fichas["Tú"] <= 0:
            print("¡Te has quedado sin fichas! Fin del juego.")
            break
            
        continuar = input("\n¿Jugar otra mano? ([S]í / [N]o / [Q]uit): ").strip().lower()
        if continuar == 'q':
            print("¡Hasta la próxima!")
            break
        elif continuar == 'n':
            break

    print(f"\n¡Gracias por jugar! Fichas finales: {fichas['Tú']}")

if __name__ == "__main__":
    jugar()
