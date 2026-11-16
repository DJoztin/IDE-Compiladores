# Ejercicios finales — programa listo para cada grupo

Cada ejercicio de `referencia/EjericiosFinalesCompisII.pdf` (12 grupos) tiene su programa en `pruebas/programas/`,
con un archivo `.in` (entradas de ejemplo) y un `.esperado` (salida esperada, calculada a mano).
`python pruebas/run_tests.py` comprueba todos: la salida de la TM debe coincidir con la esperada y con el oráculo.

Como la TM sólo imprime números, las respuestas de texto van codificadas como números (igual que en el PDF: positivo=0, Aceptado=1…).
Las variantes `b`, `c` del mismo nombre prueban otras ramas del mismo programa.

Para la revisión: abrir el `.txt` en el IDE, **F8** para ver el código y **F9** para ejecutarlo, tecleando las entradas del `.in`.

## Grupo 1

| # | Ejercicio | Tipo | Archivo | Entradas de ejemplo | Salida esperada |
|---|---|---|---|---|---|
| 1 | Orden inverso de A, B, C, D | secuencial | `01_orden_inverso.txt` | 1 2 3 4 | 4 3 2 1 |
| 2 | Positivo=0, negativo=1, nulo=2 | selectivo | `02_signo.txt` | -8 | 1 |
| 3 | Orden creciente=1, 0=No | selectivo | `03_creciente.txt` | 3 7 9 | 1 |
| 4 | Término N de Fibonacci | repetitivo | `04_fibonacci.txt` | 10 | 34 |
| 5 | Lluvias NORTE/CENTRO/SUR | repetitivo | `g01_5_lluvias.txt` | 10 1 19 10 2 18 10 3 17 10 4 16 10 5 15 10 6 14 10 7 2.5 … | 6.5 7 2.5 3 |

## Grupo 2

| # | Ejercicio | Tipo | Archivo | Entradas de ejemplo | Salida esperada |
|---|---|---|---|---|---|
| 1 | ID y promedio de 5 calificaciones | secuencial | `05_promedio.txt` | 1234 8 9 10 7.5 9.5 | 1234 8.8 |
| 2 | Grillo T = h/4 + 40 | selectivo | `06_grillo.txt` | 100 | 65.0 |
| 3 | Impuesto por tramos | selectivo | `07_impuesto.txt` | 100 | 130.0 |
| 4 | Llamadas telefónicas | repetitivo | `g02_4_llamadas.txt` | 1 5 2 2 2 10 3 4 0 | 13.65 1.2 4.56 0.0 19.41 |
| 5 | Bodega de vinos | repetitivo | `g02_5_vino.txt` | 3 10 20 5 1 2 4 50 0 3 3 6 30 0 2 1 | 38.0 60.0 39.0 20.0 100.0 5.0 6.0 6.0 2 50.0 2 |

## Grupo 3

| # | Ejercicio | Tipo | Archivo | Entradas de ejemplo | Salida esperada |
|---|---|---|---|---|---|
| 1 | Perímetro y área del rectángulo | secuencial | `19_rectangulo.txt` | 3.5 2 | 11.0 7.0 |
| 2 | A, B, C en forma descendente | selectivo | `g03_2_descendente.txt` | 5 9 2 | 9 5 2 |
| 3 | Mayor de tres reales | selectivo | `08_mayor_tres_reales.txt` | 2.5 7.25 7.25 | 7.25 |
| 4 | Serie 1^1 + 2^2 + … + N^N | repetitivo | `11_serie_potencias.txt` | 4 | 288 |
| 5 | Producción de N fábricas | repetitivo | `g03_5_fabricas.txt` | 2 101 1000000 1000000 1000000 1000000 1000000 1000000 350… | 101 14500000.0 1 202 24000000.0 0 202 24000000.0 |

## Grupo 4

| # | Ejercicio | Tipo | Archivo | Entradas de ejemplo | Salida esperada |
|---|---|---|---|---|---|
| 1 | Dinosaurio: libras→kg, pies→m | secuencial | `g04_1_dinosaurio.txt` | 150 20 | 68.04 6.096 |
| 2 | Función VAL según NUM | selectivo | `g04_2_funcion_val.txt` | 2 3 | 1000000.0 |
| 3 | Pago con horas extra por categoría | selectivo | `g04_3_horas_extra.txt` | 1500 35 2 | 2640.0 |
| 4 | Ventas por rangos | repetitivo | `g04_4_ventas.txt` | 6 150 200 250 399.5 400 1000 | 2 350.0 2 649.5 2 1400.0 |
| 5 | Estadio | repetitivo | `18_estadio.txt` | 100 80.5 50 30 10 1 2 3 4 1 1 5 10 -1 -1 | 1 2 200.0 3 4 200.0 1 1 100.0 5 10 100.0 3 0 4 0 10 600.0 |

