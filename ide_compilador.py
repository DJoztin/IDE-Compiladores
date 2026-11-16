# -*- coding: utf-8 -*-
from highlighter import LexicoHighlighter
from token_panel import TokenPanel

import sys, os, subprocess, tempfile
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QSplitter,
    QTabWidget, QTextEdit, QPlainTextEdit, QLabel,
    QToolBar, QStatusBar, QFileDialog, QMessageBox,
    QTableWidget, QHeaderView, QVBoxLayout, QHBoxLayout,
    QFrame, QTreeWidget, QTreeWidgetItem, QDockWidget,
    QPushButton, QAbstractItemView, QMenu, QComboBox,
    QDialog, QDialogButtonBox, QLineEdit, QCheckBox, QStackedWidget,
    QTableWidgetItem,
)
from PyQt6.QtGui import (
    QAction, QFont, QColor, QPainter, QTextFormat,
    QFontMetrics, QKeySequence, QPalette, QIcon, QPixmap, QPen,
)
from PyQt6.QtCore import Qt, QSize, QRect, pyqtSignal, QTimer

# ══════════════════════════════════════════════════════
#  TEMAS
# ══════════════════════════════════════════════════════
THEMES = {
    "VS Dark": {
        "bg": "#1e1e1e", "bg2": "#252526", "bg3": "#2d2d30",
        "editor": "#1e1e1e", "line_hl": "#2a2d2e",
        "gutter_bg": "#1e1e1e", "gutter_fg": "#858585",
        "tab_active": "#1e1e1e", "tab_inactive": "#2d2d2d",
        "tab_border": "#007acc", "fg": "#d4d4d4", "fg_dim": "#858585",
        "selection": "#264f78", "border": "#3f3f46",
        "separator": "#333337", "hover": "#3e3e40",
        "active": "#007acc", "statusbar": "#007acc",
        "green": "#4ec9b0", "red": "#f44747",
        "orange": "#d7ba7d", "terminal_bg": "#0c0c0c",
        "tree_bg": "#252526",
    },
    "Light": {
        "bg": "#ffffff", "bg2": "#f3f3f3", "bg3": "#dddddd",
        "editor": "#ffffff", "line_hl": "#e8e8e8",
        "gutter_bg": "#f3f3f3", "gutter_fg": "#999999",
        "tab_active": "#ffffff", "tab_inactive": "#ececec",
        "tab_border": "#007acc", "fg": "#1e1e1e", "fg_dim": "#717171",
        "selection": "#add6ff", "border": "#c8c8c8",
        "separator": "#d4d4d4", "hover": "#e8e8e8",
        "active": "#007acc", "statusbar": "#007acc",
        "green": "#008000", "red": "#cc0000",
        "orange": "#795e26", "terminal_bg": "#1e1e1e",
        "tree_bg": "#f3f3f3",
    },
    "Monokai": {
        "bg": "#272822", "bg2": "#1e1f1c", "bg3": "#333228",
        "editor": "#272822", "line_hl": "#3e3d32",
        "gutter_bg": "#272822", "gutter_fg": "#75715e",
        "tab_active": "#272822", "tab_inactive": "#1e1f1c",
        "tab_border": "#a6e22e", "fg": "#f8f8f2", "fg_dim": "#75715e",
        "selection": "#49483e", "border": "#49483e",
        "separator": "#3e3d32", "hover": "#3e3d32",
        "active": "#a6e22e", "statusbar": "#75715e",
        "green": "#a6e22e", "red": "#f92672",
        "orange": "#fd971f", "terminal_bg": "#1e1f1c",
        "tree_bg": "#1e1f1c",
    },
    "Dracula": {
        "bg": "#282a36", "bg2": "#21222c", "bg3": "#343746",
        "editor": "#282a36", "line_hl": "#44475a",
        "gutter_bg": "#282a36", "gutter_fg": "#6272a4",
        "tab_active": "#282a36", "tab_inactive": "#21222c",
        "tab_border": "#bd93f9", "fg": "#f8f8f2", "fg_dim": "#6272a4",
        "selection": "#44475a", "border": "#44475a",
        "separator": "#44475a", "hover": "#44475a",
        "active": "#bd93f9", "statusbar": "#bd93f9",
        "green": "#50fa7b", "red": "#ff5555",
        "orange": "#ffb86c", "terminal_bg": "#21222c",
        "tree_bg": "#21222c",
    },
    "Solarized": {
        "bg": "#002b36", "bg2": "#073642", "bg3": "#094553",
        "editor": "#002b36", "line_hl": "#073642",
        "gutter_bg": "#002b36", "gutter_fg": "#586e75",
        "tab_active": "#002b36", "tab_inactive": "#073642",
        "tab_border": "#268bd2", "fg": "#839496", "fg_dim": "#586e75",
        "selection": "#073642", "border": "#094553",
        "separator": "#094553", "hover": "#094553",
        "active": "#268bd2", "statusbar": "#268bd2",
        "green": "#859900", "red": "#dc322f",
        "orange": "#cb4b16", "terminal_bg": "#073642",
        "tree_bg": "#073642",
    },
    "Nord": {
        "bg": "#2e3440", "bg2": "#3b4252", "bg3": "#434c5e",
        "editor": "#2e3440", "line_hl": "#3b4252",
        "gutter_bg": "#2e3440", "gutter_fg": "#4c566a",
        "tab_active": "#2e3440", "tab_inactive": "#3b4252",
        "tab_border": "#88c0d0", "fg": "#d8dee9", "fg_dim": "#4c566a",
        "selection": "#434c5e", "border": "#434c5e",
        "separator": "#434c5e", "hover": "#434c5e",
        "active": "#88c0d0", "statusbar": "#5e81ac",
        "green": "#a3be8c", "red": "#bf616a",
        "orange": "#d08770", "terminal_bg": "#3b4252",
        "tree_bg": "#3b4252",
    },
}

C = dict(THEMES["VS Dark"])


def build_stylesheet(t):
    return f"""
* {{ font-family: 'Segoe UI', Arial; font-size: 9pt; }}
QMainWindow {{ background-color: {t['bg']}; }}
QMainWindow::separator {{ background-color: {t['separator']}; width:4px; height:4px; }}
QWidget {{ background-color: {t['bg']}; color: {t['fg']}; }}
QMenuBar {{
    background-color: {t['bg3']}; color: {t['fg']};
    border-bottom: 1px solid {t['separator']}; padding: 2px 0;
}}
QMenuBar::item {{ padding: 4px 10px; background: transparent; }}
QMenuBar::item:selected {{ background-color: {t['active']}; color: white; }}
QMenu {{
    background-color: {t['bg2']}; color: {t['fg']};
    border: 1px solid {t['border']}; padding: 4px 0;
}}
QMenu::item {{ padding: 5px 28px 5px 20px; }}
QMenu::item:selected {{ background-color: {t['active']}; color: white; }}
QMenu::separator {{ height:1px; background:{t['separator']}; margin:3px 0; }}
QToolBar {{
    background-color: {t['bg2']};
    border-bottom: 1px solid {t['separator']};
    spacing: 1px; padding: 3px 8px;
}}
QToolBar::separator {{ background-color:{t['border']}; width:1px; margin:4px 6px; }}
QToolButton {{
    background: transparent; color: {t['fg_dim']};
    border: 1px solid transparent; border-radius: 2px; padding: 4px 12px;
}}
QToolButton:hover {{
    background-color: {t['hover']}; color: {t['fg']};
    border-color: {t['border']};
}}
QToolButton:pressed {{ background-color: {t['active']}; color: white; }}
QTabWidget::pane {{ border: none; background-color: {t['bg']}; }}
QTabBar {{ background-color: {t['tab_inactive']}; }}
QTabBar::tab {{
    background-color: {t['tab_inactive']}; color: {t['fg_dim']};
    padding: 6px 16px; border: none;
    border-right: 1px solid {t['separator']}; min-width: 80px;
}}
QTabBar::tab:selected {{
    background-color: {t['tab_active']}; color: {t['fg']};
    border-top: 2px solid {t['tab_border']};
}}
QTabBar::tab:hover:!selected {{ background-color: {t['hover']}; color: {t['fg']}; }}
QTabBar::scroller {{ width: 20px; }}
QTabBar QToolButton {{
    background-color: {t['tab_inactive']}; border: none; color: {t['fg_dim']};
}}
QDockWidget {{ color: {t['fg']}; }}
QDockWidget::title {{
    background-color: {t['bg3']}; padding: 5px 8px;
    border-bottom: 1px solid {t['separator']};
    text-align: left; font-size: 8pt; font-weight: bold;
    letter-spacing: 1px; color: {t['fg_dim']};
}}
QDockWidget::close-button {{
    background: transparent; border: none; padding: 2px;
}}
QDockWidget::close-button:hover {{ background-color: {t['hover']}; }}
QTreeWidget {{
    background-color: {t['tree_bg']}; color: {t['fg']};
    border: none; outline: none;
}}
QTreeWidget::item {{ padding: 3px 4px; }}
QTreeWidget::item:hover {{ background-color: {t['hover']}; }}
QTreeWidget::item:selected {{ background-color: {t['active']}; color: white; }}
QTreeWidget::branch {{ background-color: {t['tree_bg']}; }}
QPlainTextEdit {{
    background-color: {t['editor']}; color: {t['fg']};
    border: none; font-family: 'Consolas','Courier New';
    font-size: 11pt; selection-background-color: {t['selection']};
}}
QTextEdit {{
    background-color: {t['bg']}; color: {t['fg']};
    border: none; font-family: 'Consolas','Courier New';
    font-size: 10pt; selection-background-color: {t['selection']};
}}
QTableWidget {{
    background-color: {t['bg']}; color: {t['fg']};
    gridline-color: {t['separator']}; border: none;
    font-family: 'Consolas'; font-size: 9pt;
    selection-background-color: {t['selection']};
    alternate-background-color: {t['bg2']};
}}
QTableWidget QHeaderView::section {{
    background-color: {t['bg3']}; color: {t['fg_dim']};
    border: none; border-right: 1px solid {t['separator']};
    border-bottom: 1px solid {t['separator']};
    padding: 4px 8px; font-size: 8pt; font-weight: bold;
}}
QHeaderView {{ background-color: {t['bg3']}; }}
QScrollBar:vertical {{
    background: {t['bg']}; width: 10px; border: none; margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {t['border']}; min-height: 24px; border-radius: 3px; margin: 1px;
}}
QScrollBar::handle:vertical:hover {{ background: {t['fg_dim']}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar:horizontal {{
    background: {t['bg']}; height: 10px; border: none;
}}
QScrollBar::handle:horizontal {{
    background: {t['border']}; min-width: 24px; border-radius: 3px; margin: 1px;
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}
QSplitter::handle {{ background-color: {t['separator']}; }}
QSplitter::handle:horizontal {{ width: 4px; }}
QSplitter::handle:vertical   {{ height: 4px; }}
QStatusBar {{
    background-color: {t['statusbar']}; color: white;
    font-size: 8pt; border-top: none;
}}
QStatusBar::item {{ border: none; }}
QLabel {{ color: {t['fg']}; background: transparent; }}
QFrame {{ background: transparent; }}
QPushButton {{
    background: transparent; color: {t['fg_dim']};
    border: none; padding: 2px 8px; border-radius: 2px;
}}
QPushButton:hover {{ background-color: {t['hover']}; color: {t['fg']}; }}
QComboBox {{
    background-color: {t['bg2']}; color: {t['fg']};
    border: 1px solid {t['border']}; border-radius: 2px;
    padding: 2px 8px; min-width: 110px;
}}
QComboBox:hover {{ border-color: {t['active']}; }}
QComboBox::drop-down {{ border: none; width: 20px; }}
QComboBox QAbstractItemView {{
    background-color: {t['bg2']}; color: {t['fg']};
    selection-background-color: {t['active']};
    border: 1px solid {t['border']};
}}
"""


# ══════════════════════════════════════════════════════
#  EDITOR CON NUMERACION DE LINEAS
# ══════════════════════════════════════════════════════
class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return QSize(self.editor._gutter_width(), 0)

    def paintEvent(self, event):
        self.editor._paint_gutter(event)

def limpiar_ruta(path):
    """Ruta absoluta con separadores normalizados (C:/a/b -> C:\\a\\b en Windows).
    QFileDialog devuelve '/' y os.path usa '\\'; sin esto un mismo archivo
    parecía distinto y se abría dos veces."""
    return os.path.normpath(os.path.abspath(path)) if path else path


def clave_ruta(path):
    """Clave para comparar rutas: además ignora mayúsculas en Windows."""
    return os.path.normcase(limpiar_ruta(path)) if path else path


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)
MODULOS_COMPILADOR = ("compilador", "code_tm", "cgen", "intermedio", "tm")


