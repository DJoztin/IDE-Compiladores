# Lo que el lenguaje NO soporta

| Característica | Estado | Cómo resolver los ejercicios sin ella |
|---|---|---|
| Arreglos | no existe | leer los datos dentro de un ciclo y usar acumuladores / máximos parciales |
| Variables de texto, concatenar cadenas | no existe: los textos sólo sirven como indicación en `cin("…", x)`, etiqueta en `cout "…", expr` o mensaje en `cout "…"` | las respuestas se siguen dando como números (positivo = 0, Aceptado = 1…) con una etiqueta que lo explica |
| Funciones / procedimientos | no existe | todo el programa va dentro de `main() { ... }` |
| `switch` / `case` | palabras reservadas sin regla gramatical | `if` anidados |
| Negación lógica `!` | el léxico la reconoce, la gramática no | invertir la comparación (`a != b` en vez de `!(a == b)`) |
| Paréntesis en condiciones lógicas | `if ((a > 1 && a < 5) \|\| b == 0)` es error sintáctico; `&&` y `\|\|` tienen la misma precedencia y se evalúan de izquierda a derecha | ordenar la condición (`a > 1 && a < 5 \|\| b == 0`) o usar `if` anidados |
| Corto circuito en `&&` / `\|\|` | no: se evalúan ambos lados | separar en `if` anidados si el lado derecho puede fallar (p. ej. dividir entre cero) |
| Relacionales fuera de condiciones | `cout a < b;` y `x = a < b;` son error sintáctico | `if (a < b) then cout 1; else cout 0; end;` |
| Exponente real o negativo en `^` | el exponente debe ser `int`; si es ≤ 0 el resultado es 1 | — |
| `%` con reales | sólo `int % int` | — |
| Optimización de código | no se hace (tampoco plegado de constantes) | — |
| Traducir `.ci` → `.tm` | no: ambos se generan en paralelo desde el árbol | — |
| Ámbitos anidados | un solo ámbito (`main`) | — |
