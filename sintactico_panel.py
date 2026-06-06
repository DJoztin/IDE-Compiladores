"""
sintactico_panel.py — Panel visual del árbol sintáctico (QTreeWidget colapsable)
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
    QLabel, QFrame, QPushButton, QSizePolicy,
)
from PyQt6.QtGui import QColor, QFont, QBrush, QIcon, QPixmap
from PyQt6.QtCore import Qt


# ─── Colores por tipo de nodo ───────────────────────────────
_NODE_COLORS = {
    # Nodos internos (gramática)
    "programa":      "#569cd6",
    "bloque":        "#9cdcfe",
    "declaraciones": "#4ec9b0",
    "declaracion":   "#4ec9b0",
    "lista_ids":     "#4ec9b0",
    "sentencias":    "#d4d4d4",
    "asignacion":    "#dcdcaa",
    "if":            "#c586c0",
    "do_while":      "#ce9178",
    "while":         "#ce9178",
    "cin":           "#b5cea8",
    "cout":          "#b5cea8",
    "condicion":     "#d7ba7d",
    "expresion":     "#d4d4d4",
    "termino":       "#d4d4d4",
    "factor":        "#d4d4d4",
    "cuerpo_do":     "#ce9178",
    # Hojas: palabras reservadas
    "main":   "#569cd6",
    "int":    "#569cd6",
    "real":   "#569cd6",
    "if_kw":  "#c586c0",
    "else":   "#c586c0",
    "end":    "#c586c0",
    "then":   "#c586c0",
    "do":     "#ce9178",
    "while_kw": "#ce9178",
    "until":  "#ce9178",
    "cin_kw": "#b5cea8",
    "cout_kw":"#b5cea8",
    # Literales
    "_id":   "#9cdcfe",
    "_num":  "#b5cea8",
    "_op":   "#d7ba7d",
    "_sym":  "#757575",
    "_asig": "#808080",
}

_RESERVED = {
    "main","int","real","if","else","end","then","do","while","until","cin","cout",
    "switch","case","float",
}

_ARIT_OPS = {"+","-","*","/","%","^","++","--"}
_REL_OPS  = {"<",">","<=",">=","==","!="}
_LOG_OPS  = {"&&","||","!"}
_SYMBOLS  = {"{","}","(",")",",",";",":","[","]"}


def _color_hoja(token) -> str:
    if token is None:
        return "#d4d4d4"
    v = token.valor
    t = token.tipo
    if v in _RESERVED or t == "RESERVADA":
        return "#569cd6"
    if t in ("ENTERO", "REAL"):
        return "#b5cea8"
    if t == "IDENTIFICADOR":
        return "#9cdcfe"
    if t == "OP_ARITMETICO":
        return "#d4d4d4"
    if t in ("OP_RELACIONAL", "OP_LOGICO"):
        return "#d7ba7d"
    if t == "ASIGNACION":
        return "#808080"
    if t == "SIMBOLO":
        return "#757575"
    return "#d4d4d4"


def _color_nodo_interno(etiqueta: str) -> str:
    return _NODE_COLORS.get(etiqueta, "#d4d4d4")


def _make_item(etiqueta: str, token=None, es_hoja=False) -> QTreeWidgetItem:
    item = QTreeWidgetItem()
    if es_hoja and token is not None:
        display = f'"{token.valor}"  ·  {token.tipo}  (L{token.linea}:C{token.columna})'
        color   = _color_hoja(token)
    else:
        display = etiqueta
        color   = _color_nodo_interno(etiqueta)

    item.setText(0, display)
    item.setForeground(0, QBrush(QColor(color)))
    font = QFont("Consolas", 9 if es_hoja else 10)
    if not es_hoja:
        font.setBold(True)
    item.setFont(0, font)
    return item


def _construir_arbol(nodo, parent_item: QTreeWidgetItem):
    """Recursivamente convierte NodoArbol → QTreeWidgetItem."""
    from sintactico import NodoArbol  # import local para evitar circularidad
    es_hoja = (nodo.token is not None) and not nodo.hijos
    item = _make_item(nodo.etiqueta, nodo.token, es_hoja=es_hoja)
    parent_item.addChild(item)
    for hijo in nodo.hijos:
        _construir_arbol(hijo, item)
    return item


# ─── Panel principal ────────────────────────────────────────
class SintacticoPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── barra superior ──
        bar = QFrame()
        bar.setFixedHeight(32)
        bar_lay = QHBoxLayout(bar)
        bar_lay.setContentsMargins(10, 0, 10, 0)
        bar_lay.setSpacing(6)

        self._lbl_info = QLabel("Sin análisis")
        self._lbl_info.setFont(QFont("Consolas", 8))
        bar_lay.addWidget(self._lbl_info)
        bar_lay.addStretch()

        btn_exp = QPushButton("⊞ Expandir todo")
        btn_col = QPushButton("⊟ Colapsar todo")
        for b in (btn_exp, btn_col):
            b.setFont(QFont("Consolas", 8))
            b.setFixedHeight(22)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_exp.clicked.connect(self._expandir_todo)
        btn_col.clicked.connect(self._colapsar_todo)
        bar_lay.addWidget(btn_exp)
        bar_lay.addWidget(btn_col)

        self._btn_exp = btn_exp
        self._btn_col = btn_col
        root.addWidget(bar)
        self._bar = bar

        # ── árbol ──
        self.tree = QTreeWidget()
        self.tree.setColumnCount(1)
        self.tree.setHeaderHidden(True)
        self.tree.setAnimated(True)
        self.tree.setIndentation(18)
        self.tree.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        root.addWidget(self.tree)

        self.refresh_theme()

    # ── datos ───────────────────────────────────────────────
    def cargar_arbol(self, arbol, n_errores: int = 0):
        """arbol: NodoArbol raíz devuelta por el parser."""
        self.tree.clear()
        if arbol is None:
            self._lbl_info.setText("No se generó árbol")
            return

        # Construir items
        from sintactico import NodoArbol
        raiz_item = QTreeWidgetItem(self.tree, ["programa"])
        raiz_item.setFont(0, QFont("Consolas", 11, QFont.Weight.Bold))
        raiz_item.setForeground(0, QBrush(QColor("#007acc")))

        # arbol.hijos[0] es el nodo 'programa' interno — bajamos sus hijos
        for hijo in arbol.hijos:
            _construir_arbol(hijo, raiz_item)

        self.tree.expandAll()

        total_nodos = self._contar_nodos(raiz_item)
        estado = f"  {total_nodos} nodos"
        if n_errores:
            estado += f"  ·  {n_errores} error(es) sintáctico(s)"
            self._lbl_info.setStyleSheet("color:#f44747; font-weight:bold;")
        else:
            self._lbl_info.setStyleSheet("color:#4ec9b0; font-weight:bold;")
        self._lbl_info.setText(estado)

    def _contar_nodos(self, item: QTreeWidgetItem) -> int:
        total = 1
        for i in range(item.childCount()):
            total += self._contar_nodos(item.child(i))
        return total

    def cargar_texto(self, texto: str):
        """Compatibilidad con la interfaz de make_output."""
        # Ignorado — usamos cargar_arbol directamente
        pass

    # ── expandir/colapsar ───────────────────────────────────
    def _expandir_todo(self):
        self.tree.expandAll()

    def _colapsar_todo(self):
        self.tree.collapseAll()
        # Mantener raíz visible
        if self.tree.topLevelItemCount():
            self.tree.topLevelItem(0).setExpanded(True)

    # ── tema ─────────────────────────────────────────────────
    def refresh_theme(self):
        try:
            from ide_compilador import C
        except ImportError:
            C = {
                "bg": "#1e1e1e", "bg2": "#252526", "bg3": "#2d2d30",
                "fg": "#d4d4d4", "fg_dim": "#858585",
                "separator": "#333337", "active": "#007acc",
            }

        bg  = C.get("bg",        "#1e1e1e")
        bg2 = C.get("bg2",       "#252526")
        bg3 = C.get("bg3",       "#2d2d30")
        fg  = C.get("fg",        "#d4d4d4")
        fg2 = C.get("fg_dim",    "#858585")
        sep = C.get("separator", "#333337")
        act = C.get("active",    "#007acc")

        self._bar.setStyleSheet(
            f"background:{bg3}; border-bottom:1px solid {sep};")
        self._lbl_info.setStyleSheet(f"color:{act};")

        for b in (self._btn_exp, self._btn_col):
            b.setStyleSheet(
                f"QPushButton {{ color:{fg2}; background:{bg2};"
                f"border:1px solid {sep}; border-radius:3px; padding:1px 8px; }}"
                f"QPushButton:hover {{ color:{fg}; border-color:{fg2}; }}")

        self.tree.setStyleSheet(f"""
            QTreeWidget {{
                background-color: {bg};
                color: {fg};
                border: none;
                font-family: Consolas;
            }}
            QTreeWidget::item {{
                padding: 2px 4px;
                border: none;
            }}
            QTreeWidget::item:hover {{
                background-color: {bg2};
            }}
            QTreeWidget::item:selected {{
                background-color: {C.get('selection','#264f78')};
            }}
            QTreeWidget::branch {{
                background: {bg};
            }}
            QTreeWidget::branch:has-siblings:!adjoins-item {{
                border-image: none;
            }}
            QScrollBar:vertical {{
                background: {bg}; width: 8px; border: none;
            }}
            QScrollBar::handle:vertical {{
                background: {sep}; border-radius: 4px; min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{ background: {fg2}; }}
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{ height: 0; }}
            QScrollBar:horizontal {{
                background: {bg}; height: 8px; border: none;
            }}
            QScrollBar::handle:horizontal {{
                background: {sep}; border-radius: 4px; min-width: 20px;
            }}
            QScrollBar::handle:horizontal:hover {{ background: {fg2}; }}
            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal {{ width: 0; }}
        """)
