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
TK_OP_ARIT       = "OP_ARITMETICO"
TK_OP_REL        = "OP_RELACIONAL"
TK_OP_LOG        = "OP_LOGICO"
TK_ASIGNACION    = "ASIGNACION"
TK_SIMBOLO       = "SIMBOLO"
TK_CADENA        = "CADENA"
TK_CARACTER      = "CARACTER"
TK_ERROR         = "ERROR"
# Nota: TK_COMENTARIO eliminado — los comentarios se ignoran en tokens


# ═══════════════════════════════════════════════════════════════
#  CLASES
# ═══════════════════════════════════════════════════════════════
class Token:
    def __init__(self, tipo, valor, linea, columna):
        self.tipo    = tipo
        self.valor   = valor
        self.linea   = linea
        self.columna = columna


class ErrorLexico:
    def __init__(self, mensaje, linea, columna):
        self.mensaje = mensaje
        self.linea   = linea
        self.columna = columna

    def __str__(self):
        return (f"[ERROR LÉXICO] Línea {self.linea}, "
                f"Columna {self.columna}: {self.mensaje}")


# ═══════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════
def es_letra(c):
    return c.isalpha() or c == '_'

def es_digito(c):
    return c.isdigit()

def es_blanco(c):
    return c in (' ', '\t', '\r', '\n')


# ═══════════════════════════════════════════════════════════════
#  ANALIZADOR (DFA)
# ═══════════════════════════════════════════════════════════════
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

    def saltar_blancos():
        """Avanza mientras haya espacios/tabs/saltos. Devuelve el siguiente char."""
        while i < n and es_blanco(peek()):
            avanzar()

    while i < n:
        c = peek()

        # ── blancos / saltos — siempre ignorados ─────────
        if es_blanco(c):
            avanzar()
            continue

        tok_lin = linea
        tok_col = col
        lexema  = ""

        # ── COMILLA SIMPLE → CARACTER ────────────────────
        if c == "'":
            lexema += avanzar()
            while peek() not in ("'", '\0', '\n'):
                lexema += avanzar()
            if peek() == "'":
                lexema += avanzar()
                tokens.append(Token(TK_CARACTER, lexema, tok_lin, tok_col))
            else:
                errores.append(ErrorLexico(
                    f"Carácter no cerrado: {lexema!r}", tok_lin, tok_col))
            continue

        # ── COMILLA DOBLE → CADENA ───────────────────────
        if c == '"':
            lexema += avanzar()
            while peek() not in ('"', '\0', '\n'):
                lexema += avanzar()
            if peek() == '"':
                lexema += avanzar()
                tokens.append(Token(TK_CADENA, lexema, tok_lin, tok_col))
            else:
                errores.append(ErrorLexico(
                    f"Cadena no cerrada: {lexema!r}", tok_lin, tok_col))
            continue

        # ── DÍGITO → ENTERO o REAL ───────────────────────
        # Reglas:
        #   123       → ENTERO
        #   123.456   → REAL
        #   123.      → ERROR (punto sin dígitos)
        #   123.4.5   → ERROR (más de un punto)
        if es_digito(c):
            while es_digito(peek()):
                lexema += avanzar()

            if peek() == '.':
                # Hay un punto — ¿le sigue un dígito?
                if es_digito(peek(1)):
                    lexema += avanzar()          # consume '.'
                    while es_digito(peek()):
                        lexema += avanzar()
                    # El REAL termina aquí aunque siga otro '.'
                    # El punto sobrante lo manejará el loop principal como error
                    tokens.append(Token(TK_REAL, lexema, tok_lin, tok_col))
                else:
                    # Punto sin dígitos después → error, NO se emite token
                    punto = avanzar()            # consume '.'
                    errores.append(ErrorLexico(
                        f"Número mal formado: '{lexema}{punto}' "
                        f"(punto sin dígitos después)",
                        tok_lin, tok_col))
            else:
                tokens.append(Token(TK_ENTERO, lexema, tok_lin, tok_col))
            continue

        # ── PUNTO SOLO → ERROR (no es símbolo válido) ────
        if c == '.':
            avanzar()
            errores.append(ErrorLexico(
                f"Carácter no reconocido: '.' (el punto solo no es válido)",
                tok_lin, tok_col))
            continue

        # ── LETRA → IDENTIFICADOR o RESERVADA ───────────
        if es_letra(c):
            while es_letra(peek()) or es_digito(peek()):
                lexema += avanzar()
            if lexema in PALABRAS_RESERVADAS:
                tokens.append(Token(TK_RESERVADA, lexema, tok_lin, tok_col))
            else:
                tokens.append(Token(TK_IDENTIFICADOR, lexema, tok_lin, tok_col))
            continue

        # ── / → DIVISION, COMENTARIO LINEA, COMENTARIO MULTI ──
        # Los comentarios se consumen y DESCARTAN (no generan token)
        if c == '/':
            avanzar()
            if peek() == '/':
                # Comentario de una línea — ignorar hasta fin de línea
                avanzar()
                while peek() not in ('\n', '\0'):
                    avanzar()
                # No se agrega token
            elif peek() == '*':
                # Comentario multilínea — ignorar hasta */
                avanzar()
                cerrado = False
                while peek() != '\0':
                    ch = avanzar()
                    if ch == '*' and peek() == '/':
                        avanzar()
                        cerrado = True
                        break
                if not cerrado:
                    errores.append(ErrorLexico(
                        "Comentario multilínea sin cerrar '/*'",
                        tok_lin, tok_col))
            else:
                tokens.append(Token(TK_OP_ARIT, '/', tok_lin, tok_col))
            continue

        # ── | → OR (ignora blancos/saltos entre || ) ─────
        if c == '|':
            avanzar()
            saltar_blancos()
            if peek() == '|':
                avanzar()
                tokens.append(Token(TK_OP_LOG, '||', tok_lin, tok_col))
            else:
                errores.append(ErrorLexico(
                    "'|' solitario no reconocido", tok_lin, tok_col))
            continue

        # ── & → AND (ignora blancos/saltos entre &&) ─────
        if c == '&':
            avanzar()
            saltar_blancos()
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
            # Ignorar blancos entre los caracteres del operador (ej: = \n =)
            saltar_blancos()
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

        # ── - o -- (ignora blancos entre -- ) ────────────
        if c == '-':
            avanzar()
            saltar_blancos()
            if peek() == '-':
                avanzar()
                tokens.append(Token(TK_OP_ARIT, '--', tok_lin, tok_col))
            else:
                tokens.append(Token(TK_OP_ARIT, '-', tok_lin, tok_col))
            continue

        # ── + o ++ (ignora blancos entre ++) ─────────────
        if c == '+':
            avanzar()
            saltar_blancos()
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

        # ── Símbolos válidos (punto eliminado de aquí) ───
        if c in ('(', ')', '{', '}', '[', ']', ',', ';', ':'):
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
        f"{'─'*60}",
        f"  Total de errores léxicos: {len(errores)}",
        f"{'─'*60}",
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

    print(formatear_tokens(tokens))

    if errores:
        print(formatear_errores(errores), file=sys.stderr)


if __name__ == "__main__":
    main()