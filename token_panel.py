
"""
token_panel.py — Panel visual de tokens
"""

import re
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QLabel, QFrame, QAbstractItemView, QPushButton,
    QScrollArea,
)
from PyQt6.QtGui import QColor, QFont, QBrush, QPalette
from PyQt6.QtCore import Qt


# ── Colores de badge por tipo de token ─────────────────────────
TOKEN_BADGE = {
    "RESERVADA":       ("#569cd6", "#0d2a42"),
    "IDENTIFICADOR":   ("#9cdcfe", "#0d2233"),
    "ENTERO":          ("#b5cea8", "#1a2b1a"),
    "REAL":            ("#4ec9b0", "#0d2622"),
    "CADENA":          ("#ce9178", "#2e1a12"),
    "CARACTER":        ("#d7a06a", "#2a1a0d"),
    "OP_ARITMETICO":   ("#dcdcaa", "#2a2a10"),
    "OP_RELACIONAL":   ("#d7ba7d", "#2a2310"),
    "OP_LOGICO":       ("#c586c0", "#261326"),
    "ASIGNACION":      ("#808080", "#1a1a1a"),
    "SIMBOLO":         ("#757575", "#1c1c1c"),
    "ERROR":           ("#f44747", "#2a0d0d"),
}

TOKEN_LABEL = {
    "RESERVADA":     "reservada",
    "IDENTIFICADOR": "identificador",
    "ENTERO":        "entero",
    "REAL":          "real",
    "CADENA":        "cadena",
    "CARACTER":      "carácter",
    "OP_ARITMETICO": "aritmético",
    "OP_RELACIONAL": "relacional",
    "OP_LOGICO":     "lógico",
    "ASIGNACION":    "asignación",
    "SIMBOLO":       "símbolo",
    "ERROR":         "error",
}

_RE_TOKEN = re.compile(
    r"^\s*([A-Z_]+)\s+"
    r"((?:'[^']*')|(?:\S+))\s+"
    r"(\d+)\s+"
    r"(\d+)\s*$"
)


def _parse_tokens(texto: str):
    resultado = []
    for line in texto.splitlines():
        m = _RE_TOKEN.match(line)
        if m:
            tipo  = m.group(1).strip()
            valor = m.group(2).strip().strip("'")
            lin   = int(m.group(3))
            col   = int(m.group(4))
            resultado.append((tipo, valor, lin, col))
    return resultado


# ── Chip de filtro clickeable ──────────────────────────────────
class FilterChip(QPushButton):
    def __init__(self, tipo, label, fg, bg, parent=None):
        super().__init__(parent)
        self.tipo    = tipo
        self._fg     = fg
        self._bg     = bg
        self._label  = label
        self._count  = 0
        self.setCheckable(True)
        self.setFixedHeight(22)
        self.setFont(QFont("Consolas", 7))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setText(f" {label} ")
        self._apply_style()

    def set_count(self, n):
        self._count = n
        # Muestra el conteo como badge numérico junto al label
        self.setText(f" {self._label}  {n} " if n > 0 else f" {self._label} ")
        self.setEnabled(n > 0)
        self._apply_style()

    def _apply_style(self):
        if not self.isEnabled():
            self.setStyleSheet(
                "QPushButton { color:#3a3a3a; background:#161616;"
                "border-radius:3px; padding:1px 5px;"
                "border:1px solid #252525; }")
            return

        if self.isChecked():
            # Activo: colores invertidos — fondo = color del token
            self.setStyleSheet(
                f"QPushButton {{ color:{self._bg}; background:{self._fg};"
                f"border-radius:3px; padding:1px 5px;"
                f"border:1px solid {self._fg}; font-weight:bold; }}"
                f"QPushButton:hover {{ background:{self._fg}cc; }}")
        else:
            # Inactivo: borde sutil, listo para activarse
            self.setStyleSheet(
                f"QPushButton {{ color:{self._fg}; background:{self._bg};"
                f"border-radius:3px; padding:1px 5px;"
                f"border:1px solid transparent; }}"
                f"QPushButton:hover {{ border:1px solid {self._fg}88; }}")

    def nextCheckState(self):
        self.setChecked(not self.isChecked())
        self._apply_style()


# ── Celda con badge ────────────────────────────────────────────
class BadgeItem(QTableWidgetItem):
    def __init__(self, text, fg, bg):
        super().__init__(text)
        self.setForeground(QBrush(QColor(fg)))
        self.setBackground(QBrush(QColor(bg)))
        self.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)


