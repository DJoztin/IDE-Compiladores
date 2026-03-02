
import sys
import os
import re


# ══════════════════════════════════════════════════════
#  ANÁLISIS LÉXICO  (stub demo)
# ══════════════════════════════════════════════════════
PALABRAS_RESERVADAS = {
    "if", "else", "while", "for", "do", "return",
    "int", "float", "string", "bool", "void",
    "true", "false", "and", "or", "not", "print"
}

TOKEN_PATTERNS = [
    ("COMENTARIO",   r"//[^\n]*"),
    ("REAL",         r"\d+\.\d+"),
    ("ENTERO",       r"\d+"),
    ("CADENA",       r'"[^"]*"'),
    ("ID",           r"[a-zA-Z_]\w*"),
    ("ASIGNACION",   r"==|!=|<=|>=|:=|="),
    ("OP_ARIT",      r"[+\-*/]"),
    ("OP_COMP",      r"[<>]"),
    ("DELIMITADOR",  r"[(){};,\[\]]"),
    ("ESPACIO",      r"[ \t\r\n]+"),
    ("DESCONOCIDO",  r"."),
]

MASTER = re.compile(
    "|".join(f"(?P<{name}>{pat})" for name, pat in TOKEN_PATTERNS)
)


def analisis_lexico(codigo):
    tokens = []
    errores = []
   
    linea = 1
    for m in MASTER.finditer(codigo):
        tipo = m.lastgroup
        valor = m.group()
        if tipo == "ESPACIO":
            linea += valor.count("\n")
            continue
        if tipo == "COMENTARIO":
            continue
        if tipo == "DESCONOCIDO":
            errores.append(f"[Léxico] Línea {linea}: carácter desconocido '{valor}'")
            continue
        if tipo == "ID" and valor in PALABRAS_RESERVADAS:
            tipo = "RESERVADA"
        tokens.append((tipo, valor, linea))

    salida = f"{'TOKEN':<20} {'VALOR':<20} {'LÍNEA':>6}\n"
    salida += "─" * 50 + "\n"
    for t, v, l in tokens:
        salida += f"{t:<20} {v:<20} {l:>6}\n"
    salida += f"\nTotal tokens: {len(tokens)}\n"

    return salida, "\n".join(errores)


# ══════════════════════════════════════════════════════
#  ANÁLISIS SINTÁCTICO  (stub demo)
# ══════════════════════════════════════════════════════
def analisis_sintactico(codigo):
    """
    Stub: verifica balanceo de {}, () y []
    Reemplaza con tu parser real (LL1, LR, etc.)
    """
    pares = {')': '(', '}': '{', ']': '['}
    pila = []
    errores = []
    linea = 1
    arbol = "Programa\n"
    indent = "  "
    nivel = 0

    for i, c in enumerate(codigo):
        if c == '\n':
            linea += 1
        elif c in '({[':
            pila.append((c, linea))
            nivel += 1
        elif c in ')}]':
            if not pila:
                errores.append(f"[Sintáctico] Línea {linea}: '{c}' sin apertura correspondiente")
            elif pila[-1][0] != pares[c]:
                errores.append(f"[Sintáctico] Línea {linea}: se esperaba cierre de '{pila[-1][0]}'")
                pila.pop()
            else:
                pila.pop()
                nivel -= 1

    for sym, ln in pila:
        errores.append(f"[Sintáctico] Línea {ln}: '{sym}' sin cierre correspondiente")

    # Árbol simplificado por líneas de código
    lineas_codigo = [l.strip() for l in codigo.strip().split('\n') if l.strip()]
    arbol = "Programa\n"
    for l in lineas_codigo:
        arbol += f"  └─ Sentencia: {l[:60]}\n"

    if not errores:
        arbol += "\n✔ Análisis sintáctico: sin errores\n"

    return arbol, "\n".join(errores)