## Grupo 5

| # | Ejercicio | Tipo | Archivo | Entradas de ejemplo | Salida esperada |
|---|---|---|---|---|---|
| 1 | Área y volumen del cilindro | secuencial | `17_cilindro.txt` | 3 5 | 94.248 141.372 |
| 2 | Aumento 15% / 12% | selectivo | `g05_2_aumento.txt` | 800 | 920.0 |
| 3 | Facultades menores | selectivo | `g05_3_facultades.txt` | 12345 2 7 9.1 | 12345 2 1 |
| 4 | Mayor y menor de N enteros | repetitivo | `09_mayor_menor.txt` | 5 4 -2 17 3 8 | 17 -2 |
| 5 | Bodega de vinos | repetitivo | `g02_5_vino.txt` | 3 10 20 5 1 2 4 50 0 3 3 6 30 0 2 1 | 38.0 60.0 39.0 20.0 100.0 5.0 6.0 6.0 2 50.0 2 |

## Grupo 6

| # | Ejercicio | Tipo | Archivo | Entradas de ejemplo | Salida esperada |
|---|---|---|---|---|---|
| 1 | Segundos en N días | secuencial | `g06_1_segundos.txt` | 3 | 259200 |
| 2 | Aprobado=1 / reprobado=0 | selectivo | `g06_2_aprobado.txt` | 8 | 1 |
| 3 | Costo de hospital | selectivo | `g06_3_hospital.txt` | 4 20 5 | 176.0 |
| 4 | Serie 1 − 1/2 + 1/3 − … | repetitivo | `10_serie_alterna.txt` | 4 | 0.583333 |
| 5 | Producción de N fábricas | repetitivo | `g03_5_fabricas.txt` | 2 101 1000000 1000000 1000000 1000000 1000000 1000000 350… | 101 14500000.0 1 202 24000000.0 0 202 24000000.0 |

## Grupo 7

| # | Ejercicio | Tipo | Archivo | Entradas de ejemplo | Salida esperada |
|---|---|---|---|---|---|
| 1 | (A + B)^2 / 3 | secuencial | `g07_1_expresion.txt` | 3 4 | 16.333333 |
| 2 | Positivo=0, negativo=1, nulo=2 | selectivo | `02_signo.txt` | -8 | 1 |
| 3 | Tres enteros en orden creciente | selectivo | `g07_3_orden_creciente.txt` | 7 -3 4 | -3 4 7 |
| 4 | Votos de 4 candidatos | repetitivo | `13b_votos_pdf.txt` | 1 3 1 4 2 2 1 4 1 1 1 2 1 3 1 4 0 | 8 3 2 3 50.0 18.75 12.5 18.75 |
| 5 | Producción de N fábricas | repetitivo | `g03_5_fabricas.txt` | 2 101 1000000 1000000 1000000 1000000 1000000 1000000 350… | 101 14500000.0 1 202 24000000.0 0 202 24000000.0 |

## Grupo 8

| # | Ejercicio | Tipo | Archivo | Entradas de ejemplo | Salida esperada |
|---|---|---|---|---|---|
| 1 | Cambio a entregar | secuencial | `g08_1_cambio.txt` | 37.5 50 | 12.5 |
| 2 | P^3 + Q^4 − 2·P^2 < 680 | selectivo | `g08_2_expresion_pq.txt` | 3 4 | 1 |
| 3 | Descuento por monto | selectivo | `g08_3_descuento.txt` | 800 | 760.0 |
| 4 | Ceros hasta −1 | repetitivo | `12_ceros_centinela.txt` | 0 5 0 0 3 -1 | 3 |
| 5 | Bodega de vinos | repetitivo | `g02_5_vino.txt` | 3 10 20 5 1 2 4 50 0 3 3 6 30 0 2 1 | 38.0 60.0 39.0 20.0 100.0 5.0 6.0 6.0 2 50.0 2 |

## Grupo 9

| # | Ejercicio | Tipo | Archivo | Entradas de ejemplo | Salida esperada |
|---|---|---|---|---|---|
| 1 | Área y volumen del cilindro | secuencial | `17_cilindro.txt` | 3 5 | 94.248 141.372 |
| 2 | Grillo T = h/4 + 40 | selectivo | `06_grillo.txt` | 100 | 65.0 |
| 3 | Impuesto por tramos | selectivo | `07_impuesto.txt` | 100 | 130.0 |
| 4 | Primos menores que M (y cuántos) | repetitivo | `14_primos.txt` | 20 | 2 3 5 7 11 13 17 19 8 |
| 5 | Lluvias NORTE/CENTRO/SUR | repetitivo | `g01_5_lluvias.txt` | 10 1 19 10 2 18 10 3 17 10 4 16 10 5 15 10 6 14 10 7 2.5 … | 6.5 7 2.5 3 |

