Aquí tienes un **README.md** en formato Markdown para GitHub, con la descripción, el enfoque educativo, licencia y un mini tutorial de uso:

````markdown
# 🎲 Poker Educativo en Consola (Texas Hold'em)

Este proyecto es un **simulador de Texas Hold'em** para consola escrito en Python.  
El énfasis no está en "ganar dinero" ni en replicar un casino, sino en **aprender a tomar decisiones con información incompleta**, una de las habilidades centrales del póker y que también se aplica en otros contextos de la vida y el trabajo.

---

## ✨ Características principales

- **Juego contra bots**: 4 oponentes con diferentes estilos (agresivo, conservador, balanceado, con bluffs).  
- **Análisis educativo** en cada ronda y al final de cada mano:  
  - Evaluación de la fuerza de tu mano en escala 0–100.  
  - Cálculo de *pot odds*.  
  - Consejos sobre si tu jugada fue razonable, arriesgada o correcta.  
  - Lecciones específicas según la etapa de la mano (*pre-flop*, *flop*, *turn*, *river*).  
- **Rotación de dealer y blinds**, para reflejar el flujo real de la mesa.  
- **Orden aleatorio de jugadores** en cada partida.  
- **Visualización a color** de las cartas (rojo y blanco en terminal compatible).  
- **Salida elegante** con la tecla `Q` en cualquier turno.  

---

## 🎯 Objetivo educativo

El juego busca **entrenar la toma de decisiones con información parcial**, tal como ocurre en el póker real:  

- Aprender cuándo retirarse, igualar o subir una apuesta.  
- Reconocer manos fuertes, medias o débiles.  
- Entender cómo el azar y la estrategia de los oponentes influyen en el resultado.  
- Reflexionar sobre el balance entre **riesgo, probabilidad y recompensa**.  

Más que "ganar", el propósito es **mejorar la intuición y el criterio estratégico**.

---

## 🚀 Cómo usarlo

### Requisitos
- Python 3.8 o superior.  
- Sistema operativo con consola (Linux, macOS, Windows).  

### Ejecución
Clona el repositorio y ejecuta:

```bash
python3 poker.py
````

### Controles en tu turno

* `[C]` → Call / Pasar (igualar la apuesta o pasar si es gratis).
* `[S]` → Subir (apostar más fichas).
* `[R]` → Retirarse.
* `[Q]` → Salir del juego en cualquier momento.

---

## 📖 Ejemplo de flujo de juego

1. Se muestra el **orden aleatorio de jugadores**.
2. Cada mano comienza con **blinds** automáticos.
3. En cada fase (*pre-flop, flop, turn, river*):

   * Ves tus cartas y las de la mesa.
   * Decides si **call**, **subir** o **retirarte**.
   * El sistema da un **análisis inmediato de tu jugada**.
4. Al final de la mano, un **análisis completo** resume tus decisiones y resultados.

---

## 📜 Licencia

Este software se distribuye bajo la siguiente licencia abierta:

* **Permisos**: Usar, modificar y compartir libremente.
* **Restricciones**: **No se permite la comercialización sin autorización explícita del autor**.
* **Atribución**: Se recomienda mantener referencia al autor original en proyectos derivados.

En otras palabras:

> "Úsalo, cámbialo y mejóralo, pero no lo vendas sin permiso."

---

## 🧩 Próximos pasos sugeridos

* Agregar más personalidades de bots.
* Implementar niveles de dificultad.
* Guardar estadísticas de manos jugadas y decisiones.
* Incluir un modo *torneo*.

---

¡Diviértete aprendiendo y mejorando tu intuición en el póker! 🃏

