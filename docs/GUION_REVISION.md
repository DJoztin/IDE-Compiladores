# Guion para la revisión — generación de código y ejecución en la TM

**Para:** el equipo, el día de la revisión. Por cada programa de la docente:
1 punto si el IDE **muestra el `.tm` correcto** y 1 punto si **se ejecuta en la TM** con resultados correctos.

## Antes de empezar (2 minutos)

1. Abrir `dist/Ide.exe` (o `python ide_compilador.py`).
2. Opcional: `python pruebas/run_tests.py` debe terminar en `TODAS LAS PRUEBAS PASARON`.
3. Tener a la mano `pruebas/programas/` como respaldo (hay 30 programas de ejercicios con entradas y salidas esperadas).

## Flujo por cada programa (los 7 pasos)

| # | Paso | Qué hacer en el IDE | Qué se ve |
|---|---|---|---|
| 1 | Escribir / cargar el fuente | **Ctrl+N** y escribir, o **Ctrl+O** para abrir | el editor con el programa |
| 2 | Compilar | **F8** (Cod. Intermedio). Guarda el archivo y corre léxico → sintáctico → semántico → generación | barra inferior: `Código generado: N instrucciones` |
| 3 | Árbol válido | pestaña **Sintactico** (árbol) y **Semantico** (árbol anotado); **Errores Semanticos** dice `(sin errores)` | árbol y tabla de símbolos llenos |
| 4 | Generar `.tm` | ya lo hizo F8: `programa.tm` y `programa.ci` quedan junto al fuente | — |
| 5 | Ver el `.tm` y el `.ci` | pestaña **Código Intermedio** → sub-pestaña **Código TM (.tm)**: vista *Tabla* (Dir · Instrucción · Operandos · Comentario) o *Archivo* (el texto tal cual, estilo TINY). Sub-pestaña **Código intermedio de tres direcciones (.ci)** | direcciones, instrucciones y operandos |
| 6 | Ejecutar en la TM | **F9** (o ▶ Ejecutar). Recompila y carga en la TM el `.tm` recién generado. Cuando aparece `Ingrese un numero (IN):` escribir el valor en la línea de abajo y **Enter** | pestaña **Máquina TM (ejecución)** |
| 7 | Comprobar el resultado | `Resultado del programa (OUT): …` y `Ejecucion finalizada (HALT)`; a la derecha registros y memoria de variables | valores finales de cada variable |

Extras que se pueden mostrar si la docente lo pide (en la línea de comandos de la TM, igual que `tm.exe`):
`h` ayuda · `v` ver el `.ci` · `i 0 10` ver instrucciones · `d 0 5` ver memoria · `r` registros ·
`s` / botón **Paso** para ir instrucción por instrucción (la fila del `pc` se resalta en la tabla del `.tm`) ·
`t` rastreo · `p` contar instrucciones · `c` reiniciar.

Si el programa tiene un error: no se genera código, el panel dice `No se generó código: hay errores` y se abre la pestaña de errores. Al editar el fuente después de compilar, los paneles muestran `⚠ desactualizado` hasta volver a compilar.

## Checklist de prueba manual (hacerla antes de la revisión)

Programa A — `pruebas/oro/factorial.txt`:
- [ ] F8 → la tabla del `.tm` tiene 42 instrucciones (0–41); la vista *Archivo* muestra la 13 después de la 39.
- [ ] El `.ci` coincide con `referencia/Tiny_Intermedio_TM/ejemplos/factorial.ci`.
- [ ] F9 → pide un número; con `5` muestra `Resultado del programa (OUT): 120` y `Ejecucion finalizada (HALT)`.
- [ ] Memoria de variables: `x = 0`, `fact = 120`.
- [ ] Botón **Paso** avanza una instrucción y resalta su fila.

Programa B — `pruebas/programas/13_votos.txt` (reales y varias entradas):
- [ ] F9 con entradas `1 2 2 4 1 2 3 2 0` → `2 4 1 1 25.0 50.0 12.5 12.5`.
- [ ] Escribir `abc` cuando pide IN → `Illegal value` y vuelve a pedir.

Errores y coherencia:
- [ ] Cambiar `cout(fact)` por `cout(z)` y F8 → no hay código, pestaña Errores Semanticos abierta, el `.tm` viejo se borró.
- [ ] Escribir algo en el editor tras compilar → aviso `⚠ desactualizado` y **Paso** deshabilitado.
- [ ] `while (i == 0) { i = 0; };` → F9 y luego **■ Detener**: la ejecución se detiene y el IDE responde.

---

## Ejemplo explicado (asignación → TM y `.ci`)

Programa: `int x, y;  cin(x);  y = (x + 1) * (x - 2);  cout y;`   (`x` en loc 0, `y` en loc 1)

```
  4:     LD  0,0(5) 	load id value        ac = x
  5:     ST  0,0(6) 	op: push left        temporal 0(mp) = x
  6:    LDC  0,1(0) 	load const           ac = 1
  7:     LD  1,0(6) 	op: load left        ac1 = x
  8:    ADD  0,1,0 	op +                 ac = x + 1
  9:     ST  0,0(6) 	op: push left        temporal 0(mp) = x + 1
 10:     LD  0,0(5) 	load id value        ac = x
 11:     ST  0,-1(6) 	op: push left        temporal -1(mp) = x  (tmpOffset bajó)
 12:    LDC  0,2(0) 	load const           ac = 2
 13:     LD  1,-1(6) 	op: load left        ac1 = x
 14:    SUB  0,1,0 	op -                 ac = x - 2
 15:     LD  1,0(6) 	op: load left        ac1 = x + 1
 16:    MUL  0,1,0 	op *                 ac = (x + 1) * (x - 2)
 17:     ST  0,1(5) 	assign: store value  y = ac
```

`.ci` del mismo fuente (mismo árbol, recorrido en postorden):

```
read x
t1 = x + 1
t2 = x - 2
t3 = t1 * t2
y = t3
write y
```

## Cómo se resuelven los saltos (`emitSkip` / `emitBackup`)

Al generar un `while` todavía no se sabe a dónde saltar cuando la condición es falsa, porque el cuerpo no se ha generado. Programa: `i = 0; while (i < 3) { i++; };`

1. `inicio = emitSkip(0)` → recuerda la dirección 4, donde empieza la condición.
2. Se genera la condición (direcciones 4–12; deja 1 o 0 en `ac`).
3. `salto = emitSkip(1)` → **reserva** la dirección 13 sin escribirla.
4. Se genera el cuerpo (14–19) y `LDA 7,-17(7)` en la 20: vuelve a la condición (20 + 1 − 17 = 4).
5. `fin = emitSkip(0)` = 21. `emitBackup(13)` regresa a la dirección reservada y
   `emitRM_Abs("JEQ", ac, 21)` escribe `13: JEQ 0,7(7)` (13 + 1 + 7 = 21: si la condición es 0, sale del ciclo).
6. `emitRestore()` vuelve a la 21 para seguir generando.

Por eso en el archivo `.tm` la línea 13 aparece **después** de la 20: se escribe en orden de emisión, igual que en `factorial.tm` de TINY. El `if` usa exactamente el mismo mecanismo (dos huecos: salto al `else` y salto al final).
