"""
run_tests.py — Pruebas de la fase final (sin dependencias externas).

    python pruebas/run_tests.py          (todo)
    python pruebas/run_tests.py -v       (muestra cada caso)

1. Oro contra TINY: mismas instrucciones TM y mismo .ci que los ejemplos de
   la docente (referencia/Tiny_Intermedio_TM/ejemplos).
2. La TM en Python ejecuta los .tm de la docente tal cual.
3. Casos por construcción: TM == oráculo (intérprete del árbol) == esperado.
4. Errores: sin .tm si hay errores; división entre cero; ciclo infinito.
5. Programas de ejercicios en pruebas/programas (.txt, .in, .esperado).
6. No regresión del semántico (Fase 0).
"""
import os
import re
import sys
import tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, RAIZ)
sys.path.insert(0, AQUI)

import compilador                      # noqa: E402
import tm                              # noqa: E402
from interprete_ast import interpretar  # noqa: E402

REF = os.path.join(RAIZ, "referencia", "Tiny_Intermedio_TM", "ejemplos")
VERBOSE = "-v" in sys.argv

ok_total = 0
fallos: list[str] = []


def check(nombre, cond, detalle=""):
    global ok_total
    if cond:
        ok_total += 1
        if VERBOSE:
            print(f"  ok   {nombre}")
    else:
        fallos.append(f"{nombre}: {detalle}")
        print(f"  FALLO {nombre}: {detalle}")


def instr_tm(texto):
    """Líneas de instrucción normalizadas (sin comentarios de traza)."""
    res = []
    for l in texto.splitlines():
        if not l.strip() or l.lstrip().startswith("*"):
            continue
        res.append(re.sub(r"\s+", " ", l.split("\t")[0]).strip())
    return res


def cuerpo_ci(texto):
    return [l for l in texto.splitlines() if l.strip() and not l.startswith("#")]


def fmt(salidas):
    return [tm.fmt_valor(v) for v in salidas]


def compilar_ok(src):
    r = compilador.compilar(src, escribir=False)
    return r


def correr(src, entradas, max_pasos=5_000_000):
    """Compila y ejecuta en la TM y en el oráculo. Devuelve
    (r, estado_tm, salidas_tm, salidas_oraculo)."""
    r = compilar_ok(src)
    if not r.ok:
        return r, None, None, None
    m = tm.MaquinaTM(max_pasos=max_pasos)
    errs = m.cargar(r.codigo_tm)
    assert not errs, errs
    st, sal = m.ejecutar(entradas)
    try:
        orac = interpretar(r.anotado, r.tabla, entradas)
    except ZeroDivisionError:
        orac = "ZERODIVIDE"
    return r, st, fmt(sal), (fmt(orac) if isinstance(orac, list) else orac)


def parse_in(txt):
    vals = []
    for t in txt.split():
        vals.append(float(t) if any(c in t for c in ".eE") else int(t))
    return vals


# ═══════════════════════════════════════════════════════════════
print("1. Oro contra TINY (.tm y .ci)")
ORO = {
    "factorial": open(os.path.join(AQUI, "oro", "factorial.txt"), encoding="utf-8").read(),
    "aritmetica": """main() {
    int x, y;
    cin(x);
    y = (x + 1) * (x - 2);
    cout y;
}""",
    "condicional": """main() {
    int x;
    cin(x);
    if (x < 3) then
        cout 1;
    else
        cout 2;
    end;
}""",
    "ciclo": """main() {
    int x;
    cin(x);
    do {
        x = x - 1;
    } until (x == 0);
    cout x;
}""",
}
for nombre, src in ORO.items():
    r = compilar_ok(src)
    check(f"oro {nombre}: compila", r.ok, r.mensajes)
    if not r.ok:
        continue
    ref_tm = open(os.path.join(REF, nombre + ".tm"), encoding="utf-8").read()
    ref_ci = open(os.path.join(REF, nombre + ".ci"), encoding="utf-8").read()
    a, b = instr_tm(r.codigo_tm), instr_tm(ref_tm)
    dif = [f"{x!r} != {y!r}" for x, y in zip(a, b) if x != y][:3]
    check(f"oro {nombre}: .tm igual a TINY ({len(b)} instrucciones)",
          a == b, f"{len(a)} vs {len(b)} {dif}")
    check(f"oro {nombre}: .ci igual a TINY", cuerpo_ci(r.codigo_ci) == cuerpo_ci(ref_ci),
          f"\n{cuerpo_ci(r.codigo_ci)}\n{cuerpo_ci(ref_ci)}")
    # orden de emisión: la instrucción parchada aparece fuera de orden
    if nombre == "factorial":
        locs = [int(l.split(":")[0]) for l in instr_tm(r.codigo_tm)]
        check("oro factorial: 13 aparece tras 39 (backpatch)",
              locs.index(13) == locs.index(39) + 1, locs)

