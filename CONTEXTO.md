# Contexto del Proyecto — IDE Compiladores (UAA)

> Documento de contexto del proyecto de **Compiladores II**. Resume la arquitectura, el lenguaje, el estado actual y lo que falta. Sirve como referencia para el equipo y para retomar el desarrollo (o para dárselo como contexto a un asistente de IA).

**Ubicación:** `C:\Users\zzzup\Documents\8tavoSemestre\compiladores\IDE\IDE-Compiladores`
**Lenguaje de implementación:** Python 3.10+ · **GUI:** PyQt6 · **Empaquetado:** PyInstaller (`IDE.spec`)

---

## 1. Qué es el proyecto

Un **IDE con compilador integrado** para un lenguaje propio de tipo C/Pascal. El IDE (interfaz gráfica) y el compilador (motor de análisis) son **módulos separados**: el IDE llama al compilador y captura su salida. El compilador también puede ejecutarse solo, desde consola.

```
ide_compilador.py  ──importa como módulo──►  compilador.py
   (interfaz GUI)   ◄──stdout / stderr──────  (motor de análisis)
```

---

## 2. Archivos del proyecto

| Archivo | Rol | Estado |
|---|---|---|
| `compilador.py` | **Motor del compilador** (léxico + sintáctico + semántico). | Léxico ✅ · Sintáctico ✅ · Semántico ✅ · resto ❌ |
| `ide_compilador.py` | **IDE / GUI** (PyQt6): editor, pestañas, docks, temas. 1409 líneas. | ✅ |
| `highlighter.py` | Resaltado de sintaxis del editor (`LexicoHighlighter`). | ✅ |
| `token_panel.py` | Panel visual de tokens con filtros por tipo (`TokenPanel`). | ✅ |
| `IDE.spec` | Configuración de PyInstaller para generar el `.exe`. | ✅ |
| `README.md` | Documentación de uso del IDE. | ✅ |
| `codigo_prueba.txt`, `testSintactico.txt` | Programas de prueba. | — |

---

## 3. El lenguaje (especificación)

### 3.1 Palabras reservadas
```
if  else  end  do  while  switch  case  int  float  real  main  cin  cout  then  until
```
> Nota: `switch` y `case` son palabras reservadas pero **aún no** tienen regla gramatical (ver §7 Pendientes).

### 3.2 Tipos de dato
`int`, `real`, `float` (numéricos; `real` y `float` con parte flotante).

### 3.3 Tipos de token (categorías del léxico)
`ENTERO`, `REAL`, `IDENTIFICADOR`, `RESERVADA`, `OP_ARITMETICO` (`+ - * / % ^ ++ --`), `OP_RELACIONAL` (`< > <= >= ==`), `OP_LOGICO` (`&& || !`), `ASIGNACION` (`=`), `SIMBOLO` (`( ) { } [ ] , ; :`), `CADENA` (`"..."`), `CARACTER` (`'...'`), `ERROR`.

### 3.4 Comentarios
`// una línea` y `/* multilínea */` — se descartan en el léxico (no generan token).

### 3.5 Gramática (descenso recursivo)
```
programa    → 'main' '(' ')' '{' lista_sent '}'
lista_sent  → sentencia*
sentencia   → declaracion | asig_incr | if_stmt | do_until
            | while_stmt | cin_stmt | cout_stmt
declaracion → ('int'|'real'|'float') lista_ids ';'
lista_ids   → ID (',' ID)*
asig_incr   → ID ('=' expresion | '++' | '--') ';'
if_stmt     → 'if' '(' condicion ')' 'then' lista_sent ('else' lista_sent)? 'end' ';'
do_until    → 'do' '{' lista_sent '}' 'until' '(' condicion ')' ';'
while_stmt  → 'while' '(' condicion ')' '{' lista_sent '}' ';'
cin_stmt    → 'cin' '(' ID ')' ';'
cout_stmt   → 'cout' expresion ';'
condicion   → expr_rel (('&&'|'||') expr_rel)*
expr_rel    → expresion (OP_REL expresion)?
expresion   → termino (('+'|'-') termino)*
termino     → factor (('*'|'/') factor)*
factor      → '(' expresion ')' | ENTERO | REAL | ID | '-' factor
```

