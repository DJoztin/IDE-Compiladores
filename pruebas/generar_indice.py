"""Genera docs/EJERCICIOS.md a partir de pruebas/programas (.txt, .in, .esperado).

    python pruebas/generar_indice.py
"""
import os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(RAIZ, "pruebas", "programas")

G = {
    1: [("Orden inverso de A, B, C, D", "01_orden_inverso"), ("Positivo=0, negativo=1, nulo=2", "02_signo"),
        ("Orden creciente=1, 0=No", "03_creciente"), ("Término N de Fibonacci", "04_fibonacci"),
        ("Lluvias NORTE/CENTRO/SUR", "g01_5_lluvias")],
    2: [("ID y promedio de 5 calificaciones", "05_promedio"), ("Grillo T = h/4 + 40", "06_grillo"),
        ("Impuesto por tramos", "07_impuesto"), ("Llamadas telefónicas", "g02_4_llamadas"),
        ("Bodega de vinos", "g02_5_vino")],
    3: [("Perímetro y área del rectángulo", "19_rectangulo"), ("A, B, C en forma descendente", "g03_2_descendente"),
        ("Mayor de tres reales", "08_mayor_tres_reales"), ("Serie 1^1 + 2^2 + … + N^N", "11_serie_potencias"),
        ("Producción de N fábricas", "g03_5_fabricas")],
    4: [("Dinosaurio: libras→kg, pies→m", "g04_1_dinosaurio"), ("Función VAL según NUM", "g04_2_funcion_val"),
        ("Pago con horas extra por categoría", "g04_3_horas_extra"), ("Ventas por rangos", "g04_4_ventas"),
        ("Estadio", "18_estadio")],
    5: [("Área y volumen del cilindro", "17_cilindro"), ("Aumento 15% / 12%", "g05_2_aumento"),
        ("Facultades menores", "g05_3_facultades"), ("Mayor y menor de N enteros", "09_mayor_menor"),
        ("Bodega de vinos", "g02_5_vino")],
    6: [("Segundos en N días", "g06_1_segundos"), ("Aprobado=1 / reprobado=0", "g06_2_aprobado"),
        ("Costo de hospital", "g06_3_hospital"), ("Serie 1 − 1/2 + 1/3 − …", "10_serie_alterna"),
        ("Producción de N fábricas", "g03_5_fabricas")],
    7: [("(A + B)^2 / 3", "g07_1_expresion"), ("Positivo=0, negativo=1, nulo=2", "02_signo"),
        ("Tres enteros en orden creciente", "g07_3_orden_creciente"), ("Votos de 4 candidatos", "13b_votos_pdf"),
        ("Producción de N fábricas", "g03_5_fabricas")],
    8: [("Cambio a entregar", "g08_1_cambio"), ("P^3 + Q^4 − 2·P^2 < 680", "g08_2_expresion_pq"),
        ("Descuento por monto", "g08_3_descuento"), ("Ceros hasta −1", "12_ceros_centinela"),
        ("Bodega de vinos", "g02_5_vino")],
    9: [("Área y volumen del cilindro", "17_cilindro"), ("Grillo T = h/4 + 40", "06_grillo"),
        ("Impuesto por tramos", "07_impuesto"), ("Primos menores que M (y cuántos)", "14_primos"),
        ("Lluvias NORTE/CENTRO/SUR", "g01_5_lluvias")],
    10: [("Perímetro y área del rectángulo", "19_rectangulo"), ("Aumento por categoría", "g10_2_categoria"),
         ("Mayor de tres reales", "08_mayor_tres_reales"), ("Números perfectos ≤ N", "15_perfectos"),
         ("Estadio", "18_estadio")],
    11: [("Cambio a entregar", "g08_1_cambio"), ("Aumento por categoría", "g10_2_categoria"),
         ("Llamada internacional por zona", "g11_3_llamada_zona"), ("Sucesión de ULAM", "16_ulam"),
         ("Lluvias NORTE/CENTRO/SUR", "g01_5_lluvias")],
    12: [("(A + B)^2 / 3", "g07_1_expresion"), ("P^3 + Q^4 − 2·P^2 < 680", "g08_2_expresion_pq"),
         ("Descuento por monto", "g08_3_descuento"), ("Votos de 4 candidatos", "13b_votos_pdf"),
         ("Estadio", "18_estadio")],
}
TIPO = {1: "secuencial", 2: "selectivo", 3: "selectivo", 4: "repetitivo", 5: "repetitivo"}


