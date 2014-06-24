#!/usr/bin/env python
# coding=utf-8

from PySide import QtGui, QtCore
from mainView import mainView
from toolBox import toolBox
from toolOptions import toolOptions


class mainWindow(QtGui.QMainWindow):
    """La fenêtre principale de notre application"""
    def __init__(self):
        super(mainWindow, self).__init__()
        self.setWindowTitle("IED Logic Simulator")
        view = mainView(self)               # Une zone de travail
        self.setCentralWidget(view)         # principale.
        toolbox = toolBox()                # Une boîte à outils
        boxDock = QtGui.QDockWidget('Toolbox')  # dans un dock.
        boxDock.setWidget(toolbox)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, boxDock)
        tooloptions = toolOptions()    # Options de l'outil sélectionné
        optionsDock = QtGui.QDockWidget('Tool options')     # dans un dock.
        optionsDock.setWidget(tooloptions)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, optionsDock)

        fileMenu = QtGui.QMenu('File')
        fileMenu.addAction('Quit', self.close)
        self.menuBar().addMenu(fileMenu)
        helpMenu = QtGui.QMenu('Help')
        helpMenu.addAction('Documentation')
        helpMenu.addAction('About', self.about)
        self.menuBar().addMenu(helpMenu)
        self.show()

    def about(self):
        """Affiche un dialogue d'informations sur le programme"""
        msgBox = QtGui.QMessageBox()
        msgBox.setText(u'v0.1\nPar Mathieu Fourcroy & Sébastien Magnien.')
        msgBox.exec_()
