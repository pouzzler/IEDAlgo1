#!/usr/bin/env python3
# coding=utf-8

from math import atan2, pi, pow, sqrt
from PySide.QtCore import QPointF, QRectF, Qt
from PySide.QtGui import (
    QBrush, QColor, QFont, QGraphicsItem, QGraphicsPathItem, 
    QGraphicsSimpleTextItem, QImage, QPainterPath, QPen, QStyle)
from .util import filePath
from engine.simulator import Circuit, Plug


class WireItem(QGraphicsPathItem):
    """Represents an electrical wire connecting two items."""

    RADIUS = 2.5

    def __init__(self, startIO, points, endIO=None):
        """Handles two use cases:
        __init__(self, startIO, onePoint, None) to create a Wire.
        __init__(self, startIO, pointList, endIO) to load from file.
        """
        super(WireItem, self).__init__()
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        # Remembering the Plug where the WireItem starts, for creating the
        # connection, when the last segment is drawn over another IO.
        self.startIO = startIO
        self.endIO = endIO
        # The first point of our segments. The "moving point" used to
        # redraw during mouseMove events.
        self.points = (
            points if isinstance(points, list) else [points, points])
        # We dont want't to catch the WireItem handle when it is connected
        # to a Plug, this puts our item under the Plug, and itemAt()
        # will grab the Plug.
        self.setZValue(-1)
        self.complete = True if endIO else False

    def addPoint(self):
        """Duplicates the end point, for use as a moving point during moves."""
        self.points.append(self.points[-1])

    def connect(self, endIO):
        """Try to connect the end points of the Wire."""
        if not self.startIO.connect(endIO):
            return False
        else:
            self.endIO = endIO
            self.complete = True
            self.setupPaint()
            return True

    def handleAtPos(self, pos):
        """Is there an interactive handle where the mouse is?"""
        if self.complete:
            return
        path = QPainterPath()
        path.addEllipse(self.points[-1], self.RADIUS, self.RADIUS)
        return path.contains(pos)

    def moveLastPoint(self, endPoint):
        """Redraw the last, unfinished segment while the mouse moves."""
        sq2 = sqrt(2) / 2
        A = [[0, 1], [sq2, sq2], [1, 0], [sq2, -sq2],
            [0, -1], [-sq2, -sq2], [-1, 0], [-sq2, sq2]]
        x = self.points[-2].x()
        y = self.points[-2].y()
        L = sqrt(pow(endPoint.x() - x, 2) + pow(endPoint.y() - y, 2))
        angle = atan2(endPoint.x() - x, endPoint.y() - y)
        a = round(8 * angle / (2 * pi)) % 8
        self.points[-1] = QPointF(x + A[a][0] * L, y + A[a][1] * L)
        self.setupPaint()

    def setupPaint(self):
        """Draw the wire segments and handle."""
        self.setPen(QPen(QBrush(QColor(QColor('black'))), 2))
        path = QPainterPath()
        path.moveTo(self.points[0])
        for p in self.points[1:]:
            path.lineTo(p)
        if not self.complete:
            path.addEllipse(self.points[-1], self.RADIUS, self.RADIUS)
        self.setPath(path)

    def removeLast(self):
        """Remove the last segment (user corrects user errors)."""
        if self.complete:
            return
        scene = self.scene()
        scene.removeItem(self)
        self.points = self.points[0:-2]
        if len(self.points) > 1:
            self.addPoint()
            self.setupPaint()
            scene.addItem(self)

