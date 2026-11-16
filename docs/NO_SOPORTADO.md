# Lo que el lenguaje NO soporta

| Característica | Estado | Cómo resolver los ejercicios sin ella |
|---|---|---|
| Arreglos | no existe | leer los datos dentro de un ciclo y usar acumuladores / máximos parciales |
| Cadenas y caracteres en `cout` | no existe (la TM sólo imprime números) | codificar la respuesta como número (p. ej. positivo = 0, negativo = 1, nulo = 2) |
| Funciones / procedimientos | no existe | todo el programa va dentro de `main() { ... }` |
| `switch` / `case` | palabras reservadas sin regla gramatical | `if` anidados |
| Negación lógica `!` | el léxico la reconoce, la gramática no | invertir la comparación (`a != b` en vez de `!(a == b)`) |
| Corto circuito en `&&` / `\|\|` | no: se evalúan ambos lados | separar en `if` anidados si el lado derecho puede fallar (p. ej. dividir entre cero) |
| Relacionales fuera de condiciones | `cout a < b;` y `x = a < b;` son error sintáctico | `if (a < b) then cout 1; else cout 0; end;` |
| Exponente real o negativo en `^` | el exponente debe ser `int`; si es ≤ 0 el resultado es 1 | — |
| `%` con reales | sólo `int % int` | — |
| Optimización de código | no se hace (tampoco plegado de constantes) | — |
| Traducir `.ci` → `.tm` | no: ambos se generan en paralelo desde el árbol | — |
| Ámbitos anidados | un solo ámbito (`main`) | — |
