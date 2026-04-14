
from PyQt6.QtGui import (
    QSyntaxHighlighter, QTextCharFormat, QColor, QFont
)
from PyQt6.QtCore import QRegularExpression

# ═══════════════════════════════════════════════
#  PALETA DE COLORES POR CATEGORÍA
#  (Ajustables según el tema activo)
# ═══════════════════════════════════════════════
COLORS = {
    # Color 1 — Números
    "numero":       "#b5cea8",   # verde claro
    # Color 2 — Identificadores
    "identificador":"#9cdcfe",   # azul claro
    # Color 3 — Comentarios
    "comentario":   "#6a9955",   # verde opaco
    # Color 4 — Palabras reservadas
    "reservada":    "#569cd6",   # azul VS Code
    # Color 5 — Operadores aritméticos
    "op_arit":      "#d4d4d4",   # blanco suave
    # Color 6 — Operadores relacionales y lógicos
    "op_rel_log":   "#d7ba7d",   # dorado/naranja
    # Cadenas
    "cadena":       "#ce9178",   # salmón
    # Caracteres
    "caracter":     "#ce9178",
    # Asignación y símbolos
    "asignacion":   "#d4d4d4",
    "simbolo":      "#d4d4d4",
    # Errores
    "error":        "#f44747",   # rojo
}

PALABRAS_RESERVADAS = [
    "if", "else", "end", "do", "while",
    "switch", "case", "int", "float",
    "main", "cin", "cout"
]


def _fmt(color_hex, bold=False, italic=False):
    fmt = QTextCharFormat()
    fmt.setForeground(QColor(color_hex))
    if bold:
        fmt.setFontWeight(QFont.Weight.Bold)
    if italic:
        fmt.setFontItalic(True)
    return fmt


class LexicoHighlighter(QSyntaxHighlighter):
    """Resaltador de sintaxis léxico en tiempo real."""

    def __init__(self, document):
        super().__init__(document)
        self._rules = []
        self._build_rules()

        # Estado para comentarios multilínea
        self._ml_start = QRegularExpression(r"/\*")
        self._ml_end   = QRegularExpression(r"\*/")
        self._fmt_comment = _fmt(COLORS["comentario"], italic=True)

    def _build_rules(self):
        rules = []

        # ── Color 4: Palabras reservadas (antes que identificadores) ──
        fmt_res = _fmt(COLORS["reservada"], bold=True)
        for word in PALABRAS_RESERVADAS:
            pat = QRegularExpression(r'\b' + word + r'\b')
            rules.append((pat, fmt_res))

        # ── Color 1: Números reales (antes que enteros) ──
        fmt_num = _fmt(COLORS["numero"])
        rules.append((QRegularExpression(r'\b\d+\.\d+\b'), fmt_num))
        # Enteros
        rules.append((QRegularExpression(r'\b\d+\b'), fmt_num))

        # ── Color 5: Operadores aritméticos ──
        fmt_arit = _fmt(COLORS["op_arit"])
        rules.append((QRegularExpression(r'\+\+|--|[\+\-\*/%\^]'), fmt_arit))

        # ── Color 6: Operadores relacionales y lógicos ──
        fmt_rel = _fmt(COLORS["op_rel_log"])
        rules.append((QRegularExpression(r'&&|\|\||<=|>=|==|!=|[<>!]'), fmt_rel))

        # ── Asignación ──
        fmt_asig = _fmt(COLORS["asignacion"])
        rules.append((QRegularExpression(r'(?<![=!<>])=(?!=)'), fmt_asig))

        # ── Cadenas de texto ──
        fmt_str = _fmt(COLORS["cadena"])
        rules.append((QRegularExpression(r'"[^"\\]*(?:\\.[^"\\]*)*"'), fmt_str))

        # ── Caracteres ──
        fmt_char = _fmt(COLORS["caracter"])
        rules.append((QRegularExpression(r"'[^'\\]?(?:\\.[^']*)?'"), fmt_char))

        # ── Color 2: Identificadores ──
        fmt_id = _fmt(COLORS["identificador"])
        rules.append((QRegularExpression(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b'), fmt_id))

        # ── Color 3: Comentario de una línea ──
        fmt_cm = _fmt(COLORS["comentario"], italic=True)
        rules.append((QRegularExpression(r'//[^\n]*'), fmt_cm))

        self._rules = rules

    def highlightBlock(self, text):
        # Aplicar reglas de una sola línea
        for pattern, fmt in self._rules:
            it = pattern.globalMatch(text)
            while it.hasNext():
                m = it.next()
                self.setFormat(m.capturedStart(), m.capturedLength(), fmt)

        # ── Comentarios multilínea (estado 1 = dentro de /* ... */) ──
        self.setCurrentBlockState(0)

        start = 0
        if self.previousBlockState() != 1:
            m = self._ml_start.match(text)
            if not m.hasMatch():
                return
            start = m.capturedStart()

        while True:
            m_end = self._ml_end.match(text, start)
            if m_end.hasMatch():
                length = m_end.capturedEnd() - start
                self.setFormat(start, length, self._fmt_comment)
                start = m_end.capturedEnd()
                m_start = self._ml_start.match(text, start)
                if not m_start.hasMatch():
                    self.setCurrentBlockState(0)
                    break
                start = m_start.capturedStart()
            else:
                self.setCurrentBlockState(1)
                self.setFormat(start, len(text) - start, self._fmt_comment)
                break

    def update_theme(self, theme_colors: dict):
        """Permite actualizar los colores cuando cambia el tema del IDE."""
        global COLORS
        mapping = {
            "numero":       theme_colors.get("numero",       COLORS["numero"]),
            "identificador":theme_colors.get("identificador",COLORS["identificador"]),
            "comentario":   theme_colors.get("comentario",   COLORS["comentario"]),
            "reservada":    theme_colors.get("reservada",    COLORS["reservada"]),
            "op_arit":      theme_colors.get("op_arit",      COLORS["op_arit"]),
            "op_rel_log":   theme_colors.get("op_rel_log",   COLORS["op_rel_log"]),
            "cadena":       theme_colors.get("cadena",       COLORS["cadena"]),
            "caracter":     theme_colors.get("caracter",     COLORS["caracter"]),
        }
        COLORS.update(mapping)
        self._rules.clear()
        self._build_rules()
        self._fmt_comment = _fmt(COLORS["comentario"], italic=True)
        self.rehighlight()