class PlugItem(QGraphicsPathItem):
    """Graphical wrapper around the engine Plug class."""

    LARGE_DIAMETER = 25
    SMALL_DIAMETER = 5
    VALUE_OFFSET = 8
    NAME_OFFSET = LARGE_DIAMETER + 1

    def __init__(self, isInput, owner):
        super(PlugItem, self).__init__()
        self.item = Plug(isInput, None, owner)
        self.showName = False
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setAcceptsHoverEvents(True)
        self.oldPos = QPointF(0, 0)
        self.ignoreChange = False
        # This path is needed at each mouse over event, to check if
        # the mouse is over a pin. We save it as an instance field,
        # rather than recreate it at each event.
        self.pinPath = QPainterPath()
        self.pinPath.addEllipse(
            self.LARGE_DIAMETER - self.SMALL_DIAMETER,
            self.LARGE_DIAMETER / 2 - self.SMALL_DIAMETER,
            self.SMALL_DIAMETER * 2,
            self.SMALL_DIAMETER * 2)
        f = QFont('Times', 12, 75)
        # Won't rotate when we rotate our PlugItem.
        self.name = QGraphicsSimpleTextItem(self)
        self.name.setFlag(QGraphicsItem.ItemIgnoresTransformations)
        self.name.setText(self.item.name)
        self.name.setFont(f)
        self.value = QGraphicsSimpleTextItem(self)
        self.value.setFlag(QGraphicsItem.ItemIgnoresTransformations)
        self.value.setPos(self.VALUE_OFFSET, self.VALUE_OFFSET)
        self.value.setFlag(QGraphicsItem.ItemStacksBehindParent)
        self.value.setFont(f)
        self.setupPaint()

    def handleAtPos(self, pos):
        """Is there an interactive handle where the mouse is?
        Also return the Plug under this handle.
        """
        return self.item if self.pinPath.contains(pos) else None

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            p = value - self.oldPos
            if (p.manhattanLength() > 10):
                if self.ignoreChange:
                    self.ignoreChange = False
                    return
                else:
                    self.ignoreChange = True
                self.oldPos = value
                #~ self.setPos(300, 300)
        return QGraphicsItem.itemChange(self, change, value)

    def setCategoryVisibility(self, isVisible):
        """MainView requires PlugItems to function like CircuitItems."""
        pass

    def setNameVisibility(self, isVisible):
        """Shows/Hide the item name in the graphical view."""
        self.showName = isVisible
        self.setupPaint()

    def setupPaint(self):
        """Offscreen rather than onscreen redraw (few changes)."""
        path = QPainterPath()
        if self.item.isInput:
            path.addEllipse(0, 0, self.LARGE_DIAMETER, self.LARGE_DIAMETER)
        else:
            path.addRect(0, 0, self.LARGE_DIAMETER, self.LARGE_DIAMETER)
        path.addEllipse(
            self.LARGE_DIAMETER + 1,
            (self.LARGE_DIAMETER - self.SMALL_DIAMETER) / 2,
            self.SMALL_DIAMETER,
            self.SMALL_DIAMETER)
        self.setPath(path)
        br = self.mapToScene(self.boundingRect())
        realX = min([item.x() for item in br])
        realY = min([item.y() for item in br])
        self.name.setVisible(self.showName)
        self.name.setText(self.item.name)
        self.name.setPos(self.mapFromScene(realX, realY + self.NAME_OFFSET))
        self.value.setText(str(int(self.item.value)))
        self.value.setPos(self.mapFromScene(
            realX + self.VALUE_OFFSET, realY + self.VALUE_OFFSET))
        self.value.setBrush(QColor('green' if self.item.value else 'red'))
        self.update()       # Force onscreen redraw after changes.


