"""
intermedio.py — Código intermedio de tres direcciones (.ci).

Port en Python de intermedio.c (extensión didáctica de la docente sobre el
compilador TINY). Se genera desde el mismo árbol validado que el .tm, en
paralelo; el .ci NO es entrada de la TM.

  * Expresiones en postorden: constantes e identificadores se devuelven tal
    cual; cada operador crea un temporal tN.
  * if:        if_false c goto L1 / then / (goto L2) / label L1 / else / label L2
  * do-until:  label L1 / cuerpo / if_false c goto L1
  * while:     label L1 / tN = cond / if_false tN goto L2 / cuerpo / goto L1 / label L2
"""


class _ContextoIR:
    def __init__(self):
        self.lineas: list[str] = []
        self.temporal = 0
        self.etiqueta = 0

    def emit(self, s):
        self.lineas.append(s)

    def nuevo_temp(self):
        self.temporal += 1
        return f"t{self.temporal}"

    def nueva_etiqueta(self):
        self.etiqueta += 1
        return f"L{self.etiqueta}"


def _expresion(ctx: _ContextoIR, n) -> str:
    k = n.tipo
    if k in ("entero", "real_lit", "booleano", "identificador"):
        res = n.valor
    elif k == "factor_par":
        res = _expresion(ctx, n.hijos[0])
    elif k == "negativo":
        a = _expresion(ctx, n.hijos[0])
        res = ctx.nuevo_temp()
        ctx.emit(f"{res} = - {a}")
    elif k in ("expresion", "termino", "expr_rel", "condicion", "potencia"):
        izq = _expresion(ctx, n.hijos[0])
        der = _expresion(ctx, n.hijos[1])
        res = ctx.nuevo_temp()
        ctx.emit(f"{res} = {izq} {n.valor} {der}")
    else:
        raise ValueError(f"Nodo inesperado en expresión: {k}")
    if getattr(n, "atrib", {}).get("conv"):
        t = ctx.nuevo_temp()
        ctx.emit(f"{t} = (float) {res}")
        res = t
    return res


def _sentencias(ctx: _ContextoIR, n):
    if n is None:
        return
    k = n.tipo
    if k == "declaracion":
        return
    if k == "cin_stmt":
        ctx.emit(f"read {n.id_nombre}")
    elif k == "cout_stmt":
        ctx.emit(f"write {_expresion(ctx, n.hijos[0])}")
    elif k == "asignacion":
        ctx.emit(f"{n.id_nombre} = {_expresion(ctx, n.hijos[0])}")
    elif k in ("incremento", "decremento"):
        # en el árbol anotado: hijo 'expresion'  id (+|-) 1
        ctx.emit(f"{n.id_nombre} = {_expresion(ctx, n.hijos[0])}")
    elif k == "if_stmt":
        cond = _expresion(ctx, n.hijos[0])
        then_b = next((h for h in n.hijos[1:] if h.tipo == "then_branch"), None)
        else_b = next((h for h in n.hijos[1:] if h.tipo == "else_branch"), None)
        et1 = ctx.nueva_etiqueta()
        ctx.emit(f"if_false {cond} goto {et1}")
        _sentencias(ctx, then_b)
        et2 = None
        if else_b is not None:
            et2 = ctx.nueva_etiqueta()
            ctx.emit(f"goto {et2}")
        ctx.emit(f"label {et1}")
        if else_b is not None:
            _sentencias(ctx, else_b)
            ctx.emit(f"label {et2}")
    elif k == "do_until_stmt":
        et1 = ctx.nueva_etiqueta()
        ctx.emit(f"label {et1}")
        _sentencias(ctx, n.hijos[0])
        cond = _expresion(ctx, n.hijos[1])
        ctx.emit(f"if_false {cond} goto {et1}")
    elif k == "while_stmt":
        et1 = ctx.nueva_etiqueta()
        et2 = ctx.nueva_etiqueta()
        ctx.emit(f"label {et1}")
        cond = _expresion(ctx, n.hijos[0])
        ctx.emit(f"if_false {cond} goto {et2}")
        _sentencias(ctx, n.hijos[1])
        ctx.emit(f"goto {et1}")
        ctx.emit(f"label {et2}")
    else:            # programa, lista_sentencias, then/else_branch
        for h in n.hijos:
            _sentencias(ctx, h)


ENCABEZADO = ("# CODIGO INTERMEDIO DE TRES DIRECCIONES\n"
              "# Generado desde el arbol anotado, en paralelo con el codigo TM.\n"
              "# Los temporales t1, t2... y etiquetas L1, L2... son simbolicos.\n\n")


def generar_codigo_intermedio(arbol_anotado) -> str:
    ctx = _ContextoIR()
    _sentencias(ctx, arbol_anotado)
    ctx.emit("halt")
    return ENCABEZADO + "\n".join(ctx.lineas) + "\n"
