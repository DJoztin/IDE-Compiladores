"""
cgen.py — Generador de código TM.

Port en Python de cgen.c del compilador TINY (Kenneth C. Louden).
Mismo algoritmo:
  * El resultado de toda expresión queda en el acumulador ac (reg 0).
  * El operando izquierdo de un operador binario se guarda en un temporal
    en tmpOffset(mp) (tmpOffset se decrementa al guardar y se incrementa
    al recuperar) y se vuelve a cargar en ac1 (reg 1).
  * Los saltos hacia adelante se resuelven con emitSkip / emitBackup /
    emitRestore / emitRM_Abs (backpatching).
  * Las variables viven en loc(gp), con loc = dirección de la tabla de
    símbolos (equivalente a st_lookup).

Recorre el ÁRBOL ANOTADO por el semántico. La tabla de correspondencia
nodo ↔ TINY ↔ instrucciones está en docs/CORRESPONDENCIA_TINY.md.
"""
from code_tm import EmisorTM, PC, MP, GP, AC, AC1

_ARIT = {"+": ("ADD", "op +"), "-": ("SUB", "op -"),
         "*": ("MUL", "op *"), "/": ("DIV", "op /")}
_REL = {"<": "JLT", "<=": "JLE", ">": "JGT", ">=": "JGE",
        "==": "JEQ", "!=": "JNE"}


class ErrorGeneracion(Exception):
    pass


