# PLAN — Fase final: generación de código TM y ejecución en el IDE

**Proyecto:** IDE-Compiladores (Compiladores II, UAA) · **Equipo:** Carabez · Pastrana · Salas · Grupo 9B
**Para:** Claude Code. Este documento es autocontenido: léelo completo antes de tocar código.
**Material de referencia (ya copiado al repo):** carpeta `referencia/`

| Archivo | Qué es |
|---|---|
| `referencia/Entrega_Final_Proyecto_Compiladores_II_UAA.pdf` | Requerimientos oficiales de la docente (rúbrica: 5 programas × 2 puntos) |
| `referencia/EjericiosFinalesCompisII.pdf` + `ejercicios.txt` + `formulas_*.png` | Los ejercicios de prueba (12 grupos de 5 programas). Las fórmulas vienen como imagen: ver los PNG |
| `referencia/Tiny_Intermedio_TM/` | TINY + TM de la docente (Louden + extensión `.ci`). **Es el modelo a seguir**: `cgen.c`, `code.c`, `code.h`, `intermedio.c`, `tm.c`, `ejemplos/*.tny|.ci|.tm` |
| `CONTEXTO.md` | Estado del compilador hasta la Fase 3 (léxico, sintáctico, semántico). Leer §3, §4 y §11 |

---

## 0. Objetivo y criterio de éxito

La docente entregará **cinco programas** el día de la revisión. Por cada uno se gana:

- **1 punto** si el IDE genera y **muestra** el código TM correcto de ese programa (direcciones, instrucciones y operandos visibles, en un área rotulada "Código Intermedio").
- **1 punto** si ese `.tm` **se ejecuta en la TM** dentro del IDE, pidiendo las entradas (`IN`) y mostrando los resultados (`OUT`) correctos.

Flujo que debe poder demostrarse sin fricción, para cualquier programa:
(1) escribir/cargar el fuente → (2) compilar → (3) mostrar árbol válido → (4) generar `.tm` → (5) ver el `.tm` (y el `.ci`) → (6) ejecutar en TM → (7) comprobar el resultado.

**Todo lo demás es secundario frente a esto.** Prioridad absoluta: corrección del código generado y de la ejecución, con cualquier programa razonable que use las construcciones del lenguaje.

### Reglas duras (vienen del PDF de requerimientos)
1. El `.tm` y el `.ci` se generan **en paralelo desde el árbol validado**. El `.ci` no es entrada de la TM.
2. El simulador recibe **el texto del `.tm`** (lo parsea), no el árbol, ni el fuente, ni el `.ci`.
3. Solo se genera código si **no hay errores** léxicos, sintácticos ni semánticos.
4. Nunca mostrar una salida vieja como válida: si la compilación falla o el fuente cambió, los paneles de código y ejecución se **limpian o se marcan como desactualizados**.
5. Sin rutas absolutas. Debe funcionar con `python ide_compilador.py` y con el `.exe` de PyInstaller.
6. No presentar como implementado lo que no lo esté.

---

## 1. Estado actual (no rehacer)

- `compilador.py` (~1550 líneas): léxico (`analizar`), sintáctico (`AnalizadorSintactico` → árbol `NodoSint`), semántico (`analizar_semantico(codigo) -> ResultadoSemantico` con `.arbol`, `.anotado`, `.tabla`, `.errores_*`, `.ejecutado`).
- `ide_compilador.py` (~1880 líneas, PyQt6): editor, docks, `SyntaxTreePanel`/`BranchTree`, `SemanticPanel`, tabla de símbolos. Importa el compilador con `_load_compilador()` (importlib desde `resource_path`).
- En el IDE ya existen pero **sin backend**: pestaña `Cod. Intermedio` (`self.out_ci`), pestaña `Resultado Ejecucion` (`self.out_exec`), acciones `_codigo_intermedio` (F8) y `_ejecutar` (F9). `_run_compiler` devuelve "no implementado" para esos flags.
- Gramática vigente:

```
programa   → 'main' '(' ')' '{' lista_sent '}'
sentencia  → declaracion | asig_incr | if_stmt | do_until | while_stmt | cin_stmt | cout_stmt
declaracion→ ('int'|'real'|'float'|'bool') lista_ids ';'
asig_incr  → ID ('=' expresion | '++' | '--') ';'
if_stmt    → 'if' '(' condicion ')' 'then' lista_sent ('else' lista_sent)? 'end' ';'
do_until   → 'do' '{' lista_sent '}' 'until' '(' condicion ')' ';'
while_stmt → 'while' '(' condicion ')' '{' lista_sent '}' ';'
cin_stmt   → 'cin' '(' ID ')' ';'
cout_stmt  → 'cout' expresion ';'
condicion  → expr_rel (('&&'|'||') expr_rel)*
expr_rel   → expresion (OP_REL expresion)?        OP_REL: < > <= >= == !=
expresion  → termino (('+'|'-') termino)*
termino    → factor (('*'|'/') factor)*
factor     → '(' expresion ')' | ENTERO | REAL | 'true' | 'false' | ID | '-' factor
```

- Tipos de nodo (`NodoSint.tipo`): `programa`, `lista_sentencias`, `declaracion`, `lista_ids`, `identificador`, `asignacion` (`id_nombre`), `incremento`/`decremento` (`id_nombre`; en el árbol **anotado** tienen un hijo `expresion` `+`/`-` con hijos `identificador` y `entero 1`), `if_stmt` (hijos: condición, `then_branch`, `else_branch?`), `do_until_stmt` (hijos: cuerpo, condición), `while_stmt` (hijos: condición, cuerpo), `cin_stmt` (`id_nombre`), `cout_stmt`, `condicion` (&&, ||), `expr_rel`, `expresion` (+ −), `termino` (* /), `factor_par`, `negativo`, `entero`, `real_lit`, `booleano`.
- Árbol anotado: cada nodo tiene `atrib` (dict) con `tipo` (`int`/`float`/`bool`/`error`), `valor`, `conv` (`"int→float"` en el nodo que debe convertirse), `loc`, `chk`.
- Tabla de símbolos: `tabla.buscar(nombre).loc` = dirección tipo TINY (0, 1, 2… en orden de declaración). `real` ≡ `float`.
- Semántica de tipos: `int op int → int` (la división entre enteros es entera y trunca); si hay un float → float; `float ← int` permitido; `int ← float` es error.

**Antes de empezar:** el working tree tiene cambios sin commit (incluye ediciones del usuario en `TestSemantica_adaptado.txt`). Hacer un commit de respaldo "estado previo a fase final" sin revertir nada, y trabajar en una rama `fase-final`.

---

## 2. Decisiones de diseño (ya tomadas)

| # | Decisión | Motivo |
|---|---|---|
| D1 | **TM reimplementada en Python** (`tm.py`), port fiel de `tm.c`, integrada al IDE. No depender de `tm.exe` ni de GCC. | Requisito de ambiente sin dependencias; el IDE es Python |
| D2 | Mismo **juego de instrucciones** de Louden (HALT IN OUT ADD SUB MUL DIV LD ST LDA LDC JLT JLE JGT JGE JEQ JNE), mismos registros (`ac=0, ac1=1, gp=5, mp=6, pc=7`), mismo **formato de archivo** `.tm`. **Ningún opcode nuevo.** | "Basarnos en el display del TINY"; la docente reconoce el formato |
| D3 | **Extensión única de la TM: valores numéricos reales.** Registros y memoria guardan `int` o `float`; `LDC` acepta constante real (`LDC 0,3.14(0)`); `IN` acepta enteros o reales; `DIV` es entera si ambos operandos son `int` y real si alguno es `float`. | Los ejercicios exigen reales (7.59, 15 %, π…); la TM original es solo de enteros. Documentarlo como extensión |
| D4 | Conversión `int→float` **sin opcode nuevo**: `LDC ac1,1.0(0)` + `MUL ac,ac,ac1`. Se emite donde el árbol anotado marca `conv`, y tras `IN` cuando la variable es float. | `ac1` nunca está vivo entre subexpresiones en el esquema de Louden, así que es seguro usarlo |
| D5 | Generador con el **mismo algoritmo de `cgen.c`** (acumulador + temporales en `mp`, `emitSkip`/`emitBackup`/`emitRestore`/`emitRM_Abs`), mismos comentarios de traza. | Para programas equivalentes debe salir **el mismo listado** que el TINY de la docente |
| D6 | Módulos separados espejo de TINY: `code_tm.py` (=code.c/h), `cgen.py` (=cgen.c), `intermedio.py` (=intermedio.c), `tm.py` (=tm.c). `compilador.py` los orquesta. | El PDF pide establecer y documentar la correspondencia archivo por archivo |
| D7 | Booleanos = `1`/`0`. `&&` = `MUL`; `||` = `ADD` + normalización. Sin corto circuito. | Simple y correcto para valores 0/1 |
| D8 | Extensión de lenguaje **confirmada por el equipo** (Fase 2): operadores `%` (módulo) y `^` (potencia entera), generados solo con instrucciones existentes. | Los ejercicios piden pares/impares, primos, perfectos, `(A+B)^2`, `P^3+Q^4`, `N^N`. Sin esto hay que escribirlos con rodeos |
| D9 | Sin arreglos ni cadenas. Los ejercicios "de tablas" se resuelven leyendo datos en ciclos y con acumuladores; las salidas son números. | La TM no imprime texto; la docente ya codificó las respuestas como números ("positivo=0, negativo=1…") |

