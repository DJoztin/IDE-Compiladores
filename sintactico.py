#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sintactico.py — Analizador Sintáctico para CompiladorIDE UAA
Parser descendente recursivo (LL)

Gramática soportada:
  programa        → 'main' bloque
  bloque          → '{' declaraciones sentencias '}'
  declaraciones   → declaracion declaraciones | ε
  declaracion     → tipo lista_ids ';'
  tipo            → 'int' | 'real'
  lista_ids       → IDENTIFICADOR (',' IDENTIFICADOR)*
  sentencias      → sentencia sentencias | ε
  sentencia       → asignacion | if_stmt | do_while | while_stmt | cin_stmt | cout_stmt
  asignacion      → IDENTIFICADOR '=' expresion ';'
  if_stmt         → 'if' '(' condicion ')' 'then' sentencia_o_bloque
                    ( 'else' sentencia_o_bloque )? 'end' ';'
  do_while        → 'do' cuerpo_do 'until' '(' condicion ')' ';'
  cuerpo_do       → sentencia* 'while' '(' condicion ')' '{' sentencias '}'  ';'
  while_stmt      → 'while' '(' condicion ')' '{' sentencias '}' ';'
  cin_stmt        → 'cin' IDENTIFICADOR ';'
  cout_stmt       → 'cout' IDENTIFICADOR ';'
  condicion       → expresion op_rel expresion (op_log expresion op_rel expresion)*
  expresion       → termino ( ('+' | '-') termino )*
  termino         → factor ( ('*' | '/') factor )*
  factor          → '(' expresion ')' | IDENTIFICADOR | ENTERO | REAL
                    | IDENTIFICADOR ('++' | '--')
  op_rel          → '<' | '>' | '<=' | '>=' | '==' | '!='
  op_log          → '&&' | '||'
