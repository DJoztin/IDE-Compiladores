"""
tm.py — La máquina TM ("Tiny Machine") en Python.

Port de tm.c (Kenneth C. Louden, versión en español de la docente).
Mismo juego de instrucciones, mismos registros y mismo formato de archivo .tm.

Extensión única (documentada en docs/CORRESPONDENCIA_TINY.md):
  * Registros y memoria guardan int o float.
  * LDC acepta una constante real:   LDC 0,3.14(0)
  * IN acepta enteros o reales (con signo).
  * DIV es entera (trunca hacia cero, como C) si ambos operandos son int,
    y real si alguno es float.
No hay opcodes nuevos.

Se usa de dos formas:
  * Como máquina de estados no bloqueante (MaquinaTM.paso), para el IDE:
    cuando la TM necesita una entrada devuelve NECESITA_ENTRADA y espera a
    que se llame dar_entrada(texto).
  * Como consola (python tm.py archivo.tm), con los mismos comandos que
    tm.exe: h v i d r s g t p c q.
"""
import os
import sys

IADDR_SIZE = 4096     # tm.c usa 1024; se amplía para programas grandes
DADDR_SIZE = 1024
NO_REGS = 8
PC_REG = 7
MAX_PASOS = 20_000_000

OPS_RR = ("HALT", "IN", "OUT", "ADD", "SUB", "MUL", "DIV")
OPS_RM = ("LD", "ST")
OPS_RA = ("LDA", "LDC", "JLT", "JLE", "JGT", "JGE", "JEQ", "JNE")
OPCODES = OPS_RR + OPS_RM + OPS_RA

ALIAS_REG = {0: "ac", 1: "ac1", 5: "gp", 6: "mp", 7: "pc"}


class Estado:
    OKAY = "OKAY"
    HALT = "HALT"
    NECESITA_ENTRADA = "NECESITA_ENTRADA"
    SALIDA = "SALIDA"
    IMEM_ERR = "IMEM_ERR"
    DMEM_ERR = "DMEM_ERR"
    ZERODIVIDE = "ZERODIVIDE"
    LIMITE = "LIMITE"


MENSAJE_ESTADO = {
    Estado.OKAY: "Correcto",
    Estado.HALT: "Ejecucion finalizada (HALT)",
    Estado.IMEM_ERR: "Error: memoria de instrucciones",
    Estado.DMEM_ERR: "Error: memoria de datos",
    Estado.ZERODIVIDE: "Error: division entre cero",
    Estado.LIMITE: "Error: limite de pasos alcanzado (posible ciclo infinito)",
}

ERRORES = (Estado.IMEM_ERR, Estado.DMEM_ERR, Estado.ZERODIVIDE, Estado.LIMITE)


def fmt_valor(v) -> str:
    """OUT: int con %d; float con hasta 6 decimales, siempre con punto."""
    if isinstance(v, float):
        if v != v or v in (float("inf"), float("-inf")):
            return str(v)
        s = f"{v:.6f}".rstrip("0")
        if s.endswith("."):
            s += "0"
        if s in ("-0.0",):
            s = "0.0"
        return s
    return str(v)


def fmt_operando(v) -> str:
    return repr(v) if isinstance(v, float) else str(v)


def _div_entera(a: int, b: int) -> int:
    """División entera truncando hacia cero (como C). // de Python
    redondea hacia -infinito, por eso no se usa directo."""
    q = abs(a) // abs(b)
    return q if (a >= 0) == (b >= 0) else -q


def _normaliza(x):
    """Un float con valor entero sigue siendo float (no se pierde el tipo)."""
    return x


