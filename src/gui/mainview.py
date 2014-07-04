#!/usr/bin/env python3
# coding=utf-8

from PySide import QtGui, QtCore
from .toolbox import ToolBox
from .tooloptions import ToolOptions
from .graphicitem import CircuitItem, IOItem
from engine.simulator import Circuit

mainCircuit = Circuit("Main Circuit")

class MainView(QtGui.QGraphicsView):
    """A graphic view representing a circuit schematic, as created by
    the user. This view manages most user interaction, in particular:
    * Adding logic gates & circuits
    * Linking outputs and inputs
    * Translating and rotating elements around
    * Setting input values
    """

    def __init__(self, parent):
        super(MainView, self).__init__(parent)
        # Accept dragged items from the toolbox to the main view.
        self.setAcceptDrops(True)
        # Allow mouseover effects (self.mouseMoveEvent)
        self.setMouseTracking(True)
        scene = QtGui.QGraphicsScene(parent)
        self.setScene(scene)

    def setName(self, item):
        item.name = QtGui.QInputDialog.getText(self,  u'Set name', u'Enter a name for this item:')

    def toggleValue(self, item):
        item.value = not item.value
        
    def contextMenuEvent(self, e):
        """Pops a contextual menu up on right-clicks"""
        item = self.itemAt(e.pos())
        if isinstance(item, CircuitItem) or isinstance(item, IOItem):
            pos = item.mapFromScene(self.mapToScene(e.pos()))
            ioatpos = item.IOAtPos(pos)
            if ioatpos:
                item = ioatpos
            elif isinstance(item, CircuitItem):
                item = item.circuit
            elif isinstance(item, IOItem):
                item = item.plug
            menu = QtGui.QMenu(self)
            menu.addAction("Set name", lambda: self.setName(item))
            if ioatpos and ioatpos.owner == mainCircuit and ioatpos.isInput:
                menu.addAction(str(item.value), lambda: self.toggleValue(item))
            menu.popup(e.globalPos())
            
    def dragEnterEvent(self, e):
        """Accept drag events coming from ToolBox."""
        if isinstance(e.source(), ToolBox):
            e.accept()
        # Refuse drags from anything but our ToolBox
        else:
            e.ignore()

    def dragMoveEvent(self, e):
        """Accept drag move events."""
        e.accept()

    def dropEvent(self, e):
        """Accept drop events."""
        # TODO: Found on the web, maybe a cleaner way exists.
        # it would be better to receive the correct item directly,
        # rather than test some text string.
        model = QtGui.QStandardItemModel()
        model.dropMimeData(
            e.mimeData(),
            QtCore.Qt.CopyAction,
            0,
            0,
            QtCore.QModelIndex())
        name = model.item(0).text()
        item = None
        if name in ['And', 'Or', 'Nand', 'Nor', 'Not', 'Xor', 'Xnor']:
            item = CircuitItem(name, mainCircuit)
        elif name == 'Input Pin':
            item = IOItem(True, mainCircuit)
        elif name == 'Output Pin':
            item = IOItem(False, mainCircuit)
        if item:
            self.scene().addItem(item)
            item.setPos(e.pos())

    def keyPressEvent(self, e):
        """Manages keyboard events, in particular item rotation,
        translation, removal and alignment.
        """
        scene = self.scene()
        selection = scene.selectedItems()
        # ESC, unselect all items
        if e.key() == QtCore.Qt.Key_Escape:
            for item in selection:
                item.setSelected(False)
        # Del, suppression
        if e.key() == QtCore.Qt.Key_Delete:
            for item in selection:
                scene.removeItem(item)
        # <- , anti-clockwise rotation
        elif e.key() == QtCore.Qt.Key_Left:
            group = scene.createItemGroup(selection)
            group.setRotation(group.rotation() - 90)
            scene.destroyItemGroup(group)
        # -> , clockwise rotation
        elif e.key() == QtCore.Qt.Key_Right:
            group = scene.createItemGroup(selection)
            group.setRotation(group.rotation() + 90)
            scene.destroyItemGroup(group)
        # L, left align
        elif e.key() == QtCore.Qt.Key_L:
            left = min([item.scenePos().x() for item in selection])
            for item in selection:
                item.setPos(left, item.scenePos().y())
        # R, right align
        elif e.key() == QtCore.Qt.Key_R:
            right = max([item.scenePos().x() for item in selection])
            for item in selection:
                item.setPos(right, item.scenePos().y())
        # T, top align
        elif e.key() == QtCore.Qt.Key_T:
            top = min([item.scenePos().y() for item in selection])
            for item in selection:
                item.setPos(item.scenePos().x(), top)
        # B, bottom align
        elif e.key() == QtCore.Qt.Key_B:
            bottom = max([item.scenePos().y() for item in selection])
            for item in selection:
                item.setPos(item.scenePos().x(), bottom)

    def mousePressEvent(self, e):
        """When the mouse is pressed over a portion of a graphic item
        that represents an engine.simulator.Plug, that Plug is appended
        to self.connectionData.
        """
        if e.buttons() == QtCore.Qt.RightButton:
            super(MainView, self).mousePressEvent(e)
            return
        self.connStart = None
        self.connEnd = None
        item = self.itemAt(e.pos())
        if item:
            pos = item.mapFromScene(self.mapToScene(e.pos()))
            if isinstance(item, CircuitItem) or isinstance(item, IOItem):
                ioatpos = item.IOAtPos(pos)
                if ioatpos:
                    self.connStart = ioatpos
                    # No super() processing, therefore no dragging
                    return
        # If we didn't click an I/O, we probably wanted to drag the
        # circuit.
        super(MainView, self).mousePressEvent(e)

    def mouseReleaseEvent(self, e):
        """When the mouse is released over an I/O, and was previously
        pressed over another I/O, if one is an input, and the other an
        output, a connection will be created between the two of them.
        """
        if e.buttons() == QtCore.Qt.RightButton:
            super(MainView, self).mousePressEvent(e)
            return
        if self.connStart:
            item = self.itemAt(e.pos())
            if item:
                pos = item.mapFromScene(self.mapToScene(e.pos()))
                if isinstance(item, CircuitItem) or isinstance(item, IOItem):
                    ioatpos = item.IOAtPos(pos)
                    if ioatpos:
                        self.connEnd = ioatpos
        #keeping old drawing code here
                #~ origin = item.mapToScene(
                    #~ item.I_LEFT, i * item.IO_HEIGHT + item.iOffset
                    #~ + item.BODY_OFFSET + item.DIAMETER / 2.)
                #~ end = self.connectionData[0].mapToScene(
                    #~ self.connectionData[0].left,
                    #~ self.connectionData[2] *
                    #~ self.connectionData[0].IO_HEIGHT
                    #~ + self.connectionData[0].oOffset
                    #~ + self.connectionData[0].BODY_OFFSET
                    #~ + self.connectionData[0].DIAMETER / 2.)
                #~ line = QtCore.QLineF(origin, end)
                #~ self.scene().addLine(line)
                #~ item.circuit.inputList[i].connect(
                    #~ self.connectionData[1])
                #~ return

                #~ origin = self.connectionData[0].mapToScene(
                    #~ self.connectionData[0].I_LEFT,
                    #~ self.connectionData[2] *
                    #~ self.connectionData[0].IO_HEIGHT
                    #~ + self.connectionData[0].iOffset
                    #~ + self.connectionData[0].BODY_OFFSET +
                    #~ self.connectionData[0].DIAMETER / 2.)
                #~ end = item.mapToScene(
                    #~ item.left, i * item.IO_HEIGHT + item.oOffset +
                    #~ item.BODY_OFFSET + item.DIAMETER / 2.)
                #~ line = QtCore.QLineF(origin, end)
                #~ self.scene().addLine(line)
                #~ item.circuit.inputList[i].connect(
                    #~ self.connectionData[1])
                #~ return
        if (
                not self.connStart
                or not self.connEnd
                or self.connStart == self.connEnd):
            super(MainView, self).mouseReleaseEvent(e)
            return
        elif (
                self.connStart.owner == TopLevel.TC
                and self.connEnd.owner == TopLevel.TC
                and self.connStart.isInput == self.connEnd.isInput):
            self.toast(
                "Don't connect two global " +
                ("inputs" if self.connStart.isInput else "outputs"))
            return
        elif (
                self.connStart.owner != TopLevel.TC
                and self.connEnd.owner != TopLevel.TC
                and self.connStart.isInput == self.connEnd.isInput):
            self.toast(
                "Don't connect two circuit " +
                ("inputs" if self.connStart.isInput else "outputs"))
            return
        elif ((
                (self.connStart.owner != TopLevel.TC
                    and self.connEnd.owner == TopLevel.TC)
                or (self.connStart.owner == TopLevel.TC
                    and self.connEnd.owner != TopLevel.TC))
                and self.connStart.isInput != self.connEnd.isInput):
            a = "local " if self.connStart.owner != TopLevel.TC else "global "
            b = "input" if self.connStart.isInput else "output"
            c = "global " if a == "local " else "local "
            d = "output" if b == "inputs" else "input"
            self.toast("Don't connect a " + a + b + " with a " + c + d)
            return
        else:
            self.connStart.connect(self.connEnd)
        super(MainView, self).mouseReleaseEvent(e)

    def mouseMoveEvent(self, e):
        """Changes the cursor shape when the mouse hovers over an
        input or output pin.
        """
        item = self.itemAt(e.pos())
        if item:
            pos = item.mapFromScene(self.mapToScene(e.pos()))
            if isinstance(item, CircuitItem) or isinstance(item, IOItem):
                ioatpos = item.IOAtPos(pos)
                if ioatpos:
                    self.setCursor(QtCore.Qt.CursorShape.UpArrowCursor)
                    return
        self.setCursor(QtCore.Qt.CursorShape.ArrowCursor)
        super(MainView, self).mouseMoveEvent(e)

    def toast(self, message):
        """Displays a short-lived informative message."""
        scene = self.scene()
        toast = scene.addText(message)
        QtCore.QTimer.singleShot(1500, lambda: scene.removeItem(toast))