"""

import sys
from compilador import analizar, Token

# ─────────────────────────────────────────────────────────────
#  NODO DEL ÁRBOL
# ─────────────────────────────────────────────────────────────
class NodoArbol:
    def __init__(self, etiqueta, token=None):
        self.etiqueta = etiqueta      # texto del nodo
        self.token    = token         # Token hoja (o None si es interno)
        self.hijos: list['NodoArbol'] = []

    def agregar(self, hijo):
        if hijo is not None:
            self.hijos.append(hijo)
        return hijo

    def hoja(etiqueta, token):
        return NodoArbol(etiqueta, token)

    hoja = staticmethod(hoja)


# ─────────────────────────────────────────────────────────────
#  ERROR SINTÁCTICO
# ─────────────────────────────────────────────────────────────
class ErrorSintactico(Exception):
    def __init__(self, mensaje, linea=0, columna=0):
        super().__init__(mensaje)
        self.linea   = linea
        self.columna = columna

    def __str__(self):
        return (f"[ERROR SINTÁCTICO] Línea {self.linea}, "
                f"Columna {self.columna}: {self.args[0]}")


# ─────────────────────────────────────────────────────────────
#  PARSER
# ─────────────────────────────────────────────────────────────
class Parser:
    def __init__(self, tokens: list):
        # Filtrar sólo tokens relevantes (sin comentarios ni errores previos)
        self._tokens = [t for t in tokens
                        if t.tipo not in ("COMENTARIO", "ERROR")]
        self._pos    = 0
        self._errores: list[ErrorSintactico] = []

    # ── helpers ──────────────────────────────────────────────
    def _actual(self) -> Token | None:
        if self._pos < len(self._tokens):
            return self._tokens[self._pos]
        return None

    def _siguiente(self) -> Token | None:
        if self._pos + 1 < len(self._tokens):
            return self._tokens[self._pos + 1]
        return None

    def _avanzar(self) -> Token:
        t = self._actual()
        self._pos += 1
        return t

    def _es(self, tipo, valor=None) -> bool:
        t = self._actual()
        if t is None:
            return False
        if t.tipo != tipo:
            return False
        if valor is not None and t.valor != valor:
            return False
        return True

    def _consumir(self, tipo, valor=None) -> Token:
        t = self._actual()
        if t is None:
            err = ErrorSintactico(
                f"Se esperaba '{valor or tipo}' pero se llegó al fin del archivo",
                0, 0)
            self._errores.append(err)
            raise err
        if t.tipo != tipo or (valor and t.valor != valor):
            desc = f"'{valor}'" if valor else tipo
            err = ErrorSintactico(
                f"Se esperaba {desc} pero se encontró '{t.valor}' ({t.tipo})",
                t.linea, t.columna)
            self._errores.append(err)
            raise err
        return self._avanzar()

    def _recuperar(self, *sincronizadores):
        """Avanza hasta encontrar uno de los tokens de sincronización."""
        while self._actual() is not None:
            t = self._actual()
            for (tp, vl) in sincronizadores:
                if t.tipo == tp and (vl is None or t.valor == vl):
                    return
            self._avanzar()

    # ── Punto de entrada ─────────────────────────────────────
    def parsear(self) -> NodoArbol:
        try:
            return self._programa()
        except ErrorSintactico:
            return NodoArbol("programa")

    # ── programa ─────────────────────────────────────────────
    def _programa(self) -> NodoArbol:
        nodo = NodoArbol("programa")
        tok = self._consumir("RESERVADA", "main")
        nodo.agregar(NodoArbol.hoja("main", tok))
        nodo.agregar(self._bloque())
        return nodo

    # ── bloque  { decls stmts } ──────────────────────────────
    def _bloque(self) -> NodoArbol:
        nodo = NodoArbol("bloque")
        tok = self._consumir("SIMBOLO", "{")
        nodo.agregar(NodoArbol.hoja("{", tok))
        nodo.agregar(self._declaraciones())
        nodo.agregar(self._sentencias())
        tok2 = self._consumir("SIMBOLO", "}")
        nodo.agregar(NodoArbol.hoja("}", tok2))
        return nodo

    # ── declaraciones ────────────────────────────────────────
    def _declaraciones(self) -> NodoArbol:
        nodo = NodoArbol("declaraciones")
        while self._es("RESERVADA", "int") or self._es("RESERVADA", "real"):
            nodo.agregar(self._declaracion())
        return nodo

    def _declaracion(self) -> NodoArbol:
        nodo = NodoArbol("declaracion")
        tok = self._avanzar()   # int | real
        nodo.agregar(NodoArbol.hoja(tok.valor, tok))
        nodo.agregar(self._lista_ids())
        tok_sc = self._consumir("SIMBOLO", ";")
        nodo.agregar(NodoArbol.hoja(";", tok_sc))
        return nodo

    def _lista_ids(self) -> NodoArbol:
        nodo = NodoArbol("lista_ids")
        tok = self._consumir("IDENTIFICADOR")
        nodo.agregar(NodoArbol.hoja(tok.valor, tok))
        while self._es("SIMBOLO", ","):
            nodo.agregar(NodoArbol.hoja(",", self._avanzar()))
            tok2 = self._consumir("IDENTIFICADOR")
            nodo.agregar(NodoArbol.hoja(tok2.valor, tok2))
        return nodo

    # ── sentencias ───────────────────────────────────────────
    def _sentencias(self) -> NodoArbol:
        nodo = NodoArbol("sentencias")
        while self._actual() is not None and not self._es("SIMBOLO", "}"):
            # Tokens de cierre que no son sentencias
            if self._es("RESERVADA", "end") or self._es("RESERVADA", "else"):
                break
            if self._es("RESERVADA", "until"):
                break
            stmt = self._sentencia()
            if stmt:
                nodo.agregar(stmt)
            else:
                break
        return nodo

    def _sentencia(self) -> NodoArbol | None:
        t = self._actual()
        if t is None:
            return None

        try:
            if t.tipo == "IDENTIFICADOR":
                return self._asignacion()
            elif t.tipo == "RESERVADA":
                if t.valor == "if":
                    return self._if_stmt()
                elif t.valor == "do":
                    return self._do_while()
                elif t.valor == "while":
                    return self._while_stmt()
                elif t.valor == "cin":
                    return self._cin_stmt()
                elif t.valor == "cout":
                    return self._cout_stmt()
                else:
                    err = ErrorSintactico(
                        f"Sentencia inesperada: '{t.valor}'",
                        t.linea, t.columna)
                    self._errores.append(err)
                    self._avanzar()
                    return None
            else:
                # token inesperado — recuperar
                err = ErrorSintactico(
                    f"Token inesperado: '{t.valor}' ({t.tipo})",
                    t.linea, t.columna)
                self._errores.append(err)
                self._avanzar()
                return None
        except ErrorSintactico:
            # ya registrado; sincronizar al siguiente ';' o '}'
            self._recuperar(
                ("SIMBOLO", ";"), ("SIMBOLO", "}"),
                ("RESERVADA", "end"), ("RESERVADA", "else"),
                ("RESERVADA", "until"),
            )
            if self._es("SIMBOLO", ";"):
                self._avanzar()
            return None

    # ── asignacion ───────────────────────────────────────────
    def _asignacion(self) -> NodoArbol:
        nodo = NodoArbol("asignacion")
        tok_id = self._consumir("IDENTIFICADOR")
        nodo.agregar(NodoArbol.hoja(tok_id.valor, tok_id))
        tok_eq = self._consumir("ASIGNACION", "=")
        nodo.agregar(NodoArbol.hoja("=", tok_eq))
        nodo.agregar(self._expresion())
        tok_sc = self._consumir("SIMBOLO", ";")
        nodo.agregar(NodoArbol.hoja(";", tok_sc))
        return nodo

    # ── if ───────────────────────────────────────────────────
    def _if_stmt(self) -> NodoArbol:
        nodo = NodoArbol("if")
        nodo.agregar(NodoArbol.hoja("if", self._consumir("RESERVADA", "if")))
        nodo.agregar(NodoArbol.hoja("(", self._consumir("SIMBOLO", "(")))
        nodo.agregar(self._condicion())
        nodo.agregar(NodoArbol.hoja(")", self._consumir("SIMBOLO", ")")))
        nodo.agregar(NodoArbol.hoja("then", self._consumir("RESERVADA", "then")))
        nodo.agregar(self._sentencia_o_bloque_simple())
        if self._es("RESERVADA", "else"):
            nodo.agregar(NodoArbol.hoja("else", self._avanzar()))
            nodo.agregar(self._sentencia_o_bloque_simple())
        nodo.agregar(NodoArbol.hoja("end", self._consumir("RESERVADA", "end")))
        nodo.agregar(NodoArbol.hoja(";", self._consumir("SIMBOLO", ";")))
        return nodo

    def _sentencia_o_bloque_simple(self) -> NodoArbol:
        """Una sola sentencia o un bloque {…}."""
        if self._es("SIMBOLO", "{"):
            return self._bloque()
        else:
            return self._sentencia()

    # ── do … while … until ───────────────────────────────────
    def _do_while(self) -> NodoArbol:
        nodo = NodoArbol("do_while")
        nodo.agregar(NodoArbol.hoja("do", self._consumir("RESERVADA", "do")))
        # cuerpo antes del while
        cuerpo = NodoArbol("cuerpo_do")
        while (self._actual() is not None
               and not self._es("RESERVADA", "while")
               and not self._es("RESERVADA", "until")):
            stmt = self._sentencia()
            if stmt:
                cuerpo.agregar(stmt)
        nodo.agregar(cuerpo)
        # while( cond ){ stmts };
        if self._es("RESERVADA", "while"):
            nodo.agregar(NodoArbol.hoja("while", self._avanzar()))
            nodo.agregar(NodoArbol.hoja("(", self._consumir("SIMBOLO", "(")))
            nodo.agregar(self._condicion())
            nodo.agregar(NodoArbol.hoja(")", self._consumir("SIMBOLO", ")")))
            nodo.agregar(NodoArbol.hoja("{", self._consumir("SIMBOLO", "{")))
            nodo.agregar(self._sentencias())
            nodo.agregar(NodoArbol.hoja("}", self._consumir("SIMBOLO", "}")))
            nodo.agregar(NodoArbol.hoja(";", self._consumir("SIMBOLO", ";")))
        # until( cond );
        nodo.agregar(NodoArbol.hoja("until", self._consumir("RESERVADA", "until")))
        nodo.agregar(NodoArbol.hoja("(", self._consumir("SIMBOLO", "(")))
        nodo.agregar(self._condicion())
        nodo.agregar(NodoArbol.hoja(")", self._consumir("SIMBOLO", ")")))
        nodo.agregar(NodoArbol.hoja(";", self._consumir("SIMBOLO", ";")))
        return nodo

    # ── while ────────────────────────────────────────────────
    def _while_stmt(self) -> NodoArbol:
        nodo = NodoArbol("while")
        nodo.agregar(NodoArbol.hoja("while", self._consumir("RESERVADA", "while")))
        nodo.agregar(NodoArbol.hoja("(", self._consumir("SIMBOLO", "(")))
        nodo.agregar(self._condicion())
        nodo.agregar(NodoArbol.hoja(")", self._consumir("SIMBOLO", ")")))
        nodo.agregar(NodoArbol.hoja("{", self._consumir("SIMBOLO", "{")))
        nodo.agregar(self._sentencias())
        nodo.agregar(NodoArbol.hoja("}", self._consumir("SIMBOLO", "}")))
        nodo.agregar(NodoArbol.hoja(";", self._consumir("SIMBOLO", ";")))
        return nodo

    # ── cin / cout ───────────────────────────────────────────
    def _cin_stmt(self) -> NodoArbol:
        nodo = NodoArbol("cin")
        nodo.agregar(NodoArbol.hoja("cin", self._consumir("RESERVADA", "cin")))
        tok = self._consumir("IDENTIFICADOR")
        nodo.agregar(NodoArbol.hoja(tok.valor, tok))
        nodo.agregar(NodoArbol.hoja(";", self._consumir("SIMBOLO", ";")))
        return nodo

    def _cout_stmt(self) -> NodoArbol:
        nodo = NodoArbol("cout")
        nodo.agregar(NodoArbol.hoja("cout", self._consumir("RESERVADA", "cout")))
        tok = self._consumir("IDENTIFICADOR")
        nodo.agregar(NodoArbol.hoja(tok.valor, tok))
        nodo.agregar(NodoArbol.hoja(";", self._consumir("SIMBOLO", ";")))
        return nodo

    # ── condicion ────────────────────────────────────────────
    def _condicion(self) -> NodoArbol:
        nodo = NodoArbol("condicion")
        nodo.agregar(self._expresion())
        if self._es_op_rel():
            nodo.agregar(self._op_rel())
            nodo.agregar(self._expresion())
            # operadores lógicos adicionales
            while self._es_op_log():
                nodo.agregar(self._op_log())
                nodo.agregar(self._expresion())
                if self._es_op_rel():
                    nodo.agregar(self._op_rel())
                    nodo.agregar(self._expresion())
        return nodo

    def _es_op_rel(self) -> bool:
        return self._es("OP_RELACIONAL")

    def _es_op_log(self) -> bool:
        return self._es("OP_LOGICO")

    def _op_rel(self) -> NodoArbol:
        tok = self._consumir("OP_RELACIONAL")
        return NodoArbol.hoja(tok.valor, tok)

    def _op_log(self) -> NodoArbol:
        tok = self._consumir("OP_LOGICO")
        return NodoArbol.hoja(tok.valor, tok)

    # ── expresion ────────────────────────────────────────────
    def _expresion(self) -> NodoArbol:
        nodo = NodoArbol("expresion")
        nodo.agregar(self._termino())
        while self._es("OP_ARITMETICO", "+") or self._es("OP_ARITMETICO", "-"):
            tok = self._avanzar()
            nodo.agregar(NodoArbol.hoja(tok.valor, tok))
            nodo.agregar(self._termino())
        return nodo

    # ── termino ──────────────────────────────────────────────
    def _termino(self) -> NodoArbol:
        nodo = NodoArbol("termino")
        nodo.agregar(self._factor())
        while self._es("OP_ARITMETICO", "*") or self._es("OP_ARITMETICO", "/"):
            tok = self._avanzar()
            nodo.agregar(NodoArbol.hoja(tok.valor, tok))
            nodo.agregar(self._factor())
        return nodo

    # ── factor ───────────────────────────────────────────────
    def _factor(self) -> NodoArbol:
        nodo = NodoArbol("factor")
        t = self._actual()
        if t is None:
            err = ErrorSintactico("Se esperaba un factor pero llegó fin de archivo")
            self._errores.append(err)
            raise err

        if self._es("SIMBOLO", "("):
            nodo.agregar(NodoArbol.hoja("(", self._avanzar()))
            nodo.agregar(self._expresion())
            nodo.agregar(NodoArbol.hoja(")", self._consumir("SIMBOLO", ")")))
        elif t.tipo == "IDENTIFICADOR":
            tok_id = self._avanzar()
            nodo.agregar(NodoArbol.hoja(tok_id.valor, tok_id))
            if self._es("OP_ARITMETICO", "++") or self._es("OP_ARITMETICO", "--"):
                tok_op = self._avanzar()
                nodo.agregar(NodoArbol.hoja(tok_op.valor, tok_op))
        elif t.tipo == "ENTERO":
            nodo.agregar(NodoArbol.hoja(t.valor, t))
            self._avanzar()
        elif t.tipo == "REAL":
            nodo.agregar(NodoArbol.hoja(t.valor, t))
            self._avanzar()
        else:
            err = ErrorSintactico(
                f"Factor inesperado: '{t.valor}' ({t.tipo})",
                t.linea, t.columna)
            self._errores.append(err)
            raise err
        return nodo


# ─────────────────────────────────────────────────────────────
#  API PÚBLICA
# ─────────────────────────────────────────────────────────────
def analizar_sintactico(codigo: str):
    """
    Devuelve (arbol: NodoArbol, errores: list[ErrorSintactico])
    Primero corre el léxico; si hay errores léxicos los incluye.
    """
    tokens, errores_lex = analizar(codigo)
    # No abortamos por errores léxicos — el parser intentará igual
    parser = Parser(tokens)
    arbol  = parser.parsear()
    # Combinar errores léxicos convertidos + sintácticos
    class _EL:
        def __init__(self, e): self._e = e
        @property
        def linea(self): return self._e.linea
        @property
        def columna(self): return self._e.columna
        def __str__(self): return str(self._e)

    errores = [_EL(e) for e in errores_lex] + parser._errores
    return arbol, errores


def formatear_errores_sint(errores):
    if not errores:
        return ""
    lineas = [
        f"{'─'*60}",
        f"  Total de errores: {len(errores)}",
        f"{'─'*60}",
    ]
    for e in errores:
        lineas.append(str(e))
    return "\n".join(lineas)