def cargar_compilador():
    """Importa compilador.py (y sus módulos de generación: code_tm, cgen,
    intermedio, tm) desde su ruta real, recargándolos cada vez.
    Funciona igual con 'python ide_compilador.py' y con el .exe."""
    import importlib.util
    compiler_path = resource_path("compilador.py")
    if not os.path.isfile(compiler_path):
        return None, (f"[Error] No se encontró 'compilador.py' en:\n"
                      f"{os.path.dirname(compiler_path)}")
    carpeta = os.path.dirname(compiler_path)
    if carpeta not in sys.path:
        sys.path.insert(0, carpeta)
    for nombre in MODULOS_COMPILADOR:
        sys.modules.pop(nombre, None)
    spec = importlib.util.spec_from_file_location("compilador", compiler_path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["compilador"] = mod
    spec.loader.exec_module(mod)
    return mod, None


def autoprueba(fuente, salida, entradas):
    """Ide.exe --autoprueba prog.txt resultado.txt [entradas...]
    Compila con el mismo cargador que F8/F9, ejecuta el .tm en la TM y
    escribe el resultado en 'salida'. Sirve para probar el .exe."""
    lineas = []
    try:
        mod, err = cargar_compilador()
        if err:
            raise RuntimeError(err)
        import tm as tm_mod
        with open(fuente, encoding="utf-8") as f:
            r = mod.compilar(f.read(), None)
        lineas.append(f"ok={r.ok} instrucciones={len(r.instrucciones)}")
        if r.ok:
            m = tm_mod.MaquinaTM()
            errs = m.cargar(r.codigo_tm)
            st, sal = m.ejecutar(entradas)
            lineas.append(f"carga={errs} estado={st}")
            lineas.append("OUT " + " ".join(tm_mod.fmt_valor(v) for v in sal))
    except Exception as ex:
        import traceback
        lineas.append("ERROR " + traceback.format_exc())
    with open(salida, "w", encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")


class CodeEditor(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._gutter = LineNumberArea(self)
        self._error_sels: list = []
        self.blockCountChanged.connect(self._update_gutter_width)
        self.updateRequest.connect(self._update_gutter_area)
        self.cursorPositionChanged.connect(self._highlight_line)
        self._update_gutter_width(0)
        self._highlight_line()

        font = QFont("Consolas", 11)
        font.setFixedPitch(True)
        self.setFont(font)
        self.setTabStopDistance(
            QFontMetrics(font).horizontalAdvance(' ') * 4)
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.setAcceptDrops(True)
        self._apply_palette()

    def _apply_palette(self):
        p = self.palette()
        p.setColor(QPalette.ColorRole.Base,            QColor(C['editor']))
        p.setColor(QPalette.ColorRole.Text,            QColor(C['fg']))
        p.setColor(QPalette.ColorRole.Highlight,       QColor(C['selection']))
        p.setColor(QPalette.ColorRole.HighlightedText, QColor(C['fg']))
        self.setPalette(p)

    def refresh_theme(self):
        self._apply_palette()
        self._highlight_line()
        self._gutter.update()

    def _gutter_width(self):
        digits = max(3, len(str(max(1, self.blockCount()))))
        return QFontMetrics(QFont("Consolas", 9)).horizontalAdvance('9') * digits + 18

    def _update_gutter_width(self, _=None):
        self.setViewportMargins(self._gutter_width(), 0, 0, 0)

    def _update_gutter_area(self, rect, dy):
        if dy:
            self._gutter.scroll(0, dy)
        else:
            self._gutter.update(
                0, rect.y(), self._gutter.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self._update_gutter_width()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        cr = self.contentsRect()
        self._gutter.setGeometry(
            QRect(cr.left(), cr.top(), self._gutter_width(), cr.height()))

    def set_error_lines(self, errores: list):
        """Marca las líneas con errores con fondo rojo en el editor."""
        self._error_sels = []
        doc = self.document()
        for e in errores:
            linea = getattr(e, 'linea', 0) - 1
            if linea < 0:
                continue
            block = doc.findBlockByLineNumber(linea)
            if not block.isValid():
                continue
            sel = QTextEdit.ExtraSelection()
            sel.format.setBackground(QColor("#4a1a1a"))
            sel.format.setProperty(
                QTextFormat.Property.FullWidthSelection, True)
            c = self.textCursor()
            c.setPosition(block.position())
            c.clearSelection()
            sel.cursor = c
            self._error_sels.append(sel)
        self._highlight_line()

    def clear_error_lines(self):
        self._error_sels = []
        self._highlight_line()

    def _highlight_line(self):
        sel = QTextEdit.ExtraSelection()
        sel.format.setBackground(QColor(C['line_hl']))
        sel.format.setProperty(
            QTextFormat.Property.FullWidthSelection, True)
        sel.cursor = self.textCursor()
        sel.cursor.clearSelection()
        self.setExtraSelections([sel] + self._error_sels)

    def _paint_gutter(self, event):
        p = QPainter(self._gutter)
        p.fillRect(event.rect(), QColor(C['gutter_bg']))
        p.setPen(QColor(C['separator']))
        p.drawLine(self._gutter.width() - 1, event.rect().top(),
                   self._gutter.width() - 1, event.rect().bottom())
        block  = self.firstVisibleBlock()
        num    = block.blockNumber()
        top    = int(self.blockBoundingGeometry(block)
                     .translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())
        cur    = self.textCursor().blockNumber()
        p.setFont(QFont("Consolas", 9))
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                clr = QColor("#c6c6c6") if num == cur \
                      else QColor(C['gutter_fg'])
                p.setPen(clr)
                p.drawText(0, top, self._gutter.width() - 6,
                           int(self.blockBoundingRect(block).height()),
                           Qt.AlignmentFlag.AlignRight, str(num + 1))
            block  = block.next()
            top    = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            num   += 1

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            e.acceptProposedAction()
        else:
            super().dragEnterEvent(e)

    def dropEvent(self, e):
        if e.mimeData().hasUrls():
            path = e.mimeData().urls()[0].toLocalFile()
            w = self.window()
            if hasattr(w, '_open_file'):
                w._open_file(path)
        else:
            super().dropEvent(e)


# ══════════════════════════════════════════════════════
#  EXPLORADOR DE ARCHIVOS
# ══════════════════════════════════════════════════════
class FileExplorer(QWidget):
    file_opened = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        self._bar = QFrame()
        self._bar.setFixedHeight(28)
        bl = QHBoxLayout(self._bar)
        bl.setContentsMargins(8, 0, 6, 0)
        self.lbl_folder = QLabel("SIN CARPETA")
        bl.addWidget(self.lbl_folder)
        bl.addStretch()
        btn = QPushButton("📂")
        btn.setFixedSize(22, 22)
        btn.setToolTip("Abrir carpeta")
        btn.clicked.connect(self._open_folder)
        bl.addWidget(btn)
        lay.addWidget(self._bar)

        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setDragEnabled(True)
        self.tree.setAcceptDrops(False)
        self.tree.setDragDropMode(QAbstractItemView.DragDropMode.DragOnly)
        self.tree.itemDoubleClicked.connect(self._on_double_click)
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self._ctx_menu)
        lay.addWidget(self.tree)
        self.root_path = None
        self._refresh_styles()

    def _refresh_styles(self):
        self._bar.setStyleSheet(
            f"background:{C['bg2']}; border-bottom:1px solid {C['separator']};")
        self.lbl_folder.setStyleSheet(
            f"color:{C['fg_dim']}; font-size:8pt; font-weight:bold;")
        self.tree.setStyleSheet(
            f"QTreeWidget {{ background:{C['tree_bg']}; color:{C['fg']}; border:none; outline:none; }}"
            f"QTreeWidget::item {{ padding:3px 4px; }}"
            f"QTreeWidget::item:hover {{ background:{C['hover']}; }}"
            f"QTreeWidget::item:selected {{ background:{C['active']}; color:white; }}"
            f"QTreeWidget::branch {{ background:{C['tree_bg']}; }}")

    def refresh_theme(self):
        self._refresh_styles()

    def _open_folder(self):
        f = QFileDialog.getExistingDirectory(self, "Abrir carpeta")
        if f:
            self.load_folder(f)

    def load_folder(self, path):
        path = limpiar_ruta(path)
        self.root_path = path
        self.tree.clear()
        self.lbl_folder.setText((os.path.basename(path) or path).upper())
        self._populate(self.tree.invisibleRootItem(), path)
        self.tree.expandToDepth(1)

    def _populate(self, parent, path):
        try:
            entries = sorted(os.scandir(path),
                             key=lambda e: (not e.is_dir(), e.name.lower()))
        except PermissionError:
            return
        for e in entries:
            if e.name.startswith('.'):
                continue
            item = QTreeWidgetItem([e.name])
            item.setData(0, Qt.ItemDataRole.UserRole, e.path)
            item.setIcon(0, self._icon(e))
            if e.is_dir():
                self._populate(item, e.path)
            parent.addChild(item)

    def _icon(self, entry):
        color = "#dcb67a" if entry.is_dir() else {
            ".py": "#4ec9b0", ".c": "#86c691", ".txt": "#d4d4d4",
            ".java": "#f0a500", ".pas": "#569cd6",
            ".cl": "#ce9178",  ".lng": "#c586c0",
        }.get(os.path.splitext(entry.name)[1].lower(), "#858585")
        px = QPixmap(14, 14)
        px.fill(QColor(color))
        return QIcon(px)

    def _on_double_click(self, item, _):
        path = item.data(0, Qt.ItemDataRole.UserRole)
        if path and os.path.isfile(path):
            self.file_opened.emit(path)

    def _ctx_menu(self, pos):
        item = self.tree.itemAt(pos)
        if not item:
            return
        path = item.data(0, Qt.ItemDataRole.UserRole)
        m = QMenu(self)
        if os.path.isfile(path):
            m.addAction("Abrir", lambda: self.file_opened.emit(path))
        m.exec(self.tree.viewport().mapToGlobal(pos))

    def refresh(self):
        if self.root_path:
            self.load_folder(self.root_path)


# ══════════════════════════════════════════════════════
#  HELPER: output panel con color inicial correcto
# ══════════════════════════════════════════════════════
def make_output(color_key="fg", bg_key="bg"):
    t = QTextEdit()
    t.setReadOnly(True)
    t.setFont(QFont("Consolas", 10))
    # Guardar las claves para poder refrescar con el tema
    t._color_key = color_key
    t._bg_key    = bg_key
    _apply_output_style(t)
    return t


def _apply_output_style(widget):
    bg    = C.get(widget._bg_key,    C['bg'])
    color = C.get(widget._color_key, C['fg'])
    widget.setStyleSheet(
        f"background:{bg}; color:{color}; border:none;"
        f"font-family:Consolas; font-size:10pt;")
    # Tambien aplicar via palette para que cargue bien desde el inicio
    p = widget.palette()
    p.setColor(QPalette.ColorRole.Base,            QColor(bg))
    p.setColor(QPalette.ColorRole.Text,            QColor(color))
    p.setColor(QPalette.ColorRole.Window,          QColor(bg))
    p.setColor(QPalette.ColorRole.WindowText,      QColor(color))
    widget.setPalette(p)


# ══════════════════════════════════════════════════════
#  ÁRBOL SINTÁCTICO — PANEL
# ══════════════════════════════════════════════════════
_TREE_NODE_COLOR = {
    "programa":        "#4ec9b0",
    "lista_sentencias":"#569cd6",
    "declaracion":     "#569cd6",
    "tipo":            "#569cd6",
    "lista_ids":       "#9cdcfe",
    "asignacion":      "#dcdcaa",
    "incremento":      "#dcdcaa",
    "decremento":      "#dcdcaa",
    "if_stmt":         "#c586c0",
    "then_branch":     "#c586c0",
    "else_branch":     "#c586c0",
    "do_until_stmt":   "#c586c0",
    "while_stmt":      "#c586c0",
    "cin_stmt":        "#9cdcfe",
    "cout_stmt":       "#9cdcfe",
    "condicion":       "#d7ba7d",
    "expr_rel":        "#d7ba7d",
    "expresion":       "#d4d4d4",
    "termino":         "#b0b0b0",
    "potencia":        "#ce9178",
    "factor_par":      "#b0b0b0",
    "negativo":        "#dcdcaa",
    "reservada":       "#569cd6",
    "identificador":   "#9cdcfe",
    "entero":          "#b5cea8",
    "real_lit":        "#4ec9b0",
    "booleano":        "#569cd6",
    "op_aritmetico":   "#d4d4d4",
    "op_relacional":   "#d7ba7d",
    "op_logico":       "#c586c0",
    "operador":        "#d4d4d4",
    "simbolo":         "#606060",
    "error":           "#f44747",
}

class BranchTree(QTreeWidget):
    """QTreeWidget que dibuja las ramas del árbol (├── └── │) con
    indentación por profundidad, conservando expandir/colapsar.
    El recuadro [+]/[−] de cada nodo con hijos se puede clicar."""

    INDENT = 22

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setIndentation(self.INDENT)
        self.setRootIsDecorated(True)
        self.setUniformRowHeights(True)
        self.setVerticalScrollMode(
            QAbstractItemView.ScrollMode.ScrollPerPixel)

    @staticmethod
    def _tiene_siguiente(tree, it):
        p = it.parent()
        if p is None:
            return tree.indexOfTopLevelItem(it) < tree.topLevelItemCount() - 1
        return p.indexOfChild(it) < p.childCount() - 1

    def drawBranches(self, painter, rect, index):
        item = self.itemFromIndex(index)
        if item is None:
            return super().drawBranches(painter, rect, index)

        ind = self.indentation()
        h = max(1, rect.height())
        painter.save()

        # Fondo: respeta las filas alternadas del resto de la fila
        bg = C['tree_bg']
        if self.alternatingRowColors():
            fila = (rect.top() + self.verticalScrollBar().value()) // h
            if fila % 2:
                bg = C['bg2']
        painter.fillRect(rect, QColor(bg))

        pen = QPen(QColor(C['fg_dim']))
        pen.setWidth(1)
        painter.setPen(pen)

        # cadena: [item, padre, abuelo, ..., raíz]
        cadena = []
        it = item
        while it is not None:
            cadena.append(it)
            it = it.parent()

        derecha = rect.right() + 1
        mid_y = rect.top() + h // 2

        def centro_x(k):  # columna de la rama del nivel k (0 = el propio nodo)
            return derecha - (k + 1) * ind + ind // 2

        # Líneas verticales "│" de los ancestros que aún tienen hermanos abajo
        for k in range(1, len(cadena)):
            anc = cadena[k]
            if anc.parent() is None and self.topLevelItemCount() == 1:
                continue
            if self._tiene_siguiente(self, anc):
                x = centro_x(k)
                painter.drawLine(x, rect.top(), x, rect.bottom())

        # Conector del propio nodo: "├──" o "└──"
        x = centro_x(0)
        es_raiz_unica = item.parent() is None and self.topLevelItemCount() == 1
        if not es_raiz_unica:
            painter.drawLine(x, rect.top(), x, mid_y)
            if self._tiene_siguiente(self, item):
                painter.drawLine(x, mid_y, x, rect.bottom())
        painter.drawLine(x, mid_y, derecha - 2, mid_y)

        # Recuadro [+]/[−] si tiene hijos
        if item.childCount() > 0:
            s = 9
            caja = QRect(x - s // 2, mid_y - s // 2, s, s)
            painter.fillRect(caja, QColor(bg))
            painter.setPen(QPen(QColor(C['fg'])))
            painter.drawRect(caja)
            painter.drawLine(caja.left() + 2, mid_y, caja.right() - 2, mid_y)
            if not item.isExpanded():
                painter.drawLine(x, caja.top() + 2, x, caja.bottom() - 2)

        painter.restore()


def arbol_a_texto(tree: QTreeWidget) -> str:
    """Representación en texto del árbol con ramas (para exportar / copiar)."""
    lineas = []

    def etiqueta(it):
        txt = it.text(0)
        if it.text(1):
            txt += f"  '{it.text(1)}'"
        if it.columnCount() > 2 and it.text(2):
            txt += f"  [L{it.text(2)}]"
        if it.columnCount() > 3 and it.text(3):
            txt += f"   ⟨ {it.text(3)} ⟩"
        return txt

    def rec(it, prefijo, ultimo, es_raiz):
        if es_raiz:
            lineas.append(etiqueta(it))
            nuevo = ""
        else:
            lineas.append(prefijo + ("└── " if ultimo else "├── ") + etiqueta(it))
            nuevo = prefijo + ("    " if ultimo else "│   ")
        n = it.childCount()
        for i in range(n):
            rec(it.child(i), nuevo, i == n - 1, False)

    for i in range(tree.topLevelItemCount()):
        rec(tree.topLevelItem(i), "", True, True)
    return "\n".join(lineas)


class SyntaxTreePanel(QWidget):
    """Panel con árbol colapsable. Con `con_atributos=True` agrega la columna
    de anotaciones semánticas (árbol anotado)."""

    def __init__(self, parent=None, titulo="Árbol Sintáctico",
                 con_atributos=False, archivo_txt="arbol_sintactico.txt"):
        super().__init__(parent)
        self._titulo = titulo
        self._con_atrib = con_atributos
        self._archivo_txt = archivo_txt
        self.fmt_atrib = None          # función nodo -> texto de atributos
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        # ── barra de estado ──────────────────────────────────
        self._bar = QFrame()
        self._bar.setFixedHeight(32)
        bl = QHBoxLayout(self._bar)
        bl.setContentsMargins(8, 0, 8, 0)
        self._lbl_info = QLabel(titulo)
        bl.addWidget(self._lbl_info)
        bl.addStretch()
        btn_exp  = QPushButton("↕ Expandir todo")
        btn_col  = QPushButton("↔ Colapsar todo")
        btn_txt  = QPushButton("⎘ Exportar .txt")
        btn_win  = QPushButton("⊞ Ventana")
        btn_txt.setToolTip("Guardar el árbol con ramas como archivo de texto")
        for b in (btn_exp, btn_col, btn_txt, btn_win):
            b.setFixedHeight(22)
            bl.addWidget(b)
        lay.addWidget(self._bar)

        # ── árbol ────────────────────────────────────────────
        self.tree = BranchTree()
        self.tree.setHeaderLabels(self._headers())
        self.tree.setColumnWidth(0, 300)
        self.tree.setColumnWidth(1, 110 if con_atributos else 160)
        self.tree.setColumnWidth(2, 45)
        if con_atributos:
            self.tree.setColumnWidth(3, 420)
            self.tree.headerItem().setToolTip(
                3, "↑sintetizado: se calcula a partir de los hijos y sube al padre\n"
                   "↓heredado: viene del padre / contexto (dtype de la declaración)\n"
                   "(tabla): obtenido de la tabla de símbolos")
            self.tree.header().setStretchLastSection(True)
        else:
            self.tree.header().setStretchLastSection(False)
            self.tree.header().setSectionResizeMode(
                1, QHeaderView.ResizeMode.Stretch)
        self.tree.setAlternatingRowColors(True)
        lay.addWidget(self.tree)

        btn_exp.clicked.connect(self.tree.expandAll)
        btn_col.clicked.connect(self.tree.collapseAll)
        btn_win.clicked.connect(self._abrir_ventana)
        btn_txt.clicked.connect(self._exportar_txt)

        self._refresh_styles()

    # ── estilos ──────────────────────────────────────────────
    def _refresh_styles(self):
        self._bar.setStyleSheet(
            f"background:{C['bg3']}; border-bottom:1px solid {C['separator']};")
        self._lbl_info.setStyleSheet(
            f"color:{C['fg_dim']}; font-size:8pt; font-weight:bold;")
        self.tree.setStyleSheet(
            f"QTreeWidget {{ background:{C['tree_bg']}; color:{C['fg']};"
            f"  border:none; outline:none; alternate-background-color:{C['bg2']}; }}"
            f"QTreeWidget::item {{ padding:2px 4px; }}"
            f"QTreeWidget::item:hover {{ background:{C['hover']}; }}"
            f"QTreeWidget::item:selected {{ background:{C['active']}; color:white; }}"
            f"QTreeWidget::branch {{ background:{C['tree_bg']}; }}"
            f"QHeaderView::section {{ background:{C['bg3']}; color:{C['fg_dim']};"
            f"  border:none; border-right:1px solid {C['separator']};"
            f"  border-bottom:1px solid {C['separator']}; padding:4px 6px;"
            f"  font-size:8pt; font-weight:bold; }}")

    def refresh_theme(self):
        self._refresh_styles()

    def _headers(self):
        h = ["Nodo", "Valor", "Ln"]
        return h + ["Atributos semánticos"] if self._con_atrib else h

    # ── carga del árbol ──────────────────────────────────────
    def cargar_arbol(self, nodo_raiz, errores=None):
        self.tree.clear()
        if nodo_raiz:
            item = self._hacer_item(nodo_raiz)
            self.tree.addTopLevelItem(item)
            self.tree.expandAll()
        err_cnt = len(errores) if errores else 0
        if err_cnt:
            self._lbl_info.setText(
                f"{self._titulo}  —  {err_cnt} error(es)")
            self._lbl_info.setStyleSheet(
                f"color:{C['red']}; font-size:8pt; font-weight:bold;")
        else:
            self._lbl_info.setText(f"{self._titulo}  —  ✓ Sin errores")
            self._lbl_info.setStyleSheet(
                f"color:{C['green']}; font-size:8pt; font-weight:bold;")

    def _hacer_item(self, nodo) -> QTreeWidgetItem:
        tipo  = nodo.tipo
        valor = nodo.valor or ""
        linea = str(nodo.linea) if getattr(nodo, 'linea', 0) else ""
        cols  = [tipo, valor, linea]
        atrib = ""
        if self._con_atrib:
            atrib = self.fmt_atrib(nodo) if self.fmt_atrib else ""
            cols.append(atrib)
        item  = QTreeWidgetItem(cols)
        if atrib:
            if "✗" in atrib:
                c_at = C['red']
            elif "conv" in atrib:
                c_at = C['orange']
            else:
                c_at = C['green']
            item.setForeground(3, QColor(c_at))
            item.setToolTip(3, atrib)
        color = QColor(_TREE_NODE_COLOR.get(tipo, C['fg']))
        item.setForeground(0, color)
        if valor:
            item.setForeground(1, QColor(_TREE_NODE_COLOR.get(tipo, C['fg_dim'])))
        if linea:
            item.setForeground(2, QColor(C['fg_dim']))
            item.setTextAlignment(2, Qt.AlignmentFlag.AlignRight)
        for hijo in nodo.hijos:
            item.addChild(self._hacer_item(hijo))
        return item

    def mostrar_error(self, texto: str):
        self.tree.clear()
        self._lbl_info.setText(f"{self._titulo}  —  Error")
        self._lbl_info.setStyleSheet(
            f"color:{C['red']}; font-size:8pt; font-weight:bold;")
        root = QTreeWidgetItem(["ERROR", texto])
        root.setForeground(0, QColor("#f44747"))
        self.tree.addTopLevelItem(root)

    # ── exportar ─────────────────────────────────────────────
    def _exportar_txt(self):
        if self.tree.topLevelItemCount() == 0:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Exportar árbol", self._archivo_txt,
            "Texto (*.txt);;Todos (*.*)")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(arbol_a_texto(self.tree) + "\n")

    # ── ventana separada ─────────────────────────────────────
    def _abrir_ventana(self):
        if self.tree.topLevelItemCount() == 0:
            return
        dlg = QDialog(self)
        dlg.setWindowTitle(f"{self._titulo} — Vista ampliada")
        dlg.resize(900, 680)
        lay = QVBoxLayout(dlg)

        tree2 = BranchTree()
        tree2.setHeaderLabels(self._headers())
        tree2.setColumnWidth(0, 380)
        tree2.setColumnWidth(1, 200)
        tree2.setColumnWidth(2, 50)
        if self._con_atrib:
            tree2.setColumnWidth(1, 140)
            tree2.header().setStretchLastSection(True)
        else:
            tree2.header().setStretchLastSection(False)
            tree2.header().setSectionResizeMode(
                1, QHeaderView.ResizeMode.Stretch)
        tree2.setAlternatingRowColors(True)
        tree2.setStyleSheet(self.tree.styleSheet())
        _copiar = copiar_item

        for i in range(self.tree.topLevelItemCount()):
            tree2.addTopLevelItem(_copiar(self.tree.topLevelItem(i)))
        tree2.expandAll()

        bar = QHBoxLayout()
        b_exp = QPushButton("↕ Expandir todo")
        b_col = QPushButton("↔ Colapsar todo")
        b_exp.clicked.connect(tree2.expandAll)
        b_col.clicked.connect(tree2.collapseAll)
        bar.addWidget(b_exp); bar.addWidget(b_col); bar.addStretch()

        lay.addLayout(bar)
        lay.addWidget(tree2)
        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        btns.rejected.connect(dlg.reject)
        lay.addWidget(btns)
        dlg.exec()


def copiar_item(src_item):
    """Copia profunda de un QTreeWidgetItem (texto, colores y tooltips)."""
    n = src_item.columnCount()
    dst = QTreeWidgetItem([src_item.text(i) for i in range(n)])
    for i in range(n):
        dst.setForeground(i, src_item.foreground(i))
        if src_item.toolTip(i):
            dst.setToolTip(i, src_item.toolTip(i))
    for i in range(src_item.childCount()):
        dst.addChild(copiar_item(src_item.child(i)))
    return dst


# ══════════════════════════════════════════════════════
#  ANÁLISIS SEMÁNTICO — PANEL
# ══════════════════════════════════════════════════════
class SemanticPanel(QWidget):
    """AST original · AST anotado · Recorrido (bitácora) + comparar/exportar."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._res = None
        self._mod = None
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        self._bar = QFrame()
        self._bar.setFixedHeight(32)
        bl = QHBoxLayout(self._bar)
        bl.setContentsMargins(8, 0, 8, 0)
        self._lbl = QLabel("Análisis Semántico")
        bl.addWidget(self._lbl)
        bl.addStretch()
        b_cmp = QPushButton("⊞ Comparar AST")
        b_exp = QPushButton("⎘ Exportar evidencias")
        b_cmp.setToolTip("AST original y AST anotado lado a lado")
        b_exp.setToolTip("Guarda árbol, árbol anotado, tabla, recorrido y "
                         "errores como archivos .txt")
        for b in (b_cmp, b_exp):
            b.setFixedHeight(22)
            bl.addWidget(b)
        b_cmp.clicked.connect(self._comparar)
        b_exp.clicked.connect(self._exportar)
        lay.addWidget(self._bar)

        self.tabs = QTabWidget()
        self.ast_original = SyntaxTreePanel(
            titulo="AST original", archivo_txt="arbol_sintactico.txt")
        self.ast_anotado = SyntaxTreePanel(
            titulo="AST anotado", con_atributos=True,
            archivo_txt="arbol_anotado.txt")
        self.recorrido = make_output("fg", "bg")
        self.tabs.addTab(self.ast_anotado,  "AST anotado")
        self.tabs.addTab(self.ast_original, "AST original")
        self.tabs.addTab(self.recorrido,    "Recorrido")
        lay.addWidget(self.tabs)
        self._refresh_styles()

    def _refresh_styles(self):
        self._bar.setStyleSheet(
            f"background:{C['bg3']}; border-bottom:1px solid {C['separator']};")
        self._lbl.setStyleSheet(
            f"color:{C['fg_dim']}; font-size:8pt; font-weight:bold;")

    def refresh_theme(self):
        self._refresh_styles()
        self.ast_original.refresh_theme()
        self.ast_anotado.refresh_theme()
        _apply_output_style(self.recorrido)

    def cargar(self, res, mod):
        self._res, self._mod = res, mod
        self.ast_original.cargar_arbol(res.arbol, [])
        self.ast_anotado.fmt_atrib = mod.texto_atributos
        self.ast_anotado.cargar_arbol(res.anotado, res.errores_sem)
        self.recorrido.setPlainText(mod.formatear_bitacora(res.bitacora))
        n = len(res.errores_sem)
        self._lbl.setText(
            f"Análisis Semántico  —  {len(res.tabla)} símbolo(s), "
            + (f"{n} error(es)" if n else "✓ sin errores"))
        self._lbl.setStyleSheet(
            f"color:{C['red'] if n else C['green']}; font-size:8pt;"
            f" font-weight:bold;")
        self.tabs.setCurrentWidget(self.ast_anotado)

    def mostrar_error(self, texto):
        self._res = None
        self.ast_anotado.mostrar_error(texto)
        self.ast_original.mostrar_error(texto)
        self.recorrido.setPlainText(texto)
        self._lbl.setText("Análisis Semántico  —  no ejecutado")
        self._lbl.setStyleSheet(
            f"color:{C['red']}; font-size:8pt; font-weight:bold;")

    def _comparar(self):
        if not self._res:
            return
        dlg = QDialog(self)
        dlg.setWindowTitle("AST original  →  AST con anotaciones semánticas")
        dlg.resize(1500, 820)
        lay = QVBoxLayout(dlg)
        split = QSplitter(Qt.Orientation.Horizontal)
        arboles = []
        for titulo, panel in (("AST original", self.ast_original),
                              ("AST anotado", self.ast_anotado)):
            cont = QWidget()
            cl = QVBoxLayout(cont)
            cl.setContentsMargins(0, 0, 0, 0)
            lbl = QLabel(titulo)
            lbl.setStyleSheet(f"color:{C['fg_dim']}; font-weight:bold;"
                              f" padding:4px;")
            cl.addWidget(lbl)
            t = BranchTree()
            t.setHeaderLabels(panel._headers())
            t.setColumnWidth(0, 300)
            t.setColumnWidth(1, 110)
            t.setColumnWidth(2, 40)
            t.setAlternatingRowColors(True)
            t.setStyleSheet(panel.tree.styleSheet())
            for i in range(panel.tree.topLevelItemCount()):
                t.addTopLevelItem(copiar_item(panel.tree.topLevelItem(i)))
            t.expandAll()
            cl.addWidget(t)
            split.addWidget(cont)
            arboles.append(t)
        split.setSizes([600, 900])
        # expandir/colapsar sincronizado (misma forma de árbol)
        def _ruta(t, it):
            r = []
            while it is not None:
                p = it.parent()
                r.append(p.indexOfChild(it) if p else t.indexOfTopLevelItem(it))
                it = p
            return r[::-1]
        def _item(t, ruta):
            it = t.topLevelItem(ruta[0]) if ruta else None
            for i in ruta[1:]:
                if it is None:
                    return None
                it = it.child(i)
            return it
        def _sync(origen, destino, expandir):
            def f(it):
                d = _item(destino, _ruta(origen, it))
                if d is not None and d.isExpanded() != expandir:
                    d.setExpanded(expandir)
            return f
        a, b = arboles
        a.itemExpanded.connect(_sync(a, b, True))
        a.itemCollapsed.connect(_sync(a, b, False))
        b.itemExpanded.connect(_sync(b, a, True))
        b.itemCollapsed.connect(_sync(b, a, False))
        # scroll sincronizado
        a.verticalScrollBar().valueChanged.connect(b.verticalScrollBar().setValue)
        b.verticalScrollBar().valueChanged.connect(a.verticalScrollBar().setValue)
        lay.addWidget(split)
        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        btns.rejected.connect(dlg.reject)
        lay.addWidget(btns)
        dlg.exec()

    def _exportar(self):
        if not self._res:
            QMessageBox.information(self, "Exportar evidencias",
                                    "Primero ejecuta el análisis semántico.")
            return
        carpeta = QFileDialog.getExistingDirectory(
            self, "Carpeta donde guardar las evidencias")
        if not carpeta:
            return
        m, r = self._mod, self._res
        archivos = {
            "arbol_sintactico.txt": m.arbol_texto(r.arbol),
            "arbol_anotado.txt":    m.arbol_texto(r.anotado, con_atributos=True),
            "tabla_simbolos.txt":   m.formatear_tabla(r.tabla),
            "recorrido_semantico.txt": m.formatear_bitacora(r.bitacora),
            "errores_semanticos.txt":
                m.formatear_errores_sem(r.errores_sem) or "(sin errores semánticos)",
        }
        for nombre, contenido in archivos.items():
            with open(os.path.join(carpeta, nombre), "w",
                      encoding="utf-8") as f:
                f.write(contenido + "\n")
        QMessageBox.information(
            self, "Exportar evidencias",
            "Se guardaron:\n" + "\n".join(archivos) + f"\n\nen {carpeta}")


# ══════════════════════════════════════════════════════
#  CÓDIGO INTERMEDIO (.tm y .ci) — PANEL
# ══════════════════════════════════════════════════════
_TM_CATEGORIA = {
    "LD": "mem", "ST": "mem", "LDA": "mem", "LDC": "mem",
    "ADD": "arit", "SUB": "arit", "MUL": "arit", "DIV": "arit",
    "JLT": "salto", "JLE": "salto", "JGT": "salto", "JGE": "salto",
    "JEQ": "salto", "JNE": "salto",
    "IN": "es", "OUT": "es", "HALT": "halt",
}
_TM_COLOR = {"mem": "#569cd6", "arit": "#4ec9b0", "salto": "#c586c0",
             "es": "#d7ba7d", "halt": "#f44747"}


def _boton_barra(texto, tip=""):
    b = QPushButton(texto)
    b.setFixedHeight(22)
    if tip:
        b.setToolTip(tip)
    return b


class CodigoPanel(QWidget):
    """Muestra el código generado: .tm (tabla / archivo) y .ci."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._r = None
        self._fuente = ""
        self._fila_pc = {}
        self._pc_resaltado = None
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        self._bar = QFrame()
        self._bar.setFixedHeight(32)
        bl = QHBoxLayout(self._bar)
        bl.setContentsMargins(8, 0, 8, 0)
        self._lbl = QLabel("Código Intermedio — sin generar (F8)")
        bl.addWidget(self._lbl)
        bl.addStretch()
        self.b_tm = _boton_barra("💾 Guardar .tm", "Guardar el código TM en otro archivo")
        self.b_ci = _boton_barra("💾 Guardar .ci", "Guardar el código de tres direcciones")
        self.b_cp = _boton_barra("⎘ Copiar", "Copiar al portapapeles la vista actual")
        for b in (self.b_tm, self.b_ci, self.b_cp):
            bl.addWidget(b)
        self.b_tm.clicked.connect(lambda: self._guardar("tm"))
        self.b_ci.clicked.connect(lambda: self._guardar("ci"))
        self.b_cp.clicked.connect(self._copiar)
        lay.addWidget(self._bar)

        self._aviso = QLabel("")
        self._aviso.setWordWrap(True)
        self._aviso.hide()
        lay.addWidget(self._aviso)

        self.tabs = QTabWidget()
        # ── .tm ──
        tm_w = QWidget()
        tl = QVBoxLayout(tm_w)
        tl.setContentsMargins(0, 0, 0, 0)
        tl.setSpacing(0)
        vbar = QFrame()
        vbar.setFixedHeight(28)
        vl = QHBoxLayout(vbar)
        vl.setContentsMargins(6, 0, 6, 0)
        self.btn_tabla = QPushButton("Tabla")
        self.btn_archivo = QPushButton("Archivo")
        for b in (self.btn_tabla, self.btn_archivo):
            b.setCheckable(True)
            b.setFixedHeight(22)
            vl.addWidget(b)
        vl.addStretch()
        self._lbl_leyenda = QLabel("")
        vl.addWidget(self._lbl_leyenda)
        self._vbar = vbar
        tl.addWidget(vbar)

        self.stack = QStackedWidget()
        self.tabla = QTableWidget(0, 4)
        self.tabla.setHorizontalHeaderLabels(["Dir", "Instrucción", "Operandos", "Comentario"])
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabla.setAlternatingRowColors(True)
        hh = self.tabla.horizontalHeader()
        hh.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        hh.setStretchLastSection(True)
        self.tabla.setFont(QFont("Consolas", 10))
        self.tabla.verticalHeader().setDefaultSectionSize(21)
        self.archivo = make_output("fg", "bg")
        self.archivo.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.stack.addWidget(self.tabla)
        self.stack.addWidget(self.archivo)
        tl.addWidget(self.stack)
        self.btn_tabla.clicked.connect(lambda: self._vista(0))
        self.btn_archivo.clicked.connect(lambda: self._vista(1))
        self._vista(0)

        self.ci = make_output("fg", "bg")
        self.ci.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.tabs.addTab(tm_w, "Código TM (.tm)")
        self.tabs.addTab(self.ci, "Código intermedio de tres direcciones (.ci)")
        lay.addWidget(self.tabs)
        self._refresh_styles()
        self.limpiar()

    # ── estilo ──
    def _refresh_styles(self):
        self._bar.setStyleSheet(
            f"background:{C['bg3']}; border-bottom:1px solid {C['separator']};")
        self._vbar.setStyleSheet(f"background:{C['bg2']};")
        self._aviso.setStyleSheet(
            f"background:{C['orange']}; color:#1e1e1e; padding:4px 8px;"
            f" font-weight:bold;")
        self._color_lbl(self._lbl_color if hasattr(self, "_lbl_color") else "fg_dim")
        chk = (f"QPushButton {{ color:{C['fg_dim']}; border:1px solid {C['border']};"
               f" padding:1px 10px; }} QPushButton:checked {{ background:{C['active']};"
               f" color:white; }}")
        self.btn_tabla.setStyleSheet(chk)
        self.btn_archivo.setStyleSheet(chk)
        ley = "  ".join(f"<span style='color:{_TM_COLOR[k]}'>■</span> {t}" for k, t in
                        (("mem", "carga/almacén"), ("arit", "aritmética"),
                         ("salto", "saltos"), ("es", "E/S")))
        self._lbl_leyenda.setText(ley)
        self._lbl_leyenda.setStyleSheet(f"color:{C['fg_dim']}; font-size:8pt;")

    def _color_lbl(self, clave):
        self._lbl_color = clave
        self._lbl.setStyleSheet(f"color:{C[clave]}; font-size:8pt; font-weight:bold;")

    def refresh_theme(self):
        self._refresh_styles()
        _apply_output_style(self.archivo)
        _apply_output_style(self.ci)
        if self._r is not None:
            self._llenar_tabla()

    def _vista(self, i):
        self.stack.setCurrentIndex(i)
        self.btn_tabla.setChecked(i == 0)
        self.btn_archivo.setChecked(i == 1)

    # ── contenido ──
    def limpiar(self, mensaje="Código Intermedio — sin generar (F8)", error=False):
        self._r = None
        self._fila_pc = {}
        self._pc_resaltado = None
        self.tabla.setRowCount(0)
        self.archivo.setPlainText("")
        self.ci.setPlainText("")
        self._lbl.setText(mensaje)
        self._color_lbl("red" if error else "fg_dim")
        self._aviso.hide()
        for b in (self.b_tm, self.b_ci, self.b_cp):
            b.setEnabled(False)
        if error:
            self.archivo.setPlainText(mensaje)
            self.ci.setPlainText(mensaje)

    def cargar(self, r, nombre_fuente):
        import datetime
        self._r = r
        self._fuente = nombre_fuente
        self._llenar_tabla()
        self.archivo.setPlainText(r.codigo_tm)
        self.ci.setPlainText(r.codigo_ci)
        hora = datetime.datetime.now().strftime("%H:%M:%S")
        self._lbl.setText(f"{nombre_fuente}  ·  generado {hora}  ·  "
                          f"{len(r.instrucciones)} instrucciones TM")
        self._color_lbl("green")
        self._aviso.hide()
        self.tabla.setEnabled(True)
        for b in (self.b_tm, self.b_ci, self.b_cp):
            b.setEnabled(True)
        self.tabs.setCurrentIndex(0)

    @staticmethod
    def _operandos(ins):
        _loc, op, a1, a2, a3 = ins[:5]
        if op in ("HALT", "IN", "OUT", "ADD", "SUB", "MUL", "DIV"):
            return f"{a1},{a2},{a3}"
        d = repr(a2) if isinstance(a2, float) else str(a2)
        return f"{a1},{d}({a3})"

    def _llenar_tabla(self):
        t = self.tabla
        t.setRowCount(0)
        self._fila_pc = {}
        self._pc_resaltado = None
        for fila, ins in enumerate(self._r.instrucciones):
            loc, op = ins[0], ins[1]
            t.insertRow(fila)
            color = QColor(_TM_COLOR[_TM_CATEGORIA.get(op, "mem")])
            datos = [str(loc), op, self._operandos(ins), ins[5]]
            for c, d in enumerate(datos):
                it = QTableWidgetItem(d)
                if c == 0:
                    it.setTextAlignment(Qt.AlignmentFlag.AlignRight |
                                        Qt.AlignmentFlag.AlignVCenter)
                    it.setForeground(QColor(C['fg_dim']))
                elif c in (1, 2):
                    it.setForeground(color)
                    if c == 1:
                        f = it.font(); f.setBold(True); it.setFont(f)
                else:
                    it.setForeground(QColor(C['fg_dim']))
                t.setItem(fila, c, it)
            self._fila_pc[loc] = fila

    def marcar_desactualizado(self, si=True):
        if self._r is None:
            return
        if si:
            self._aviso.setText("⚠ desactualizado — el fuente cambió, vuelve a compilar (F8 / F9)")
            self._aviso.show()
            self.tabla.setEnabled(False)
        else:
            self._aviso.hide()
            self.tabla.setEnabled(True)

    def resaltar_pc(self, pc):
        """Resalta la fila de la instrucción que la TM va a ejecutar."""
        t = self.tabla
        if self._pc_resaltado is not None and self._pc_resaltado < t.rowCount():
            for c in range(t.columnCount()):
                it = t.item(self._pc_resaltado, c)
                if it:
                    it.setBackground(QColor(0, 0, 0, 0))
        self._pc_resaltado = None
        fila = self._fila_pc.get(pc)
        if fila is None:
            return
        for c in range(t.columnCount()):
            it = t.item(fila, c)
            if it:
                it.setBackground(QColor(C['selection']))
        self._pc_resaltado = fila
        t.scrollToItem(t.item(fila, 0))

    def _guardar(self, cual):
        if self._r is None:
            return
        base = os.path.splitext(self._fuente or "programa")[0]
        path, _ = QFileDialog.getSaveFileName(
            self, f"Guardar .{cual}", f"{base}.{cual}",
            f"Código {'TM' if cual == 'tm' else 'intermedio'} (*.{cual});;Todos (*.*)")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self._r.codigo_tm if cual == "tm" else self._r.codigo_ci)

    def _copiar(self):
        if self._r is None:
            return
        if self.tabs.currentIndex() == 1:
            txt = self._r.codigo_ci
        else:
            txt = self._r.codigo_tm
        QApplication.clipboard().setText(txt)


# ══════════════════════════════════════════════════════
#  MÁQUINA TM — PANEL (consola, registros, memoria)
# ══════════════════════════════════════════════════════
class TMPanel(QWidget):
    """Simulador TM integrado. Ejecuta por lotes con QTimer para no
    congelar la interfaz; cuando la TM pide IN se pausa hasta que el
    usuario escribe un valor."""

    ejecutar_pedido = pyqtSignal()       # F9: recompilar y ejecutar
    pc_cambiado = pyqtSignal(int)
    estado = pyqtSignal(str)

    LOTE = 20000          # pasos por tick
    LOTE_TRAZA = 300

    def __init__(self, parent=None):
        super().__init__(parent)
        self.tm = None                    # módulo tm
        self.m = None                     # MaquinaTM
        self.consola = None               # ConsolaTM (comandos h v i d r c)
        self._tabla_sim = None
        self._corriendo = False
        self._modo = None                 # 'g' o 's'
        self._pasos_rest = 0
        self._contador = 0
        self._esperando = False
        self._desactualizado = False
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._tick)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        split = QSplitter(Qt.Orientation.Horizontal)
        lay.addWidget(split)

        # ── izquierda: botones, consola, entrada ──
        izq = QWidget()
        il = QVBoxLayout(izq)
        il.setContentsMargins(0, 0, 0, 0)
        il.setSpacing(0)
        self._bar = QFrame()
        self._bar.setFixedHeight(32)
        bl = QHBoxLayout(self._bar)
        bl.setContentsMargins(6, 0, 6, 0)
        self.b_run = _boton_barra("▶ Ejecutar (g)", "Recompila el fuente actual y lo ejecuta (F9)")
        self.b_step = _boton_barra("Paso (s)", "Ejecuta una instrucción")
        self.b_reset = _boton_barra("Reiniciar (c)", "Reinicia registros y memoria")
        self.b_stop = _boton_barra("■ Detener", "Detiene la ejecución")
        for b in (self.b_run, self.b_step, self.b_reset, self.b_stop):
            bl.addWidget(b)
        self.chk_traza = QCheckBox("Rastreo (t)")
        self.chk_contar = QCheckBox("Contar instrucciones (p)")
        bl.addSpacing(10)
        bl.addWidget(self.chk_traza)
        bl.addWidget(self.chk_contar)
        bl.addStretch()
        self._lbl = QLabel("Máquina TM")
        bl.addWidget(self._lbl)
        il.addWidget(self._bar)

        self.out = QPlainTextEdit()
        self.out.setReadOnly(True)
        self.out.setMaximumBlockCount(20000)
        self.out.setFont(QFont("Consolas", 10))
        il.addWidget(self.out)

        ent = QFrame()
        el = QHBoxLayout(ent)
        el.setContentsMargins(6, 3, 6, 3)
        self._lbl_ent = QLabel("Comando TM (h=ayuda):")
        self.entrada = QLineEdit()
        self.entrada.setFont(QFont("Consolas", 10))
        self.entrada.returnPressed.connect(self._enter)
        el.addWidget(self._lbl_ent)
        el.addWidget(self.entrada)
        self._ent = ent
        il.addWidget(ent)
        split.addWidget(izq)

        # ── derecha: registros y memoria ──
        der = QWidget()
        dl = QVBoxLayout(der)
        dl.setContentsMargins(0, 0, 0, 0)
        dl.setSpacing(0)
        self._lbl_reg = QLabel("  REGISTROS")
        dl.addWidget(self._lbl_reg)
        self.t_reg = QTableWidget(8, 3)
        self.t_reg.setHorizontalHeaderLabels(["Reg", "Alias", "Valor"])
        self._lbl_mem = QLabel("  MEMORIA DE VARIABLES")
        self.t_mem = QTableWidget(0, 3)
        self.t_mem.setHorizontalHeaderLabels(["Nombre", "loc", "Valor"])
        for t in (self.t_reg, self.t_mem):
            t.verticalHeader().setVisible(False)
            t.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
            t.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
            t.horizontalHeader().setStretchLastSection(True)
            t.setAlternatingRowColors(True)
            t.verticalHeader().setDefaultSectionSize(20)
        self.t_reg.setFixedHeight(8 * 20 + 30)
        dl.addWidget(self.t_reg)
        dl.addWidget(self._lbl_mem)
        dl.addWidget(self.t_mem)
        split.addWidget(der)
        split.setSizes([680, 300])

        self.b_run.clicked.connect(self.ejecutar_pedido.emit)
        self.b_step.clicked.connect(lambda: self._iniciar("s", 1))
        self.b_reset.clicked.connect(self._reiniciar)
        self.b_stop.clicked.connect(self.detener)
        self.chk_traza.toggled.connect(self._sync_flags)
        self.chk_contar.toggled.connect(self._sync_flags)
        self._refresh_styles()
        self._actualizar_botones()
        self._escribir("Simulador TM: compila y ejecuta con F9 (o ▶ Ejecutar).", "dim")

    # ── estilo ──
    def _refresh_styles(self):
        self._bar.setStyleSheet(
            f"background:{C['bg3']}; border-bottom:1px solid {C['separator']};")
        self._ent.setStyleSheet(f"background:{C['bg2']};")
        self.out.setStyleSheet(
            f"background:{C['terminal_bg']}; color:{C['green']}; border:none;"
            f" font-family:Consolas; font-size:10pt;")
        estilo_ent = (f"background:{C['bg']}; color:{C['fg']};"
                      f" border:1px solid {C['border']}; padding:2px;")
        if self._esperando:
            estilo_ent = (f"background:{C['bg']}; color:{C['fg']};"
                          f" border:2px solid {C['orange']}; padding:2px;")
        self.entrada.setStyleSheet(estilo_ent)
        self._lbl_ent.setStyleSheet(
            f"color:{C['orange'] if self._esperando else C['fg_dim']}; font-weight:bold;")
        for l in (self._lbl_reg, self._lbl_mem):
            l.setStyleSheet(f"background:{C['bg3']}; color:{C['fg_dim']};"
                            f" font-size:8pt; font-weight:bold; padding:4px;")
        self._lbl.setStyleSheet(f"color:{C['fg_dim']}; font-size:8pt; font-weight:bold;")

    def refresh_theme(self):
        self._refresh_styles()

    # ── consola ──
    def _escribir(self, texto, tipo="normal"):
        import html
        color = {"normal": C['green'], "dim": C['fg_dim'], "err": C['red'],
                 "out": C['fg'], "in": C['orange'], "ok": C['active']}.get(tipo, C['green'])
        for linea in texto.split("\n"):
            peso = "bold" if tipo in ("out", "err") else "normal"
            self.out.appendHtml(
                f"<span style='color:{color}; font-weight:{peso};"
                f" white-space:pre'>{html.escape(linea) or '&nbsp;'}</span>")
        self.out.verticalScrollBar().setValue(self.out.verticalScrollBar().maximum())

    def limpiar(self, mensaje=""):
        self.detener(silencioso=True)
        self.m = None
        self.consola = None
        self._tabla_sim = None
        self.out.clear()
        self.t_mem.setRowCount(0)
        for i in range(8):
            for c in range(3):
                self.t_reg.setItem(i, c, QTableWidgetItem(""))
        if mensaje:
            self._escribir(mensaje, "err")
        self._desactualizado = False
        self._actualizar_botones()

    def cargar_programa(self, tm_mod, texto_tm, tabla, texto_ci, nombre):
        """Carga el texto del .tm recién generado (lo parsea la TM)."""
        self.detener(silencioso=True)
        self.tm = tm_mod
        self.m = tm_mod.MaquinaTM()
        errores = self.m.cargar(texto_tm)
        self._tabla_sim = tabla
        self.out.clear()
        self._desactualizado = False
        if errores:
            for e in errores:
                self._escribir(e, "err")
            self.m = None
            self._actualizar_botones()
            return False
        self.consola = tm_mod.ConsolaTM(self.m, None,
                                        escribir=lambda s: self._escribir(s.rstrip("\n")),
                                        texto_ci=texto_ci)
        self._sync_flags()
        self._escribir(f"Programa cargado: {nombre}  ({len(self.m.cargadas)} instrucciones)", "dim")
        self._escribir("Simulador TM listo. Escriba h para ver la ayuda.")
        self._actualizar_vistas()
        self._actualizar_botones()
        return True

    def marcar_desactualizado(self, si=True):
        if self.m is None or self._desactualizado == si:
            return
        self._desactualizado = si
        if si:
            self.detener(silencioso=True)
            self._escribir("⚠ desactualizado — el fuente cambió: vuelve a compilar (F9)", "in")
        self._actualizar_botones()

    def _actualizar_botones(self):
        hay = self.m is not None and not self._desactualizado
        self.b_step.setEnabled(hay and not self._corriendo and not self._esperando)
        self.b_reset.setEnabled(hay and not self._corriendo)
        self.b_stop.setEnabled(self._corriendo or self._esperando)
        self.b_run.setEnabled(not self._corriendo)

    def _sync_flags(self):
        if self.consola:
            self.consola.traza = self.chk_traza.isChecked()
            self.consola.contar = self.chk_contar.isChecked()

    # ── ejecución no bloqueante ──
    def ejecutar(self):
        """Comando g desde el inicio (registros y memoria limpios)."""
        if self.m is None:
            return
        self.m.reiniciar()
        self._iniciar("g", 0)

    def _iniciar(self, modo, pasos):
        if self.m is None:
            self._escribir("No hay programa cargado: presiona F9.", "err")
            return
        if self._desactualizado:
            self._escribir("El código está desactualizado: presiona F9 para recompilar.", "err")
            return
        if self._corriendo or self._esperando:
            return
        self._modo = modo
        self._pasos_rest = pasos
        self._contador = 0
        self._corriendo = True
        self._actualizar_botones()
        self.estado.emit("Ejecutando en la TM...")
        self._timer.start(0)

    def _tick(self):
        if not self._corriendo or self.m is None:
            return
        tm, m = self.tm, self.m
        E = tm.Estado
        lote = self.LOTE_TRAZA if self.chk_traza.isChecked() else self.LOTE
        for _ in range(lote):
            if self._modo == "s" and self._pasos_rest <= 0:
                self._fin(None)
                return
            if self.chk_traza.isChecked():
                self._escribir(m.texto_instruccion(m.pc), "dim")
            st = m.paso()
            self._contador += 1
            if self._modo == "s":
                self._pasos_rest -= 1
            if st == E.OKAY:
                continue
            if st == E.SALIDA:
                self._escribir(f"Resultado del programa (OUT): {tm.fmt_valor(m.ultima_salida)}", "out")
                continue
            if st == E.NECESITA_ENTRADA:
                self._pedir_entrada()
                return
            self._fin(st)
            return
        self._actualizar_vistas()
        self._timer.start(0)

    def _pedir_entrada(self):
        self._corriendo = False
        self._esperando = True
        self._escribir("Ingrese un numero (IN):", "in")
        self._lbl_ent.setText("Ingrese un numero (IN):")
        self._refresh_styles()
        self._actualizar_vistas()
        self._actualizar_botones()
        self.estado.emit("La TM espera una entrada (IN)")
        self.entrada.setFocus()

    def _fin(self, st):
        self._corriendo = False
        tm = self.tm
        if st is None:                       # terminó el lote de 's'
            self._escribir(tm.MENSAJE_ESTADO[tm.Estado.OKAY], "dim")
            self.estado.emit(f"Paso ejecutado (pc = {self.m.pc})")
        elif st == tm.Estado.HALT:
            if self.chk_contar.isChecked() and self._modo == "g":
                self._escribir(f"Number of instructions executed = {self._contador}", "dim")
            self._escribir(tm.MENSAJE_ESTADO[st], "ok")
            self.estado.emit(f"Ejecución finalizada (HALT), {self.m.pasos} instrucciones ejecutadas")
        else:
            loc = self.m.pc - 1
            self._escribir(f"{tm.MENSAJE_ESTADO.get(st, st)}  (instrucción {loc})", "err")
            self.estado.emit(f"Error en la TM: {tm.MENSAJE_ESTADO.get(st, st)}")
        self._actualizar_vistas()
        self._actualizar_botones()

    def detener(self, silencioso=False):
        estaba = self._corriendo or self._esperando
        self._timer.stop()
        self._corriendo = False
        if self._esperando:
            self._esperando = False
            self._lbl_ent.setText("Comando TM (h=ayuda):")
            self._refresh_styles()
        if estaba and not silencioso:
            self._escribir("Ejecución detenida por el usuario.", "err")
            self.estado.emit("Ejecución detenida")
            self._actualizar_vistas()
        self._actualizar_botones()

    def _reiniciar(self):
        if self.m is None:
            return
        self.detener(silencioso=True)
        self.consola.comando("c")
        self._escribir("Registros y memoria reiniciados (c).", "dim")
        self._actualizar_vistas()

    def _enter(self):
        txt = self.entrada.text()
        self.entrada.clear()
        if self._esperando:
            self._escribir(txt, "in")
            if not self.m.dar_entrada(txt):
                self._escribir("Illegal value", "err")
                self._escribir("Ingrese un numero (IN):", "in")
                return
            self._esperando = False
            self._corriendo = True
            self._lbl_ent.setText("Comando TM (h=ayuda):")
            self._refresh_styles()
            self._actualizar_botones()
            self._timer.start(0)
            return
        cmd = txt.strip()
        if not cmd:
            return
        self._escribir(f"Comando TM (h=ayuda): {cmd}", "dim")
        if self.m is None:
            self._escribir("No hay programa cargado: presiona F9.", "err")
            return
        letra = cmd[0]
        if letra == "g":
            self._iniciar("g", 0)
        elif letra == "s":
            partes = cmd.split()
            try:
                n = abs(int(partes[1])) if len(partes) > 1 else 1
            except ValueError:
                self._escribir("Step count?")
                return
            self._iniciar("s", n)
        elif letra == "t":
            self.chk_traza.setChecked(not self.chk_traza.isChecked())
            self._escribir("Tracing now " + ("on." if self.chk_traza.isChecked() else "off."))
        elif letra == "p":
            self.chk_contar.setChecked(not self.chk_contar.isChecked())
            self._escribir("Printing instruction count now " +
                           ("on." if self.chk_contar.isChecked() else "off."))
        elif letra == "q":
            self.detener(silencioso=True)
            self._escribir("Fin de la simulacion TM.")
        else:
            self.consola.comando(cmd)          # h v i d r c
            self._actualizar_vistas()

    # ── registros / memoria ──
    def _actualizar_vistas(self):
        if self.m is None:
            return
        tm, m = self.tm, self.m
        for i in range(8):
            datos = [str(i), tm.ALIAS_REG.get(i, ""), tm.fmt_operando(m.reg[i])]
            for c, d in enumerate(datos):
                it = QTableWidgetItem(d)
                if c == 2:
                    it.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                if c == 1:
                    it.setForeground(QColor(C['orange']))
                self.t_reg.setItem(i, c, it)
        sims = self._tabla_sim.simbolos() if self._tabla_sim else []
        self.t_mem.setRowCount(len(sims))
        for fila, s in enumerate(sims):
            v = m.dMem[s.loc] if 0 <= s.loc < len(m.dMem) else "?"
            datos = [s.nombre, str(s.loc), tm.fmt_valor(v) if v != "?" else v]
            for c, d in enumerate(datos):
                it = QTableWidgetItem(d)
                if c == 0:
                    it.setForeground(QColor(_TREE_NODE_COLOR["identificador"]))
                if c == 2:
                    it.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.t_mem.setItem(fila, c, it)
        self.pc_cambiado.emit(m.pc)
        self._lbl.setText(f"pc = {m.pc}   ·   {m.pasos} pasos")


# ══════════════════════════════════════════════════════
#  VENTANA PRINCIPAL
# ══════════════════════════════════════════════════════
class IDEMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CompiladorIDE — UAA")
        self.resize(1500, 880)
        self.setMinimumSize(1100, 650)
        self.setDockNestingEnabled(True)
        self.setAcceptDrops(True)

        # Mapa: path -> CodeEditor
        self._editors: dict[str, CodeEditor] = {}
        # Archivo activo (None = sin titulo)
        self._active_path: str | None = None
        # Editor cuyo código está mostrado en los paneles de código / TM
        self._editor_compilado = None

        self._build_central()
        self._build_docks()
        self._build_menu()
        self._build_toolbar()
        self._build_statusbar()

        # Primer tab vacío
        self._new_tab()

    # ══════════════════════════════════════════════════
    #  CENTRAL — tabs de archivos
    # ══════════════════════════════════════════════════
    def _build_central(self):
        self.file_tabs = QTabWidget()
        self.file_tabs.setTabsClosable(True)
        self.file_tabs.setMovable(True)
        self.file_tabs.setDocumentMode(True)
        self.file_tabs.tabCloseRequested.connect(self._close_tab_by_index)
        self.file_tabs.currentChanged.connect(self._on_tab_changed)
        self.setCentralWidget(self.file_tabs)

    def _new_tab(self, path=None, content=""):
        """Crea un nuevo tab con un CodeEditor."""
        path = limpiar_ruta(path) if path else None
        editor = CodeEditor()
        editor._highlighter = LexicoHighlighter(editor.document())
        editor.document().setPlainText(content)
        editor.document().setModified(False)
        editor.cursorPositionChanged.connect(self._update_cursor)
        editor.document().modificationChanged.connect(
            lambda mod, e=editor: self._on_modified(mod, e))
        editor.document().contentsChanged.connect(
            lambda e=editor: self._on_fuente_cambiado(e))

        label = os.path.basename(path) if path else "sin titulo"
        idx   = self.file_tabs.addTab(editor, label)
        self.file_tabs.setCurrentIndex(idx)

        if path:
            self._editors[clave_ruta(path)] = editor
        else:
            # Clave temporal por id de objeto
            self._editors[id(editor)] = editor

        editor._file_path = path
        return editor

    @property
    def editor(self) -> CodeEditor:
        """Editor activo en el tab actual."""
        w = self.file_tabs.currentWidget()
        return w if isinstance(w, CodeEditor) else None

    def _on_fuente_cambiado(self, editor):
        """Regla: nunca mostrar como válido código de un fuente que cambió."""
        if editor is self._editor_compilado:
            self._marcar_desactualizado(True)

    def _marcar_desactualizado(self, si):
        self.out_ci.marcar_desactualizado(si)
        self.out_exec.marcar_desactualizado(si)

    def _on_tab_changed(self, idx):
        self._update_cursor()
        if getattr(self, "_editor_compilado", None) is not None:
            self._marcar_desactualizado(
                self.file_tabs.widget(idx) is not self._editor_compilado)
        e = self.file_tabs.widget(idx)
        if e and hasattr(e, '_file_path'):
            name = (os.path.basename(e._file_path)
                    if e._file_path else "sin titulo")
            dot  = " ●" if e.document().isModified() else ""
            self.setWindowTitle(f"CompiladorIDE  —  {name}{dot}")

    def _on_modified(self, mod, editor):
        idx = self.file_tabs.indexOf(editor)
        if idx < 0:
            return
        name = (os.path.basename(editor._file_path)
                if editor._file_path else "sin titulo")
        self.file_tabs.setTabText(idx, name + (" ●" if mod else ""))
        self._on_tab_changed(idx)

    # ══════════════════════════════════════════════════
    #  DOCKS (arrastrables, sin flotante)
    # ══════════════════════════════════════════════════
    def _make_dock(self, title, widget, area):
        dock = QDockWidget(title, self)
        dock.setWidget(widget)
        dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable |
            QDockWidget.DockWidgetFeature.DockWidgetClosable)
        self.addDockWidget(area, dock)
        return dock

    def _build_docks(self):
        LEFT   = Qt.DockWidgetArea.LeftDockWidgetArea
        RIGHT  = Qt.DockWidgetArea.RightDockWidgetArea
        BOTTOM = Qt.DockWidgetArea.BottomDockWidgetArea

        # ── Explorador (izquierda) ──
        self.file_explorer = FileExplorer()
        self.file_explorer.file_opened.connect(self._open_file)
        self.dock_explorer = self._make_dock("EXPLORADOR",
                                             self.file_explorer, LEFT)

        # ── Resultados del compilador (derecha) ──
        self.nb_results = QTabWidget()
        self.out_lexico = TokenPanel()          # ← panel visual
        self.out_sint   = SyntaxTreePanel()     # ← árbol sintáctico
        self.out_sem    = SemanticPanel()       # ← árbol anotado / recorrido
        self.out_ci     = CodigoPanel()         # ← .tm (tabla/archivo) y .ci
        self.nb_results.addTab(self.out_lexico, "Lexico")
        self.nb_results.addTab(self.out_sint,   "Sintactico")
        self.nb_results.addTab(self.out_sem,    "Semantico")
        self.nb_results.addTab(self.out_ci,     "Código Intermedio")
 

        self.symbol_table = QTableWidget(0, 6)
        self.symbol_table.setHorizontalHeaderLabels(
            ["Nombre", "Tipo", "Loc", "Valor", "Ámbito", "Líneas"])
        self.symbol_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents)
        self.symbol_table.horizontalHeader().setStretchLastSection(True)
        self.symbol_table.verticalHeader().setVisible(False)
        self.symbol_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers)
        self.symbol_table.setAlternatingRowColors(True)
        self.nb_results.addTab(self.symbol_table, "Tabla de Simbolos")

        self.dock_results = self._make_dock(
            "RESULTADOS DEL COMPILADOR", self.nb_results, RIGHT)

        # ── Errores + ejecucion (abajo) ──
        self.nb_errors  = QTabWidget()
        self.err_lexico = make_output("red", "bg")
        self.err_sint   = make_output("red", "bg")
        self.err_sem    = make_output("red", "bg")
        self.out_exec   = TMPanel()             # ← simulador TM integrado
        self.out_exec.ejecutar_pedido.connect(self._ejecutar)
        self.out_exec.pc_cambiado.connect(self.out_ci.resaltar_pc)
        self.out_exec.estado.connect(self.lbl_status_set)
        self.nb_errors.addTab(self.err_lexico, "Errores Lexicos")
        self.nb_errors.addTab(self.err_sint,   "Errores Sintacticos")
        self.nb_errors.addTab(self.err_sem,    "Errores Semanticos")
        self.nb_errors.addTab(self.out_exec,   "Máquina TM (ejecución)")

        self.dock_errors = self._make_dock("ERRORES / SALIDA",
                                           self.nb_errors, BOTTOM)

        # Tamaños iniciales
        self.resizeDocks([self.dock_explorer], [200], Qt.Orientation.Horizontal)
        self.resizeDocks([self.dock_results],  [380], Qt.Orientation.Horizontal)
        self.resizeDocks([self.dock_errors],   [260], Qt.Orientation.Vertical)
 
        
        self.dock_results.setMinimumWidth(80)
        self.dock_results.setMaximumWidth(16777215)
        
        self.dock_results.visibilityChanged.connect(
            lambda v: self._btn_toggle_results.setChecked(v))

    # ══════════════════════════════════════════════════
    #  MENU
    # ══════════════════════════════════════════════════
    def _build_menu(self):
        mb = self.menuBar()

        def act(m, lbl, sc, cb):
            a = QAction(lbl, self)
            if sc:
                a.setShortcut(QKeySequence(sc))
            a.triggered.connect(cb)
            m.addAction(a)

        fa = mb.addMenu("Archivo")
        act(fa, "Nuevo",            "Ctrl+N",        self._nuevo)
        act(fa, "Abrir...",         "Ctrl+O",        self._abrir)
        act(fa, "Abrir carpeta...", "Ctrl+K Ctrl+O", self._abrir_carpeta)
        fa.addSeparator()
        act(fa, "Cerrar pestaña",   "Ctrl+W",        self._cerrar_tab_actual)
        fa.addSeparator()
        act(fa, "Guardar",          "Ctrl+S",        self._guardar)
        act(fa, "Guardar como...",  "Ctrl+Shift+S",  self._guardar_como)
        fa.addSeparator()
        act(fa, "Salir",            "Alt+F4",        self.close)

        ed = mb.addMenu("Editar")
        act(ed, "Deshacer", "Ctrl+Z", lambda: self.editor and self.editor.undo())
        act(ed, "Rehacer",  "Ctrl+Y", lambda: self.editor and self.editor.redo())
        ed.addSeparator()
        act(ed, "Cortar",   "Ctrl+X", lambda: self.editor and self.editor.cut())
        act(ed, "Copiar",   "Ctrl+C", lambda: self.editor and self.editor.copy())
        act(ed, "Pegar",    "Ctrl+V", lambda: self.editor and self.editor.paste())

        ve = mb.addMenu("Ver")
        ve.addAction(self.dock_explorer.toggleViewAction())
        ve.addAction(self.dock_results.toggleViewAction())
        ve.addAction(self.dock_errors.toggleViewAction())

        co = mb.addMenu("Compilar")
        act(co, "Analisis Lexico",     "F5", self._lexico)
        act(co, "Analisis Sintactico", "F6", self._sintactico)
        act(co, "Analisis Semantico",  "F7", self._semantico)
        act(co, "Codigo Intermedio",   "F8", self._codigo_intermedio)
        co.addSeparator()
        act(co, "Ejecutar",            "F9", self._ejecutar)

    # ══════════════════════════════════════════════════
    #  TOOLBAR
    # ══════════════════════════════════════════════════
    def _build_toolbar(self):
        self._tb = QToolBar("Acciones")
        self._tb.setObjectName("Acciones")
        self._tb.setMovable(False)
        self.addToolBar(self._tb)
        
        self._tb.addSeparator()
        self._btn_toggle_results = QAction("▶  Resultados", self)
        self._btn_toggle_results.setCheckable(True)
        self._btn_toggle_results.setChecked(True)
        self._btn_toggle_results.triggered.connect(self._toggle_results)
        self._tb.addAction(self._btn_toggle_results)
        w = self._tb.widgetForAction(self._btn_toggle_results)
        if w:
            w.setStyleSheet(
                f"color:{C['fg_dim']}; border:1px solid {C['border']};"
                f"border-radius:2px; padding:4px 10px;")
        self._btn_toggle_results_widget = w

        def tbtn(lbl, cb, color=None):
            a = QAction(lbl, self)
            a.triggered.connect(cb)
            self._tb.addAction(a)
            w = self._tb.widgetForAction(a)
            if w and color:
                w.setStyleSheet(f"color:{color}; font-weight:bold;")
            return w

        tbtn("Nuevo",   self._nuevo)
        tbtn("Abrir",   self._abrir)
        tbtn("Guardar", self._guardar)
        self._tb.addSeparator()
        tbtn("Lexico",          self._lexico,            C['green'])
        tbtn("Sintactico",      self._sintactico,         C['green'])
        tbtn("Semantico",       self._semantico,          C['green'])
        tbtn("Cod. Intermedio", self._codigo_intermedio,  C['orange'])
        self._tb.addSeparator()
        self._btn_ejecutar = tbtn("▶  Ejecutar", self._ejecutar)
        self._update_ejecutar_btn()
        self._tb.addSeparator()

        lbl = QLabel("  Tema: ")
        lbl.setStyleSheet(f"color:{C['fg_dim']}; background:transparent;")
        self._tb.addWidget(lbl)
        self._lbl_tema = lbl

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(list(THEMES.keys()))
        self.theme_combo.setCurrentText("VS Dark")
        self.theme_combo.currentTextChanged.connect(self._apply_theme)
        self._tb.addWidget(self.theme_combo)

    def _update_ejecutar_btn(self):
        if self._btn_ejecutar:
            self._btn_ejecutar.setStyleSheet(
                f"background:{C['active']}; color:white;"
                f"font-weight:bold; padding:4px 16px; border-radius:2px;")

    # ══════════════════════════════════════════════════
    #  STATUS BAR
    # ══════════════════════════════════════════════════
    def _build_statusbar(self):
        sb = QStatusBar()
        self.setStatusBar(sb)
        self.lbl_status = QLabel("Listo")
        self.lbl_pos    = QLabel("Ln 1,  Col 1")
        self.lbl_enc    = QLabel("UTF-8")
        for l in (self.lbl_status, self.lbl_pos, self.lbl_enc):
            l.setStyleSheet("color:white; padding:0 12px; font-size:8pt;")
        sb.addWidget(self.lbl_status)
        sb.addPermanentWidget(self.lbl_enc)
        sb.addPermanentWidget(self.lbl_pos)

    # ══════════════════════════════════════════════════
    #  TEMAS
    # ══════════════════════════════════════════════════
    def _apply_theme(self, name):
        global C
        C = dict(THEMES[name])
        QApplication.instance().setStyleSheet(build_stylesheet(C))

        # Refrescar widgets con palette propia
        for e in self._all_editors():
            e.refresh_theme()
            
        self.file_explorer.refresh_theme()
        self.out_lexico.refresh_theme()
        self.out_sint.refresh_theme()           # árbol sintáctico
        self.out_sem.refresh_theme()            # panel semántico
        self.out_ci.refresh_theme()             # código intermedio
        self.out_exec.refresh_theme()           # máquina TM
        for w in (self.err_lexico, self.err_sint, self.err_sem):
            _apply_output_style(w)
 

        self._lbl_tema.setStyleSheet(
            f"color:{C['fg_dim']}; background:transparent;")
        self._update_ejecutar_btn()
        for e in self._all_editors():
            if hasattr(e, '_highlighter'):
                e._highlighter.rehighlight()

    # ══════════════════════════════════════════════════
    #  HELPERS
    # ══════════════════════════════════════════════════
    def _all_editors(self):
        for i in range(self.file_tabs.count()):
            w = self.file_tabs.widget(i)
            if isinstance(w, CodeEditor):
                yield w

    def _update_cursor(self):
        if self.editor:
            c = self.editor.textCursor()
            self.lbl_pos.setText(
                f"Ln {c.blockNumber()+1},  Col {c.columnNumber()+1}")

    def lbl_status_set(self, texto):
        if hasattr(self, "lbl_status"):
            self.lbl_status.setText(texto)

    def _set_output(self, widget, text):
        widget.setPlainText(text or "(sin salida)")

    def _set_errors(self, widget, stderr_text):
        if not stderr_text or not stderr_text.strip():
            widget.setPlainText("(sin errores)")
            widget.setStyleSheet(
                f"background:{C['bg']}; color:{C['green']}; border:none;"
                f"font-family:Consolas; font-size:10pt;")
        else:
            widget.setPlainText(stderr_text.strip())
            widget.setStyleSheet(
                f"background:{C['bg']}; color:{C['red']}; border:none;"
                f"font-family:Consolas; font-size:10pt;")

    def closeEvent(self, e):
        # Verificar si hay tabs sin guardar
        unsaved = [
            self.file_tabs.tabText(i).rstrip(" ●")
            for i in range(self.file_tabs.count())
            if isinstance(self.file_tabs.widget(i), CodeEditor)
            and self.file_tabs.widget(i).document().isModified()
        ]
        if unsaved:
            r = QMessageBox.question(
                self, "Cambios sin guardar",
                f"Hay {len(unsaved)} archivo(s) con cambios sin guardar.\n"
                f"¿Salir de todas formas?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if r != QMessageBox.StandardButton.Yes:
                e.ignore()
                return
        e.accept()

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            e.acceptProposedAction()

    def dropEvent(self, e):
        for url in e.mimeData().urls():
            path = url.toLocalFile()
            if os.path.isfile(path):
                self._open_file(path)
            elif os.path.isdir(path):
                self.file_explorer.load_folder(path)
                self.dock_explorer.show()

    # ══════════════════════════════════════════════════
    #  GESTION DE ARCHIVOS
    # ══════════════════════════════════════════════════
    def _nuevo(self):
        self._new_tab()
        self.lbl_status.setText("Nuevo archivo")

    def _abrir(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Abrir archivo(s)", "",
            "Codigo fuente (*.txt *.c *.cl *.lng *.java *.pas);;Todos (*.*)")
        for path in paths:
            self._open_file(path)

    def _abrir_carpeta(self):
        f = QFileDialog.getExistingDirectory(self, "Abrir carpeta")
        if f:
            self.file_explorer.load_folder(f)
            self.dock_explorer.show()

    def _open_file(self, path):
        path = limpiar_ruta(path)

        # Si ya esta abierto, solo enfocarlo
        i = self._tab_de_ruta(path)
        if i >= 0:
            self.file_tabs.setCurrentIndex(i)
            self._explorer_reveal(path)
            self.lbl_status.setText(
                f"Ya abierto: {os.path.basename(path)}")
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            editor = self._new_tab(path, content)
            editor.document().setModified(False)
            self.lbl_status.setText(f"Abierto: {os.path.basename(path)}")

            # Cargar carpeta padre en explorador si no esta ya cargada
            folder = os.path.dirname(path)
            if clave_ruta(self.file_explorer.root_path) != clave_ruta(folder):
                self.file_explorer.load_folder(folder)
                self.dock_explorer.show()
            self._explorer_reveal(path)
        except Exception as ex:
            QMessageBox.warning(self, "Error al abrir",
                                f"No se pudo abrir:\n{ex}")

    def _tab_de_ruta(self, path, excepto=None):
        """Índice de la pestaña que tiene abierto `path` (o -1)."""
        clave = clave_ruta(path)
        for i in range(self.file_tabs.count()):
            w = self.file_tabs.widget(i)
            if (isinstance(w, CodeEditor) and w is not excepto
                    and w._file_path and clave_ruta(w._file_path) == clave):
                return i
        return -1

    def _explorer_reveal(self, path):
        """Selecciona y hace visible el archivo en el arbol del explorador."""
        root = self.file_explorer.tree.invisibleRootItem()
        self._find_and_select(root, clave_ruta(path))

    def _find_and_select(self, parent, path):
        for i in range(parent.childCount()):
            item = parent.child(i)
            item_path = item.data(0, Qt.ItemDataRole.UserRole)
            if item_path and clave_ruta(item_path) == path:
                self.file_explorer.tree.setCurrentItem(item)
                self.file_explorer.tree.scrollToItem(item)
                return True
            if self._find_and_select(item, path):
                return True
        return False

    def _cerrar_tab_actual(self):
        idx = self.file_tabs.currentIndex()
        if idx >= 0:
            self._close_tab_by_index(idx)

    def _close_tab_by_index(self, idx):
        w = self.file_tabs.widget(idx)
        if not isinstance(w, CodeEditor):
            return
        if w.document().isModified():
            name = (os.path.basename(w._file_path)
                    if w._file_path else "sin titulo")
            r = QMessageBox.question(
                self, "Cambios sin guardar",
                f"'{name}' tiene cambios sin guardar.\n¿Cerrar de todas formas?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if r != QMessageBox.StandardButton.Yes:
                return
        # Eliminar del mapa
        key = clave_ruta(w._file_path) if w._file_path else id(w)
        self._editors.pop(key, None)
        self.file_tabs.removeTab(idx)
        # Si no quedan tabs, crear uno vacío
        if self.file_tabs.count() == 0:
            self._new_tab()

    def _guardar(self):
        e = self.editor
        if not e:
            return
        if e._file_path:
            self._write_file(e, e._file_path)
        else:
            self._guardar_como()

    def _guardar_como(self):
        e = self.editor
        if not e:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Guardar como", "",
            "Codigo fuente (*.txt *.c *.cl *.lng);;Todos (*.*)")
        if path:
            path = limpiar_ruta(path)
            # ¿Ese archivo ya está abierto en otra pestaña?
            otra = self._tab_de_ruta(path, excepto=e)
            if otra >= 0:
                w = self.file_tabs.widget(otra)
                if w.document().isModified():
                    QMessageBox.warning(
                        self, "Archivo abierto",
                        f"'{os.path.basename(path)}' está abierto en otra "
                        f"pestaña con cambios sin guardar.\n"
                        f"Guárdalo o ciérralo primero.")
                    return
                # Sin cambios: se cierra la pestaña vieja para no duplicar
                self._editors.pop(clave_ruta(path), None)
                self.file_tabs.removeTab(otra)
            # Si antes era sin titulo, actualizar clave
            old_key = clave_ruta(e._file_path) if e._file_path else id(e)
            self._editors.pop(old_key, None)
            e._file_path = path
            self._editors[clave_ruta(path)] = e
            self._write_file(e, path)
            self._on_tab_changed(self.file_tabs.currentIndex())

    def _write_file(self, editor, path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(editor.toPlainText())
        editor.document().setModified(False)
        idx = self.file_tabs.indexOf(editor)
        self.file_tabs.setTabText(idx, os.path.basename(path))
        self.lbl_status.setText(f"Guardado: {os.path.basename(path)}")
        self.file_explorer.refresh()

    # ══════════════════════════════════════════════════
    #  COMPILACION
    # ══════════════════════════════════════════════════
    def _get_source_path(self):
        e = self.editor
        if not e:
            return None, False
        if e._file_path:
            self._write_file(e, e._file_path)
            return e._file_path, False
        # Sin guardar: temporal
        tmp = tempfile.NamedTemporaryFile(
            delete=False, suffix=".txt", mode="w", encoding="utf-8")
        tmp.write(e.toPlainText())
        tmp.close()
        return tmp.name, True

    def _load_compilador(self):
        return cargar_compilador()

    def _run_compiler(self, flag):
        path, is_tmp = self._get_source_path()
        if not path:
            return "", "[Error] No hay archivo activo."

        mod, err = self._load_compilador()
        if err:
            return "", err

        try:
            with open(path, "r", encoding="utf-8") as f:
                codigo = f.read()

            if flag == "lexico":
                tokens, errores = mod.analizar(codigo)
                out = mod.formatear_tokens(tokens)
                err = mod.formatear_errores(errores)
                return out, err

            # Para los demás flags aún no implementados:
            return "", f"[Error] Flag '--{flag}' no implementado aún."

        except Exception as ex:
            return "", f"[Error al ejecutar compilador] {ex}"
        finally:
            if is_tmp:
                try:
                    os.unlink(path)
                except Exception:
                    pass
    def _lexico(self):
        self.lbl_status.setText("Ejecutando analisis lexico...")
        QApplication.processEvents()
        if self.editor:
            self.editor.clear_error_lines()
        out, err = self._run_compiler("lexico")
        self.out_lexico.cargar_texto(out)
        self._set_errors(self.err_lexico, err)
        self.nb_results.setCurrentWidget(self.out_lexico)
        self.dock_results.show(); self.dock_results.raise_()
        if err and err.strip():
            self.nb_errors.setCurrentWidget(self.err_lexico)
            self.dock_errors.show(); self.dock_errors.raise_()
        self.lbl_status.setText("Analisis lexico completado")

    def _sintactico(self):
        self.lbl_status.setText("Ejecutando análisis sintáctico...")
        QApplication.processEvents()

        path, is_tmp = self._get_source_path()
        if not path:
            return

        mod, err_msg = self._load_compilador()
        if err_msg:
            self.out_sint.mostrar_error(err_msg)
            self.nb_results.setCurrentWidget(self.out_sint)
            self.dock_results.show(); self.dock_results.raise_()
            return

        errores_sint = []
        errores_lex  = []
        try:
            with open(path, "r", encoding="utf-8") as f:
                codigo = f.read()

            arbol, errores_lex, errores_sint = mod.analizar_sintactico(codigo)

            # Siempre mostrar el árbol (aunque haya errores)
            todos = errores_lex + errores_sint
            self.out_sint.cargar_arbol(arbol, todos)

            # Panel de errores: léxicos + sintácticos juntos
            partes = []
            if errores_lex:
                partes.append(mod.formatear_errores(errores_lex))
            if errores_sint:
                partes.append(mod.formatear_errores_sint(errores_sint))
            self._set_errors(self.err_sint, "\n".join(partes) if partes else "")

            # Resaltar líneas con error directamente en el editor
            if self.editor:
                self.editor.set_error_lines(todos)

        except Exception as ex:
            self.out_sint.mostrar_error(f"Error interno: {ex}")
        finally:
            if is_tmp:
                try:
                    os.unlink(path)
                except Exception:
                    pass

        self.nb_results.setCurrentWidget(self.out_sint)
        self.dock_results.show(); self.dock_results.raise_()
        if errores_sint:
            self.nb_errors.setCurrentWidget(self.err_sint)
            self.dock_errors.show(); self.dock_errors.raise_()
        ok = "con errores" if errores_sint else "sin errores"
        self.lbl_status.setText(f"Análisis sintáctico completado ({ok})")

    def _semantico(self):
        self.lbl_status.setText("Ejecutando análisis semántico...")
        QApplication.processEvents()

        path, is_tmp = self._get_source_path()
        if not path:
            return
        mod, err_msg = self._load_compilador()
        if err_msg:
            self.out_sem.mostrar_error(err_msg)
            self.nb_results.setCurrentWidget(self.out_sem)
            self.dock_results.show(); self.dock_results.raise_()
            return

        hay_errores = False
        try:
            with open(path, "r", encoding="utf-8") as f:
                codigo = f.read()
            r = mod.analizar_semantico(codigo)

            if not r.ejecutado:
                # El semántico necesita un AST sin errores previos
                partes = ["No se ejecutó el análisis semántico: corrige "
                          "primero los errores léxicos/sintácticos.", ""]
                if r.errores_lex:
                    partes.append(mod.formatear_errores(r.errores_lex))
                if r.errores_sint:
                    partes.append(mod.formatear_errores_sint(r.errores_sint))
                texto = "\n".join(partes)
                self.out_sem.mostrar_error("Hay errores léxicos/sintácticos")
                self._llenar_tabla_simbolos(None, mod)
                self._set_errors(self.err_sem, texto)
                if self.editor:
                    self.editor.set_error_lines(
                        r.errores_lex + r.errores_sint)
                hay_errores = True
                estado = "no ejecutado (errores previos)"
            else:
                self.out_sint.cargar_arbol(r.arbol, [])
                self.out_sem.cargar(r, mod)
                self._llenar_tabla_simbolos(r.tabla, mod)
                self._set_errors(self.err_sem,
                                 mod.formatear_errores_sem(r.errores_sem))
                if self.editor:
                    self.editor.set_error_lines(r.errores_sem)
                hay_errores = bool(r.errores_sem)
                estado = (f"{len(r.errores_sem)} error(es)" if hay_errores
                          else "sin errores")
        except Exception as ex:
            import traceback
            self.out_sem.mostrar_error(f"Error interno: {ex}")
            self._set_errors(self.err_sem, traceback.format_exc())
            hay_errores = True
            estado = "error interno"
        finally:
            if is_tmp:
                try:
                    os.unlink(path)
                except Exception:
                    pass

        self.nb_results.setCurrentWidget(self.out_sem)
        self.dock_results.show(); self.dock_results.raise_()
        if hay_errores:
            self.nb_errors.setCurrentWidget(self.err_sem)
            self.dock_errors.show(); self.dock_errors.raise_()
        self.lbl_status.setText(f"Análisis semántico completado ({estado})")

    def _llenar_tabla_simbolos(self, tabla, mod):
        from PyQt6.QtWidgets import QTableWidgetItem
        t = self.symbol_table
        t.setRowCount(0)
        if tabla is None:
            return
        for s in tabla.simbolos():
            fila = t.rowCount()
            t.insertRow(fila)
            datos = [s.nombre, s.tipo_decl, str(s.loc),
                     mod.valor_simbolo(s), "main",
                     ", ".join(str(l) for l in s.lineas)]
            for c, d in enumerate(datos):
                it = QTableWidgetItem(d)
                if c in (2, 3):
                    it.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if c == 0:
                    it.setForeground(QColor(_TREE_NODE_COLOR["identificador"]))
                elif c == 1:
                    it.setForeground(QColor(_TREE_NODE_COLOR["declaracion"]))
                t.setItem(fila, c, it)

    # ── Generación de código y ejecución ─────────────────────
    def _compilar_todo(self):
        """Guarda y compila TODAS las fases del fuente actual. Actualiza
        árbol, semántico, tabla de símbolos, errores y el panel de código.
        Devuelve (resultado, módulo) o (None, None)."""
        self.out_exec.detener(silencioso=True)
        e = self.editor
        if not e:
            return None, None
        path, is_tmp = self._get_source_path()
        if not path:
            return None, None
        mod, err_msg = self._load_compilador()
        if err_msg:
            self.out_ci.limpiar(err_msg, error=True)
            return None, None
        try:
            with open(path, "r", encoding="utf-8") as f:
                codigo = f.read()
            r = mod.compilar(codigo, None if is_tmp else path)
        except Exception as ex:
            import traceback
            self.out_ci.limpiar(f"Error interno: {ex}", error=True)
            self._set_errors(self.err_sem, traceback.format_exc())
            return None, None
        finally:
            if is_tmp:
                try:
                    os.unlink(path)
                except Exception:
                    pass

        nombre = os.path.basename(path) if not is_tmp else "sin titulo"
        # Árbol / semántico / tabla de símbolos / errores de cada fase
        self._set_errors(self.err_lexico, mod.formatear_errores(r.errores_lex)
                         if r.errores_lex else "")
        partes = []
        if r.errores_lex:
            partes.append(mod.formatear_errores(r.errores_lex))
        if r.errores_sint:
            partes.append(mod.formatear_errores_sint(r.errores_sint))
        self._set_errors(self.err_sint, "\n".join(partes))
        if r.arbol is not None:
            self.out_sint.cargar_arbol(r.arbol, r.errores_lex + r.errores_sint)
        if r.ejecutado:
            self.out_sem.cargar(r, mod)
            self._llenar_tabla_simbolos(r.tabla, mod)
            texto_sem = mod.formatear_errores_sem(r.errores_sem)
            if r.error_gen:
                texto_sem = (texto_sem + "\n" if texto_sem else "") + r.error_gen
            self._set_errors(self.err_sem, texto_sem)
            if not texto_sem and r.avisos:
                self.err_sem.setPlainText(
                    "(sin errores)\n\nAvisos (no impiden generar código):\n" +
                    "\n".join(f"[AVISO] Línea {l}: {m}" for l, m in r.avisos))
                self.err_sem.setStyleSheet(
                    f"background:{C['bg']}; color:{C['orange']}; border:none;"
                    f"font-family:Consolas; font-size:10pt;")
        else:
            self.out_sem.mostrar_error("Hay errores léxicos/sintácticos")
            self._llenar_tabla_simbolos(None, mod)
            self._set_errors(self.err_sem, "No se ejecutó el análisis semántico: "
                             "corrige primero los errores léxicos/sintácticos.")
        if e:
            e.set_error_lines(r.errores_lex + r.errores_sint + r.errores_sem)

        self._editor_compilado = e
        if r.ok:
            self.out_ci.cargar(r, nombre)
            self._marcar_desactualizado(False)
        else:
            self.out_ci.limpiar(f"No se generó código: hay {r.n_errores or 1} "
                                f"error(es) — {nombre}", error=True)
            self.out_exec.limpiar("No se generó código: hay errores de análisis. "
                                  "Corrígelos y vuelve a compilar.")
            if r.errores_lex:
                w = self.err_lexico
            elif r.errores_sint:
                w = self.err_sint
            else:
                w = self.err_sem
            self.nb_errors.setCurrentWidget(w)
            self.dock_errors.show(); self.dock_errors.raise_()
        return r, mod

    def _codigo_intermedio(self):
        self.lbl_status.setText("Compilando y generando código...")
        QApplication.processEvents()
        r, mod = self._compilar_todo()
        self.nb_results.setCurrentWidget(self.out_ci)
        self.dock_results.show(); self.dock_results.raise_()
        if r is not None and r.ok:
            self.lbl_status.setText(f"Código generado: {len(r.instrucciones)} instrucciones")
        else:
            self.lbl_status.setText("No se generó código (hay errores)")

    def _ejecutar(self):
        """F9: recompila SIEMPRE el fuente actual y ejecuta en la TM el texto
        del .tm recién generado (nunca reutiliza un .tm anterior)."""
        self.lbl_status.setText("Compilando...")
        QApplication.processEvents()
        r, mod = self._compilar_todo()
        self.nb_results.setCurrentWidget(self.out_ci)
        self.dock_results.show(); self.dock_results.raise_()
        if r is None or not r.ok:
            self.lbl_status.setText("No se ejecutó: hay errores de análisis")
            return
        import tm as tm_mod
        nombre = self.out_ci._fuente
        self.nb_errors.setCurrentWidget(self.out_exec)
        self.dock_errors.show(); self.dock_errors.raise_()
        if self.out_exec.cargar_programa(tm_mod, r.codigo_tm, r.tabla, r.codigo_ci, nombre):
            self.out_exec.ejecutar()
    
    def _toggle_results(self, checked):
        """Muestra u oculta el panel de resultados del compilador."""
        if checked:
            self.dock_results.show()
            self.dock_results.raise_()
            if self._btn_toggle_results_widget:
                self._btn_toggle_results_widget.setStyleSheet(
                    f"color:white; background:{C['active']};"
                    f"border-radius:2px; padding:4px 10px; font-weight:bold;")
        else:
            self.dock_results.hide()
            if self._btn_toggle_results_widget:
                self._btn_toggle_results_widget.setStyleSheet(
                    f"color:{C['fg_dim']}; border:1px solid {C['border']};"
                    f"border-radius:2px; padding:4px 10px;")        


# ══════════════════════════════════════════════════════
if __name__ == "__main__":
    if len(sys.argv) >= 4 and sys.argv[1] == "--autoprueba":
        autoprueba(sys.argv[2], sys.argv[3], sys.argv[4:])
        sys.exit(0)
    app = QApplication(sys.argv)
    app.setStyleSheet(build_stylesheet(C))
    win = IDEMainWindow()
    win.show()
    sys.exit(app.exec())