# ── Panel principal ────────────────────────────────────────────
class TokenPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._all_tokens: list = []
        self._active_filters: set = set()
        self._chips: dict[str, FilterChip] = {}
        self._build_ui()

    # ── UI ─────────────────────────────────────────────────────
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Barra superior — totales
        self._bar = QFrame()
        self._bar.setFixedHeight(30)
        bar_lay = QHBoxLayout(self._bar)
        bar_lay.setContentsMargins(12, 0, 12, 0)
        self._lbl_total   = QLabel("Sin análisis")
        self._lbl_visible = QLabel("")
        self._lbl_total.setFont(QFont("Consolas", 8))
        self._lbl_visible.setFont(QFont("Consolas", 8))
        bar_lay.addWidget(self._lbl_total)
        bar_lay.addStretch()
        bar_lay.addWidget(self._lbl_visible)
        root.addWidget(self._bar)

        # Tabla
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Tipo", "Valor", "Línea", "Col"])
        self.table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setMaximumSectionSize(220)
        self.table.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(
            3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setDefaultSectionSize(24)
        root.addWidget(self.table)

        # Barra de filtros — abajo con scroll horizontal
        self._filter_bar = QFrame()
        self._filter_bar.setFixedHeight(36)
        outer_lay = QHBoxLayout(self._filter_bar)
        outer_lay.setContentsMargins(0, 0, 0, 0)
        outer_lay.setSpacing(0)

        # Etiqueta "Filtrar:" fija a la izquierda
        self._lbl_filtrar = QLabel(" Filtrar: ")
        self._lbl_filtrar.setFont(QFont("Consolas", 7))
        self._lbl_filtrar.setFixedHeight(36)
        outer_lay.addWidget(self._lbl_filtrar)

        # Área scrollable con los chips
        scroll = QScrollArea()
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFixedHeight(36)
        scroll.setWidgetResizable(True)

        chips_widget = QWidget()
        chips_widget.setFixedHeight(30)
        chips_lay = QHBoxLayout(chips_widget)
        chips_lay.setContentsMargins(4, 0, 4, 0)
        chips_lay.setSpacing(4)

        for tipo, label in TOKEN_LABEL.items():
            fg, bg = TOKEN_BADGE[tipo]
            chip = FilterChip(tipo, label, fg, bg)
            chip.toggled.connect(self._on_filter_toggled)
            chips_lay.addWidget(chip)
            self._chips[tipo] = chip

        chips_lay.addStretch()
        scroll.setWidget(chips_widget)
        outer_lay.addWidget(scroll)

        # Botón limpiar fijo a la derecha
        self._btn_limpiar = QPushButton("✕")
        self._btn_limpiar.setFixedSize(28, 22)
        self._btn_limpiar.setFont(QFont("Consolas", 7))
        self._btn_limpiar.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_limpiar.setToolTip("Limpiar filtros")
        self._btn_limpiar.clicked.connect(self._limpiar_filtros)
        outer_lay.addWidget(self._btn_limpiar)

        root.addWidget(self._filter_bar)
        self._chips_widget = chips_widget
        self._scroll_chips = scroll
        self.refresh_theme()

    # ── Datos ──────────────────────────────────────────────────
    def cargar_texto(self, texto: str):
        self._all_tokens = _parse_tokens(texto)
        # Resetear filtros
        self._active_filters.clear()
        for chip in self._chips.values():
            chip.blockSignals(True)
            chip.setChecked(False)
            chip.blockSignals(False)
            chip._apply_style()
        # Actualizar conteos en chips
        conteo: dict[str, int] = {}
        for tipo, *_ in self._all_tokens:
            conteo[tipo] = conteo.get(tipo, 0) + 1
        for tipo, chip in self._chips.items():
            chip.set_count(conteo.get(tipo, 0))
        self._refrescar_tabla()

    def _on_filter_toggled(self, checked):
        chip = self.sender()
        if checked:
            self._active_filters.add(chip.tipo)
        else:
            self._active_filters.discard(chip.tipo)
        chip._apply_style()
        self._refrescar_tabla()

    def _limpiar_filtros(self):
        self._active_filters.clear()
        for chip in self._chips.values():
            chip.blockSignals(True)
            chip.setChecked(False)
            chip.blockSignals(False)
            chip._apply_style()
        self._refrescar_tabla()

    def _refrescar_tabla(self):
        visible = (
            [t for t in self._all_tokens if t[0] in self._active_filters]
            if self._active_filters else self._all_tokens
        )

        self.table.setRowCount(0)
        self.table.setRowCount(len(visible))
        font_val = QFont("Consolas", 9)

        for row, (tipo, valor, linea, col) in enumerate(visible):
            fg, bg = TOKEN_BADGE.get(tipo, ("#d4d4d4", "#2d2d30"))
            label  = TOKEN_LABEL.get(tipo, tipo.lower())

            badge = BadgeItem(f"  {label}  ", fg, bg)
            badge.setFont(QFont("Consolas", 8))
            self.table.setItem(row, 0, badge)

            val_item = QTableWidgetItem(valor)
            val_item.setFont(font_val)
            val_item.setForeground(QBrush(QColor(fg)))
            val_item.setFlags(
                Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            self.table.setItem(row, 1, val_item)

            for col_idx, val in enumerate((str(linea), str(col)), start=2):
                it = QTableWidgetItem(val)
                it.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                it.setFont(font_val)
                it.setFlags(
                    Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
                self.table.setItem(row, col_idx, it)

        total = len(self._all_tokens)
        n_vis = len(visible)
        self._lbl_total.setText(f"  {total} tokens totales")
        if self._active_filters:
            names = ", ".join(
                TOKEN_LABEL.get(t, t) for t in sorted(self._active_filters))
            self._lbl_visible.setText(f"mostrando {n_vis}  ·  {names}  ")
        else:
            self._lbl_visible.setText("mostrando todos  ")

    # ── Tema ───────────────────────────────────────────────────
    def refresh_theme(self):
        try:
            from ide import C
        except ImportError:
            C = {
                "bg": "#1e1e1e", "bg2": "#252526", "bg3": "#2d2d30",
                "fg": "#d4d4d4", "fg_dim": "#858585",
                "separator": "#333337", "selection": "#264f78",
                "active": "#007acc",
            }

        bg  = C.get("bg",        "#1e1e1e")
        bg2 = C.get("bg2",       "#252526")
        bg3 = C.get("bg3",       "#2d2d30")
        fg  = C.get("fg",        "#d4d4d4")
        fg2 = C.get("fg_dim",    "#858585")
        sep = C.get("separator", "#333337")
        sel = C.get("selection", "#264f78")
        act = C.get("active",    "#007acc")

        self._bar.setStyleSheet(
            f"background:{bg3}; border-bottom:1px solid {sep};")
        self._lbl_total.setStyleSheet(f"color:{act}; font-weight:bold;")
        self._lbl_visible.setStyleSheet(f"color:{fg2};")

        self._filter_bar.setStyleSheet(
            f"background:{bg2}; border-top:1px solid {sep};")
        self._lbl_filtrar.setStyleSheet(
            f"color:{fg2}; background:{bg2};")
        self._btn_limpiar.setStyleSheet(
            f"QPushButton {{ color:{fg2}; background:{bg2};"
            f"border:1px solid {sep}; border-radius:3px; }}"
            f"QPushButton:hover {{ color:{fg}; border-color:{fg2}; }}")
        # Scroll area y widget interno — mismo color de fondo
        if hasattr(self, "_scroll_chips"):
            self._scroll_chips.setStyleSheet(f"background:{bg2}; border:none;")
            self._scroll_chips.horizontalScrollBar().setStyleSheet(
                f"QScrollBar:horizontal {{ background:{bg2}; height:6px; border:none; }}"
                f"QScrollBar::handle:horizontal {{ background:{sep}; border-radius:3px; min-width:20px; }}"
                f"QScrollBar::handle:horizontal:hover {{ background:{fg2}; }}"
                f"QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width:0; }}")
            self._chips_widget.setStyleSheet(f"background:{bg2};")

        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {bg};
                alternate-background-color: {bg2};
                color: {fg};
                border: none;
                gridline-color: transparent;
                selection-background-color: {sel};
                font-family: Consolas;
            }}
            QTableWidget QHeaderView::section {{
                background-color: {bg3};
                color: {fg2};
                border: none;
                border-bottom: 2px solid {act};
                padding: 5px 10px;
                font-size: 8pt;
                font-weight: bold;
                letter-spacing: 1px;
            }}
            QHeaderView {{ background-color: {bg3}; }}
            QScrollBar:vertical {{
                background: {bg}; width: 8px; border: none;
            }}
            QScrollBar::handle:vertical {{
                background: {sep}; border-radius: 4px; min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{ background: {fg2}; }}
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{ height: 0; }}
        """)

        p = self.table.palette()
        p.setColor(QPalette.ColorRole.Base,          QColor(bg))
        p.setColor(QPalette.ColorRole.AlternateBase, QColor(bg2))
        p.setColor(QPalette.ColorRole.Text,          QColor(fg))
        p.setColor(QPalette.ColorRole.Highlight,     QColor(sel))
        self.table.setPalette(p)