---

## 4. Arquitectura del compilador (`compilador.py`)

### 4.1 Analizador Léxico — `analizar(codigo) -> (tokens, errores)`
- Autómata de estado finito (DFA) que recorre el texto carácter por carácter con `peek()` / `avanzar()`.
- Reconoce: enteros y reales (valida `123.` y `123.4.5` como errores), identificadores vs. reservadas, operadores (incluye `++`, `--`, `&&`, `||`, `<=`, `>=`, `==`), cadenas, caracteres y comentarios.
- Clase `Token(tipo, valor, linea, columna)` y `ErrorLexico(mensaje, linea, columna)`.

### 4.2 Analizador Sintáctico — `AnalizadorSintactico` (parser de descenso recursivo)
- Entrada: los tokens **válidos** (ignora los de tipo ERROR).
- Genera un **árbol** de nodos `NodoSint(tipo, valor, linea, hijos[])`.
- En las expresiones, el **operador es la raíz** y los operandos son los hijos izquierdo/derecho — así el árbol ya queda listo para recorrerlo en el análisis semántico.
- `ErrorSintactico(mensaje, linea, columna)`. Recuperación básica: ante un token inesperado, reporta y avanza.
- Interfaz pública: `analizar_sintactico(codigo) -> (arbol, errores_lex, errores_sint)`.

