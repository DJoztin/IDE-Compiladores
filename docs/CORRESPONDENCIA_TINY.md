# Correspondencia con TINY (Louden) — generación de código y máquina TM

**Proyecto:** IDE-Compiladores · Compiladores II, UAA · Equipo Carabez · Pastrana · Salas (9B)

El generador de código y la máquina TM de este proyecto son un **port a Python** del
compilador TINY de Kenneth C. Louden, en la versión que entregó la docente
(`referencia/Tiny_Intermedio_TM`). Se conservan el algoritmo, el juego de instrucciones,
los registros y el formato de archivo. Lo nuevo (tipos reales, `while`, operadores
relacionales y lógicos extra, `%` y `^`) se generó **sin agregar instrucciones a la TM**.

---

## 1. Archivo por archivo

| TINY (C) | Este proyecto (Python) | Qué hace |
|---|---|---|
| `code.h` / `code.c` | `code_tm.py` (`EmisorTM`) | `emitComment`, `emitRO`, `emitRM`, `emitSkip`, `emitBackup`, `emitRestore`, `emitRM_Abs`. Mismo formato de línea (`%3d:  %5s  ...`). |
| `cgen.c` | `cgen.py` (`GeneradorTM`, `generar_codigo_tm`) | Recorre el árbol y emite TM. Mismo esquema: resultado en `ac`, temporales en `tmpOffset(mp)`, backpatching. |
| `intermedio.c` | `intermedio.py` (`generar_codigo_intermedio`) | Código de tres direcciones (`.ci`) en postorden con `tN` y `LN`. |
| `tm.c` | `tm.py` (`MaquinaTM`, `ConsolaTM`) | Simulador TM: lector del `.tm`, `stepTM`, comandos `h v i d r s g t p c q`. |
| `main.c` | `compilador.py` → `compilar()` | Analiza; sólo si no hay errores genera `.tm` y `.ci` en paralelo desde el árbol validado. |
| `symtab.c` (`st_lookup`) | `TablaSimbolos.buscar(nombre).loc` | Dirección de cada variable (0, 1, 2… en orden de declaración). |
| `analyze.c` | `AnalizadorSemantico` (`compilador.py`) | Tabla de símbolos y verificación de tipos; produce el **árbol anotado** que usa el generador. |

Registros (iguales a `code.h`): `ac = 0`, `ac1 = 1`, `gp = 5`, `mp = 6`, `pc = 7`.
Instrucciones (iguales a `tm.c`): `HALT IN OUT ADD SUB MUL DIV` (RO) y
`LD ST LDA LDC JLT JLE JGT JGE JEQ JNE` (RM). **Ninguna nueva.**

---

## 2. Nodo del árbol → TINY → código TM