# ═══════════════════════════════════════════════════════════════
#  LECTOR DE LÍNEAS (getNum, getWord, skipCh... de tm.c)
# ═══════════════════════════════════════════════════════════════
class _Lector:
    def __init__(self, linea: str):
        self.s = linea
        self.col = 0
        self.num = 0
        self.word = ""

    def _ch(self):
        return self.s[self.col] if self.col < len(self.s) else " "

    def non_blank(self) -> bool:
        while self.col < len(self.s) and self.s[self.col] in " \t":
            self.col += 1
        return self.col < len(self.s)

    def at_eol(self) -> bool:
        return not self.non_blank()

    def skip_ch(self, c) -> bool:
        if self.non_blank() and self._ch() == c:
            self.col += 1
            return True
        return False

    def get_word(self) -> bool:
        self.word = ""
        if self.non_blank():
            ini = self.col
            while self.col < len(self.s) and self.s[self.col].isalnum():
                self.col += 1
            self.word = self.s[ini:self.col][:19]
        return self.word != ""

    def get_num(self) -> bool:
        """Como getNum de tm.c (signos y sumas de términos), extendido
        para aceptar una parte decimal y exponente: 3.14, -2.5, 1e-05."""
        hay = False
        total = 0
        while True:
            signo = 1
            while self.non_blank() and self._ch() in "+-":
                hay = False
                if self._ch() == "-":
                    signo = -signo
                self.col += 1
            self.non_blank()
            ini = self.col
            while self._ch().isdigit():
                self.col += 1
            es_real = False
            if self._ch() == "." :
                j = self.col + 1
                while j < len(self.s) and self.s[j].isdigit():
                    j += 1
                if j > self.col + 1 or self.col > ini:
                    self.col = j
                    es_real = True
            if self.col > ini and self._ch() in "eE":
                j = self.col + 1
                if j < len(self.s) and self.s[j] in "+-":
                    j += 1
                k = j
                while k < len(self.s) and self.s[k].isdigit():
                    k += 1
                if k > j:
                    self.col = k
                    es_real = True
            texto = self.s[ini:self.col]
            if texto and texto != ".":
                hay = True
                termino = float(texto) if es_real else int(texto)
            else:
                termino = 0
            total = total + termino * signo
            if not (self.non_blank() and self._ch() in "+-"):
                break
        self.num = total
        return hay


