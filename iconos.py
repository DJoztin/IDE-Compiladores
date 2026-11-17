"""
iconos.py — Íconos vectoriales del IDE (sin emojis ni archivos de imagen).

Cada ícono se dibuja con QPainter en el color que se pida, así se adapta a
los 6 temas. Uso:

    from iconos import icono
    boton.setIcon(icono("guardar", "#d4d4d4"))
"""
from PyQt6.QtCore import Qt, QPointF, QRectF
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QPen, QColor, QPolygonF, QPainterPath

_ESCALA = 2          # se dibuja al doble para que se vea nítido en pantallas HiDPI
_TAM = 16
_cache: dict = {}


def _poligono(*pts):
    return QPolygonF([QPointF(x, y) for x, y in pts])


def _dibujar(p: QPainter, nombre: str, c: QColor):
    pen = QPen(c, 1.4)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    p.setPen(pen)
    p.setBrush(Qt.BrushStyle.NoBrush)
    relleno = lambda: p.setBrush(c)

    if nombre == "ejecutar":                       # triángulo ▷ relleno
        relleno()
        p.drawPolygon(_poligono((4.5, 2.5), (13, 8), (4.5, 13.5)))
    elif nombre == "detener":                      # cuadrado relleno
        relleno()
        p.drawRoundedRect(QRectF(3.5, 3.5, 9, 9), 1.2, 1.2)
    elif nombre == "paso":                         # triángulo + barra
        relleno()
        p.drawPolygon(_poligono((3, 3), (10, 8), (3, 13)))
        p.drawRect(QRectF(11.2, 3, 1.8, 10))
    elif nombre == "reiniciar":                    # flecha circular
        p.drawArc(QRectF(3, 3, 10, 10), 60 * 16, 290 * 16)
        relleno()
        p.drawPolygon(_poligono((9.6, 1.6), (13.6, 3.6), (10.2, 6.4)))
    elif nombre == "guardar":                      # disquete
        p.drawRoundedRect(QRectF(2.5, 2.5, 11, 11), 1.2, 1.2)
        p.drawRect(QRectF(5, 2.5, 6, 3.5))
        p.drawRect(QRectF(4.5, 9, 7, 4.5))
    elif nombre == "copiar":                       # dos hojas
        p.drawRoundedRect(QRectF(5.5, 5.5, 8, 8.5), 1, 1)
        p.drawPolyline(_poligono((10.5, 3.5), (10.5, 2.5), (2.5, 2.5), (2.5, 11), (3.5, 11)))
    elif nombre == "exportar":                     # bandeja con flecha
        p.drawPolyline(_poligono((2.5, 9), (2.5, 13.5), (13.5, 13.5), (13.5, 9)))
        p.drawLine(QPointF(8, 2.5), QPointF(8, 10))
        p.drawPolyline(_poligono((5, 5.5), (8, 2.5), (11, 5.5)))
    elif nombre == "carpeta":
        path = QPainterPath()
        path.moveTo(2, 4)
        path.lineTo(6.5, 4)
        path.lineTo(8, 5.5)
        path.lineTo(14, 5.5)
        path.lineTo(14, 13)
        path.lineTo(2, 13)
        path.closeSubpath()
        p.drawPath(path)
    elif nombre == "expandir":                     # flechas que se separan
        p.drawLine(QPointF(8, 2), QPointF(8, 14))
        p.drawPolyline(_poligono((5, 5), (8, 2), (11, 5)))
        p.drawPolyline(_poligono((5, 11), (8, 14), (11, 11)))
    elif nombre == "colapsar":                     # flechas que se juntan
        p.drawLine(QPointF(3, 8), QPointF(13, 8))
        p.drawPolyline(_poligono((5, 2.5), (8, 5.5), (11, 2.5)))
        p.drawPolyline(_poligono((5, 13.5), (8, 10.5), (11, 13.5)))
    elif nombre == "ventana":                      # ventana con barra de título
        p.drawRoundedRect(QRectF(2.5, 3, 11, 10), 1.2, 1.2)
        p.drawLine(QPointF(2.5, 6), QPointF(13.5, 6))
    elif nombre == "comparar":                     # dos paneles
        p.drawRoundedRect(QRectF(2, 3, 5.5, 10), 1, 1)
        p.drawRoundedRect(QRectF(8.5, 3, 5.5, 10), 1, 1)
    elif nombre == "panel":                        # ventana con panel lateral
        p.drawRoundedRect(QRectF(2, 3, 12, 10), 1.2, 1.2)
        relleno()
        p.drawRect(QRectF(9.5, 3.5, 4, 9))
    elif nombre == "aviso":                        # triángulo con "!"
        p.drawPolygon(_poligono((8, 2), (14.5, 13.5), (1.5, 13.5)))
        p.drawLine(QPointF(8, 6), QPointF(8, 9.5))
        relleno()
        p.drawEllipse(QPointF(8, 11.6), 0.7, 0.7)
    elif nombre == "limpiar":                      # X
        p.drawLine(QPointF(4, 4), QPointF(12, 12))
        p.drawLine(QPointF(12, 4), QPointF(4, 12))
    elif nombre == "ok":                           # palomita
        p.drawPolyline(_poligono((3, 8.5), (6.5, 12), (13, 4.5)))
    elif nombre == "error":                        # círculo con X
        p.drawEllipse(QRectF(2, 2, 12, 12))
        p.drawLine(QPointF(5.8, 5.8), QPointF(10.2, 10.2))
        p.drawLine(QPointF(10.2, 5.8), QPointF(5.8, 10.2))
    elif nombre == "codigo":                       # < >
        p.drawPolyline(_poligono((6, 4), (2.5, 8), (6, 12)))
        p.drawPolyline(_poligono((10, 4), (13.5, 8), (10, 12)))
    else:
        p.drawRect(QRectF(3, 3, 10, 10))


def pixmap(nombre: str, color: str, tam: int = _TAM) -> QPixmap:
    clave = (nombre, color, tam)
    if clave in _cache:
        return _cache[clave]
    pm = QPixmap(tam * _ESCALA, tam * _ESCALA)
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.scale(tam * _ESCALA / _TAM, tam * _ESCALA / _TAM)
    _dibujar(p, nombre, QColor(color))
    p.end()
    pm.setDevicePixelRatio(_ESCALA)
    _cache[clave] = pm
    return pm


def icono(nombre: str, color: str) -> QIcon:
    return QIcon(pixmap(nombre, color))