def leer(n, ext):
    return " ".join(open(os.path.join(D, n + ext), encoding="utf-8").read().split())


out = ["# Ejercicios finales — programa listo para cada grupo", "",
       "Cada ejercicio de `referencia/EjericiosFinalesCompisII.pdf` (12 grupos) tiene su programa en "
       "`pruebas/programas/`, con un `.in` (entradas de ejemplo) y un `.esperado` (salida esperada, "
       "calculada a mano). `python pruebas/run_tests.py` los comprueba todos: la salida de la TM debe "
       "coincidir con la esperada y con el oráculo.", "",
       "Cada `cin` dice qué se pide (con las opciones válidas) y cada `cout` lleva una etiqueta. "
       "Las respuestas siguen siendo números, como pide el PDF (positivo = 0, Aceptado = 1…).", "",
       "**Validación:** en los ejercicios repetitivos (4 y 5) un dato inválido se avisa y se vuelve a "
       "pedir con `do … until`; en los selectivos (2 y 3) se avisa con un mensaje dentro del `if` "
       "(sin agregar ciclos, para respetar la estructura pedida).", "",
       "Para la revisión: abrir el `.txt` en el IDE, **F8** para ver el código y **F9** para "
       "ejecutarlo, tecleando las entradas del `.in`. Los archivos con sufijo `b`, `c` son el mismo "
       "programa con otras entradas (otras ramas o datos inválidos).", ""]
for g, ej in G.items():
    out += [f"## Grupo {g}", "",
            "| # | Ejercicio | Tipo | Archivo | Entradas de ejemplo | Salida esperada |",
            "|---|---|---|---|---|---|"]
    for i, (t, f) in enumerate(ej, 1):
        e, s = leer(f, ".in"), leer(f, ".esperado") or "(sólo mensaje)"
        if len(e) > 60:
            e = e[:57] + "…"
        out.append(f"| {i} | {t} | {TIPO[i]} | `{f}.txt` | {e} | {s} |")
    out.append("")
out += ["## Supuestos de interpretación", "",
        "- **Lluvias:** por cada mes se leen tres valores (norte, centro, sur); se imprime el número de mes "
        "antes de pedirlos. Al final: promedio del centro, mes y registro mínimos del sur, y la región con "
        "más lluvia (1 = norte, 2 = centro, 3 = sur).",
        "- **Llamadas (G2):** tipo (1 internacional, 2 nacional, 3 local) y minutos, hasta tipo 0. Los 3 "
        "primeros minutos tienen costo fijo. Las primeras 50 llamadas locales no se cobran.",
        "- **Vinos:** se imprime el número de año y el total de ese año dentro del ciclo; al final, los totales "
        "por tipo, el año y los litros del máximo del tipo 2, y el **primer** año sin vino tipo 3 (0 si no "
        "hubo). Sin arreglos no se pueden guardar todos los años para imprimirlos después.",
        "- **Fábricas:** por fábrica: clave, total anual y 1/0 si julio superó 3 000 000. Al final: clave y "
        "total de la que más produjo.",
        "- **Función VAL (G4):** `100**V` se toma como potencia `100 ^ V`; `100 / V` es división real y con "
        "V = 0 avisa y da 0.",
        "- **Ventas (G4):** se lee N y luego N ventas; se imprime cantidad y suma de cada rango.",
        "- **Facultades (G5):** carrera 1 Economía, 2 Computación, 3 Administración, 4 Contabilidad.",
        "- **Estadio:** las ventas terminan con `-1, -1` (como en el PDF).", ""]
open(os.path.join(RAIZ, "docs", "EJERCICIOS.md"), "w", encoding="utf-8").write("\n".join(out))
print("docs/EJERCICIOS.md generado")
