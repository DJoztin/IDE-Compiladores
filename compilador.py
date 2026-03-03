# -*- coding: utf-8 -*-

import sys
import os
import re

# Forzar UTF-8 en Windows (evita errores con cp1252)
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
elif hasattr(sys.stdout, 'buffer'):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


# ══════════════════════════════════════════════════════
#  ANALISIS LEXICO  (stub)
# ══════════════════════════════════════════════════════
PALABRAS_RESERVADAS = {
    "if", "else", "while", "for", "do", "return",
    "int", "float", "string", "bool", "void",
    "true", "false", "and", "or", "not", "print"
}

TOKEN_PATTERNS = [
    ("COMENTARIO",  r"//[^\n]*"),
    ("REAL",        r"\d+\.\d+"),
    ("ENTERO",      r"\d+"),
    ("CADENA",      r'"[^"]*"'),
    ("ID",          r"[a-zA-Z_]\w*"),
    ("ASIGNACION",  r"==|!=|<=|>=|:=|="),
    ("OP_ARIT",     r"[+\-*/]"),
    ("OP_COMP",     r"[<>]"),
    ("DELIMITADOR", r"[(){};,\[\]]"),
    ("ESPACIO",     r"[ \t\r\n]+"),
    ("DESCONOCIDO", r"."),
]

MASTER = re.compile(
    "|".join(f"(?P<{name}>{pat})" for name, pat in TOKEN_PATTERNS)
)


def analisis_lexico(codigo):
    tokens       = []
    errores      = []
    linea        = 1
    inicio_linea = 0   # offset del primer char de la linea actual

    for m in MASTER.finditer(codigo):
        tipo  = m.lastgroup
        valor = m.group()

        if tipo == "ESPACIO":
            nl = valor.count("\n")
            if nl:
                linea += nl
                inicio_linea = m.end() - (len(valor) - valor.rfind("\n") - 1)
            continue
        if tipo == "COMENTARIO":
            continue
        if tipo == "DESCONOCIDO":
            col = m.start() - inicio_linea + 1
            errores.append(
                f"[Lexico] Linea {linea}, Col {col}: caracter desconocido '{valor}'")
            continue
        if tipo == "ID" and valor in PALABRAS_RESERVADAS:
            tipo = "RESERVADA"

        tokens.append((tipo, valor, linea))

    salida  = f"{'TOKEN':<20} {'VALOR':<20} {'LINEA':>6}\n"
    salida += "-" * 50 + "\n"
    for t, v, l in tokens:
        salida += f"{t:<20} {v:<20} {l:>6}\n"
    salida += f"\nTotal tokens: {len(tokens)}\n"

    return salida, "\n".join(errores)


# ══════════════════════════════════════════════════════
#  ANALISIS SINTACTICO  (stub)
# ══════════════════════════════════════════════════════
def analisis_sintactico(codigo):
    pares  = {')': '(', '}': '{', ']': '['}
    pila   = []
    errores = []
    linea  = 1

    for c in codigo:
        if c == '\n':
            linea += 1
        elif c in '({[':
            pila.append((c, linea))
        elif c in ')}]':
            if not pila:
                errores.append(f"[Sintactico] Linea {linea}: '{c}' sin apertura")
            elif pila[-1][0] != pares[c]:
                errores.append(
                    f"[Sintactico] Linea {linea}: se esperaba cierre de '{pila[-1][0]}'")
                pila.pop()
            else:
                pila.pop()

    for sym, ln in pila:
        errores.append(f"[Sintactico] Linea {ln}: '{sym}' sin cierre")

    lineas_codigo = [l.strip() for l in codigo.strip().split('\n') if l.strip()]
    arbol = "Programa\n"
    for l in lineas_codigo:
        arbol += f"  +-- Sentencia: {l[:60]}\n"
    if not errores:
        arbol += "\n[OK] Sin errores sintacticos\n"

    return arbol, "\n".join(errores)