---

## 3. Fases de trabajo

Orden obligatorio. Cada fase termina con sus pruebas en verde y un commit.

### FASE 0 — Arreglo previo del semántico (bloqueante)

**Problema comprobado:** el semántico marca como **error** "Variable sin valor asignado" en programas válidos. Ejemplo real (mayor/menor de N números):

```
cin(n); i = 0;
while (i < n) {
    cin(x);
    if (i == 0) then mayor = x; menor = x;
    else if (x > mayor) then mayor = x; end; ...
    end;
    i++;
};
cout(mayor);        ← hoy: ERROR "se usa sin tener un valor asignado"
```

Hoy una variable asignada en una sola rama de un `if`, o dentro de un `while`, queda "sin asignar" después, y su uso es error. Eso impediría generar código para muchos de los ejercicios.

**Cambio:** distinguir tres estados por variable: *nunca asignada*, *posiblemente asignada*, *asignada*.
- **Error** solo si la variable **nunca** fue asignada (ni por `=`, ni `cin`, ni `++/--` válido) en ningún punto anterior del programa.
- *Posiblemente asignada* (asignada en alguna rama, o dentro de un ciclo, o más adelante dentro del mismo cuerpo de ciclo que se está analizando): **no es error**. Registrar una línea `AVISO` en la bitácora y no bloquear la generación.
- Al entrar a un ciclo, toda variable que se asigna en su cuerpo pasa al menos a *posiblemente asignada* (por las iteraciones siguientes).
- En la tabla de símbolos, la columna Valor muestra `?` para estas (no "sin asignar").

**Verificación de no regresión:** `TestSemantica_casos_extra.txt` debe seguir dando 13 errores (`w++` y `j = w * 2` siguen siendo error: `w` nunca se asigna). Para el test adaptado usar la copia limpia que está dentro de `entrega/Fase3_Carabez_Pastrana_Salas.zip` (`codigo_fuente/TestSemantica_adaptado.txt`): debe seguir dando 7 errores (`c--`: `c` nunca se asigna). El programa de ejemplo de arriba debe dar **0 errores**.

### FASE 1 — Emisor y generador TM (`code_tm.py`, `cgen.py`)

**`code_tm.py`** — port de `code.c`. Clase `EmisorTM` con estado propio (nada global):
- `emit_comment(c)`, `emit_ro(op, r, s, t, c)`, `emit_rm(op, r, d, s, c)`, `emit_skip(n) -> loc`, `emit_backup(loc)`, `emit_restore()`, `emit_rm_abs(op, r, a, c)`.
- Constantes `PC=7, MP=6, GP=5, AC=0, AC1=1`.
- **Formato idéntico a `code.c`** (con `TraceCode` activo):
  - RO: `"%3d:  %5s  %d,%d,%d \t%s"` · RM: `"%3d:  %5s  %d,%d(%d) \t%s"` · comentario: `"* %s"`.
  - Las líneas se guardan **en orden de emisión** (los saltos parchados aparecen fuera de orden, igual que en `factorial.tm`: la 13 después de la 39).
- `d` puede ser real en `LDC`; se escribe con `repr` de Python (`3.14`, `1.0`).
- Además de las líneas de texto, conservar una lista estructurada `(loc, op, a1, a2, a3, comentario)` para la vista en tabla del IDE.

**`cgen.py`** — port de `cgen.c`. `generar_codigo_tm(arbol_anotado, tabla, nombre_archivo) -> EmisorTM`.
Recorre el **árbol anotado**. Mismo esquema: resultado de toda expresión en `ac`; operando izquierdo guardado en `tmpOffset--(mp)` y recuperado en `ac1`.

