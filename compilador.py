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
    "switch", "case", "int", "float", "real",
    "main", "cin", "cout", "then", "until"
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
    def __init__(self, tipo: str, valor: str = "", linea: int = 0):
        self.tipo  = tipo
        self.valor = valor
        self.linea = linea
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
      declaracion    → ('int'|'real'|'float') lista_ids ';'
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
      factor         → '(' expresion ')' | ENTERO | REAL | ID | '-' factor
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
                'int', 'real', 'float', 'if', 'do', 'while', 'cin', 'cout'):
            return True
        return t.tipo == TK_IDENTIFICADOR

    # ── gramática ───────────────────────────────────────────────
    def parsear(self) -> NodoSint:
        return self._programa()

    def _programa(self) -> NodoSint:
        n = NodoSint("programa", "main")
        t = self._consumir(TK_RESERVADA, "main")
        if t: n.linea = t.linea
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
        if t.tipo == TK_RESERVADA and v in ('int', 'real', 'float'):
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
            n.valor = t.valor   # "int" / "real" / "float" como valor del nodo
            n.linea = t.linea
        n.agregar(self._lista_ids())
        self._consumir(TK_SIMBOLO, ";")
        return n

    def _lista_ids(self) -> NodoSint:
        n = NodoSint("lista_ids")
        t = self._consumir(TK_IDENTIFICADOR)
        if t:
            n.linea = t.linea
            n.agregar(NodoSint("identificador", t.valor, t.linea))
        while self._espera(TK_SIMBOLO, ","):
            self._consumir(TK_SIMBOLO, ",")
            t = self._consumir(TK_IDENTIFICADOR)
            if t: n.agregar(NodoSint("identificador", t.valor, t.linea))
        return n

    def _asig_incr(self) -> NodoSint | None:
        id_tok = self._consumir(TK_IDENTIFICADOR)
        if id_tok is None:
            return None
        t2 = self._tok()
        if t2 and t2.tipo == TK_ASIGNACION:
            n = NodoSint("asignacion", f"{id_tok.valor} =", id_tok.linea)
            self._consumir(TK_ASIGNACION, "=")
            n.agregar(self._expresion())
            self._consumir(TK_SIMBOLO, ";")
            return n
        if t2 and t2.tipo == TK_OP_ARIT and t2.valor == '++':
            n = NodoSint("incremento", f"{id_tok.valor}++", id_tok.linea)
            self._consumir(TK_OP_ARIT, "++")
            self._consumir(TK_SIMBOLO, ";")
            return n
        if t2 and t2.tipo == TK_OP_ARIT and t2.valor == '--':
            n = NodoSint("decremento", f"{id_tok.valor}--", id_tok.linea)
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
        if t: n.linea = t.linea
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
        if t: n.linea = t.linea
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
        if t: n.linea = t.linea
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
        if t: n.linea = t.linea
        self._consumir(TK_SIMBOLO, "(")
        t = self._consumir(TK_IDENTIFICADOR)
        if t: n.valor = f"cin({t.valor})"
        self._consumir(TK_SIMBOLO, ")")
        self._consumir(TK_SIMBOLO, ";")
        return n

    def _cout_stmt(self) -> NodoSint:
        n = NodoSint("cout_stmt", "cout")
        t = self._consumir(TK_RESERVADA, "cout")
        if t: n.linea = t.linea
        n.agregar(self._expresion())
        self._consumir(TK_SIMBOLO, ";")
        return n

    def _condicion(self) -> NodoSint:
        # El operador lógico es la raíz; operandos son hijos izq/der
        left = self._expr_rel()
        while self._espera(TK_OP_LOG) and self._tok().valor in ('&&', '||'):
            t = self._consumir(TK_OP_LOG)
            right = self._expr_rel()
            node = NodoSint("condicion", t.valor, t.linea)
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
            node = NodoSint("expr_rel", t.valor, t.linea)
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
            node = NodoSint("expresion", t.valor, t.linea)
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
            node = NodoSint("termino", t.valor, t.linea)
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
            n = NodoSint("factor_par", "(expr)", t.linea)
            self._consumir(TK_SIMBOLO, "(")
            n.agregar(self._expresion())
            self._consumir(TK_SIMBOLO, ")")
            return n
        if t.tipo == TK_ENTERO:
            self.pos += 1
            return NodoSint("entero", t.valor, t.linea)
        if t.tipo == TK_REAL:
            self.pos += 1
            return NodoSint("real_lit", t.valor, t.linea)
        if t.tipo == TK_IDENTIFICADOR:
            self.pos += 1
            return NodoSint("identificador", t.valor, t.linea)
        if t.tipo == TK_OP_ARIT and t.valor == '-':
            n = NodoSint("negativo", "-", t.linea)
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
#  PUNTO DE ENTRADA
# ═══════════════════════════════════════════════════════════════
def main():
    args = sys.argv[1:]

    flag = None
    for f in ("--lexico", "--sintactico"):
        if f in args:
            flag = f
            break

    if flag is None:
        print("Uso: python compilador.py --lexico|--sintactico <archivo>",
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


if __name__ == "__main__":
    main()