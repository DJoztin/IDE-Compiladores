
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