Prelude y cierre idénticos a Louden:
```
* <cabecera>
* Standard prelude:
  0:     LD  6,0(0) 	load maxaddress from location 0
  1:     ST  0,0(0) 	clear location 0
* End of standard prelude.
  ...
* End of execution.
 NN:   HALT  0,0,0
```

Tabla de traducción (esta tabla **es** la correspondencia que pide el PDF §7.1; copiarla también a `docs/CORRESPONDENCIA_TINY.md`):

| Nodo nuestro | Equivalente TINY | Código TM |
|---|---|---|
| `programa`, `lista_sentencias`, `then_branch`, `else_branch` | recorrido de `sibling` en `cGen` | generar hijos en orden |
| `declaracion` | — (TINY no declara) | sin código; solo comentario `* declaracion int x, y (loc 0, 1)` |
| `entero` / `real_lit` | `ConstK` | `LDC ac,valor(0)` "load const" |
| `booleano` | — | `LDC ac,1(0)` / `LDC ac,0(0)` |
| `identificador` (en expresión) | `IdK` | `LD ac,loc(gp)` "load id value" |
| `factor_par` | — | generar el hijo (sin código propio) |
| `negativo` | — | hijo; `LDC ac1,0(0)`; `SUB ac,ac1,ac` |
| `expresion` + − / `termino` * / | `OpK` PLUS MINUS TIMES OVER | izq; `ST ac,tmp--(mp)` "op: push left"; der; `LD ac1,++tmp(mp)` "op: load left"; `ADD|SUB|MUL|DIV ac,ac1,ac` |
| `expr_rel` `<` | `OpK` LT | `SUB ac,ac1,ac`; `JLT ac,2(pc)`; `LDC ac,0(ac)`; `LDA pc,1(pc)`; `LDC ac,1(ac)` (idéntico a Louden) |
| `expr_rel` `==` | `OpK` EQ | igual con `JEQ` |
| `expr_rel` `<=` `>` `>=` `!=` | — (extensión) | mismo patrón con `JLE` / `JGT` / `JGE` / `JNE` |
| `condicion` `&&` | — | evaluar ambos como OpK; `MUL ac,ac1,ac` |
| `condicion` `\|\|` | — | `ADD ac,ac1,ac`; `JEQ ac,1(pc)`; `LDC ac,1(0)` |
| nodo con `atrib["conv"]` | — | tras generar el nodo: `LDC ac1,1.0(0)`; `MUL ac,ac,ac1` "conv int->float" |
| `asignacion` | `AssignK` | generar expresión; `ST ac,loc(gp)` "assign: store value" |
| `incremento` / `decremento` | — | generar el hijo `expresion` del anotado (`a + 1`); `ST ac,loc(gp)` |
| `cin_stmt` | `ReadK` | `IN ac,0,0` "read integer value"; (si la variable es float: conversión D4); `ST ac,loc(gp)` "read: store value" |
| `cout_stmt` | `WriteK` | generar expresión; `OUT ac,0,0` "write ac" |
| `if_stmt` | `IfK` | **exactamente** el esquema de Louden: cond; `emitSkip(1)`; then; `emitSkip(1)`; backpatch `JEQ ac → else`; else; backpatch `LDA pc → fin` (el salto al fin se emite aunque no haya else, igual que TINY) |
| `do_until_stmt` | `RepeatK` | `savedLoc = emitSkip(0)`; cuerpo; cond; `emitRM_Abs("JEQ", ac, savedLoc)` |
| `while_stmt` | — (extensión) | `inicio = emitSkip(0)`; cond; `salto = emitSkip(1)`; cuerpo; `emitRM_Abs("LDA", pc, inicio)`; `fin = emitSkip(0)`; `emitBackup(salto)`; `emitRM_Abs("JEQ", ac, fin)`; `emitRestore()` |

Notas:
- Las ubicaciones salen de `tabla.buscar(nombre).loc` (equivalente a `st_lookup`).
- No hacer plegado de constantes: aunque el semántico conozca el valor, **se genera el cálculo real**.
- Comentarios de traza `* -> if`, `* <- if`, `* -> Op`, `* -> Id`, `* -> assign`… como en Louden; para lo nuevo usar el mismo estilo (`* -> while`, `* <- while`).

**Prueba de oro (obligatoria):** este programa en nuestro lenguaje