class CircuitItem(QGraphicsItem):
    """Graphical wrapper around the engine Circuit class."""

    textH = 12
    ioH = 10
    ioW = 20
    radius = 2.5

    def __init__(self, circuitClass, owner):
        super(CircuitItem, self).__init__()
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.showName = True
        self.showCategory = False
        imgDir = filePath('icons/')
        self.item = owner.add_circuit(circuitClass)
        self.image = QImage(imgDir + circuitClass.__name__ + '.png')
        if not self.image:
            self.image = QImage(imgDir + 'Default.png')
            self.showCategory = True
        self.setupPaint()

    def boundingRect(self):
        """Qt requires overloading this when overloading QGraphicsItem."""
        H = self.maxH
        W = 4 * self.radius + 2 * self.ioW + self.imgW
        if self.showCategory:
            H = H + 2 * self.textH
        elif self.showName:
            H = H + self.textH
        return QRectF(0, 0, W, H)

    def handleAtPos(self, pos):
        """Is there an interactive handle where the mouse is?
        Also return the Plug under this handle.
        """
        for i in range(self.nIn):
            if self.inputPaths[i].contains(pos):
                return self.item.inputList[i]
        for i in range(self.nOut):
            if self.outputPaths[i].contains(pos):
                return self.item.outputList[i]

    def paint(self, painter, option, widget):
        """Draws the item."""
        painter.setPen(QPen(QColor('black'), 2))
        for i in range(self.nIn):   # Handles drawn 'by hand'.
            painter.drawPath(self.inputPaths[i])
            painter.drawLine(
                2 * self.radius,
                i * self.ioH + self.inOff + self.radius,
                2 * self.radius + self.ioW,
                i * self.ioH + self.inOff + self.radius)
        painter.drawLine(
            2 * self.radius + self.ioW,
            self.inOff + self.radius,
            2 * self.radius + self.ioW,
            (self.nIn - 1) * self.ioH + self.inOff + self.radius)
        for i in range(self.nOut):
            painter.drawPath(self.outputPaths[i])
            painter.drawLine(
                2 * self.radius + self.ioW + self.imgW,
                i * self.ioH + self.outOff + self.radius,
                2 * self.radius + 2 * self.ioW + self.imgW,
                i * self.ioH + self.outOff + self.radius)
        painter.drawLine(
            2 * self.radius + self.ioW + self.imgW,
            self.outOff + self.radius,
            2 * self.radius + self.ioW + self.imgW,
            (self.nOut - 1) * self.ioH + self.outOff + self.radius)
        painter.drawImage(
            QRectF(
                2 * self.radius + self.ioW,
                self.imgOff,
                self.imgW,
                self.imgH),
            self.image)                 # Body drawn from a png.
        f = QFont('Times')              # Draw name & category.
        f.setPixelSize(self.textH)
        painter.setFont(f)
        if self.showName:
            painter.setPen(QPen(QColor('red')))
            painter.drawText(
                QPointF(0, self.maxH + self.textH),
                self.item.name)
        if self.showCategory:
            painter.setPen(QPen(QColor('green')))
            painter.drawText(
                QPointF(0, self.maxH + 2 * self.textH), (
                    self.item.category if self.item.category 
                    else self.item.__class__.__name__))
        # Default selection box doesn't work; simple reimplementation.
        if option.state & QStyle.State_Selected:
            pen = QPen(Qt.black, 1, Qt.DashLine)
            painter.setPen(pen)
            painter.drawRect(self.boundingRect())

    def setCategoryVisibility(self, isVisible):
        """Show/Hide circuit category (mostly useful for user circuits)."""
        self.showCategory = isVisible
        self.setupPaint()

    def setNameVisibility(self, isVisible):
        """Shows/Hide the item name in the graphical view."""
        self.showName = isVisible
        self.setupPaint()

    def setNbInputs(self, nb):
        """Add/Remove inputs (for logical gates)."""
        if nb > self.item.nb_inputs():
            for x in range(nb - self.item.nb_inputs()):
                Plug(True, None, self.item)
        elif nb < self.item.nb_inputs():
            for x in range(self.item.nb_inputs() - nb):
                self.item.remove_input(self.item.inputList[0])
        self.setupPaint()

    def setupPaint(self):
        """Offscreen rather than onscreen redraw (few changes)."""
        self.nIn = self.item.nb_inputs()
        self.nOut = self.item.nb_outputs()
        # 3 sections with different heights must be aligned :
        self.imgH = self.image.size().height()   # central (png image)
        self.imgW = self.image.size().width()
        self.inH = (self.nIn - 1) * self.ioH + 2 * self.radius  # inputs
        self.outH = (self.nOut - 1) * self.ioH + 2 * self.radius    # outputs
        # therefore we calculate a vertical offset for each section :
        self.maxH = max(self.imgH, self.inH, self.outH)
        self.imgOff = (
            0 if self.maxH == self.imgH else (self.maxH - self.imgH) / 2.)
        self.inOff = (
            0 if self.maxH == self.inH else (self.maxH - self.inH) / 2.)
        self.outOff = (
            0 if self.maxH == self.outH else (self.maxH - self.outH) / 2.)
        # i/o mouseover detection. Create once, use on each mouseMoveEvent.
        self.inputPaths = []
        self.outputPaths = []
        for i in range(self.nIn):
            path = QPainterPath()
            path.addEllipse(
                0,
                i * self.ioH + self.inOff,
                2 * self.radius,
                2 * self.radius)
            self.inputPaths.append(path)
        for i in range(self.nOut):
            path = QPainterPath()
            path.addEllipse(
                2 * self.radius + 2 * self.ioW + self.imgW,
                i * self.ioH + self.outOff,
                2 * self.radius,
                2 * self.radius)
            self.outputPaths.append(path)
        self.prepareGeometryChange()
        self.update()       # Force onscreen redraw after changes.