# ══════════════════════════════════════════════════════
#  ANÁLISIS SEMÁNTICO  (stub demo)
# ══════════════════════════════════════════════════════
def analisis_semantico(codigo):
    """
    Stub: verifica declaración de variables antes de uso.
    Reemplaza con tu analizador semántico real.
    """
    declaradas = set()
    errores = []
    reporte = ""
    tipo_re = re.compile(r'\b(int|float|string|bool)\s+([a-zA-Z_]\w*)')
    uso_re  = re.compile(r'([a-zA-Z_]\w*)')

    lineas = codigo.split('\n')
    for i, linea in enumerate(lineas, 1):
        for m in tipo_re.finditer(linea):
            declaradas.add(m.group(2))

    reporte += f"Variables declaradas: {', '.join(sorted(declaradas)) or 'ninguna'}\n\n"

    for i, linea in enumerate(lineas, 1):
        # Saltar declaraciones y palabras reservadas
        if tipo_re.search(linea):
            continue
        for m in uso_re.finditer(linea):
            nombre = m.group(1)
            if nombre in PALABRAS_RESERVADAS or nombre in {"true","false"}:
                continue
            # Heurística: solo marcar si aparece como operando (después de =, (, o al inicio)
            # Stub muy simple — reemplazar con tabla de símbolos real

    if not errores:
        reporte += "✔ Análisis semántico: sin errores detectados en este stub.\n"
        reporte += "(Implementa validación de tipos y tabla de símbolos real aquí)\n"

    return reporte, "\n".join(errores)


# ══════════════════════════════════════════════════════
#  GENERACIÓN DE CÓDIGO INTERMEDIO  (stub demo)
# ══════════════════════════════════════════════════════
def codigo_intermedio(codigo):
    """
    Stub: genera código de tres direcciones aproximado.
    Reemplaza con tu generador real.
    """
    salida = "─── Código de Tres Direcciones (STUB) ───\n\n"
    temp_count = 1
    asig_re = re.compile(r'(\w+)\s*:?=\s*(.+)')

    for linea in codigo.strip().split('\n'):
        linea = linea.strip()
        if not linea or linea.startswith("//"):
            continue
        m = asig_re.match(linea)
        if m:
            var, expr = m.group(1), m.group(2)
            # Separar expresión en partes
            partes = re.split(r'([+\-*/])', expr.strip())
            if len(partes) == 3:
                salida += f"  t{temp_count} = {partes[0].strip()} {partes[1]} {partes[2].strip()}\n"
                salida += f"  {var} = t{temp_count}\n"
                temp_count += 1
            else:
                salida += f"  {var} = {expr.strip()}\n"
        elif linea.lower().startswith("print"):
            salida += f"  PRINT {linea[5:].strip()}\n"
        elif linea.lower().startswith("if"):
            salida += f"  IF_FALSE ({linea[2:].strip()}) GOTO L{temp_count}\n"
            temp_count += 1
        elif linea.lower().startswith("while"):
            salida += f"  L{temp_count}: IF_FALSE ({linea[5:].strip()}) GOTO L{temp_count+1}\n"
            temp_count += 2
        else:
            salida += f"  ; {linea}\n"

    salida += "\n(Reemplaza con tu generador de código intermedio real)\n"
    return salida, ""


# ══════════════════════════════════════════════════════
#  EJECUCIÓN  (stub demo)
# ══════════════════════════════════════════════════════
def ejecutar(codigo):
    """
    Stub: interpreta print statements básicos.
    Reemplaza con tu intérprete/generador de código real.
    """
    salida = "─── Resultado de Ejecución (STUB) ───\n\n"
    variables = {}

    for linea in codigo.strip().split('\n'):
        linea = linea.strip()
        if not linea or linea.startswith("//"):
            continue

        # int x = valor
        m = re.match(r'(int|float|string)\s+(\w+)\s*:?=\s*(.+)', linea)
        if m:
            tipo, nombre, valor = m.group(1), m.group(2), m.group(3).strip().rstrip(';')
            try:
                if tipo == "int":
                    variables[nombre] = int(valor)
                elif tipo == "float":
                    variables[nombre] = float(valor)
                else:
                    variables[nombre] = valor.strip('"')
            except Exception:
                variables[nombre] = valor
            continue

        # print(...)
        m = re.match(r'print\s*\((.+)\)', linea)
        if m:
            expr = m.group(1).strip().rstrip(';').strip('"\'')
            valor = variables.get(expr, expr)
            salida += f"{valor}\n"

    salida += "\n(Implementa tu intérprete o ejecutable real aquí)\n"
    return salida, ""


# ══════════════════════════════════════════════════════
#  PUNTO DE ENTRADA
# ══════════════════════════════════════════════════════
def main():
    if len(sys.argv) < 3:
        print("Uso: python compilador.py --<fase> <archivo>")
        print("Fases disponibles: --lexico | --sintactico | --semantico | --intermedio | --ejecutar")
        sys.exit(1)

    flag   = sys.argv[1]
    archivo = sys.argv[2]

    if not os.path.isfile(archivo):
        print(f"Error: no se encontró el archivo '{archivo}'", file=sys.stderr)
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
    print(salida, end="")
    if errores:
        print(errores, file=sys.stderr)
    sys.exit(1 if errores else 0)


if __name__ == "__main__":
    main()