# ═══════════════════════════════════════════════════════════════
#  MÁQUINA TM
# ═══════════════════════════════════════════════════════════════
class MaquinaTM:
    IADDR_SIZE = IADDR_SIZE
    DADDR_SIZE = DADDR_SIZE
    NO_REGS = NO_REGS
    PC_REG = PC_REG

    def __init__(self, max_pasos: int = MAX_PASOS):
        self.max_pasos = max_pasos
        self.iMem = [("HALT", 0, 0, 0)] * IADDR_SIZE
        self.cargadas: set[int] = set()     # direcciones definidas en el .tm
        self.reg = [0] * NO_REGS
        self.dMem = [0] * DADDR_SIZE
        self.salidas: list = []
        self.pasos = 0
        self.esperando_reg = None           # registro destino de un IN pendiente
        self.ultima_salida = None
        self.estado = Estado.OKAY
        self.reiniciar()

    # ── readInstructions ──────────────────────────────────────
    def cargar(self, texto_tm: str) -> list[str]:
        """Lee el texto de un .tm. Devuelve la lista de errores (vacía si
        se cargó bien). El formato del mensaje es el de tm.c."""
        self.iMem = [("HALT", 0, 0, 0)] * IADDR_SIZE
        self.cargadas = set()
        self.reiniciar()

        def error(msg, line_no, inst_no=-1):
            t = f"Line {line_no}"
            if inst_no >= 0:
                t += f" (Instruction {inst_no})"
            return [f"{t}   {msg}"]

        for line_no, linea in enumerate(texto_tm.splitlines(), start=1):
            lx = _Lector(linea)
            if not lx.non_blank() or linea[lx.col] == "*":
                continue
            if not lx.get_num() or isinstance(lx.num, float):
                return error("Bad location", line_no)
            loc = lx.num
            if loc < 0 or loc >= IADDR_SIZE:
                return error("Location too large", line_no, loc)
            if not lx.skip_ch(":"):
                return error("Missing colon", line_no, loc)
            if not lx.get_word():
                return error("Missing opcode", line_no, loc)
            op = lx.word[:4]
            if op not in OPCODES:
                return error("Illegal opcode", line_no, loc)

            def reg_ok():
                return (lx.get_num() and not isinstance(lx.num, float)
                        and 0 <= lx.num < NO_REGS)

            if op in OPS_RR:
                if not reg_ok():
                    return error("Bad first register", line_no, loc)
                a1 = lx.num
                if not lx.skip_ch(","):
                    return error("Missing comma", line_no, loc)
                if not reg_ok():
                    return error("Bad second register", line_no, loc)
                a2 = lx.num
                if not lx.skip_ch(","):
                    return error("Missing comma", line_no, loc)
                if not reg_ok():
                    return error("Bad third register", line_no, loc)
                a3 = lx.num
            else:
                if not reg_ok():
                    return error("Bad first register", line_no, loc)
                a1 = lx.num
                if not lx.skip_ch(","):
                    return error("Missing comma", line_no, loc)
                if not lx.get_num():
                    return error("Bad displacement", line_no, loc)
                a2 = lx.num
                if isinstance(a2, float) and op != "LDC":
                    return error("Bad displacement", line_no, loc)
                if not lx.skip_ch("(") and not lx.skip_ch(","):
                    return error("Missing LParen", line_no, loc)
                if not reg_ok():
                    return error("Bad second register", line_no, loc)
                a3 = lx.num
            self.iMem[loc] = (op, a1, a2, a3)
            self.cargadas.add(loc)
        return []

    # ── comando c ─────────────────────────────────────────────
    def reiniciar(self):
        self.reg = [0] * NO_REGS
        self.dMem = [0] * DADDR_SIZE
        self.dMem[0] = DADDR_SIZE - 1
        self.salidas = []
        self.pasos = 0
        self.esperando_reg = None
        self.ultima_salida = None
        self.estado = Estado.OKAY

    @property
    def pc(self):
        return self.reg[PC_REG]

    # ── stepTM ────────────────────────────────────────────────
    def paso(self) -> str:
        if self.esperando_reg is not None:
            return Estado.NECESITA_ENTRADA
        if self.pasos >= self.max_pasos:
            return Estado.LIMITE
        pc = self.reg[PC_REG]
        if not isinstance(pc, int) or pc < 0 or pc >= IADDR_SIZE:
            return Estado.IMEM_ERR
        self.reg[PC_REG] = pc + 1
        self.pasos += 1
        op, a1, a2, a3 = self.iMem[pc]
        reg = self.reg
        r = s = t = m = 0
        if op in OPS_RR:
            r, s, t = a1, a2, a3
        else:
            r, s = a1, a3
            if op == "LDC":
                m = a2
            else:
                m = a2 + reg[s]
            if op in OPS_RM:
                if isinstance(m, float):
                    if m != int(m):
                        return Estado.DMEM_ERR
                    m = int(m)
                if m < 0 or m >= DADDR_SIZE:
                    return Estado.DMEM_ERR

        if op == "HALT":
            return Estado.HALT
        if op == "IN":
            self.esperando_reg = r
            return Estado.NECESITA_ENTRADA
        if op == "OUT":
            self.ultima_salida = reg[r]
            self.salidas.append(reg[r])
            return Estado.SALIDA
        if op == "ADD":
            reg[r] = reg[s] + reg[t]
        elif op == "SUB":
            reg[r] = reg[s] - reg[t]
        elif op == "MUL":
            reg[r] = reg[s] * reg[t]
        elif op == "DIV":
            if reg[t] == 0:
                return Estado.ZERODIVIDE
            if isinstance(reg[s], int) and isinstance(reg[t], int):
                reg[r] = _div_entera(reg[s], reg[t])
            else:
                reg[r] = reg[s] / reg[t]
        elif op == "LD":
            reg[r] = self.dMem[m]
        elif op == "ST":
            self.dMem[m] = reg[r]
        elif op == "LDA":
            reg[r] = m
        elif op == "LDC":
            reg[r] = a2
        elif op == "JLT":
            if reg[r] < 0: reg[PC_REG] = m
        elif op == "JLE":
            if reg[r] <= 0: reg[PC_REG] = m
        elif op == "JGT":
            if reg[r] > 0: reg[PC_REG] = m
        elif op == "JGE":
            if reg[r] >= 0: reg[PC_REG] = m
        elif op == "JEQ":
            if reg[r] == 0: reg[PC_REG] = m
        elif op == "JNE":
            if reg[r] != 0: reg[PC_REG] = m
        return Estado.OKAY

    @staticmethod
    def parsear_entrada(texto: str):
        """Valor numérico de una entrada de IN, o None si es ilegal."""
        lx = _Lector(texto.strip())
        if not lx.get_num() or not lx.at_eol():
            return None
        return lx.num

    def dar_entrada(self, texto: str) -> bool:
        """Responde a un IN pendiente. False si el valor es ilegal
        (la TM sigue esperando)."""
        if self.esperando_reg is None:
            return False
        v = self.parsear_entrada(texto)
        if v is None:
            return False
        self.reg[self.esperando_reg] = v
        self.esperando_reg = None
        return True

    # ── utilidades para la consola y el IDE ───────────────────
    def texto_instruccion(self, loc: int) -> str:
        """writeInstruction de tm.c."""
        t = f"{loc:5d}: "
        if 0 <= loc < IADDR_SIZE:
            op, a1, a2, a3 = self.iMem[loc]
            t += f"{op:>6s}{a1:3d},"
            if op in OPS_RR:
                t += f"{a2:1d},{a3:1d}"
            else:
                t += f"{fmt_operando(a2):>3s}({a3:1d})"
        return t

    def ejecutar(self, entradas=None, max_pasos=None):
        """Ejecuta hasta HALT o error, tomando las entradas de una lista.
        Devuelve (estado, salidas). Útil para pruebas."""
        entradas = list(entradas or [])
        if max_pasos is not None:
            self.max_pasos = max_pasos
        while True:
            st = self.paso()
            if st in (Estado.OKAY, Estado.SALIDA):
                continue
            if st == Estado.NECESITA_ENTRADA:
                if not entradas:
                    return "SIN_ENTRADA", self.salidas
                if not self.dar_entrada(str(entradas.pop(0))):
                    return "ENTRADA_ILEGAL", self.salidas
                continue
            self.estado = st
            return st, self.salidas