class GeneradorTM:

    def __init__(self, tabla, emisor: EmisorTM | None = None):
        self.tabla = tabla
        self.e = emisor or EmisorTM()
        self.tmp_offset = 0          # tmpOffset de cgen.c

    # ── utilidades ─────────────────────────────────────────────
    def _loc(self, nombre):
        sim = self.tabla.buscar(nombre)
        if sim is None:
            raise ErrorGeneracion(f"'{nombre}' no está en la tabla de símbolos")
        return sim.loc

    def _es_float(self, nombre):
        sim = self.tabla.buscar(nombre)
        return sim is not None and sim.tipo == "float"

    def _conv(self, n):
        """Conversión int→float sin opcode nuevo: ac = ac * 1.0"""
        if getattr(n, "atrib", {}).get("conv"):
            e = self.e
            e.emit_rm("LDC", AC1, 1.0, 0, "conv: load 1.0")
            e.emit_ro("MUL", AC, AC, AC1, "conv int->float")

    def _push(self, c="op: push left"):
        self.e.emit_rm("ST", AC, self.tmp_offset, MP, c)
        self.tmp_offset -= 1

    def _pop_ac1(self, c="op: load left"):
        self.tmp_offset += 1
        self.e.emit_rm("LD", AC1, self.tmp_offset, MP, c)

    # ── recorrido (cGen) ───────────────────────────────────────
    def generar(self, n):
        if n is None:
            return
        f = getattr(self, f"_s_{n.tipo}", None)
        if f is not None:
            f(n)
        else:          # programa, lista_sentencias, then/else_branch: hijos
            for h in n.hijos:
                self.generar(h)

    # ── sentencias (genStmt) ───────────────────────────────────
    def _s_declaracion(self, n):
        ids = [i for l in n.hijos for i in l.hijos]
        nombres = ", ".join(i.valor for i in ids)
        locs = ", ".join(str(self._loc(i.valor)) for i in ids
                         if self.tabla.buscar(i.valor))
        self.e.emit_comment(f"declaracion {n.valor} {nombres} (loc {locs})")

    def _s_asignacion(self, n):
        e = self.e
        e.emit_comment("-> assign")
        self.expr(n.hijos[0])
        e.emit_rm("ST", AC, self._loc(n.id_nombre), GP, "assign: store value")
        e.emit_comment("<- assign")

    def _incr_decr(self, n, signo):
        e = self.e
        e.emit_comment(f"-> assign ({n.id_nombre}{signo})")
        # en el árbol anotado: hijo 'expresion'  id (+|-) 1
        self.expr(n.hijos[0])
        e.emit_rm("ST", AC, self._loc(n.id_nombre), GP, "assign: store value")
        e.emit_comment("<- assign")

    def _s_incremento(self, n):
        self._incr_decr(n, "++")

    def _s_decremento(self, n):
        self._incr_decr(n, "--")

    def _s_cin_stmt(self, n):
        e = self.e
        nombre = n.id_nombre
        e.emit_ro("IN", AC, 0, 0, "read integer value" if not self._es_float(nombre)
                  else "read real value")
        if self._es_float(nombre):
            e.emit_rm("LDC", AC1, 1.0, 0, "conv: load 1.0")
            e.emit_ro("MUL", AC, AC, AC1, "conv int->float")
        e.emit_rm("ST", AC, self._loc(nombre), GP, "read: store value")

    def _s_cout_stmt(self, n):
        self.expr(n.hijos[0])
        self.e.emit_ro("OUT", AC, 0, 0, "write ac")

    def _s_if_stmt(self, n):
        e = self.e
        e.emit_comment("-> if")
        cond = n.hijos[0]
        then_b = next((h for h in n.hijos[1:] if h.tipo == "then_branch"), None)
        else_b = next((h for h in n.hijos[1:] if h.tipo == "else_branch"), None)
        self.expr(cond)
        saved1 = e.emit_skip(1)
        e.emit_comment("if: jump to else belongs here")
        self.generar(then_b)
        saved2 = e.emit_skip(1)
        e.emit_comment("if: jump to end belongs here")
        current = e.emit_skip(0)
        e.emit_backup(saved1)
        e.emit_rm_abs("JEQ", AC, current, "if: jmp to else")
        e.emit_restore()
        self.generar(else_b)
        current = e.emit_skip(0)
        e.emit_backup(saved2)
        e.emit_rm_abs("LDA", PC, current, "jmp to end")
        e.emit_restore()
        e.emit_comment("<- if")

    def _s_do_until_stmt(self, n):
        # equivalente a RepeatK
        e = self.e
        e.emit_comment("-> do-until")
        cuerpo, cond = n.hijos[0], n.hijos[1]
        saved = e.emit_skip(0)
        e.emit_comment("do-until: jump after body comes back here")
        self.generar(cuerpo)
        self.expr(cond)
        e.emit_rm_abs("JEQ", AC, saved, "do-until: jmp back to body")
        e.emit_comment("<- do-until")

    def _s_while_stmt(self, n):
        e = self.e
        e.emit_comment("-> while")
        cond, cuerpo = n.hijos[0], n.hijos[1]
        inicio = e.emit_skip(0)
        e.emit_comment("while: condition is evaluated here")
        self.expr(cond)
        salto = e.emit_skip(1)
        e.emit_comment("while: jump to end belongs here")
        self.generar(cuerpo)
        e.emit_rm_abs("LDA", PC, inicio, "while: jmp back to condition")
        fin = e.emit_skip(0)
        e.emit_backup(salto)
        e.emit_rm_abs("JEQ", AC, fin, "while: jmp to end")
        e.emit_restore()
        e.emit_comment("<- while")

    # ── expresiones (genExp) ───────────────────────────────────
    def expr(self, n):
        k = n.tipo
        e = self.e
        if k in ("entero", "real_lit", "booleano"):
            if k == "entero":
                val = int(n.valor)
            elif k == "real_lit":
                val = float(n.valor)
            else:
                val = 1 if n.valor == "true" else 0
            e.emit_comment("-> Const")
            e.emit_rm("LDC", AC, val, 0, "load const")
            e.emit_comment("<- Const")
        elif k == "identificador":
            e.emit_comment("-> Id")
            e.emit_rm("LD", AC, self._loc(n.valor), GP, "load id value")
            e.emit_comment("<- Id")
        elif k == "factor_par":
            self.expr(n.hijos[0])
        elif k == "negativo":
            e.emit_comment("-> Neg")
            self.expr(n.hijos[0])
            e.emit_rm("LDC", AC1, 0, 0, "neg: load 0")
            e.emit_ro("SUB", AC, AC1, AC, "op - (unario)")
            e.emit_comment("<- Neg")
        elif k == "termino" and n.valor == "%":
            self._modulo(n)
        elif k == "potencia":
            self._potencia(n)
        elif k in ("expresion", "termino", "expr_rel", "condicion"):
            self._binaria(n)
        else:
            raise ErrorGeneracion(f"Nodo inesperado en expresión: {k}")
        self._conv(n)

    def _binaria(self, n):
        e = self.e
        op = n.valor
        e.emit_comment("-> Op")
        self.expr(n.hijos[0])
        self._push()
        self.expr(n.hijos[1])
        self._pop_ac1()
        if op in _ARIT:
            ins, c = _ARIT[op]
            e.emit_ro(ins, AC, AC1, AC, c)
        elif op in _REL:
            e.emit_ro("SUB", AC, AC1, AC, f"op {op}")
            e.emit_rm(_REL[op], AC, 2, PC, "br if true")
            e.emit_rm("LDC", AC, 0, AC, "false case")
            e.emit_rm("LDA", PC, 1, PC, "unconditional jmp")
            e.emit_rm("LDC", AC, 1, AC, "true case")
        elif op == "&&":
            e.emit_ro("MUL", AC, AC1, AC, "op &&")
        elif op == "||":
            e.emit_ro("ADD", AC, AC1, AC, "op ||")
            e.emit_rm("JEQ", AC, 1, PC, "|| : false stays 0")
            e.emit_rm("LDC", AC, 1, 0, "|| : true is 1")
        else:
            e.emit_comment("BUG: Unknown operator")
        e.emit_comment("<- Op")

    def _modulo(self, n):
        """a % b = a - (a / b) * b   (solo enteros; DIV trunca)"""
        e = self.e
        e.emit_comment("-> Op %")
        self.expr(n.hijos[0])
        izq = self.tmp_offset
        self._push("mod: push left (a)")
        self.expr(n.hijos[1])
        der = self.tmp_offset
        self._push("mod: push right (b)")
        e.emit_rm("LD", AC1, izq, MP, "mod: load a")
        e.emit_ro("DIV", AC, AC1, AC, "mod: a / b")
        e.emit_rm("LD", AC1, der, MP, "mod: load b")
        e.emit_ro("MUL", AC, AC, AC1, "mod: (a / b) * b")
        e.emit_rm("LD", AC1, izq, MP, "mod: load a")
        e.emit_ro("SUB", AC, AC1, AC, "op %")
        self.tmp_offset += 2
        e.emit_comment("<- Op %")

    def _potencia(self, n):
        """a ^ b con un ciclo en línea (b entero; b <= 0 -> 1)."""
        e = self.e
        base_float = getattr(n, "atrib", {}).get("tipo") == "float"
        e.emit_comment("-> Op ^")
        self.expr(n.hijos[0])
        base = self.tmp_offset
        self._push("pow: push base")
        self.expr(n.hijos[1])
        cont = self.tmp_offset
        self._push("pow: push exponent (counter)")
        res = self.tmp_offset
        e.emit_rm("LDC", AC, 1.0 if base_float else 1, 0, "pow: result = 1")
        self._push("pow: push result")
        inicio = e.emit_skip(0)
        e.emit_rm("LD", AC, cont, MP, "pow: load counter")
        salto = e.emit_skip(1)
        e.emit_comment("pow: jump to end belongs here")
        e.emit_rm("LD", AC, res, MP, "pow: load result")
        e.emit_rm("LD", AC1, base, MP, "pow: load base")
        e.emit_ro("MUL", AC, AC, AC1, "pow: result * base")
        e.emit_rm("ST", AC, res, MP, "pow: store result")
        e.emit_rm("LD", AC, cont, MP, "pow: load counter")
        e.emit_rm("LDC", AC1, 1, 0, "pow: load 1")
        e.emit_ro("SUB", AC, AC, AC1, "pow: counter - 1")
        e.emit_rm("ST", AC, cont, MP, "pow: store counter")
        e.emit_rm_abs("LDA", PC, inicio, "pow: jmp back")
        fin = e.emit_skip(0)
        e.emit_backup(salto)
        e.emit_rm_abs("JLE", AC, fin, "pow: exit if counter <= 0")
        e.emit_restore()
        e.emit_rm("LD", AC, res, MP, "pow: load result")
        self.tmp_offset += 3
        e.emit_comment("<- Op ^")


def generar_codigo_tm(arbol_anotado, tabla, nombre_archivo="programa.tm") -> EmisorTM:
    """Equivalente a codeGen(syntaxTree, codefile)."""
    g = GeneradorTM(tabla)
    e = g.e
    e.emit_comment("Compilacion a codigo TM (esquema TINY de Louden)")
    e.emit_comment(f"File: {nombre_archivo}")
    e.emit_comment("Standard prelude:")
    e.emit_rm("LD", MP, 0, AC, "load maxaddress from location 0")
    e.emit_rm("ST", AC, 0, AC, "clear location 0")
    e.emit_comment("End of standard prelude.")
    g.generar(arbol_anotado)
    e.emit_comment("End of execution.")
    e.emit_ro("HALT", 0, 0, 0, "")
    return e
