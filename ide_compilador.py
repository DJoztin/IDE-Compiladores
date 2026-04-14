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
)
from PyQt6.QtGui import (
    QAction, QFont, QColor, QPainter, QTextFormat,
    QFontMetrics, QKeySequence, QPalette, QIcon, QPixmap,
)
from PyQt6.QtCore import Qt, QSize, QRect, pyqtSignal

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

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)
class CodeEditor(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._gutter = LineNumberArea(self)
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

    def _highlight_line(self):
        sel = QTextEdit.ExtraSelection()
        sel.format.setBackground(QColor(C['line_hl']))
        sel.format.setProperty(
            QTextFormat.Property.FullWidthSelection, True)
        sel.cursor = self.textCursor()
        sel.cursor.clearSelection()
        self.setExtraSelections([sel])

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
        editor = CodeEditor()
        hl = LexicoHighlighter(editor.document())
        editor._highlighter = hl 
        editor = CodeEditor()
        editor._highlighter = LexicoHighlighter(editor.document())  # ← agregar
        editor.document().setPlainText(content)
        editor.document().setModified(False)
        editor.cursorPositionChanged.connect(self._update_cursor)
        editor.document().modificationChanged.connect(
            lambda mod, e=editor: self._on_modified(mod, e))

        label = os.path.basename(path) if path else "sin titulo"
        idx   = self.file_tabs.addTab(editor, label)
        self.file_tabs.setCurrentIndex(idx)

        if path:
            self._editors[path] = editor
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

    def _on_tab_changed(self, idx):
        self._update_cursor()
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
        self.out_sint   = make_output("fg",  "bg")
        self.out_sem    = make_output("fg",  "bg")
        self.out_ci     = make_output("fg",  "bg")
        self.nb_results.addTab(self.out_lexico, "Lexico")
        self.nb_results.addTab(self.out_sint,   "Sintactico")
        self.nb_results.addTab(self.out_sem,    "Semantico")
        self.nb_results.addTab(self.out_ci,     "Cod. Intermedio")
 

        self.symbol_table = QTableWidget(0, 5)
        self.symbol_table.setHorizontalHeaderLabels(
            ["Nombre", "Tipo", "Valor", "Linea", "Alcance"])
        self.symbol_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch)
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
        self.out_exec   = make_output("green", "terminal_bg")
        self.nb_errors.addTab(self.err_lexico, "Errores Lexicos")
        self.nb_errors.addTab(self.err_sint,   "Errores Sintacticos")
        self.nb_errors.addTab(self.err_sem,    "Errores Semanticos")
        self.nb_errors.addTab(self.out_exec,   "Resultado Ejecucion")

        self.dock_errors = self._make_dock("ERRORES / SALIDA",
                                           self.nb_errors, BOTTOM)

        # Tamaños iniciales
        self.resizeDocks([self.dock_explorer], [200], Qt.Orientation.Horizontal)
        self.resizeDocks([self.dock_results],  [380], Qt.Orientation.Horizontal)
        self.resizeDocks([self.dock_errors],   [180], Qt.Orientation.Vertical)
 
        
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
        # Refrescar todos los paneles de output
        self.out_lexico.refresh_theme()
 
        for w in (self.out_sint, self.out_sem,
                  self.out_ci, self.out_exec,
                  self.err_lexico, self.err_sint, self.err_sem):
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
        path = os.path.abspath(path)

        # Si ya esta abierto, solo enfocarlo
        for i in range(self.file_tabs.count()):
            w = self.file_tabs.widget(i)
            if isinstance(w, CodeEditor) and w._file_path == path:
                self.file_tabs.setCurrentIndex(i)
                self._explorer_reveal(path)
                return
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            editor = self._new_tab(path, content)
            editor.document().setModified(False)
            self.lbl_status.setText(f"Abierto: {os.path.basename(path)}")

            # Cargar carpeta padre en explorador si no esta ya cargada
            folder = os.path.dirname(path)
            if self.file_explorer.root_path != folder:
                self.file_explorer.load_folder(folder)
                self.dock_explorer.show()
            self._explorer_reveal(path)
        except Exception as ex:
            QMessageBox.warning(self, "Error al abrir",
                                f"No se pudo abrir:\n{ex}")

    def _explorer_reveal(self, path):
        """Selecciona y hace visible el archivo en el arbol del explorador."""
        root = self.file_explorer.tree.invisibleRootItem()
        self._find_and_select(root, os.path.abspath(path))

    def _find_and_select(self, parent, path):
        for i in range(parent.childCount()):
            item = parent.child(i)
            item_path = item.data(0, Qt.ItemDataRole.UserRole)
            if item_path and os.path.abspath(item_path) == path:
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
        key = w._file_path if w._file_path else id(w)
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
            # Si antes era sin titulo, actualizar clave
            old_key = e._file_path if e._file_path else id(e)
            self._editors.pop(old_key, None)
            e._file_path = path
            self._editors[path] = e
            self._write_file(e, path)

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
        """Importa compilador.py como módulo desde su ruta real."""
        import importlib.util, sys
        compiler_path = resource_path("compilador.py")
        if not os.path.isfile(compiler_path):
            return None, f"[Error] No se encontró 'compilador.py' en:\n{os.path.dirname(compiler_path)}"
        sys.modules.pop("compilador", None)
        spec = importlib.util.spec_from_file_location("compilador", compiler_path)
        mod  = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod, None

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
        self.lbl_status.setText("Ejecutando analisis sintactico...")
        QApplication.processEvents()
        out, err = self._run_compiler("sintactico")
        self._set_output(self.out_sint, out)
        self._set_errors(self.err_sint, err)
        self.nb_results.setCurrentWidget(self.out_sint)
        self.dock_results.show(); self.dock_results.raise_()
        if err and err.strip():
            self.nb_errors.setCurrentWidget(self.err_sint)
            self.dock_errors.show(); self.dock_errors.raise_()
        self.lbl_status.setText("Analisis sintactico completado")

    def _semantico(self):
        self.lbl_status.setText("Ejecutando analisis semantico...")
        QApplication.processEvents()
        out, err = self._run_compiler("semantico")
        self._set_output(self.out_sem, out)
        self._set_errors(self.err_sem, err)
        self.nb_results.setCurrentWidget(self.out_sem)
        self.dock_results.show(); self.dock_results.raise_()
        if err and err.strip():
            self.nb_errors.setCurrentWidget(self.err_sem)
            self.dock_errors.show(); self.dock_errors.raise_()
        self.lbl_status.setText("Analisis semantico completado")

    def _codigo_intermedio(self):
        self.lbl_status.setText("Generando codigo intermedio...")
        QApplication.processEvents()
        out, err = self._run_compiler("intermedio")
        self._set_output(self.out_ci, out)
        self.nb_results.setCurrentWidget(self.out_ci)
        self.dock_results.show(); self.dock_results.raise_()
        self.lbl_status.setText("Codigo intermedio generado")

    def _ejecutar(self):
        self.lbl_status.setText("Ejecutando programa...")
        QApplication.processEvents()
        out, err = self._run_compiler("ejecutar")
        combined = (out or "") + ("\n\n--- Errores ---\n" + err if err else "")
        self._set_output(self.out_exec, combined)
        self.nb_errors.setCurrentWidget(self.out_exec)
        self.dock_errors.show(); self.dock_errors.raise_()
        self.lbl_status.setText("Ejecucion finalizada")
    
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
    app = QApplication(sys.argv)
    app.setStyleSheet(build_stylesheet(C))
    win = IDEMainWindow()
    win.show()
    sys.exit(app.exec())