| Nodo nuestro | Equivalente TINY | Código TM generado |
|---|---|---|
| `programa`, `lista_sentencias`, `then_branch`, `else_branch` | recorrido de `sibling` en `cGen` | genera los hijos en orden |
| `declaracion` | — (TINY no declara) | sin código; sólo comentario `* declaracion int x, y (loc 0, 1)` |
| `entero` / `real_lit` | `ConstK` | `LDC ac,valor(0)` "load const" |
| `booleano` | — | `LDC ac,1(0)` (true) / `LDC ac,0(0)` (false) |
| `identificador` en expresión | `IdK` | `LD ac,loc(gp)` "load id value" |
| `factor_par` | — | genera el hijo (sin código propio) |
| `negativo` | — | hijo; `LDC ac1,0(0)`; `SUB ac,ac1,ac` |
| `expresion` `+ −`, `termino` `* /` | `OpK` PLUS MINUS TIMES OVER | izq; `ST ac,tmp--(mp)`; der; `LD ac1,++tmp(mp)`; `ADD/SUB/MUL/DIV ac,ac1,ac` |
| `expr_rel` `<` | `OpK` LT | `SUB ac,ac1,ac`; `JLT ac,2(pc)`; `LDC ac,0(ac)`; `LDA pc,1(pc)`; `LDC ac,1(ac)` (idéntico) |
| `expr_rel` `==` | `OpK` EQ | igual con `JEQ` (idéntico) |
| `expr_rel` `<=` `>` `>=` `!=` | — (extensión) | mismo patrón con `JLE` / `JGT` / `JGE` / `JNE` |
| `condicion` `&&` | — | ambos lados; `MUL ac,ac1,ac` (1·1 = 1) |
| `condicion` `\|\|` | — | `ADD ac,ac1,ac`; `JEQ ac,1(pc)`; `LDC ac,1(0)` (normaliza a 1) |
| `termino` `%` | — (extensión) | `a − (a/b)·b` con dos temporales: `DIV`, `MUL`, `SUB` |
| `potencia` `^` | — (extensión) | ciclo en línea con tres temporales (resultado, base, contador) y `JLE` |
| nodo con `atrib["conv"]` | — | después del nodo: `LDC ac1,1.0(0)`; `MUL ac,ac,ac1` "conv int->float" |
| `asignacion` | `AssignK` | expresión; `ST ac,loc(gp)` "assign: store value" |
| `incremento` / `decremento` | — | en el árbol anotado ya es `a + 1` / `a − 1`: expresión; `ST ac,loc(gp)` |
| `cin_stmt` | `ReadK` | `IN ac,0,0`; (si la variable es float: conversión); `ST ac,loc(gp)` "read: store value" |
| `cout_stmt` | `WriteK` | expresión; `OUT ac,0,0` "write ac" |
| `if_stmt` | `IfK` | **esquema de Louden**: cond; `emitSkip(1)`; then; `emitSkip(1)`; backpatch `JEQ ac → else`; else; backpatch `LDA pc → fin` |
| `do_until_stmt` | `RepeatK` | `savedLoc = emitSkip(0)`; cuerpo; cond; `emitRM_Abs("JEQ", ac, savedLoc)` |
| `while_stmt` | — (extensión) | `inicio = emitSkip(0)`; cond; `salto = emitSkip(1)`; cuerpo; `LDA pc → inicio`; backpatch `JEQ ac → fin` |

Booleanos: `1` = verdadero, `0` = falso. `&&` y `||` evalúan ambos lados (sin corto circuito).
No hay plegado de constantes: aunque el semántico conozca un valor, se genera el cálculo.

---

## 3. Prueba de equivalencia con TINY

`python pruebas/run_tests.py` compila estos programas en nuestro lenguaje y compara las
instrucciones (sin las líneas `*`) con los `.tm` de la docente:

| Ejemplo TINY | Nuestro programa | Resultado |
|---|---|---|
| `factorial.tny` | `pruebas/oro/factorial.txt` | mismas **42 instrucciones (0–41)**, mismas direcciones y operandos; mismo `.ci` |
| `aritmetica.tny` | `y = (x + 1) * (x - 2)` | idéntico `.tm` y `.ci` |
| `condicional.tny` | `if (x < 3) then cout 1; else cout 2; end;` | idéntico `.tm` y `.ci` |
| `ciclo.tny` | `do { x = x - 1; } until (x == 0);` | idéntico `.tm` y `.ci` |

Además la TM en Python ejecuta los `.tm` de la docente tal cual (factorial con 5 → 120).
Como en TINY, las líneas se escriben **en orden de emisión**: en `factorial.tm` la
instrucción 13 (el salto parchado del `if`) aparece después de la 39.

---

## 4. Diferencias con TINY

| Aspecto | TINY | Este proyecto |
|---|---|---|
| Declaraciones | no existen | `int/real/float/bool`; no generan código (sólo comentario) |
| Tipos | entero | `int`, `float` (`real` ≡ `float`), `bool` |
| Relacionales | `<`, `=` | `< <= > >= == !=` |
| Lógicos | — | `&&`, `\|\|` |
| Ciclos | `repeat-until` | `do-until` (igual a repeat) y `while` |
| Operadores extra | — | `%` (sólo int) y `^` (exponente int) |
| Incremento | — | `a++`, `a--` |
| Comentario de cabecera | `TINY Compilation to TM Code` | `Compilacion a codigo TM (esquema TINY de Louden)` |
| Tamaño de iMem | 1024 | 4096 (programas con muchos `if`) |
| Prompt de `IN` | `Ingrese un numero entero (IN):` | `Ingrese un numero (IN):` (acepta reales) |