### 4.3 Tipos de nodo del árbol (`NodoSint.tipo`)
`programa`, `lista_sentencias`, `declaracion` (valor = int/real/float), `lista_ids`, `identificador`, `asignacion`, `incremento`, `decremento`, `if_stmt` (+ `then_branch`, `else_branch`), `do_until_stmt`, `while_stmt`, `cin_stmt`, `cout_stmt`, `condicion` (&&/||), `expr_rel` (op relacional), `expresion` (+/−), `termino` (*//), `factor_par`, `entero`, `real_lit`, `negativo`, `error`.

### 4.4 Punto de entrada — `main()`
```bash
python compilador.py --lexico      archivo.txt   # imprime tokens
python compilador.py --sintactico  archivo.txt   # construye el árbol
```
Escribe resultados a **stdout** y errores a **stderr**. Actualmente solo despacha `--lexico` y `--sintactico`.

---

## 5. El IDE (`ide_compilador.py`)

Interfaz en PyQt6. Componentes principales:
- `CodeEditor` (QPlainTextEdit): numeración de líneas, línea activa, resaltado de líneas con error, drag & drop.
- `FileExplorer`: árbol de carpetas/archivos.
- `TokenPanel` (`token_panel.py`): tabla de tokens con filtros por tipo.
- `SyntaxTreePanel`: muestra el árbol sintáctico como `QTreeWidget`.
- `LexicoHighlighter` (`highlighter.py`): resaltado de sintaxis.
- 6 temas (VS Dark, Light, Monokai, Dracula, Solarized, Nord).
- Atajos: F5 léxico · F6 sintáctico · F7 semántico · F8 intermedio · F9 ejecutar.
- Importa `compilador.py` como módulo (`resource_path`) para llamar sus fases.

---

## 6. Estado actual (fases del compilador)

| Fase | Estado | Dónde |
|---|---|---|
| **1. Léxico** | ✅ Implementado | `analizar()` |
| **2. Sintáctico** | ✅ Implementado | `AnalizadorSintactico` |
| **3. Semántico** | ✅ Implementado (ver §11) | `analizar_semantico()` · F7 |
| **4. Código intermedio** | ❌ Pendiente | — (F8) |
| **5. Ejecución** | ❌ Pendiente | — (F9) |

El IDE ya tiene los botones/atajos y paneles (Semántico, Cod. Intermedio, Tabla de Símbolos, Resultado Ejecución) pero el backend de esas fases todavía no existe en `compilador.py` (el `main()` solo reconoce `--lexico` y `--sintactico`).

---

## 7. Análisis Semántico — diseño original (modelado en TINY; implementado en §11)

El análisis semántico es la siguiente fase a implementar. Se toma como modelo el compilador **TINY** de Kenneth Louden (visto en clase). Lo que hay que construir:

1. **Recorrer el árbol** `NodoSint` con una función recursiva (equivalente a `traverse()` de TINY).
2. **Tabla de símbolos**: en Python basta un **diccionario** (`tabla = {}`) — ya es una tabla hash con manejo de colisiones integrado, así que **no** hay que programar `hash()` ni el encadenamiento como en TINY. Cada entrada guarda al menos: `tipo` (int/real/float), `linea` de declaración.
3. **Pasada 1 — construir la tabla desde las DECLARACIONES** (a diferencia de TINY, que la construye al usar la variable): recorrer los nodos `declaracion` y registrar cada id con su tipo. Reportar **doble declaración**.
4. **Pasada 2 — verificar tipos en postorden** (equivalente a `typeCheck`/`checkNode`): inferir el tipo de cada nodo de expresión (`entero`→int, `real_lit`→real, `identificador`→su tipo declarado) y aplicar reglas.

### Reglas semánticas a verificar (propias del lenguaje)
- **Variable no declarada** (TINY no lo hace; aquí sí, porque hay declaración explícita).
- **Doble declaración** del mismo identificador.
- **Compatibilidad de tipos en asignación** y **coerción int ↔ real** (TINY solo maneja Integer).
- **Condición no booleana** en `if`, `while`, `until` (debe ser una expresión relacional, no un número suelto).
- **Operador aplicado a tipo inválido**.

### Formato de errores semánticos (según README)
```
[Error Semantico] Linea X: descripción
```

### Mapeo TINY → este proyecto
| TINY (C) | Este proyecto (Python) |
|---|---|
| `traverse(t, preProc, postProc)` | función recursiva sobre `NodoSint` |
| `buildSymtab` / `insertNode` | llenar la tabla desde nodos `declaracion` (con tipo) |
| `st_insert` / `st_lookup` | `tabla[nombre] = {...}` / `nombre in tabla` |
| `hash()`, `hashTable[]`, encadenamiento | **innecesario** — lo da el `dict` de Python |
| `typeCheck` / `checkNode` | recorrido postorden que infiere y verifica tipos |
| `typeError()` | `error_semantico(linea, msg)` con formato `[Error Semantico]` |

---

## 8. Diferencias clave del lenguaje frente a TINY

| Aspecto | TINY | Este proyecto |
|---|---|---|
| Declaración | Implícita (al usarse) | **Explícita**: `int x,y,z;  real a,b,c;` |
| Tipos | Integer, Boolean, Void | `int`, `real`, `float` |
| Asignación | `:=` | `=` |
| Entrada / salida | `read` / `write` | `cin(...)` / `cout(...)` |
| Variable no declarada | No se valida | **Debe** validarse |
| Coerción de tipos | No aplica | `int` ↔ `real` |
| Control | if-then-else-end, repeat-until | if-then-else-end, do-while-until, while |
| Comentarios | `{ ... }` | `// ...` y `/* ... */` |
| Tabla de símbolos | Hash + encadenamiento a mano (C) | `dict` de Python |

---

## 9. Cómo ejecutar

```bash
pip install PyQt6
python ide_compilador.py                          # lanzar el IDE
python compilador.py --lexico     archivo.txt     # solo léxico
python compilador.py --sintactico archivo.txt     # solo sintáctico
```

Generar ejecutable: `pyinstaller IDE.spec` (produce `Ide.exe`).

---

## 10. Pendientes / notas conocidas

- `switch` / `case` son palabras reservadas pero **no** tienen regla gramatical todavía.
- Fases **semántico**, **código intermedio** y **ejecución** están en la UI (F7/F8/F9) pero **sin backend** en `compilador.py`.
- El `main()` de `compilador.py` solo maneja `--lexico` y `--sintactico`; falta agregar `--semantico`, `--intermedio`, `--ejecutar`.
- `cout_stmt` acepta `cout expresion ;` (los paréntesis, si se usan, se parsean como `factor_par`).
- Los errores léxicos no bloquean el parseo: el sintáctico usa solo los tokens válidos.

---

*Contexto generado a partir del escaneo del código fuente del proyecto (léxico y sintáctico completos; semántico pendiente).*

---

## 11. Fase 3 — Análisis Semántico (IMPLEMENTADO)

**Dónde:** `compilador.py`, sección *ANÁLISIS SEMÁNTICO* · Interfaz: `analizar_semantico(codigo) -> ResultadoSemantico` · Consola: `python compilador.py --semantico archivo.txt`

### Ajustes previos (Fase 1)
- Nuevas reservadas `bool`, `true`, `false`; `declaracion` acepta `bool`; `factor` acepta `true`/`false` (nodo `booleano`).
- `NodoSint` guarda `columna`; `asignacion`/`incremento`/`decremento`/`cin_stmt` guardan `id_nombre`.
- La gramática NO se modificó para facilitar el semántico. Limitación conocida: en una asignación sólo cabe `expresion` aritmética (`g = 3 > 2;` es error sintáctico); relacionales/lógicos sólo en condiciones.

### Decisiones
- `real` ≡ `float` (mismo tipo; la tabla muestra la palabra declarada).
- Ámbito único (`main`).
- Dirección de memoria tipo TINY: contador `loc` 0,1,2… en orden de declaración.
- Valor (opción B): se calcula para constantes y se sigue el valor de variables en código lineal. Se vuelve desconocido (`?`): tras `cin`, tras un `if` si las ramas difieren, y en ciclos para las variables asignadas en el cuerpo (al entrar y al salir).
- Se trabaja sobre `copy.deepcopy(AST)`: el AST original queda intacto para comparar.
- El semántico sólo corre si no hay errores léxicos/sintácticos.
- Tipo `error` se propaga sin generar errores en cascada.

### Atributos
| Atributo | Clase | Flujo |
|---|---|---|
| `dtype` | heredado | `declaracion` → `lista_ids` → `identificador` |
| `loc` | tabla | asignado al insertar |
| `tipo` | sintetizado | hojas → operadores → raíz; identificador = búsqueda en tabla |
| `valor` | sintetizado | sólo si se puede determinar |
| `conv` | — | `int→float` marcado en el operando convertido |
| `chk` | — | ✓ / ✗ de la verificación |

### Reglas de tipos
- `+ - * /`: int/float; int op float → float (coerción del int). `int / int` = división entera (trunca).
- `< > <= >=`: numéricos → bool. `== !=`: numéricos o bool con bool → bool.
- `&& ||`: bool con bool → bool. `-` unario: numérico.
- Asignación: igual tipo ✓; float ← int ✓ (conversión); int ← float ✗ (conversión no válida); bool ↔ numérico ✗.
- `++ --`: sólo numéricos. Condiciones de `if`/`while`/`until`: deben ser bool.

### Errores semánticos
Identificador no declarado · Declaración duplicada · Incompatibilidad de tipos · Conversión no válida · Uso indebido de operador · Inconsistencia en asignación · Condición no booleana · División entre cero (constante).
Formato: `[ERROR SEMÁNTICO] Línea X, Columna Y: [categoría] mensaje`

### IDE
- Pestaña *Semántico*: AST anotado (columna "Atributos semánticos"), AST original, Recorrido (bitácora INSERTAR/BUSCAR/TIPO/CONVERTIR/VERIFICAR/VALOR), botón *Comparar AST* (lado a lado, expandir/colapsar y scroll sincronizados), botón *Exportar evidencias* (5 .txt).
- *Tabla de Símbolos*: Nombre, Tipo, Loc, Valor, Ámbito, Líneas.
- Árboles con ramas dibujadas (├── └── │), colapsables, exportables a .txt.
- Archivos de prueba: `TestSemantica_adaptado.txt` (el test oficial en nuestra sintaxis, mismas líneas; 6 errores) y `TestSemantica_casos_extra.txt` (cubre las 7 categorías; 11 errores).