# ═══════════════════════════════════════════════════════════════
#  CONSOLA (doCommand de tm.c)
# ═══════════════════════════════════════════════════════════════
AYUDA = """
COMANDOS DE LA MAQUINA TM:
 h        Mostrar esta ayuda
 v        Ver codigo intermedio (.ci) generado por el compilador
 i b n    Ver n instrucciones TM desde la direccion b
 d b n    Ver n posiciones de memoria de datos desde b
 r        Ver el contenido de los registros
 s [n]    Ejecutar n instrucciones (por defecto 1)
 g        Ejecutar el programa hasta HALT
 t        Activar/desactivar rastreo de instrucciones
 p        Activar/desactivar contador de instrucciones
 c        Reiniciar registros y memoria de datos
 q        Salir del simulador

NOTA: el codigo intermedio lo produce el compilador, no la TM.
      El comando v muestra el archivo .ci del mismo programa.
"""


class ConsolaTM:
    """Intérprete de comandos de la TM. La E/S se hace con funciones
    inyectables para poder usarlo desde la terminal o desde el IDE."""

    def __init__(self, maquina: MaquinaTM, ruta_tm: str | None = None,
                 escribir=None, leer=None, texto_ci: str | None = None):
        self.m = maquina
        self.ruta_tm = ruta_tm
        self.texto_ci = texto_ci
        self.escribir = escribir or (lambda s: print(s, end="", flush=True))
        self.leer = leer or (lambda: input())
        self.traza = False
        self.contar = False
        self.iloc = 0
        self.dloc = 0

    def out(self, s=""):
        self.escribir(s + "\n")

    # --- comandos que no ejecutan ---
    def texto_registros(self) -> str:
        filas, linea = [], ""
        for i in range(NO_REGS):
            linea += f"{i:1d}: {fmt_operando(self.m.reg[i]):>4s}    "
            if i % 4 == 3:
                filas.append(linea.rstrip())
                linea = ""
        return "\n".join(filas)

    def ver_ci(self):
        if self.texto_ci is not None:
            self.out("\n======= CODIGO INTERMEDIO =======")
            self.escribir(self.texto_ci if self.texto_ci.endswith("\n")
                          else self.texto_ci + "\n")
            self.out("======= FIN DEL CODIGO INTERMEDIO =======\n")
            return
        if not self.ruta_tm:
            self.out("No hay archivo .ci asociado.")
            return
        ruta = os.path.splitext(self.ruta_tm)[0] + ".ci"
        if not os.path.isfile(ruta):
            self.out(f"\nNo se encontro el codigo intermedio: {ruta}")
            self.out("Primero genera los dos archivos con el compilador:")
            self.out("  python compilador.py --intermedio programa.txt\n")
            return
        self.out(f"\n======= CODIGO INTERMEDIO: {ruta} =======")
        with open(ruta, encoding="utf-8") as f:
            self.escribir(f.read())
        self.out("======= FIN DEL CODIGO INTERMEDIO =======\n")

    def comando(self, linea: str, pedir_entrada=None) -> bool:
        """Ejecuta un comando. Devuelve False con 'q'.
        pedir_entrada() se usa en la terminal para leer los IN; si es None
        se usa input()."""
        lx = _Lector(linea)
        if not lx.get_word():
            return True
        cmd = lx.word[0]
        m = self.m
        pasos = 0
        if cmd == "t":
            self.traza = not self.traza
            self.out("Tracing now " + ("on." if self.traza else "off."))
        elif cmd == "h":
            self.escribir(AYUDA + "\n")
        elif cmd == "v":
            self.ver_ci()
        elif cmd == "p":
            self.contar = not self.contar
            self.out("Printing instruction count now " +
                     ("on." if self.contar else "off."))
        elif cmd == "s":
            if lx.at_eol():
                pasos = 1
            elif lx.get_num():
                pasos = abs(int(lx.num))
            else:
                self.out("Step count?")
        elif cmd == "g":
            pasos = 1
        elif cmd == "r":
            self.out(self.texto_registros())
        elif cmd in ("i", "d"):
            cnt = 1
            if lx.get_num():
                if cmd == "i":
                    self.iloc = int(lx.num)
                else:
                    self.dloc = int(lx.num)
                if lx.get_num():
                    cnt = int(lx.num)
            if not lx.at_eol():
                self.out("Instruction locations?" if cmd == "i"
                         else "Data locations?")
            elif cmd == "i":
                while 0 <= self.iloc < IADDR_SIZE and cnt > 0:
                    self.out(m.texto_instruccion(self.iloc))
                    self.iloc += 1
                    cnt -= 1
            else:
                while 0 <= self.dloc < DADDR_SIZE and cnt > 0:
                    self.out(f"{self.dloc:5d}: {fmt_operando(m.dMem[self.dloc]):>5s}")
                    self.dloc += 1
                    cnt -= 1
        elif cmd == "c":
            self.iloc = self.dloc = 0
            m.reiniciar()
        elif cmd == "q":
            return False
        else:
            self.out(f"Command {cmd} unknown.")

        if pasos > 0:
            self._correr(cmd == "g", pasos, pedir_entrada)
        return True

    def _correr(self, hasta_halt, pasos, pedir_entrada):
        m = self.m
        contador = 0
        st = Estado.OKAY
        while True:
            if not hasta_halt and pasos <= 0:
                break
            if self.traza and m.esperando_reg is None:
                self.out(m.texto_instruccion(m.pc))
            st = m.paso()
            if st == Estado.NECESITA_ENTRADA:
                while True:
                    self.escribir("Ingrese un numero (IN): ")
                    try:
                        txt = (pedir_entrada or self.leer)()
                    except EOFError:
                        st = Estado.HALT
                        break
                    if m.dar_entrada(txt):
                        break
                    self.out("Illegal value")
                if st == Estado.HALT:
                    break
                st = Estado.OKAY
            elif st == Estado.SALIDA:
                self.out(f"Resultado del programa (OUT): {fmt_valor(m.ultima_salida)}")
                st = Estado.OKAY
            contador += 1
            if not hasta_halt:
                pasos -= 1
            if st != Estado.OKAY:
                break
        if hasta_halt and self.contar:
            self.out(f"Number of instructions executed = {contador}")
        self.out(MENSAJE_ESTADO.get(st, st))


def repl(ruta_tm: str, texto_tm: str | None = None, texto_ci: str | None = None,
         comandos_iniciales=()):
    m = MaquinaTM()
    if texto_tm is None:
        with open(ruta_tm, encoding="utf-8") as f:
            texto_tm = f.read()
    errores = m.cargar(texto_tm)
    if errores:
        for e in errores:
            print(e)
        return 1
    con = ConsolaTM(m, ruta_tm, texto_ci=texto_ci)
    print("Simulador TM listo. Escriba h para ver la ayuda.")
    for c in comandos_iniciales:
        if not con.comando(c):
            print("Fin de la simulacion TM.")
            return 0
    if comandos_iniciales:
        return 0
    while True:
        try:
            linea = input("Comando TM (h=ayuda): ")
        except EOFError:
            break
        if not con.comando(linea):
            break
    print("Fin de la simulacion TM.")
    return 0


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print(f"usage: python tm.py <filename>")
        return 1
    ruta = argv[0]
    if not os.path.splitext(os.path.basename(ruta))[1]:
        ruta += ".tm"
    if not os.path.isfile(ruta):
        print(f"file '{ruta}' not found")
        return 1
    return repl(ruta)


if __name__ == "__main__":
    sys.exit(main())