```
main() {
    int x, fact;
    cin(x);
    if (0 < x) then
        fact = 1;
        do {
            fact = fact * x;
            x = x - 1;
        } until (x == 0);
        cout(fact);
    end;
}
```
debe producir **las mismas 42 instrucciones (0–41), mismas direcciones y operandos** que `referencia/Tiny_Intermedio_TM/ejemplos/factorial.tm`. Comparar las líneas que no empiezan con `*`, normalizando espacios. Hacer lo mismo con equivalentes de `aritmetica.tny`, `condicional.tny` y `ciclo.tny`.

### FASE 2 — Extensión del lenguaje: `%` y `^` (obligatoria, confirmada)

Los tokens ya existen en el léxico (`OP_ARITMETICO`). Cambios:

```
termino  → potencia (('*'|'/'|'%') potencia)*
potencia → factor ('^' potencia)?          (asociativa a la derecha, mayor precedencia que * /)
```
- Árbol: `%` es un nodo `termino` con valor `%`; `^` es un nodo nuevo `potencia` con valor `^`.
- Semántico: `%` exige `int % int → int` (si no, "Uso indebido de operador"; divisor constante 0 → "División entre cero"). `^`: base `int` o `float`, **exponente `int`**; el tipo resultante es el de la base. Calcular valor en compilación cuando se conozca, igual que los demás.
- TM, sin opcodes nuevos (usar temporales de `mp`):
  - `a % b` = `a − (a/b)*b`: guardar `a` y `b` en temporales; `DIV`; `MUL` por `b`; `SUB` desde `a`.
  - `a ^ b`: ciclo en línea: `res = 1`; mientras `cont > 0`: `res = res * base`; `cont = cont − 1`. Exponente ≤ 0 → resultado 1.
- `.ci`: `t1 = a % b`, `t1 = a ^ b`.
- Actualizar resaltado, colores de `_TREE_NODE_COLOR` (`potencia`) y `CONTEXTO.md`.

Esta fase es parte del alcance: los programas de prueba deben usar `%` y `^` donde el ejercicio lo pida.

### FASE 3 — Código intermedio de tres direcciones (`intermedio.py`)

Port de `intermedio.c`. `generar_codigo_intermedio(arbol_anotado) -> str`. Mismo formato:

```
# CODIGO INTERMEDIO DE TRES DIRECCIONES
# Los temporales t1, t2... y etiquetas L1, L2... son simbolicos.

read x
t1 = 0 < x
if_false t1 goto L1
fact = 1
label L2
t2 = fact * x
fact = t2
...
write fact
label L1
halt
```
- Expresiones en postorden; constantes e identificadores se devuelven sin temporal; cada operador crea `tN`.
- `if`: `if_false c goto L1` / then / (`goto L2` si hay else) / `label L1` / else / `label L2`.
- `do-until`: `label L1` / cuerpo / `if_false c goto L1`.
- `while`: `label L1` / `tN = cond` / `if_false tN goto L2` / cuerpo / `goto L1` / `label L2`.
- Extras: `tN = - a` (negativo), `tN = (float) a` (conversión), `tN = a && b`, `++` como `tN = a + 1` + `a = tN`. `true`/`false` literales. Declaraciones no emiten nada.

**Prueba de oro:** el cuerpo del `.ci` del factorial debe ser idéntico al de `referencia/.../ejemplos/factorial.ci` (ignorando las líneas `#`).

### FASE 4 — Máquina TM en Python (`tm.py`)

Port de `tm.c` como **máquina de estados no bloqueante** (el IDE no puede congelarse esperando `IN`).