---

## 5. Extensión de reales en la TM

La TM original sólo maneja enteros, pero los ejercicios piden reales (7.59, 15 %, π…).
La **única** extensión es que los valores pueden ser reales; no hay opcodes nuevos:

1. **Registros y memoria** guardan `int` o `float`.
2. **`LDC`** acepta una constante real: `LDC 0,3.14(0)`.
3. **`IN`** acepta enteros o reales, con signo (`-1` sirve como centinela).
4. **`DIV`**: si los dos operandos son enteros, división entera que trunca hacia cero
   (como C: `-7/2 = -3`); si alguno es real, división real (`7.0/2 = 3.5`).
5. **`OUT`**: enteros con `%d`; reales con hasta 6 decimales y siempre con punto (`2.5`, `120.0`).

**Conversión int → float sin opcode nuevo.** Donde el semántico marcó `conv` en el árbol
anotado (y después de `IN` a una variable float), se multiplica por 1.0. `ac1` nunca
guarda un valor vivo entre subexpresiones en el esquema de Louden, así que usarlo es seguro.

Ejemplo — `int a; float r; a = 7; r = a / 2.0;`:

```
  4:     LD  0,1(5) 	load id value          ac = a = 7       (int)
  5:    LDC  1,1.0(0) 	conv: load 1.0         ac1 = 1.0
  6:    MUL  0,0,1 	conv int->float        ac = 7.0         (float)
  7:     ST  0,0(6) 	op: push left
  8:    LDC  0,2.0(0) 	load const             ac = 2.0
  9:     LD  1,0(6) 	op: load left          ac1 = 7.0
 10:    DIV  0,1,0 	op /                   ac = 3.5  (división real)
 11:     ST  0,0(5) 	assign: store value    r = 3.5
```

`.ci` del mismo fragmento:

```
a = 7
t1 = (float) a
t2 = t1 / 2.0
r = t2
```

Sin la conversión, `7 / 2` daría la división entera `3`; por eso se aplica en **todo**
nodo marcado con `conv` y después de cada `IN` a una variable float.

Para saber si un `IN` espera un entero, la TM del IDE lee el comentario de la instrucción
(`read integer value: x` o `read real value: x`); si espera un entero y se teclea `2.5`,
responde `Illegal value: se esperaba un numero entero` y vuelve a pedir.

---

## 6. Textos para el usuario (también sin opcodes nuevos)

El lenguaje admite textos sólo como ayuda para quien ejecuta el programa:

| Fuente | Instrucción TM generada | Lo que muestra la TM del IDE |
|---|---|---|
| `cin("Minutos (>= 1)", minutos);` | `IN 0,0,0   read integer value: minutos \| Minutos (>= 1)` | `Ingrese un numero (IN) - Minutos (>= 1):` |
| `cin(minutos);` | `IN 0,0,0   read integer value: minutos` | `Ingrese un numero (IN) - minutos (int):` |
| `cout "Costo ($)", costo;` | `OUT 0,0,0   write ac: costo \| Costo ($)` | `Resultado del programa (OUT): 13.65   <- Costo ($)` |
| `cout "Clave invalida";` | `LDA 0,0(0)   msg: Clave invalida` | `Clave invalida` |

Los textos viajan **en el comentario** de la instrucción. `LDA 0,0(0)` calcula `ac = 0 + ac`,
o sea, no cambia nada: es una instrucción que ya existe usada como "no-op" para colgar el
mensaje. El `tm.c` de la docente ignora los comentarios, así que el mismo `.tm` se ejecuta
igual allá (sólo que sin los textos). En el `.ci` el mensaje aparece como `write "texto"`.