# ══════════════════════════════════════════════════════
#  ANALISIS SEMANTICO  (stub)
# ══════════════════════════════════════════════════════
def analisis_semantico(codigo):
    tipo_re   = re.compile(r'\b(int|float|string|bool)\s+([a-zA-Z_]\w*)')
    declaradas = set()
    errores    = []

    for linea in codigo.split('\n'):
        for m in tipo_re.finditer(linea):
            declaradas.add(m.group(2))

    reporte  = f"Variables declaradas: {', '.join(sorted(declaradas)) or 'ninguna'}\n\n"
    reporte += "[OK] Analisis semantico (stub): sin errores\n"
    reporte += "(Reemplaza con tu implementacion real)\n"

    return reporte, "\n".join(errores)


# ══════════════════════════════════════════════════════
#  GENERACION DE CODIGO INTERMEDIO  (stub)
# ══════════════════════════════════════════════════════
def codigo_intermedio(codigo):
    salida = "--- Codigo de Tres Direcciones (stub) ---\n\n"
    temp   = 1
    asig   = re.compile(r'(\w+)\s*:?=\s*(.+)')

    for linea in codigo.strip().split('\n'):
        linea = linea.strip()
        if not linea or linea.startswith("//"):
            continue
        m = asig.match(linea)
        if m:
            var, expr = m.group(1), m.group(2).strip().rstrip(';')
            partes = re.split(r'([+\-*/])', expr)
            if len(partes) == 3:
                salida += f"  t{temp} = {partes[0].strip()} {partes[1]} {partes[2].strip()}\n"
                salida += f"  {var} = t{temp}\n"
                temp += 1
            else:
                salida += f"  {var} = {expr}\n"
        elif linea.lower().startswith("if"):
            salida += f"  IF_FALSE ({linea[2:].strip()}) GOTO L{temp}\n"
            temp += 1
        elif linea.lower().startswith("while"):
            salida += f"  L{temp}: IF_FALSE ({linea[5:].strip()}) GOTO L{temp+1}\n"
            temp += 2
        else:
            salida += f"  ; {linea}\n"

    salida += "\n(Reemplaza con tu generador real)\n"
    return salida, ""


# ══════════════════════════════════════════════════════
#  EJECUCION  (stub)
# ══════════════════════════════════════════════════════
def ejecutar(codigo):
    salida    = "--- Resultado de Ejecucion (stub) ---\n\n"
    variables = {}

    for linea in codigo.strip().split('\n'):
        linea = linea.strip()
        if not linea or linea.startswith("//"):
            continue
        m = re.match(r'(int|float|string)\s+(\w+)\s*:?=\s*(.+)', linea)
        if m:
            tipo, nombre, valor = m.group(1), m.group(2), m.group(3).strip().rstrip(';')
            try:
                variables[nombre] = int(valor) if tipo == "int" else (
                    float(valor) if tipo == "float" else valor.strip('"'))
            except Exception:
                variables[nombre] = valor
            continue
        m = re.match(r'print\s*\((.+)\)', linea)
        if m:
            expr  = m.group(1).strip().rstrip(';').strip('"\'')
            salida += f"{variables.get(expr, expr)}\n"

    salida += "\n(Reemplaza con tu interprete real)\n"
    return salida, ""


# ══════════════════════════════════════════════════════
#  PUNTO DE ENTRADA
# ══════════════════════════════════════════════════════
def main():
    if len(sys.argv) < 3:
        print("Uso: python compilador.py --<fase> <archivo>")
        print("Fases: --lexico | --sintactico | --semantico | --intermedio | --ejecutar")
        sys.exit(1)

    flag    = sys.argv[1]
    archivo = sys.argv[2]

    if not os.path.isfile(archivo):
        print(f"Error: archivo no encontrado '{archivo}'", file=sys.stderr)
        sys.exit(1)

    with open(archivo, "r", encoding="utf-8") as f:
        codigo = f.read()

    fases = {
        "--lexico":      analisis_lexico,
        "--sintactico":  analisis_sintactico,
        "--semantico":   analisis_semantico,
        "--intermedio":  codigo_intermedio,
        "--ejecutar":    ejecutar,
    }

    if flag not in fases:
        print(f"Fase desconocida: {flag}", file=sys.stderr)
        sys.exit(1)

    salida, errores = fases[flag](codigo)
    print(salida, end="", flush=True)
    if errores:
        print(errores, file=sys.stderr)
    sys.exit(1 if errores else 0)


if __name__ == "__main__":
    main()