# ═══════════════════════════════════════════════════════════════
print("2. TM en Python con los .tm de la docente")
for nombre, ent, esp in [("factorial", [5], ["120"]), ("factorial", [0], []),
                         ("aritmetica", [4], ["10"]), ("condicional", [2], ["1"]),
                         ("condicional", [8], ["2"]), ("ciclo", [3], ["0"])]:
    m = tm.MaquinaTM()
    errs = m.cargar(open(os.path.join(REF, nombre + ".tm"), encoding="utf-8").read())
    st, sal = m.ejecutar(ent)
    check(f"tm docente {nombre} {ent} -> {esp}", not errs and st == tm.Estado.HALT
          and fmt(sal) == esp, f"{errs} {st} {sal}")

m = tm.MaquinaTM()
check("tm: opcode ilegal", m.cargar("0: FOO 0,0,0") == ["Line 1 (Instruction 0)   Illegal opcode"])
check("tm: falta ':'", m.cargar("0 LD 0,0(0)") == ["Line 1 (Instruction 0)   Missing colon"])
check("tm: LDC real", m.cargar("0: LDC 0,3.14(0)\n1: OUT 0,0,0\n2: HALT 0,0,0") == []
      and m.ejecutar([]) == (tm.Estado.HALT, [3.14]))
check("tm: IN ilegal", (m.cargar("0: IN 0,0,0\n1: HALT 0,0,0") == [] and m.paso()
                         == tm.Estado.NECESITA_ENTRADA and not m.dar_entrada("abc")
                         and m.dar_entrada("-2.5") and m.reg[0] == -2.5))
check("tm: formato OUT", [tm.fmt_valor(x) for x in (2.5, 120.0, 3.14159265, -7, 0.1 + 0.2)]
      == ["2.5", "120.0", "3.141593", "-7", "0.3"])

# ═══════════════════════════════════════════════════════════════
print("3. Casos por construcción (TM == oráculo == esperado)")
def B(c):
    """Las relacionales sólo van en condiciones: se imprime 1/0 con un if."""
    return f" if ({c}) then cout 1; else cout 0; end;"