```python
class MaquinaTM:
    IADDR_SIZE = 4096; DADDR_SIZE = 1024; NO_REGS = 8; PC_REG = 7
    def cargar(self, texto_tm) -> list[str]      # parser del .tm; devuelve errores ("Line N (Instruction M)   mensaje")
    def reiniciar(self)                          # reg = 0; dMem[0] = DADDR_SIZE-1; resto 0  (comando c)
    def paso(self) -> Estado                     # OKAY | HALT | NECESITA_ENTRADA | SALIDA | IMEM_ERR | DMEM_ERR | ZERODIVIDE
    def dar_entrada(self, texto) -> bool         # False si el valor es ilegal
    reg, dMem, iMem, salidas, pasos
```
- **Parser del archivo**: igual que `readInstructions`: ignora líneas en blanco y las que empiezan con `*`; `loc: OP r,s,t` o `loc: OP r,d(s)`; todo lo que sigue es comentario. Acepta `d` real en `LDC`. Mismos mensajes de error (Bad location, Missing colon, Illegal opcode…).
- **Semántica**: la de `stepTM`. `DIV`: ambos `int` → trunca hacia cero (como C; ojo: `//` de Python redondea hacia −∞, no usarlo directo); si hay `float` → división real. Divisor 0 → `ZERODIVIDE`. Saltos `J??` comparan contra 0. Acceso a memoria fuera de rango → `DMEM_ERR`.
- **IN**: acepta enteros y reales, con signo (`-1` es centinela en varios ejercicios). Valor ilegal → "Illegal value" y vuelve a pedir.
- **OUT**: `int` → `%d`; `float` → hasta 6 decimales sin ceros de relleno, pero siempre con punto (`2.5`, `120.0`, `3.141593`).
- **REPL de consola** (`python tm.py archivo.tm`): mismos comandos y textos que `tm.c` de la docente: `h` (ayuda, copiar el texto), `v` (ver `.ci` del mismo nombre), `i b n`, `d b n`, `r`, `s [n]`, `g`, `t`, `p`, `c`, `q`. Prompts: `Comando TM (h=ayuda): `, `Ingrese un numero (IN): `, `Resultado del programa (OUT): X`, `Ejecucion finalizada (HALT)`.
- Protección: límite de pasos configurable (p. ej. 20 000 000) → "posible ciclo infinito", sin colgar.

**Prueba de oro:** `MaquinaTM` debe ejecutar **los `.tm` de la docente tal cual** (`referencia/.../ejemplos/*.tm`): factorial con entrada 5 → 120.

### FASE 5 — Orquestación en `compilador.py` y consola

```python
class ResultadoCompilacion:      # extiende/contiene ResultadoSemantico
    ok: bool                     # True solo si no hubo errores en ninguna fase
    codigo_tm: str               # texto del .tm (orden de emisión, con comentarios)
    instrucciones: list          # (loc, op, a1, a2, a3, comentario) para la vista en tabla
    codigo_ci: str
    ruta_tm, ruta_ci             # si se escribieron a disco

def compilar(codigo, ruta_fuente=None) -> ResultadoCompilacion
```
- Si hay errores en cualquier fase: `ok=False`, sin `.tm`/`.ci`, y **borrar** los `.tm`/`.ci` viejos del mismo nombre si existen (regla dura 4).
- Archivos junto al fuente, mismo nombre base: `programa.txt` → `programa.ci`, `programa.tm`.
- CLI:
  - `python compilador.py --intermedio archivo.txt` → escribe `.ci` y `.tm`, imprime ambos rotulados.
  - `python compilador.py --ejecutar archivo.txt` → compila y abre el REPL de la TM con ese `.tm`. Con `--directo` ejecuta `g` y termina (lee las entradas de stdin; útil para pruebas).
- Mensajes como TINY: `Codigo intermedio generado: …`, `Codigo TM generado: …`, `Compilacion cancelada por errores de analisis.`

### FASE 6 — Integración en el IDE

**6.1 Panel "Código Intermedio"** (reemplaza `self.out_ci`; clase `CodigoPanel`, mismo estilo que `SemanticPanel`):
- Barra superior: nombre del archivo fuente compilado + hora de generación + nº de instrucciones; botones `Guardar .tm`, `Guardar .ci`, `Copiar`.
- Sub-pestaña **"Código TM (.tm)"** (la principal, la que se evalúa):
  - Vista **Tabla**: columnas `Dir | Instrucción | Operandos | Comentario`, ordenada por dirección, fuente monoespaciada, colores por tipo de instrucción (carga/almacén, aritmética, saltos, E/S).
  - Vista **Archivo**: el texto del `.tm` tal cual se escribió (orden de emisión, con líneas `*`), como lo muestra TINY. Conmutador Tabla/Archivo.
  - Durante la ejecución paso a paso, resaltar la fila del `pc`.
- Sub-pestaña **"Código intermedio de tres direcciones (.ci)"** — con ese rótulo exacto.
- F8 / botón "Cod. Intermedio": guarda, compila todas las fases y llena el panel. Si hay errores: limpia el panel, muestra "No se generó código: hay errores" y abre la pestaña de errores correspondiente.

