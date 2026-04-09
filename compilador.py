#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analizador Léxico — CompiladorIDE UAA
Autómata de estado finito determinista (DFA)

Uso:  python compilador.py --lexico <archivo>
"""

import sys
import os

# ═══════════════════════════════════════════════════════════════
#  TOKENS
# ═══════════════════════════════════════════════════════════════
PALABRAS_RESERVADAS = {
    "if", "else", "end", "do", "while",
    "switch", "case", "int", "float",
    "main", "cin", "cout"
}

TK_ENTERO        = "ENTERO"
TK_REAL          = "REAL"
TK_IDENTIFICADOR = "IDENTIFICADOR"
TK_RESERVADA     = "RESERVADA"
TK_COMENTARIO    = "COMENTARIO"
TK_OP_ARIT       = "OP_ARITMETICO"
TK_OP_REL        = "OP_RELACIONAL"
TK_OP_LOG        = "OP_LOGICO"
TK_ASIGNACION    = "ASIGNACION"
TK_SIMBOLO       = "SIMBOLO"
TK_CADENA        = "CADENA"
TK_CARACTER      = "CARACTER"
TK_ERROR         = "ERROR"


# ═══════════════════════════════════════════════════════════════
#  CLASE TOKEN
# ═══════════════════════════════════════════════════════════════
class Token:
    def __init__(self, tipo, valor, linea, columna):
        self.tipo    = tipo
        self.valor   = valor
        self.linea   = linea
        self.columna = columna

    def __str__(self):
        return (f"{self.tipo:<22} "
                f"{repr(self.valor):<30} "
                f"Línea:{self.linea:<5} Col:{self.columna}")


class ErrorLexico:
    def __init__(self, mensaje, linea, columna):
        self.mensaje = mensaje
        self.linea   = linea
        self.columna = columna

    def __str__(self):
        return (f"[ERROR LÉXICO] Línea {self.linea}, "
                f"Columna {self.columna}: {self.mensaje}")


# ═══════════════════════════════════════════════════════════════
#  ANALIZADOR (DFA)
# ═══════════════════════════════════════════════════════════════
def es_letra(c):
    return c.isalpha() or c == '_'

def es_digito(c):
    return c.isdigit()


def analizar(codigo: str):
    tokens  = []
    errores = []

    texto = codigo
    n     = len(texto)
    i     = 0
    linea = 1
    col   = 1

    def peek(offset=0):
        pos = i + offset
        return texto[pos] if pos < n else '\0'

    def avanzar():
        nonlocal i, linea, col
        c = texto[i]
        i += 1
        if c == '\n':
            linea += 1
            col = 1
        else:
            col += 1
        return c

    while i < n:
        c = peek()

        # ── blancos / saltos ──────────────────────────────
        if c in (' ', '\t', '\r', '\n'):
            avanzar()
            continue

        tok_lin = linea
        tok_col = col
        lexema  = ""

        # ── COMILLA SIMPLE → CARACTER ────────────────────
        if c == "'":
            lexema += avanzar()                    # consume '
            while peek() not in ("'", '\0', '\n'):
                lexema += avanzar()
            if peek() == "'":
                lexema += avanzar()                # consume ' cierre
                tokens.append(Token(TK_CARACTER, lexema, tok_lin, tok_col))
            else:
                errores.append(ErrorLexico(
                    f"Carácter no cerrado: {lexema!r}", tok_lin, tok_col))
            continue

        # ── COMILLA DOBLE → CADENA ───────────────────────
        if c == '"':
            lexema += avanzar()                    # consume "
            while peek() not in ('"', '\0', '\n'):
                lexema += avanzar()
            if peek() == '"':
                lexema += avanzar()                # consume " cierre
                tokens.append(Token(TK_CADENA, lexema, tok_lin, tok_col))
            else:
                errores.append(ErrorLexico(
                    f"Cadena no cerrada: {lexema!r}", tok_lin, tok_col))
            continue

        # ── DÍGITO → ENTERO o REAL ───────────────────────
        if es_digito(c):
            while peek() and es_digito(peek()):
                lexema += avanzar()
            if peek() == '.' and es_digito(peek(1)):
                lexema += avanzar()               # consume '.'
                while peek() and es_digito(peek()):
                    lexema += avanzar()
                tokens.append(Token(TK_REAL, lexema, tok_lin, tok_col))
            else:
                tokens.append(Token(TK_ENTERO, lexema, tok_lin, tok_col))
            continue

        # ── LETRA → IDENTIFICADOR o RESERVADA ───────────
        if es_letra(c):
            while peek() and (es_letra(peek()) or es_digito(peek())):
                lexema += avanzar()
            if lexema in PALABRAS_RESERVADAS:
                tokens.append(Token(TK_RESERVADA, lexema, tok_lin, tok_col))
            else:
                tokens.append(Token(TK_IDENTIFICADOR, lexema, tok_lin, tok_col))
            continue

        # ── / → DIVISION, COMENTARIO LINEA, COMENTARIO MULTI ──
        if c == '/':
            avanzar(); lexema = '/'
            if peek() == '/':
                # Comentario de una línea
                lexema += avanzar()
                while peek() not in ('\n', '\0'):
                    lexema += avanzar()
                tokens.append(Token(TK_COMENTARIO, lexema, tok_lin, tok_col))
            elif peek() == '*':
                # Comentario multilínea
                lexema += avanzar()
                cerrado = False
                while peek() != '\0':
                    ch = avanzar()
                    lexema += ch
                    if ch == '*' and peek() == '/':
                        lexema += avanzar()
                        cerrado = True
                        break
                if cerrado:
                    tokens.append(Token(TK_COMENTARIO, lexema, tok_lin, tok_col))
                else:
                    errores.append(ErrorLexico(
                        "Comentario multilínea sin cerrar", tok_lin, tok_col))
            else:
                tokens.append(Token(TK_OP_ARIT, '/', tok_lin, tok_col))
            continue

        # ── | → OR ──────────────────────────────────────
        if c == '|':
            avanzar()
            if peek() == '|':
                avanzar()
                tokens.append(Token(TK_OP_LOG, '||', tok_lin, tok_col))
            else:
                errores.append(ErrorLexico(
                    "'|' solitario no reconocido", tok_lin, tok_col))
            continue

        # ── & → AND ─────────────────────────────────────
        if c == '&':
            avanzar()
            if peek() == '&':
                avanzar()
                tokens.append(Token(TK_OP_LOG, '&&', tok_lin, tok_col))
            else:
                errores.append(ErrorLexico(
                    "'&' solitario no reconocido", tok_lin, tok_col))
            continue

        # ── Relacionales / Asignación / Not ─────────────
        if c in ('<', '>', '!', '='):
            avanzar(); lexema = c
            if peek() == '=':
                lexema += avanzar()
                tokens.append(Token(TK_OP_REL, lexema, tok_lin, tok_col))
            elif c == '=':
                tokens.append(Token(TK_ASIGNACION, '=', tok_lin, tok_col))
            elif c == '!':
                tokens.append(Token(TK_OP_LOG, '!', tok_lin, tok_col))
            else:
                tokens.append(Token(TK_OP_REL, c, tok_lin, tok_col))
            continue

        # ── - o -- ──────────────────────────────────────
        if c == '-':
            avanzar()
            if peek() == '-':
                avanzar()
                tokens.append(Token(TK_OP_ARIT, '--', tok_lin, tok_col))
            else:
                tokens.append(Token(TK_OP_ARIT, '-', tok_lin, tok_col))
            continue

        # ── + o ++ ──────────────────────────────────────
        if c == '+':
            avanzar()
            if peek() == '+':
                avanzar()
                tokens.append(Token(TK_OP_ARIT, '++', tok_lin, tok_col))
            else:
                tokens.append(Token(TK_OP_ARIT, '+', tok_lin, tok_col))
            continue

        # ── Operadores aritméticos simples ───────────────
        if c in ('*', '%', '^'):
            avanzar()
            tokens.append(Token(TK_OP_ARIT, c, tok_lin, tok_col))
            continue

        # ── Símbolos ─────────────────────────────────────
        if c in ('(', ')', '{', '}', '[', ']', ',', ';', '.', ':'):
            avanzar()
            tokens.append(Token(TK_SIMBOLO, c, tok_lin, tok_col))
            continue

        # ── ERROR: carácter no reconocido ────────────────
        avanzar()
        errores.append(ErrorLexico(
            f"Carácter no reconocido: '{c}' (ASCII {ord(c)})",
            tok_lin, tok_col))

    return tokens, errores


# ═══════════════════════════════════════════════════════════════
#  SALIDA FORMATEADA
# ═══════════════════════════════════════════════════════════════
def formatear_tokens(tokens):
    if not tokens:
        return "(sin tokens reconocidos)"

    sep  = "─" * 68
    sep2 = "═" * 68
    lineas = [
        sep2,
        f"  {'TIPO':<22} {'VALOR':<30} {'LÍN':>4}  {'COL':>4}",
        sep2,
    ]

    grupo_anterior = None
    for tk in tokens:
        if grupo_anterior is not None and grupo_anterior != tk.tipo:
            lineas.append(sep)
        lineas.append(
            f"  {tk.tipo:<22} {repr(tk.valor):<30} {tk.linea:>4}  {tk.columna:>4}")
        grupo_anterior = tk.tipo

    lineas.append(sep2)
    lineas.append(f"  Total de tokens: {len(tokens)}")
    return "\n".join(lineas)


def formatear_errores(errores):
    if not errores:
        return ""
    lineas = [
        f"{'─'*50}",
        f"  Total de errores léxicos: {len(errores)}",
        f"{'─'*50}",
    ]
    for e in errores:
        lineas.append(str(e))
    return "\n".join(lineas)


# ═══════════════════════════════════════════════════════════════
#  PUNTO DE ENTRADA
# ═══════════════════════════════════════════════════════════════
def main():
    args = sys.argv[1:]

    if "--lexico" not in args:
        print("Uso: python compilador.py --lexico <archivo>", file=sys.stderr)
        sys.exit(1)

    idx = args.index("--lexico")
    if idx + 1 >= len(args):
        print("[compilador.py] Error: falta ruta del archivo.", file=sys.stderr)
        sys.exit(1)

    ruta = args[idx + 1]

    if not os.path.isfile(ruta):
        print(f"[compilador.py] Error: no existe el archivo: {ruta}",
              file=sys.stderr)
        sys.exit(1)

    try:
        with open(ruta, "r", encoding="utf-8") as f:
            codigo = f.read()
    except Exception as ex:
        print(f"[compilador.py] Error al leer: {ex}", file=sys.stderr)
        sys.exit(1)

    tokens, errores = analizar(codigo)

    # stdout → panel "Lexico" del IDE
    print(formatear_tokens(tokens))

    # stderr → panel "Errores Lexicos" del IDE
    if errores:
        print(formatear_errores(errores), file=sys.stderr)


if __name__ == "__main__":
    main()