CASOS = [
    # (nombre, cuerpo, entradas, esperado)
    ("suma resta", "int a,b; cin(a); cin(b); cout a+b; cout a-b;", [7, 10], ["17", "-3"]),
    ("mul", "int a; cin(a); cout a*a*3;", [4], ["48"]),
    ("div entera 7/2", "cout 7/2;", [], ["3"]),
    ("div real 7.0/2", "cout 7.0/2;", [], ["3.5"]),
    ("div negativa -7/2", "int a; cin(a); cout a/2;", [-7], ["-3"]),
    ("precedencia", "cout 2+3*4-6/2;", [], ["11"]),
    ("parentesis", "cout (2+3)*(4-6);", [], ["-10"]),
    ("negativo", "int a; cin(a); cout -a; cout -(a+1)*2;", [5], ["-5", "-12"]),
    ("rel <", "int a; cin(a);" + B("a<3") + B("3<a"), [2], ["1", "0"]),
    ("rel <=", "int a; cin(a);" + B("a<=2") + B("a<=1"), [2], ["1", "0"]),
    ("rel >", "int a; cin(a);" + B("a>1") + B("a>2"), [2], ["1", "0"]),
    ("rel >=", "int a; cin(a);" + B("a>=2") + B("a>=3"), [2], ["1", "0"]),
    ("rel ==", "int a; cin(a);" + B("a==2") + B("a==3"), [2], ["1", "0"]),
    ("rel !=", "int a; cin(a);" + B("a!=2") + B("a!=3"), [2], ["0", "1"]),
    ("rel float", "float x; cin(x);" + B("x < 2.5") + B("x > 2"), [2.25], ["1", "1"]),
    ("&&", "int a; cin(a);" + B("a>0 && a<10") + B("a>0 && a>10"), [5], ["1", "0"]),
    ("||", "int a; cin(a);" + B("a<0 || a>3") + B("a<0 || a>10") + B("a>0 || a>3"), [5],
     ["1", "0", "1"]),
    ("&& || encadenados", "int a; cin(a);" + B("a>0 && a<10 || a==-5") + B("a<0 || a>3 && a<4"),
     [-5], ["1", "1"]),
    ("bool var", "bool f, g; f = true; g = false; cout f; cout g;" + B("f == g") + B("f != g")
     + B("f") + B("g || f"), [], ["1", "0", "0", "1", "1", "1"]),
    ("++ --", "int a; a = 5; a++; a++; cout a; a--; cout a;", [], ["7", "6"]),
    ("float ++", "float x; x = 1.5; x++; cout x;", [], ["2.5"]),
    ("conv asignación", "float x; x = 7; cout x / 2;", [], ["3.5"]),
    ("conv expresión mixta", "int a; float r; a = 7; r = a / 2 + 0.5; cout r; "
                             "r = a * 1.0 / 2; cout r;", [], ["3.5", "3.5"]),
    ("cin a float con entero", "float x; cin(x); cout x / 2;", [7], ["3.5"]),
    ("cin a float con real", "float x; cin(x); cout x * 2;", [1.25], ["2.5"]),
    ("if sin else (entra)", "int a; cin(a); if (a > 0) then cout 1; end; cout 9;", [3],
     ["1", "9"]),
    ("if sin else (no entra)", "int a; cin(a); if (a > 0) then cout 1; end; cout 9;", [-3],
     ["9"]),
    ("if con else", "int a; cin(a); if (a > 0) then cout 1; else cout 2; end;", [-1], ["2"]),
    ("if anidado", "int a; cin(a); if (a > 0) then if (a > 10) then cout 2; else cout 1; "
                   "end; else cout 0; end;", [11], ["2"]),
    ("while no entra", "int i; i = 5; while (i < 3) { cout i; i++; }; cout 99;", [], ["99"]),
    ("while", "int i; i = 0; while (i < 3) { cout i; i++; };", [], ["0", "1", "2"]),
    ("while anidado", "int i, j; i = 1; while (i <= 2) { j = 1; while (j <= 2) "
                      "{ cout i*10+j; j++; }; i++; };", [], ["11", "12", "21", "22"]),
    ("do-until", "int i; i = 0; do { i = i + 2; } until (i >= 5); cout i;", [], ["6"]),
    ("do-until una vez", "int i; i = 10; do { cout i; } until (true);", [], ["10"]),
    ("centinela -1", "int x, s; s = 0; cin(x); while (x != -1) { s = s + x; cin(x); }; "
                     "cout s;", [4, 5, 6, -1], ["15"]),
    ("% positivo y negativo", "int a; cin(a); cout a % 3; cout -a % 3;", [7], ["1", "-1"]),
    ("^ entero", "int b; cin(b); cout b ^ 3; cout 2 ^ 10; cout b ^ 0;", [3],
     ["27", "1024", "1"]),
    ("^ asociativa derecha", "cout 2 ^ 3 ^ 2;", [], ["512"]),
    ("^ base float", "float x; x = 1.5; cout x ^ 2;", [], ["2.25"]),
    ("^ dentro de expresión", "int a; cin(a); cout 1 + a ^ 2 * 2;", [3], ["19"]),
    ("temporales anidados", "int a,b,c; cin(a); cin(b); cin(c); "
                            "cout ((a+b)*(b-c))/((a%b)+c^2);", [7, 3, 2], ["2"]),
]
for nombre, cuerpo, ent, esp in CASOS:
    src = "main() {\n" + cuerpo + "\n}"
    r, st, sal, orac = correr(src, ent)
    if r is None or not r.ok:
        check(f"caso {nombre}", False, f"no compila: {r.errores_sem if r else ''}")
        continue
    check(f"caso {nombre}", st == tm.Estado.HALT and sal == orac == esp,
          f"tm={st} {sal} oraculo={orac} esperado={esp}")

# ═══════════════════════════════════════════════════════════════
print("3b. Textos para el usuario (cin con indicación, cout con etiqueta/mensaje)")
src = """main() {
    int clave, m;
    float x;
    cout "Calculo de prueba";
    do {
        cin("Clave (1, 2 o 3)", clave);
        if (clave < 1 || clave > 3) then
            cout("Clave invalida, intenta de nuevo");
        end;
    } until (clave >= 1 && clave <= 3);
    cin(m);
    cin("Un real", x);
    cout "Clave elegida", clave;
    cout x * 2;
}"""
r = compilar_ok(src)
check("textos: compila", r.ok, [str(e) for e in r.errores_sint + r.errores_sem])
if r.ok:
    m = tm.MaquinaTM(); m.cargar(r.codigo_tm)
    eventos = []
    entradas = ["7", "2.5", "2", "4", "1.5"]
    while True:
        st = m.paso()
        if st == tm.Estado.NECESITA_ENTRADA:
            eventos.append(("pide", m.pista_entrada()))
            v = entradas.pop(0)
            if not m.dar_entrada(v):
                eventos.append(("rechaza", v, m.error_entrada))
                v = entradas.pop(0)
                assert m.dar_entrada(v)
        elif st == tm.Estado.MENSAJE:
            eventos.append(("msg", m.ultimo_mensaje))
        elif st == tm.Estado.SALIDA:
            eventos.append(("out", m.texto_salida()))
        elif st != tm.Estado.OKAY:
            break
    esperado = [("msg", "Calculo de prueba"), ("pide", "Clave (1, 2 o 3)"),
                ("msg", "Clave invalida, intenta de nuevo"), ("pide", "Clave (1, 2 o 3)"),
                ("rechaza", "2.5", "Illegal value: se esperaba un numero entero"),
                ("pide", "m (int)"), ("pide", "Un real"),
                ("out", "Resultado del programa (OUT): 2   <- Clave elegida"),
                ("out", "Resultado del programa (OUT): 3.0")]
    check("textos: indicaciones, rechazo de real en int, etiquetas y mensajes",
          eventos == esperado, f"\n{eventos}")
    check("textos: salidas numéricas sin los mensajes", m.salidas == [2, 3.0], m.salidas)
    check("textos: .ci con write de texto", 'write "Calculo de prueba"' in r.codigo_ci)
    check("textos: mensaje = LDA 0,0(0) (no altera registros)",
          any(i[1] == "LDA" and i[2:5] == (0, 0, 0) and i[5].startswith("msg:")
              for i in r.instrucciones))