**6.2 Panel "Máquina TM"** (reemplaza `self.out_exec` en el dock inferior; clase `TMPanel`):
- **Consola** (solo lectura) con el mismo diálogo que `tm.exe`: `Simulador TM listo…`, `Ingrese un numero (IN):`, `Resultado del programa (OUT): …`, `Ejecucion finalizada (HALT)`.
- **Línea de entrada** debajo: cuando la TM pide `IN` recibe el foco y se resalta; Enter envía el valor (eco en la consola). El resto del tiempo acepta **comandos TM** (`h v i d g r s t p c q`) para reproducir el display de TINY.
- Botones: `▶ Ejecutar (g)`, `Paso (s)`, `Reiniciar (c)`, `■ Detener`, y casillas `Rastreo (t)`, `Contar instrucciones (p)`.
- A la derecha: **Registros** (0–7 con alias `ac, ac1, gp, mp, pc`) y **Memoria de variables** (`nombre | loc | valor`, tomada de la tabla de símbolos y de `dMem[loc]`), actualizados en cada pausa/fin.
- **F9 / "▶ Ejecutar"**: siempre **recompila el fuente actual** (misma ruta que F8), carga en la TM **el texto del `.tm` recién generado** mediante `MaquinaTM.cargar` y ejecuta. Nunca reutilizar un `.tm` anterior.
- **No bloquear la UI**: ejecutar por lotes con `QTimer` (p. ej. 20 000 pasos por tick); `NECESITA_ENTRADA` pausa hasta que el usuario responde; `Detener` corta. Errores de ejecución (división entre cero, memoria) en rojo con la dirección de la instrucción.

**6.3 Coherencia fuente ↔ código**
- Al modificar el documento después de compilar, marcar ambos paneles como "⚠ desactualizado — vuelve a compilar" (atenuar) y deshabilitar `Paso`/`Ejecutar` de la TM hasta recompilar.
- Al cambiar de pestaña de archivo, limpiar o marcar igual.
- Tras F8/F9 actualizar también árbol, semántico y tabla de símbolos (para el paso "demostrar árbol válido").

**6.4 Otros**
- Botón de barra "Compilar todo" opcional = F8. Estado en la barra inferior: `Código generado: N instrucciones` / `Ejecución finalizada (HALT), N instrucciones ejecutadas`.
- `refresh_theme` para los paneles nuevos (6 temas).
- `_load_compilador`: limpiar también `sys.modules` de `code_tm`, `cgen`, `intermedio`, `tm` y asegurar que su carpeta esté en `sys.path`.
- **PyInstaller**: agregar los cuatro módulos nuevos a `datas` en `IDE.spec`, regenerar `dist/Ide.exe` y **probar el .exe** con un programa completo (compilar + ejecutar con entradas).

### FASE 7 — Pruebas

Carpeta `pruebas/` con `run_tests.py` (sin dependencias externas; `python pruebas/run_tests.py` debe terminar en verde).

1. **Pruebas de oro contra TINY** (Fases 1, 3, 4): descritas arriba.
2. **Oráculo independiente**: un intérprete directo del árbol (`pruebas/interprete_ast.py`, solo para pruebas) que ejecuta el programa con las mismas entradas. Para cada programa: salidas de la TM == salidas del intérprete.
3. **Casos por construcción** (uno pequeño por cada fila de la tabla de traducción): cada operador aritmético y relacional, `&&`/`||`, negativos, `++/--`, conversión int→float (asignación, expresión mixta, `cin` a float), división entera vs. real (`7/2 = 3`, `7.0/2 = 3.5`), `if` con y sin `else`, `if` anidados, `while` que no entra, `while` anidado, `do-until`, ciclo con centinela `-1`, `%` y `^` (precedencia, asociatividad derecha de `^`, exponente 0, `%` con negativos).
4. **Errores**: programa con error semántico → no se genera `.tm`, y se borra el anterior; división entre cero en ejecución → mensaje, sin colgar; ciclo infinito → `Detener` funciona.
5. **Programas de los ejercicios** en `pruebas/programas/` (cada uno con `.txt`, `.in` con entradas de ejemplo y `.esperado`):
   - La docente **aún no asigna** los 5 programas del equipo, así que la cobertura debe ser amplia. Como mínimo estos representativos, porque los programas de la revisión **no serán exactamente los de desarrollo**: orden inverso de 4 números · positivo/negativo/nulo · tres números en orden creciente · Fibonacci N · promedio de 5 calificaciones (float) · temperatura del grillo `T = h/4 + 40` · impuesto por tramos (float, `if` anidados) · mayor de tres reales · mayor y menor de N enteros · serie `1 − 1/2 + 1/3 − …` (float) · serie `1¹ + 2² + … + Nᴺ` · conteo de ceros hasta `-1` · votos de 4 candidatos hasta `0` con porcentajes · primos menores que M · números perfectos ≤ N · sucesión de ULAM · área y volumen del cilindro · ventas del estadio (centinela `-1`, acumuladores por tipo).
   - Sin arreglos: leer los datos dentro de ciclos y usar acumuladores. Respetar que el 1 es secuencial, 2–3 selectivos y 4–5 repetitivos.
