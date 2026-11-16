"""
interprete_ast.py — Oráculo para pruebas (NO forma parte del compilador).

Ejecuta directamente el árbol anotado, sin pasar por la TM, con la misma
semántica del lenguaje:
  * int op int → int; la división entre enteros trunca hacia cero.
  * Si algún operando es float → float (el semántico marca 'conv').
  * Booleanos como 1/0 (así los imprime la TM).
  * '%' como en C;  a ^ b con b <= 0 → 1.
Sirve para comprobar que las salidas de la TM coinciden con las del árbol.
"""


class FaltaEntrada(Exception):
    pass


class LimitePasos(Exception):
    pass


def _div_trunc(a, b):
    q = abs(a) // abs(b)
    return q if (a >= 0) == (b >= 0) else -q


class Interprete:
    def __init__(self, tabla, entradas, max_pasos=5_000_000):
        self.tabla = tabla
        self.entradas = list(entradas)
        self.mem = {}
        self.salidas = []
        self.pasos = 0
        self.max_pasos = max_pasos

    def _tick(self):
        self.pasos += 1
        if self.pasos > self.max_pasos:
            raise LimitePasos()

    def _es_float(self, nombre):
        return self.tabla.buscar(nombre).tipo == "float"

    # ── sentencias ──
    def ejecutar(self, n):
        k = n.tipo
        self._tick()
        if k == "declaracion":
            return
        if k in ("asignacion", "incremento", "decremento"):
            self.mem[n.id_nombre] = self.expr(n.hijos[0])
        elif k == "cin_stmt":
            if not self.entradas:
                raise FaltaEntrada()
            v = self.entradas.pop(0)
            v = float(v) if self._es_float(n.id_nombre) else v
            self.mem[n.id_nombre] = v
        elif k == "cout_stmt":
            self.salidas.append(self.expr(n.hijos[0]))
        elif k == "if_stmt":
            then_b = next((h for h in n.hijos[1:] if h.tipo == "then_branch"), None)
            else_b = next((h for h in n.hijos[1:] if h.tipo == "else_branch"), None)
            if self.expr(n.hijos[0]) != 0:
                self.ejecutar(then_b)
            elif else_b is not None:
                self.ejecutar(else_b)
        elif k == "while_stmt":
            while self.expr(n.hijos[0]) != 0:
                self._tick()
                self.ejecutar(n.hijos[1])
        elif k == "do_until_stmt":
            while True:
                self._tick()
                self.ejecutar(n.hijos[0])
                if self.expr(n.hijos[1]) != 0:
                    break
        else:
            for h in n.hijos:
                self.ejecutar(h)

    # ── expresiones ──
    def expr(self, n):
        v = self._expr(n)
        if getattr(n, "atrib", {}).get("conv"):
            v = float(v)
        return v

    def _expr(self, n):
        k = n.tipo
        if k == "entero":
            return int(n.valor)
        if k == "real_lit":
            return float(n.valor)
        if k == "booleano":
            return 1 if n.valor == "true" else 0
        if k == "identificador":
            return self.mem.get(n.valor, 0)
        if k == "factor_par":
            return self.expr(n.hijos[0])
        if k == "negativo":
            return -self.expr(n.hijos[0])
        a = self.expr(n.hijos[0])
        b = self.expr(n.hijos[1])
        op = n.valor
        if op == "+": return a + b
        if op == "-": return a - b
        if op == "*": return a * b
        if op == "/":
            if b == 0:
                raise ZeroDivisionError()
            if isinstance(a, int) and isinstance(b, int):
                return _div_trunc(a, b)
            return a / b
        if op == "%":
            if b == 0:
                raise ZeroDivisionError()
            return a - _div_trunc(a, b) * b
        if op == "^":
            r = 1.0 if isinstance(a, float) else 1
            for _ in range(b):
                r = r * a
            return r
        if op == "<": return int(a < b)
        if op == "<=": return int(a <= b)
        if op == ">": return int(a > b)
        if op == ">=": return int(a >= b)
        if op == "==": return int(a == b)
        if op == "!=": return int(a != b)
        if op == "&&": return int(a != 0 and b != 0)
        if op == "||": return int(a != 0 or b != 0)
        raise ValueError(f"operador {op}")


def interpretar(anotado, tabla, entradas):
    it = Interprete(tabla, entradas)
    it.ejecutar(anotado)
    return it.salidas