# ═══════════════════════════════════════════════════════════════
print("4. Errores")
with tempfile.TemporaryDirectory() as d:
    fuente = os.path.join(d, "prog.txt")
    r = compilador.compilar("main() { int a; cin(a); cout a; }", fuente)
    check("se escriben .tm y .ci", r.ok and os.path.isfile(r.ruta_tm) and os.path.isfile(r.ruta_ci))
    r2 = compilador.compilar("main() { int a; cout b; }", fuente)
    check("error semántico: no hay código", not r2.ok and r2.codigo_tm == "" and r2.instrucciones == [])
    check("error semántico: se borran .tm/.ci viejos",
          not os.path.exists(os.path.join(d, "prog.tm")) and not os.path.exists(os.path.join(d, "prog.ci")))
    r3 = compilador.compilar("main() { int a cin(a); }", fuente)
    check("error sintáctico: no hay código", not r3.ok and r3.codigo_tm == "")
r, st, sal, orac = correr("main() { int a, b; cin(a); cin(b); cout a / b; }", [5, 0])
check("división entre cero en ejecución", st == tm.Estado.ZERODIVIDE, st)
r, st, sal, orac = correr("main() { int a, b; cin(a); cin(b); cout a % b; }", [5, 0])
check("módulo entre cero en ejecución", st == tm.Estado.ZERODIVIDE, st)
r = compilar_ok("main() { int i; i = 0; while (i == 0) { i = 0; }; }")
m = tm.MaquinaTM(max_pasos=100_000)
m.cargar(r.codigo_tm)
st, _ = m.ejecutar([])
check("ciclo infinito: se detiene por límite", st == tm.Estado.LIMITE, st)
r = compilar_ok("main() { int a; cout 4 / 0; }")
check("división entre cero constante: error semántico", not r.ok)

# ═══════════════════════════════════════════════════════════════
print("5. Programas de ejercicios (pruebas/programas)")
DIR_P = os.path.join(AQUI, "programas")
for archivo in sorted(os.listdir(DIR_P)):
    if not archivo.endswith(".txt"):
        continue
    base = os.path.join(DIR_P, archivo[:-4])
    src = open(base + ".txt", encoding="utf-8").read()
    ent = parse_in(open(base + ".in", encoding="utf-8").read()) if os.path.isfile(base + ".in") else []
    esp = open(base + ".esperado", encoding="utf-8").read().split() if os.path.isfile(base + ".esperado") else None
    r, st, sal, orac = correr(src, ent)
    if r is None or not r.ok:
        check(f"programa {archivo}", False, f"no compila: {[str(e) for e in (r.errores_sem if r else [])]}")
        continue
    cond = st == tm.Estado.HALT and sal == orac and (esp is None or sal == esp)
    check(f"programa {archivo} ({len(r.instrucciones)} instr.)", cond,
          f"tm={st} {sal} oraculo={orac} esperado={esp}")

# ═══════════════════════════════════════════════════════════════
print("6. No regresión del semántico")
for archivo, n in [("TestSemantica_casos_extra.txt", 13)]:
    src = open(os.path.join(RAIZ, archivo), encoding="utf-8").read()
    rs = compilador.analizar_semantico(src)
    check(f"{archivo}: {n} errores", len(rs.errores_sem) == n, len(rs.errores_sem))
limpio = os.path.join(AQUI, "datos", "TestSemantica_adaptado_limpio.txt")
if os.path.isfile(limpio):
    rs = compilador.analizar_semantico(open(limpio, encoding="utf-8").read())
    check("TestSemantica_adaptado (copia limpia): 7 errores", len(rs.errores_sem) == 7,
          len(rs.errores_sem))

# ═══════════════════════════════════════════════════════════════
print()
if fallos:
    print(f"FALLARON {len(fallos)} de {ok_total + len(fallos)} pruebas")
    sys.exit(1)
print(f"TODAS LAS PRUEBAS PASARON ({ok_total})")