6. **Prueba manual del IDE** (checklist en `docs/GUION_REVISION.md`): los 7 pasos del flujo con dos programas, incluido uno con entradas.

### FASE 8 — Documentación y cierre

- `docs/CORRESPONDENCIA_TINY.md`: tabla nodo ↔ TINY ↔ TM (de la Fase 1), tabla archivo ↔ archivo (`cgen.c→cgen.py`, `code.c→code_tm.py`, `intermedio.c→intermedio.py`, `tm.c→tm.py`, `main.c→compilar()`), diferencias con TINY, y la **extensión de reales** de la TM (D3, D4) explicada con un ejemplo.
- `docs/GUION_REVISION.md`: pasos exactos para la revisión, y un ejemplo explicado estilo §8 del PDF (una asignación → sus instrucciones TM y su línea de `.ci`; y cómo se resuelve un salto de `if`/`while` con `emitSkip`/`emitBackup`).
- `docs/NO_SOPORTADO.md`: lo que el lenguaje no tiene (arreglos, cadenas, funciones, `switch`, `!`, corto circuito).
- Actualizar `CONTEXTO.md` (§12 nueva: fase final) y `README.md` (tabla de fases, atajos, CLI).
- Commit final en la rama y merge a `main`.

---

## 4. Riesgos y cómo evitarlos

| Riesgo | Mitigación |
|---|---|
| Desfase de saltos (el clásico de `emitSkip`/`backpatch`) | Pruebas de oro contra `factorial.tm` + oráculo en ciclos/ifs anidados |
| `DIV` con negativos (`//` de Python ≠ C) | Truncar hacia cero explícitamente; caso de prueba `-7/2 = -3` |
| Variable float con valor entero → división entera equivocada | Regla D4 en **todo** nodo con `conv` y tras `IN` a float; casos de prueba dedicados |
| Falsos errores semánticos bloquean la generación | Fase 0 antes que nada |
| IDE congelado por `IN` o ciclo infinito | TM no bloqueante + `QTimer` + `Detener` + límite de pasos |
| Mostrar código viejo | Regla dura 4 + marca "desactualizado" + F9 siempre recompila |
| Funciona en `python` pero no en el `.exe` | Actualizar `IDE.spec` y probar el `.exe` (Fase 6.4) |
| Programas grandes exceden memoria de instrucciones | `IADDR_SIZE = 4096`; error claro si se excede |

## 5. Fuera de alcance
Arreglos, cadenas/caracteres en `cout`, funciones, `switch/case`, optimización de código, traducir `.ci → .tm`.

## 6. Decisiones confirmadas por el usuario
1. Los 5 programas de la revisión **todavía no se conocen**: preparar el compilador para cualquiera de los 12 grupos de `EjericiosFinalesCompisII.pdf`.
2. `%` y `^` **sí** se agregan (Fase 2).
3. El lenguaje ya maneja reales (`real` ≡ `float`), por lo que la TM con valores reales (D3, D4) es parte del alcance, no requiere más confirmación.

## 7. Definición de terminado
- [ ] `python pruebas/run_tests.py` en verde (oro contra TINY + oráculo + ejercicios).
- [ ] Factorial: mismas 42 instrucciones que el TINY de la docente; entrada 5 → 120 en el IDE.
- [ ] F8 muestra `.tm` (tabla y archivo) y `.ci` rotulados; F9 ejecuta pidiendo entradas y muestra resultados, registros y memoria.
- [ ] Con error de análisis no se genera ni se muestra código previo.
- [ ] `dist/Ide.exe` regenerado y probado.
- [ ] Documentos de `docs/` y `CONTEXTO.md` actualizados.
