#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Compilador — CompiladorIDE UAA
Fases: léxico (DFA), sintáctico (descenso recursivo) y semántico.

Uso:  python compilador.py --lexico|--sintactico|--semantico <archivo>
"""

import sys
import os

# ═══════════════════════════════════════════════════════════════
#  TOKENS
# ═══════════════════════════════════════════════════════════════
PALABRAS_RESERVADAS = {
    "if", "else", "end", "do", "while",
    "switch", "case", "int", "float", "real",
    "main", "cin", "cout", "then", "until",
    "bool", "true", "false"
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


def formatear_errores_sint(errores):
    if not errores:
        return ""
    lineas = [
        f"{'─'*60}",
        f"  Total de errores sintácticos: {len(errores)}",
        f"{'─'*60}",
    ]
    for e in errores:
        lineas.append(str(e))
    return "\n".join(lineas)


# ═══════════════════════════════════════════════════════════════
#  NODO DEL ÁRBOL SINTÁCTICO
# ═══════════════════════════════════════════════════════════════
class NodoSint:
    """Nodo del árbol de derivación (parse tree)."""
    def __init__(self, tipo: str, valor: str = "", linea: int = 0,
                 columna: int = 0):
        self.tipo    = tipo
        self.valor   = valor
        self.linea   = linea
        self.columna = columna
        self.hijos: list = []

    def agregar(self, hijo):
        if hijo is not None:
            self.hijos.append(hijo)
        return self


class ErrorSintactico:
    def __init__(self, mensaje: str, linea: int, columna: int):
        self.mensaje = mensaje
        self.linea   = linea
        self.columna = columna

    def __str__(self):
        return (f"[ERROR SINTÁCTICO] Línea {self.linea}, "
                f"Columna {self.columna}: {self.mensaje}")


# ═══════════════════════════════════════════════════════════════
#  PARSER  —  DESCENSO RECURSIVO
# ═══════════════════════════════════════════════════════════════
class AnalizadorSintactico:
    """
    Gramática:
      programa       → 'main' '(' ')' '{' lista_sent '}'
      lista_sent     → sentencia*
      sentencia      → declaracion | asig_incr | if_stmt
                     | do_until | while_stmt | cin_stmt | cout_stmt
      declaracion    → ('int'|'real'|'float'|'bool') lista_ids ';'
      lista_ids      → ID (',' ID)*
      asig_incr      → ID ('=' expresion | '++' | '--') ';'
      if_stmt        → 'if' '(' condicion ')' 'then' lista_sent
                       ('else' lista_sent)? 'end' ';'
      do_until       → 'do' '{' lista_sent '}' 'until' '(' condicion ')' ';'
      while_stmt     → 'while' '(' condicion ')' '{' lista_sent '}' ';'
      cin_stmt       → 'cin' '(' ID ')' ';'
      cout_stmt      → 'cout' expresion ';'
      condicion      → expr_rel (('&&'|'||') expr_rel)*
      expr_rel       → expresion (OP_REL expresion)?
      expresion      → termino (('+' | '-') termino)*
      termino        → factor (('*' | '/') factor)*
      factor         → '(' expresion ')' | ENTERO | REAL | 'true' | 'false'
                     | ID | '-' factor
    """

    def __init__(self, tokens: list):
        self.tokens  = tokens
        self.pos     = 0
        self.errores: list[ErrorSintactico] = []

    # ── helpers ────────────────────────────────────────────────
    def _tok(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def _espera(self, tipo=None, valor=None) -> bool:
        t = self._tok()
        if t is None:
            return False
        if tipo  and t.tipo  != tipo:  return False
        if valor and t.valor != valor: return False
        return True

    def _consumir(self, tipo=None, valor=None):
        t = self._tok()
        if t is None:
            self.errores.append(ErrorSintactico("Final inesperado del archivo", 0, 0))
            return None
        if tipo and t.tipo != tipo:
            self.errores.append(ErrorSintactico(
                f"Se esperaba tipo {tipo!r}, se encontró {t.tipo!r} ('{t.valor}')",
                t.linea, t.columna))
            return None
        if valor and t.valor != valor:
            self.errores.append(ErrorSintactico(
                f"Se esperaba '{valor}', se encontró '{t.valor}'",
                t.linea, t.columna))
            return None
        self.pos += 1
        return t

    def _inicio_sent(self) -> bool:
        t = self._tok()
        if t is None:
            return False
        if t.tipo == TK_RESERVADA and t.valor in (
                'int', 'real', 'float', 'bool', 'if', 'do', 'while', 'cin', 'cout'):
            return True
        return t.tipo == TK_IDENTIFICADOR

    # ── gramática ───────────────────────────────────────────────
    def parsear(self) -> NodoSint:
        return self._programa()

    def _programa(self) -> NodoSint:
        n = NodoSint("programa", "main")
        t = self._consumir(TK_RESERVADA, "main")
        if t: n.linea, n.columna = t.linea, t.columna
        self._consumir(TK_SIMBOLO, "(")
        self._consumir(TK_SIMBOLO, ")")
        self._consumir(TK_SIMBOLO, "{")
        n.agregar(self._lista_sent({'else', 'end', '}'}))
        self._consumir(TK_SIMBOLO, "}")
        if self._tok() is not None:
            sobrante = self._tok()
            self.errores.append(ErrorSintactico(
                f"Código fuera de 'main': '{sobrante.valor}'",
                sobrante.linea, sobrante.columna))
        return n

    def _lista_sent(self, terminadores: set) -> NodoSint:
        n = NodoSint("lista_sentencias")
        while self._tok() is not None:
            t = self._tok()
            if t.valor in terminadores:
                break
            if not self._inicio_sent():
                self.errores.append(ErrorSintactico(
                    f"Token inesperado: '{t.valor}'", t.linea, t.columna))
                self.pos += 1
                continue
            s = self._sentencia()
            if s:
                n.agregar(s)
        return n

    def _sentencia(self) -> NodoSint | None:
        t = self._tok()
        if t is None:
            return None
        v = t.valor
        if t.tipo == TK_RESERVADA and v in ('int', 'real', 'float', 'bool'):
            return self._declaracion()
        if t.tipo == TK_RESERVADA and v == 'if':
            return self._if_stmt()
        if t.tipo == TK_RESERVADA and v == 'do':
            return self._do_until()
        if t.tipo == TK_RESERVADA and v == 'while':
            return self._while_stmt()
        if t.tipo == TK_RESERVADA and v == 'cin':
            return self._cin_stmt()
        if t.tipo == TK_RESERVADA and v == 'cout':
            return self._cout_stmt()
        if t.tipo == TK_IDENTIFICADOR:
            return self._asig_incr()
        self.errores.append(ErrorSintactico(
            f"Sentencia desconocida: '{t.valor}'", t.linea, t.columna))
        self.pos += 1
        return None

    def _declaracion(self) -> NodoSint:
        n = NodoSint("declaracion")
        t = self._consumir(TK_RESERVADA)
        if t:
            n.valor = t.valor   # "int" / "real" / "float" / "bool"
            n.linea = t.linea
            n.columna = t.columna
        n.agregar(self._lista_ids())
        self._consumir(TK_SIMBOLO, ";")
        return n

    def _lista_ids(self) -> NodoSint:
        n = NodoSint("lista_ids")
        t = self._consumir(TK_IDENTIFICADOR)
        if t:
            n.linea = t.linea
            n.columna = t.columna
            n.agregar(NodoSint("identificador", t.valor, t.linea, t.columna))
        while self._espera(TK_SIMBOLO, ","):
            self._consumir(TK_SIMBOLO, ",")
            t = self._consumir(TK_IDENTIFICADOR)
            if t: n.agregar(NodoSint("identificador", t.valor, t.linea, t.columna))
        return n

    def _asig_incr(self) -> NodoSint | None:
        id_tok = self._consumir(TK_IDENTIFICADOR)
        if id_tok is None:
            return None
        t2 = self._tok()
        if t2 and t2.tipo == TK_ASIGNACION:
            n = NodoSint("asignacion", f"{id_tok.valor} =", id_tok.linea,
                         id_tok.columna)
            n.id_nombre = id_tok.valor
            self._consumir(TK_ASIGNACION, "=")
            n.agregar(self._expresion())
            self._consumir(TK_SIMBOLO, ";")
            return n
        if t2 and t2.tipo == TK_OP_ARIT and t2.valor == '++':
            n = NodoSint("incremento", f"{id_tok.valor}++", id_tok.linea,
                         id_tok.columna)
            n.id_nombre = id_tok.valor
            self._consumir(TK_OP_ARIT, "++")
            self._consumir(TK_SIMBOLO, ";")
            return n
        if t2 and t2.tipo == TK_OP_ARIT and t2.valor == '--':
            n = NodoSint("decremento", f"{id_tok.valor}--", id_tok.linea,
                         id_tok.columna)
            n.id_nombre = id_tok.valor
            self._consumir(TK_OP_ARIT, "--")
            self._consumir(TK_SIMBOLO, ";")
            return n
        pos_tok = self._tok()
        lin = pos_tok.linea if pos_tok else id_tok.linea
        col = pos_tok.columna if pos_tok else id_tok.columna
        self.errores.append(ErrorSintactico(
            f"Se esperaba '=', '++' o '--' tras '{id_tok.valor}'", lin, col))
        return None

    def _if_stmt(self) -> NodoSint:
        n = NodoSint("if_stmt", "if")
        t = self._consumir(TK_RESERVADA, "if")
        if t: n.linea, n.columna = t.linea, t.columna
        self._consumir(TK_SIMBOLO, "(")
        n.agregar(self._condicion())
        self._consumir(TK_SIMBOLO, ")")
        self._consumir(TK_RESERVADA, "then")

        then_n = NodoSint("then_branch", "then", n.linea)
        then_n.agregar(self._lista_sent({'else', 'end'}))
        n.agregar(then_n)

        if self._espera(TK_RESERVADA, "else"):
            et = self._consumir(TK_RESERVADA, "else")
            else_n = NodoSint("else_branch", "else", et.linea if et else 0)
            else_n.agregar(self._lista_sent({'end'}))
            n.agregar(else_n)

        self._consumir(TK_RESERVADA, "end")
        self._consumir(TK_SIMBOLO, ";")
        return n

    def _do_until(self) -> NodoSint:
        n = NodoSint("do_until_stmt", "do-until")
        t = self._consumir(TK_RESERVADA, "do")
        if t: n.linea, n.columna = t.linea, t.columna
        self._consumir(TK_SIMBOLO, "{")
        n.agregar(self._lista_sent({'}'}))
        self._consumir(TK_SIMBOLO, "}")
        self._consumir(TK_RESERVADA, "until")
        self._consumir(TK_SIMBOLO, "(")
        n.agregar(self._condicion())
        self._consumir(TK_SIMBOLO, ")")
        self._consumir(TK_SIMBOLO, ";")
        return n

    def _while_stmt(self) -> NodoSint:
        n = NodoSint("while_stmt", "while")
        t = self._consumir(TK_RESERVADA, "while")
        if t: n.linea, n.columna = t.linea, t.columna
        self._consumir(TK_SIMBOLO, "(")
        n.agregar(self._condicion())
        self._consumir(TK_SIMBOLO, ")")
        self._consumir(TK_SIMBOLO, "{")
        n.agregar(self._lista_sent({'}'}))
        self._consumir(TK_SIMBOLO, "}")
        self._consumir(TK_SIMBOLO, ";")
        return n

    def _cin_stmt(self) -> NodoSint:
        n = NodoSint("cin_stmt", "cin")
        t = self._consumir(TK_RESERVADA, "cin")
        if t: n.linea, n.columna = t.linea, t.columna
        self._consumir(TK_SIMBOLO, "(")
        t = self._consumir(TK_IDENTIFICADOR)
        if t:
            n.valor = f"cin({t.valor})"
            n.id_nombre = t.valor
            n.id_columna = t.columna
        self._consumir(TK_SIMBOLO, ")")
        self._consumir(TK_SIMBOLO, ";")
        return n

    def _cout_stmt(self) -> NodoSint:
        n = NodoSint("cout_stmt", "cout")
        t = self._consumir(TK_RESERVADA, "cout")
        if t: n.linea, n.columna = t.linea, t.columna
        n.agregar(self._expresion())
        self._consumir(TK_SIMBOLO, ";")
        return n

    def _condicion(self) -> NodoSint:
        # El operador lógico es la raíz; operandos son hijos izq/der
        left = self._expr_rel()
        while self._espera(TK_OP_LOG) and self._tok().valor in ('&&', '||'):
            t = self._consumir(TK_OP_LOG)
            right = self._expr_rel()
            node = NodoSint("condicion", t.valor, t.linea, t.columna)
            node.agregar(left)
            node.agregar(right)
            left = node
        return left

    def _expr_rel(self) -> NodoSint:
        # El operador relacional es la raíz; operandos son hijos izq/der
        left = self._expresion()
        if self._espera(TK_OP_REL):
            t = self._consumir(TK_OP_REL)
            right = self._expresion()
            node = NodoSint("expr_rel", t.valor, t.linea, t.columna)
            node.agregar(left)
            node.agregar(right)
            return node
        return left

    def _expresion(self) -> NodoSint:
        # El operador + / - es la raíz; operandos son hijos izq/der
        left = self._termino()
        while self._espera(TK_OP_ARIT) and self._tok().valor in ('+', '-'):
            t = self._consumir(TK_OP_ARIT)
            right = self._termino()
            node = NodoSint("expresion", t.valor, t.linea, t.columna)
            node.agregar(left)
            node.agregar(right)
            left = node
        return left

    def _termino(self) -> NodoSint:
        # El operador * / / es la raíz; operandos son hijos izq/der
        left = self._factor()
        while self._espera(TK_OP_ARIT) and self._tok().valor in ('*', '/'):
            t = self._consumir(TK_OP_ARIT)
            right = self._factor()
            node = NodoSint("termino", t.valor, t.linea, t.columna)
            node.agregar(left)
            node.agregar(right)
            left = node
        return left

    def _factor(self) -> NodoSint:
        t = self._tok()
        if t is None:
            self.errores.append(ErrorSintactico("Factor esperado, fin de archivo", 0, 0))
            return NodoSint("error", "EOF")
        if t.tipo == TK_SIMBOLO and t.valor == '(':
            # Paréntesis: wrapping sin nodos ( ) extra
            n = NodoSint("factor_par", "(expr)", t.linea, t.columna)
            self._consumir(TK_SIMBOLO, "(")
            n.agregar(self._expresion())
            self._consumir(TK_SIMBOLO, ")")
            return n
        if t.tipo == TK_ENTERO:
            self.pos += 1
            return NodoSint("entero", t.valor, t.linea, t.columna)
        if t.tipo == TK_REAL:
            self.pos += 1
            return NodoSint("real_lit", t.valor, t.linea, t.columna)
        if t.tipo == TK_RESERVADA and t.valor in ('true', 'false'):
            self.pos += 1
            return NodoSint("booleano", t.valor, t.linea, t.columna)
        if t.tipo == TK_IDENTIFICADOR:
            self.pos += 1
            return NodoSint("identificador", t.valor, t.linea, t.columna)
        if t.tipo == TK_OP_ARIT and t.valor == '-':
            n = NodoSint("negativo", "-", t.linea, t.columna)
            self._consumir(TK_OP_ARIT, "-")
            n.agregar(self._factor())
            return n
        self.errores.append(ErrorSintactico(
            f"Factor inválido: '{t.valor}' ({t.tipo})", t.linea, t.columna))
        self.pos += 1
        return NodoSint("error", t.valor, t.linea)


# ═══════════════════════════════════════════════════════════════
#  INTERFAZ PÚBLICA DEL ANÁLISIS SINTÁCTICO
# ═══════════════════════════════════════════════════════════════
def analizar_sintactico(codigo: str):
    """Lexical → Syntactic analysis.
    Returns (arbol: NodoSint, errores_lex: list, errores_sint: list).
    Los errores léxicos no bloquean el parseo; se usan los tokens válidos.
    """
    tokens, errores_lex = analizar(codigo)
    validos = [t for t in tokens if t.tipo != TK_ERROR]
    parser  = AnalizadorSintactico(validos)
    arbol   = parser.parsear()
    return arbol, errores_lex, parser.errores


# ═══════════════════════════════════════════════════════════════
#  ANÁLISIS SEMÁNTICO
# ═══════════════════════════════════════════════════════════════
#  Flujo:  AST → copia → recorrido → reglas semánticas → atributos
#          → árbol anotado → tabla de símbolos → verificación de tipos
#          → errores semánticos
#
#  Atributos usados (se guardan en  nodo.atrib  de la COPIA del AST):
#    dtype  (HEREDADO)    declaracion → lista_ids → identificador
#    loc    (tabla)       dirección asignada al insertar (contador tipo TINY)
#    tipo   (SINTETIZADO) hojas → operadores → raíz de la expresión
#    valor  (SINTETIZADO) sólo cuando puede determinarse en compilación
#    conv                 coerción aplicada (int→float) en el operando
#    chk                  resultado de la verificación (✓ / ✗)
# ═══════════════════════════════════════════════════════════════
import copy

T_INT, T_FLOAT, T_BOOL, T_ERROR = "int", "float", "bool", "error"
# 'real' y 'float' son el mismo tipo: se puede declarar con cualquiera
TIPO_BASE = {"int": T_INT, "float": T_FLOAT, "real": T_FLOAT, "bool": T_BOOL}
NUMERICOS = (T_INT, T_FLOAT)

# Categorías de error (PDF, sección 8)
ERR_NO_DECLARADA   = "Identificador no declarado"
ERR_DUPLICADA      = "Declaración duplicada"
ERR_INCOMPATIBLES  = "Incompatibilidad de tipos"
ERR_CONVERSION     = "Conversión de tipos no válida"
ERR_OPERADOR       = "Uso indebido de operador"
ERR_ASIGNACION     = "Inconsistencia de tipos en asignación"
ERR_CONDICION      = "Condición no booleana"
ERR_DIV_CERO       = "División entre cero"
ERR_SIN_VALOR      = "Variable sin valor asignado"


class _Desconocido:
    """Valor que no puede determinarse durante la compilación."""
    def __repr__(self):
        return "?"


DESCONOCIDO = _Desconocido()


def fmt_valor(v):
    if v is DESCONOCIDO or v is None:
        return "?"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, float):
        return repr(round(v, 2))       # se muestra con 2 decimales
    return str(v)


def valor_simbolo(sim) -> str:
    """Valor para la tabla: distingue 'sin asignar' de 'desconocido'."""
    if not sim.inicializada:
        return "sin asignar"
    return fmt_valor(sim.valor)


class ErrorSemantico:
    def __init__(self, mensaje: str, linea: int, columna: int = 0,
                 categoria: str = ""):
        self.mensaje   = mensaje
        self.linea     = linea
        self.columna   = columna
        self.categoria = categoria

    def __str__(self):
        pos = f"Línea {self.linea}"
        if self.columna:
            pos += f", Columna {self.columna}"
        cat = f"[{self.categoria}] " if self.categoria else ""
        return f"[ERROR SEMÁNTICO] {pos}: {cat}{self.mensaje}"


# ───────────────────────────────────────────────────────────────
#  TABLA DE SÍMBOLOS  (diccionario: inserción, búsqueda, eliminación)
# ───────────────────────────────────────────────────────────────
class Simbolo:
    def __init__(self, nombre, tipo_decl, loc, linea, columna):
        self.nombre     = nombre
        self.tipo_decl  = tipo_decl               # como se escribió: int/real/float/bool
        self.tipo       = TIPO_BASE[tipo_decl]    # tipo para las reglas
        self.loc        = loc                     # dirección de memoria (TINY)
        self.linea_decl = linea
        self.columna    = columna
        self.lineas     = [linea]                 # todas las líneas donde aparece
        self.valor      = DESCONOCIDO             # último valor conocido
        self.inicializada = False                 # ¿ya recibió un valor?


class TablaSimbolos:
    """Ámbito único: el lenguaje sólo tiene el bloque de main, por lo que
    todas las variables son globales a ese bloque."""

    def __init__(self):
        self._tabla: dict[str, Simbolo] = {}
        self._loc = 0                             # contador de direcciones

    def insertar(self, nombre, tipo_decl, linea, columna=0) -> Simbolo:
        sim = Simbolo(nombre, tipo_decl, self._loc, linea, columna)
        self._loc += 1
        self._tabla[nombre] = sim
        return sim

    def buscar(self, nombre) -> Simbolo | None:
        return self._tabla.get(nombre)

    def existe(self, nombre) -> bool:
        return nombre in self._tabla

    def eliminar(self, nombre):
        return self._tabla.pop(nombre, None)

    def registrar_linea(self, nombre, linea):
        sim = self._tabla.get(nombre)
        if sim and linea and linea not in sim.lineas:
            sim.lineas.append(linea)

    def simbolos(self) -> list:
        return sorted(self._tabla.values(), key=lambda s: s.loc)

    # Estado de valores (para if / ciclos)
    def foto_valores(self) -> dict:
        return {n: s.valor for n, s in self._tabla.items()}

    def restaurar_valores(self, foto: dict):
        for n, v in foto.items():
            if n in self._tabla:
                self._tabla[n].valor = v

    # Estado de inicialización (para if / ciclos)
    def foto_inicializadas(self) -> set:
        return {n for n, s in self._tabla.items() if s.inicializada}

    def restaurar_inicializadas(self, nombres: set):
        for n, s in self._tabla.items():
            s.inicializada = n in nombres

    def __len__(self):
        return len(self._tabla)


# ───────────────────────────────────────────────────────────────
#  ANALIZADOR SEMÁNTICO
# ───────────────────────────────────────────────────────────────
def _anotar(n, **kw):
    if not hasattr(n, "atrib"):
        n.atrib = {}
    n.atrib.update(kw)


def _desc(n) -> str:
    """Texto corto de un nodo para la bitácora."""
    if n.tipo in ("entero", "real_lit", "booleano", "identificador"):
        return n.valor
    if n.tipo == "factor_par":
        return "(" + (_desc(n.hijos[0]) if n.hijos else "") + ")"
    if n.tipo == "negativo":
        return "-" + (_desc(n.hijos[0]) if n.hijos else "")
    if len(n.hijos) == 2:
        return f"{_desc(n.hijos[0])} {n.valor} {_desc(n.hijos[1])}"
    return n.valor or n.tipo


class AnalizadorSemantico:

    def __init__(self):
        self.tabla    = TablaSimbolos()
        self.errores: list[ErrorSemantico] = []
        self.bitacora: list[tuple] = []          # (linea, accion, detalle)

    # ── utilidades ─────────────────────────────────────────────
    def _log(self, linea, accion, detalle):
        self.bitacora.append((linea, accion, detalle))

    def _error(self, msg, nodo, categoria, columna=None):
        col = columna if columna is not None else getattr(nodo, "columna", 0)
        e = ErrorSemantico(msg, nodo.linea, col, categoria)
        self.errores.append(e)
        self._log(nodo.linea, "ERROR", f"{categoria}: {msg}")

    def _buscar(self, nombre, nodo):
        """Uso de identificador → búsqueda en la tabla."""
        sim = self.tabla.buscar(nombre)
        if sim is None:
            self._log(nodo.linea, "BUSCAR", f"'{nombre}' → no está en la tabla ✗")
            return None
        self.tabla.registrar_linea(nombre, nodo.linea)
        self._log(nodo.linea, "BUSCAR",
                  f"'{nombre}' → {sim.tipo_decl}, loc {sim.loc}, "
                  f"valor {valor_simbolo(sim)}")
        return sim

    # ── entrada ────────────────────────────────────────────────
    def analizar(self, arbol: NodoSint) -> NodoSint:
        anotado = copy.deepcopy(arbol)      # el AST original no se modifica
        self._log(0, "INICIO", "Se crea una copia del AST y se recorre en orden")
        self._sentencia(anotado)
        self._log(0, "FIN", f"{len(self.tabla)} símbolo(s), "
                            f"{len(self.errores)} error(es) semántico(s)")
        return anotado

    # ── sentencias ─────────────────────────────────────────────
    def _sentencia(self, n):
        if n is None:
            return
        f = getattr(self, f"_s_{n.tipo}", None)
        if f:
            f(n)
        else:
            for h in n.hijos:
                self._sentencia(h)

    def _s_declaracion(self, n):
        dtype = n.valor
        _anotar(n, dtype=dtype)
        self._log(n.linea, "DECLARAR",
                  f"tipo '{dtype}' → dtype se hereda a la lista de ids")
        for lista in n.hijos:
            _anotar(lista, dtype=dtype, heredado=True)
            for ident in lista.hijos:
                _anotar(ident, dtype=dtype, heredado=True)
                nombre = ident.valor
                previo = self.tabla.buscar(nombre)
                if previo is not None:
                    _anotar(ident, chk=False)
                    self._error(
                        f"'{nombre}' ya fue declarada en la línea "
                        f"{previo.linea_decl} como {previo.tipo_decl}",
                        ident, ERR_DUPLICADA)
                    continue
                sim = self.tabla.insertar(nombre, dtype, ident.linea,
                                          ident.columna)
                _anotar(ident, loc=sim.loc, chk=True)
                self._log(ident.linea, "INSERTAR",
                          f"'{nombre}' : {dtype}  (loc {sim.loc})")

    def _s_asignacion(self, n):
        nombre = getattr(n, "id_nombre", n.valor.rstrip(" ="))
        sim = self._buscar(nombre, n)
        expr = n.hijos[0] if n.hijos else None
        t_exp, v_exp = self._expr(expr) if expr else (T_ERROR, DESCONOCIDO)

        if sim is None:
            _anotar(n, tipo=T_ERROR, chk=False)
            self._error(f"Variable '{nombre}' no declarada", n,
                        ERR_NO_DECLARADA)
            return

        t_var = sim.tipo
        _anotar(n, tipo=t_var, de_tabla=True)
        # La variable queda inicializada aunque la asignación tenga error,
        # para no generar errores en cascada en sus usos posteriores.
        sim.inicializada = True
        if t_exp == T_ERROR:                      # error ya reportado abajo
            _anotar(n, chk=False)
            return

        if t_var == t_exp:
            ok, valor = True, v_exp
        elif t_var == T_FLOAT and t_exp == T_INT:  # conversión permitida
            ok = True
            valor = float(v_exp) if v_exp is not DESCONOCIDO else DESCONOCIDO
            _anotar(expr, conv="int→float")
            self._log(n.linea, "CONVERTIR",
                      f"int → float para asignar a '{nombre}'")
        elif t_var == T_INT and t_exp == T_FLOAT:
            ok = False
            self._error(
                f"No se puede asignar un valor float a '{nombre}' (int): "
                f"se perdería la parte decimal", n, ERR_CONVERSION)
        else:
            ok = False
            self._error(
                f"No se puede asignar {t_exp} a '{nombre}' ({sim.tipo_decl})",
                n, ERR_ASIGNACION)

        _anotar(n, chk=ok, asig=f"{nombre}:{t_var} ← {t_exp}")
        self._log(n.linea, "VERIFICAR",
                  f"asignación {nombre}:{t_var} ← {t_exp}  "
                  f"{'✓' if ok else '✗'}")
        if ok:
            sim.valor = valor
            _anotar(n, valor=valor)
            if valor is not DESCONOCIDO:
                self._log(n.linea, "VALOR", f"{nombre} = {fmt_valor(valor)}")

    def _incr_decr(self, n, op):
        nombre = getattr(n, "id_nombre", n.valor[:-2])
        sim = self._buscar(nombre, n)
        if sim is None:
            _anotar(n, tipo=T_ERROR, chk=False)
            self._error(f"Variable '{nombre}' no declarada", n,
                        ERR_NO_DECLARADA)
            return
        _anotar(n, tipo=sim.tipo, de_tabla=True)
        if sim.tipo not in NUMERICOS:
            _anotar(n, chk=False)
            self._error(f"El operador '{op}' no se puede aplicar a "
                        f"'{nombre}' ({sim.tipo_decl})", n, ERR_OPERADOR)
            return
        if not sim.inicializada:
            _anotar(n, chk=False)
            self._error(f"No se puede aplicar '{op}' a '{nombre}': "
                        f"la variable no tiene un valor asignado",
                        n, ERR_SIN_VALOR)
            return
        if sim.valor is not DESCONOCIDO:
            sim.valor = sim.valor + (1 if op == "++" else -1)
        _anotar(n, chk=True, valor=sim.valor)
        self._log(n.linea, "VERIFICAR",
                  f"{nombre}{op} sobre {sim.tipo} ✓  "
                  f"(valor {fmt_valor(sim.valor)})")

    def _s_incremento(self, n):
        self._incr_decr(n, "++")

    def _s_decremento(self, n):
        self._incr_decr(n, "--")

    def _s_cin_stmt(self, n):
        nombre = getattr(n, "id_nombre", None)
        if not nombre:
            return
        col = getattr(n, "id_columna", n.columna)
        sim = self._buscar(nombre, n)
        if sim is None:
            _anotar(n, tipo=T_ERROR, chk=False)
            self._error(f"Variable '{nombre}' no declarada", n,
                        ERR_NO_DECLARADA, columna=col)
            return
        sim.valor = DESCONOCIDO                   # se conoce en ejecución
        sim.inicializada = True
        _anotar(n, tipo=sim.tipo, de_tabla=True, chk=True,
                valor=DESCONOCIDO)
        self._log(n.linea, "VALOR",
                  f"'{nombre}' se lee en ejecución → valor desconocido")

    def _s_cout_stmt(self, n):
        if n.hijos:
            t, v = self._expr(n.hijos[0])
            _anotar(n, tipo=t, chk=(t != T_ERROR))

    def _condicion(self, n, estructura, nodo_padre):
        t, v = self._expr(n)
        if t == T_ERROR:
            _anotar(n, chk=False)
            return
        if t != T_BOOL:
            _anotar(n, chk=False)
            self._error(f"La condición del '{estructura}' debe ser bool, "
                        f"se obtuvo {t}", n, ERR_CONDICION)
        else:
            _anotar(n, chk=True)
            self._log(n.linea, "VERIFICAR",
                      f"condición del '{estructura}' es bool ✓")

    def _s_if_stmt(self, n):
        cond = n.hijos[0] if n.hijos else None
        if cond is not None:
            self._condicion(cond, "if", n)
        antes = self.tabla.foto_valores()
        antes_ini = self.tabla.foto_inicializadas()
        then_b = next((h for h in n.hijos if h.tipo == "then_branch"), None)
        else_b = next((h for h in n.hijos if h.tipo == "else_branch"), None)
        self._sentencia(then_b)
        tras_then = self.tabla.foto_valores()
        ini_then = self.tabla.foto_inicializadas()
        self.tabla.restaurar_valores(antes)
        self.tabla.restaurar_inicializadas(antes_ini)
        self._sentencia(else_b)
        tras_else = self.tabla.foto_valores()
        ini_else = self.tabla.foto_inicializadas()
        # Sólo queda inicializada si lo está en AMBAS ramas
        self.tabla.restaurar_inicializadas(ini_then & ini_else)
        solo_una = sorted((ini_then ^ ini_else) - antes_ini)
        if solo_una:
            self._log(n.linea, "VALOR",
                      "fin del if: " + ", ".join(solo_una) +
                      " → sin asignar (sólo se asigna en una rama)")
        # Fusión: sólo se conserva el valor si ambas ramas coinciden
        desconocidas = []
        for nombre, v_else in tras_else.items():
            v_then = tras_then.get(nombre, DESCONOCIDO)
            if (v_then is DESCONOCIDO or v_else is DESCONOCIDO
                    or v_then != v_else):
                if v_then is not DESCONOCIDO or v_else is not DESCONOCIDO:
                    desconocidas.append(nombre)
                self.tabla.buscar(nombre).valor = DESCONOCIDO
        if desconocidas:
            self._log(n.linea, "VALOR",
                      "fin del if: " + ", ".join(desconocidas) +
                      " → desconocido (depende de la rama ejecutada)")

    def _invalidar_asignadas(self, cuerpo, linea, motivo):
        nombres = sorted(_variables_asignadas(cuerpo))
        cambiadas = []
        for nombre in nombres:
            sim = self.tabla.buscar(nombre)
            if sim and sim.valor is not DESCONOCIDO:
                sim.valor = DESCONOCIDO
                cambiadas.append(nombre)
        if cambiadas:
            self._log(linea, "VALOR",
                      f"{motivo}: " + ", ".join(cambiadas) +
                      " → desconocido (cambia en cada iteración)")

    def _s_while_stmt(self, n):
        cond  = n.hijos[0] if n.hijos else None
        cuerpo = n.hijos[1] if len(n.hijos) > 1 else None
        self._invalidar_asignadas(cuerpo, n.linea, "inicio del while")
        antes_ini = self.tabla.foto_inicializadas()
        if cond is not None:
            self._condicion(cond, "while", n)
        self._sentencia(cuerpo)
        self._invalidar_asignadas(cuerpo, n.linea, "fin del while")
        # El cuerpo de un while puede no ejecutarse nunca
        nuevas = sorted(self.tabla.foto_inicializadas() - antes_ini)
        self.tabla.restaurar_inicializadas(antes_ini)
        if nuevas:
            self._log(n.linea, "VALOR",
                      "fin del while: " + ", ".join(nuevas) +
                      " → sin asignar (el ciclo podría no ejecutarse)")

    def _s_do_until_stmt(self, n):
        cuerpo = n.hijos[0] if n.hijos else None
        cond   = n.hijos[1] if len(n.hijos) > 1 else None
        self._invalidar_asignadas(cuerpo, n.linea, "inicio del do-until")
        self._sentencia(cuerpo)
        if cond is not None:
            self._condicion(cond, "until", n)
        self._invalidar_asignadas(cuerpo, n.linea, "fin del do-until")

    # ── expresiones: tipo y valor sintetizados ─────────────────
    def _expr(self, n):
        if n is None:
            return T_ERROR, DESCONOCIDO
        t, v = self._expr_calc(n)
        _anotar(n, tipo=t, valor=v)
        return t, v

    def _expr_calc(self, n):
        k = n.tipo
        if k == "entero":
            return T_INT, int(n.valor)
        if k == "real_lit":
            return T_FLOAT, float(n.valor)
        if k == "booleano":
            return T_BOOL, n.valor == "true"
        if k == "identificador":
            sim = self._buscar(n.valor, n)
            if sim is None:
                self._error(f"Variable '{n.valor}' no declarada", n,
                            ERR_NO_DECLARADA)
                return T_ERROR, DESCONOCIDO
            _anotar(n, loc=sim.loc, de_tabla=True)
            if not sim.inicializada:
                _anotar(n, chk=False)
                self._error(f"La variable '{n.valor}' se usa sin tener un "
                            f"valor asignado", n, ERR_SIN_VALOR)
                # conserva su tipo para no encadenar más errores
                return sim.tipo, DESCONOCIDO
            return sim.tipo, sim.valor
        if k == "factor_par":
            return self._expr(n.hijos[0]) if n.hijos else (T_ERROR, DESCONOCIDO)
        if k == "negativo":
            t, v = self._expr(n.hijos[0]) if n.hijos else (T_ERROR, DESCONOCIDO)
            if t == T_ERROR:
                return T_ERROR, DESCONOCIDO
            if t not in NUMERICOS:
                self._error(f"El operador '-' (negativo) no se puede aplicar "
                            f"a {t}", n, ERR_OPERADOR)
                return T_ERROR, DESCONOCIDO
            return t, (-v if v is not DESCONOCIDO else DESCONOCIDO)
        if k in ("expresion", "termino", "expr_rel", "condicion"):
            return self._binaria(n)
        return T_ERROR, DESCONOCIDO               # nodo 'error' del sintáctico

    def _binaria(self, n):
        op = n.valor
        izq, der = (n.hijos + [None, None])[:2]
        ti, vi = self._expr(izq)
        td, vd = self._expr(der)
        if T_ERROR in (ti, td):                    # no se encadenan errores
            return T_ERROR, DESCONOCIDO
        conocidos = vi is not DESCONOCIDO and vd is not DESCONOCIDO

        # ── aritméticos ──
        if op in ("+", "-", "*", "/"):
            if ti not in NUMERICOS or td not in NUMERICOS:
                malo = ti if ti not in NUMERICOS else td
                self._error(f"El operador '{op}' no se puede aplicar a {malo}",
                            n, ERR_OPERADOR)
                return T_ERROR, DESCONOCIDO
            # '/' es división real: siempre produce float (1/3 = 0.33)
            t = T_FLOAT if (T_FLOAT in (ti, td) or op == "/") else T_INT
            self._coercion(n, izq, ti, der, td, t)
            v = DESCONOCIDO
            if op == "/" and vd is not DESCONOCIDO and vd == 0:
                self._error("División entre cero", n, ERR_DIV_CERO)
                return T_ERROR, DESCONOCIDO
            if conocidos:
                if op == "+":   v = vi + vd
                elif op == "-": v = vi - vd
                elif op == "*": v = vi * vd
                else:
                    v = float(vi) / float(vd)
                if t == T_FLOAT:
                    v = float(v)
            self._log(n.linea, "TIPO",
                      f"{_desc(n)} : {ti} {op} {td} → {t}"
                      + (f"  (valor {fmt_valor(v)})" if v is not DESCONOCIDO else ""))
            return t, v

        # ── relacionales ──
        if op in ("<", ">", "<=", ">=", "==", "!="):
            if ti in NUMERICOS and td in NUMERICOS:
                self._coercion(n, izq, ti, der, td,
                               T_FLOAT if T_FLOAT in (ti, td) else T_INT)
            elif not (op in ("==", "!=") and ti == td == T_BOOL):
                self._error(f"No se puede comparar {ti} {op} {td}", n,
                            ERR_INCOMPATIBLES)
                return T_ERROR, DESCONOCIDO
            v = DESCONOCIDO
            if conocidos:
                v = {"<": vi < vd, ">": vi > vd, "<=": vi <= vd,
                     ">=": vi >= vd, "==": vi == vd, "!=": vi != vd}[op]
            self._log(n.linea, "TIPO",
                      f"{_desc(n)} : {ti} {op} {td} → bool"
                      + (f"  (valor {fmt_valor(v)})" if v is not DESCONOCIDO else ""))
            return T_BOOL, v

        # ── lógicos ──
        if op in ("&&", "||"):
            if ti != T_BOOL or td != T_BOOL:
                malo = ti if ti != T_BOOL else td
                self._error(f"El operador '{op}' requiere operandos bool, "
                            f"se encontró {malo}", n, ERR_OPERADOR)
                return T_ERROR, DESCONOCIDO
            v = DESCONOCIDO
            if conocidos:
                v = (vi and vd) if op == "&&" else (vi or vd)
            self._log(n.linea, "TIPO",
                      f"{_desc(n)} : bool {op} bool → bool"
                      + (f"  (valor {fmt_valor(v)})" if v is not DESCONOCIDO else ""))
            return T_BOOL, v

        return T_ERROR, DESCONOCIDO

    def _coercion(self, n, izq, ti, der, td, t):
        if t != T_FLOAT:
            return
        for hijo, th in ((izq, ti), (der, td)):
            if th == T_INT:
                _anotar(hijo, conv="int→float")
                self._log(n.linea, "CONVERTIR",
                          f"'{_desc(hijo)}' int → float en '{n.valor}'")


def _variables_asignadas(n) -> set:
    """Variables que se modifican dentro de un bloque (para ciclos)."""
    res = set()
    if n is None:
        return res
    if n.tipo in ("asignacion", "incremento", "decremento", "cin_stmt"):
        nombre = getattr(n, "id_nombre", None)
        if nombre:
            res.add(nombre)
    for h in n.hijos:
        res |= _variables_asignadas(h)
    return res


# ───────────────────────────────────────────────────────────────
#  TEXTO DE LOS ATRIBUTOS (IDE y exportación)
# ───────────────────────────────────────────────────────────────
def texto_atributos(n) -> str:
    a = getattr(n, "atrib", None)
    if not a:
        return ""
    partes = []
    if "dtype" in a:
        partes.append(f"dtype={a['dtype']}" +
                      (" ↓heredado" if a.get("heredado") else ""))
    if "loc" in a:
        partes.append(f"loc={a['loc']}")
    if "asig" in a:
        partes.append(a["asig"])
    elif "tipo" in a:
        partes.append(f"tipo={a['tipo']}" +
                      (" (tabla)" if a.get("de_tabla") else " ↑"))
    if "valor" in a and a.get("tipo") != T_ERROR:
        partes.append(f"val={fmt_valor(a['valor'])}")
    if "conv" in a:
        partes.append(f"conv {a['conv']}")
    if "chk" in a:
        partes.append("✓" if a["chk"] else "✗")
    return "  ·  ".join(partes)


def arbol_texto(raiz, con_atributos=False) -> str:
    lineas = []

    def etiqueta(n):
        txt = n.tipo
        if n.valor:
            txt += f"  '{n.valor}'"
        if n.linea:
            txt += f"  [L{n.linea}]"
        if con_atributos:
            at = texto_atributos(n)
            if at:
                txt += f"   ⟨ {at} ⟩"
        return txt

    def rec(n, prefijo, ultimo, es_raiz):
        if es_raiz:
            lineas.append(etiqueta(n))
            nuevo = ""
        else:
            lineas.append(prefijo + ("└── " if ultimo else "├── ") + etiqueta(n))
            nuevo = prefijo + ("    " if ultimo else "│   ")
        for i, h in enumerate(n.hijos):
            rec(h, nuevo, i == len(n.hijos) - 1, False)

    if raiz is not None:
        rec(raiz, "", True, True)
    return "\n".join(lineas)


def formatear_tabla(tabla: TablaSimbolos) -> str:
    sep = "═" * 72
    filas = [sep,
             f"  {'NOMBRE':<12} {'TIPO':<7} {'LOC':>4}  {'VALOR':<11} "
             f"{'ÁMBITO':<7} LÍNEAS",
             sep]
    for s in tabla.simbolos():
        filas.append(f"  {s.nombre:<12} {s.tipo_decl:<7} {s.loc:>4}  "
                     f"{valor_simbolo(s):<11} {'main':<7} "
                     + ", ".join(str(l) for l in s.lineas))
    filas.append(sep)
    filas.append(f"  Total de símbolos: {len(tabla)}")
    return "\n".join(filas)


def formatear_errores_sem(errores) -> str:
    if not errores:
        return ""
    lineas = [f"{'─'*60}",
              f"  Total de errores semánticos: {len(errores)}",
              f"{'─'*60}"]
    lineas += [str(e) for e in errores]
    return "\n".join(lineas)


def formatear_bitacora(bitacora) -> str:
    out = []
    for linea, accion, detalle in bitacora:
        ln = f"L{linea}" if linea else "  "
        out.append(f"{ln:<5} {accion:<10} {detalle}")
    return "\n".join(out)


class ResultadoSemantico:
    def __init__(self):
        self.arbol        = None    # AST original (fase sintáctica)
        self.anotado      = None    # copia con anotaciones semánticas
        self.tabla        = None
        self.errores_lex  = []
        self.errores_sint = []
        self.errores_sem  = []
        self.bitacora     = []
        self.ejecutado    = False   # False si hubo errores previos


def analizar_semantico(codigo: str) -> ResultadoSemantico:
    """Léxico → Sintáctico → Semántico.
    El semántico sólo se ejecuta si las fases anteriores no tienen errores."""
    r = ResultadoSemantico()
    r.arbol, r.errores_lex, r.errores_sint = analizar_sintactico(codigo)
    if r.errores_lex or r.errores_sint or r.arbol is None:
        return r
    an = AnalizadorSemantico()
    r.anotado     = an.analizar(r.arbol)
    r.tabla       = an.tabla
    r.errores_sem = an.errores
    r.bitacora    = an.bitacora
    r.ejecutado   = True
    return r


# ═══════════════════════════════════════════════════════════════
#  PUNTO DE ENTRADA
# ═══════════════════════════════════════════════════════════════
def main():
    args = sys.argv[1:]

    flag = None
    for f in ("--lexico", "--sintactico", "--semantico"):
        if f in args:
            flag = f
            break

    if flag is None:
        print("Uso: python compilador.py --lexico|--sintactico|--semantico <archivo>",
              file=sys.stderr)
        sys.exit(1)

    idx = args.index(flag)
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

    if flag == "--lexico":
        tokens, errores = analizar(codigo)
        print(formatear_tokens(tokens))
        if errores:
            print(formatear_errores(errores), file=sys.stderr)

    elif flag == "--sintactico":
        arbol, errores_lex, errores_sint = analizar_sintactico(codigo)
        if errores_lex:
            print("(con errores léxicos — sintáctico no ejecutado)")
            print(formatear_errores(errores_lex), file=sys.stderr)
        else:
            if arbol:
                print("Árbol generado correctamente.")
            if errores_sint:
                print(formatear_errores_sint(errores_sint), file=sys.stderr)

    elif flag == "--semantico":
        r = analizar_semantico(codigo)
        if not r.ejecutado:
            print("(con errores léxicos/sintácticos — semántico no ejecutado)")
            if r.errores_lex:
                print(formatear_errores(r.errores_lex), file=sys.stderr)
            if r.errores_sint:
                print(formatear_errores_sint(r.errores_sint), file=sys.stderr)
        else:
            print("ÁRBOL SINTÁCTICO (AST original)\n")
            print(arbol_texto(r.arbol))
            print("\nÁRBOL CON ANOTACIONES SEMÁNTICAS\n")
            print(arbol_texto(r.anotado, con_atributos=True))
            print("\nTABLA DE SÍMBOLOS\n")
            print(formatear_tabla(r.tabla))
            print("\nRECORRIDO SEMÁNTICO\n")
            print(formatear_bitacora(r.bitacora))
            if r.errores_sem:
                print(formatear_errores_sem(r.errores_sem), file=sys.stderr)


if __name__ == "__main__":
    main()