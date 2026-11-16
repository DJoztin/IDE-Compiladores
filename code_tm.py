"""
code_tm.py — Utilidades para emitir código TM.

Port en Python de code.c / code.h del compilador TINY (Kenneth C. Louden),
tal como lo usa la docente en referencia/Tiny_Intermedio_TM.

Diferencias con code.c:
  * El estado (emitLoc, highEmitLoc) vive en un objeto EmisorTM, no en
    variables globales, para que cada compilación empiece limpia.
  * Las líneas se guardan en memoria (en orden de emisión, igual que el
    archivo que escribe code.c) y además en una lista estructurada
    (loc, op, a1, a2, a3, comentario) para la vista en tabla del IDE.
  * El desplazamiento d de LDC puede ser real (extensión de reales de la
    TM, ver docs/CORRESPONDENCIA_TINY.md). Se escribe con repr(): 3.14, 1.0.
"""

# Registros (code.h)
PC = 7    # contador de programa
MP = 6    # "memory pointer": tope de memoria, base de los temporales
GP = 5    # "global pointer": base de las variables
AC = 0    # acumulador
AC1 = 1   # segundo acumulador

# Clasificación de opcodes (tm.c)
OPS_RO = ("HALT", "IN", "OUT", "ADD", "SUB", "MUL", "DIV")
OPS_RM = ("LD", "ST", "LDA", "LDC", "JLT", "JLE", "JGT", "JGE", "JEQ", "JNE")


def fmt_num(x) -> str:
    """Formato de un operando numérico: int con %d, float con repr."""
    if isinstance(x, bool):
        return str(int(x))
    if isinstance(x, float):
        return repr(x)
    return str(x)


class EmisorTM:
    """Equivalente a code.c. TraceCode siempre activo."""

    def __init__(self, trace_code: bool = True):
        self.trace = trace_code
        self.emit_loc = 0        # emitLoc
        self.high_emit_loc = 0   # highEmitLoc
        self.lineas: list[str] = []          # texto del .tm, orden de emisión
        self.instrucciones: list[tuple] = [] # (loc, op, a1, a2, a3, coment, es_rm)

    # ── code.c ────────────────────────────────────────────────
    def emit_comment(self, c: str):
        if self.trace:
            self.lineas.append(f"* {c}")

    def _registrar(self, texto, loc, op, a1, a2, a3, c, es_rm):
        self.lineas.append(texto)
        self.instrucciones.append((loc, op, a1, a2, a3, c, es_rm))

    def emit_ro(self, op: str, r: int, s: int, t: int, c: str = ""):
        texto = f"{self.emit_loc:3d}:  {op:>5s}  {r},{s},{t} "
        if self.trace:
            texto += f"\t{c}"
        self._registrar(texto, self.emit_loc, op, r, s, t, c, False)
        self.emit_loc += 1
        if self.high_emit_loc < self.emit_loc:
            self.high_emit_loc = self.emit_loc

    def emit_rm(self, op: str, r: int, d, s: int, c: str = ""):
        texto = f"{self.emit_loc:3d}:  {op:>5s}  {r},{fmt_num(d)}({s}) "
        if self.trace:
            texto += f"\t{c}"
        self._registrar(texto, self.emit_loc, op, r, d, s, c, True)
        self.emit_loc += 1
        if self.high_emit_loc < self.emit_loc:
            self.high_emit_loc = self.emit_loc

    def emit_skip(self, how_many: int) -> int:
        i = self.emit_loc
        self.emit_loc += how_many
        if self.high_emit_loc < self.emit_loc:
            self.high_emit_loc = self.emit_loc
        return i

    def emit_backup(self, loc: int):
        if loc > self.high_emit_loc:
            self.emit_comment("BUG in emitBackup")
        self.emit_loc = loc

    def emit_restore(self):
        self.emit_loc = self.high_emit_loc

    def emit_rm_abs(self, op: str, r: int, a: int, c: str = ""):
        """Convierte la dirección absoluta a en un salto relativo al pc."""
        self.emit_rm(op, r, a - (self.emit_loc + 1), PC, c)

    # ── salida ────────────────────────────────────────────────
    def texto(self) -> str:
        return "\n".join(self.lineas) + "\n"

    def instrucciones_ordenadas(self) -> list[tuple]:
        """(loc, op, a1, a2, a3, comentario) ordenado por dirección."""
        return [i[:6] for i in sorted(self.instrucciones, key=lambda i: i[0])]

    @staticmethod
    def operandos(instr) -> str:
        """Texto de los operandos de una instrucción estructurada."""
        _loc, op, a1, a2, a3 = instr[:5]
        if op in OPS_RO:
            return f"{a1},{a2},{a3}"
        return f"{a1},{fmt_num(a2)}({a3})"

    def __len__(self):
        return len(self.instrucciones)