## Grupo 10

| # | Ejercicio | Tipo | Archivo | Entradas de ejemplo | Salida esperada |
|---|---|---|---|---|---|
| 1 | Perímetro y área del rectángulo | secuencial | `19_rectangulo.txt` | 3.5 2 | 11.0 7.0 |
| 2 | Aumento por categoría | selectivo | `g10_2_categoria.txt` | 3 1000 | 3 1080.0 |
| 3 | Mayor de tres reales | selectivo | `08_mayor_tres_reales.txt` | 2.5 7.25 7.25 | 7.25 |
| 4 | Números perfectos ≤ N | repetitivo | `15_perfectos.txt` | 500 | 6 28 496 |
| 5 | Estadio | repetitivo | `18_estadio.txt` | 100 80.5 50 30 10 1 2 3 4 1 1 5 10 -1 -1 | 1 2 200.0 3 4 200.0 1 1 100.0 5 10 100.0 3 0 4 0 10 600.0 |

## Grupo 11

| # | Ejercicio | Tipo | Archivo | Entradas de ejemplo | Salida esperada |
|---|---|---|---|---|---|
| 1 | Cambio a entregar | secuencial | `g08_1_cambio.txt` | 37.5 50 | 12.5 |
| 2 | Aumento por categoría | selectivo | `g10_2_categoria.txt` | 3 1000 | 3 1080.0 |
| 3 | Llamada internacional por zona | selectivo | `g11_3_llamada_zona.txt` | 18 10 | 45.0 |
| 4 | Sucesión de ULAM | repetitivo | `16_ulam.txt` | 26 | 26 13 40 20 10 5 16 8 4 2 1 |
| 5 | Lluvias NORTE/CENTRO/SUR | repetitivo | `g01_5_lluvias.txt` | 10 1 19 10 2 18 10 3 17 10 4 16 10 5 15 10 6 14 10 7 2.5 … | 6.5 7 2.5 3 |

## Grupo 12

| # | Ejercicio | Tipo | Archivo | Entradas de ejemplo | Salida esperada |
|---|---|---|---|---|---|
| 1 | (A + B)^2 / 3 | secuencial | `g07_1_expresion.txt` | 3 4 | 16.333333 |
| 2 | P^3 + Q^4 − 2·P^2 < 680 | selectivo | `g08_2_expresion_pq.txt` | 3 4 | 1 |
| 3 | Descuento por monto | selectivo | `g08_3_descuento.txt` | 800 | 760.0 |
| 4 | Votos de 4 candidatos | repetitivo | `13b_votos_pdf.txt` | 1 3 1 4 2 2 1 4 1 1 1 2 1 3 1 4 0 | 8 3 2 3 50.0 18.75 12.5 18.75 |
| 5 | Estadio | repetitivo | `18_estadio.txt` | 100 80.5 50 30 10 1 2 3 4 1 1 5 10 -1 -1 | 1 2 200.0 3 4 200.0 1 1 100.0 5 10 100.0 3 0 4 0 10 600.0 |

## Supuestos de interpretación

- **Lluvias:** por cada mes se leen tres valores (norte, centro, sur). Imprime el promedio del centro, el mes y el registro mínimos del sur, y la región con más lluvia (1 = norte, 2 = centro, 3 = sur).
- **Llamadas (G2):** se lee tipo (1 internacional, 2 nacional, 3 local) y minutos hasta tipo 0. Los 3 primeros minutos tienen costo fijo. Las primeras 50 llamadas locales no se cobran.
- **Vinos:** el total de cada año se imprime dentro del ciclo. Al final van los totales por tipo, el año y los litros del máximo del tipo 2, y el **primer** año sin vino tipo 3 (0 si no hubo). Sin arreglos no se pueden guardar todos los años para imprimirlos después.
- **Fábricas:** por fábrica imprime clave, total anual y 1/0 según si julio superó 3 000 000. Al final imprime la clave y el total de la que más produjo.
- **Función VAL (G4):** `100**V` se toma como potencia `100 ^ V`. `100 / V` es división real y con V = 0 da 0.
- **Ventas (G4):** se lee N y luego N ventas. Imprime cantidad y suma de cada rango.
- **Facultades (G5):** carrera 1 Economía, 2 Computación, 3 Administración, 4 Contabilidad. Si es aceptado imprime matrícula, carrera y 1; si no, 0.
- **Llamada por zona (G11):** con una clave inválida imprime −1.
- **Estadio:** las ventas terminan con `-1, -1` (como en el PDF). Imprime clave, cantidad e importe de cada venta, luego los boletos de cada tipo y la recaudación total.
