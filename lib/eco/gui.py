# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui.ui'
#
# Created: Thu Jul 25 13:34:15 2013
#      by: PyQt4 UI code generator 4.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(979, 737)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.horizontalLayout_3 = QtGui.QHBoxLayout(self.centralwidget)
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.splitter = QtGui.QSplitter(self.centralwidget)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.groupBox_2 = QtGui.QGroupBox(self.splitter)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_2.sizePolicy().hasHeightForWidth())
        self.groupBox_2.setSizePolicy(sizePolicy)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.groupBox_2)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.scrollArea = ScopeScrollArea(self.groupBox_2)
        self.scrollArea.setFrameShape(QtGui.QFrame.StyledPanel)
        self.scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 501, 571))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scrollAreaWidgetContents.sizePolicy().hasHeightForWidth())
        self.scrollAreaWidgetContents.setSizePolicy(sizePolicy)
        self.scrollAreaWidgetContents.setAutoFillBackground(True)
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.verticalLayout_5 = QtGui.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_5.setMargin(0)
        self.verticalLayout_5.setObjectName(_fromUtf8("verticalLayout_5"))
        self.frame = NodeEditor(self.scrollAreaWidgetContents)
        self.frame.setEnabled(True)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setMinimumSize(QtCore.QSize(0, 0))
        self.frame.setBaseSize(QtCore.QSize(0, 0))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        self.frame.setPalette(palette)
        self.frame.setCursor(QtGui.QCursor(QtCore.Qt.IBeamCursor))
        self.frame.setFocusPolicy(QtCore.Qt.WheelFocus)
        self.frame.setAcceptDrops(False)
        self.frame.setAutoFillBackground(False)
        self.frame.setFrameShape(QtGui.QFrame.NoFrame)
        self.frame.setFrameShadow(QtGui.QFrame.Sunken)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.verticalLayout_5.addWidget(self.frame)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout_3.addWidget(self.scrollArea)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.cbShowLangBoxes = QtGui.QCheckBox(self.groupBox_2)
        self.cbShowLangBoxes.setObjectName(_fromUtf8("cbShowLangBoxes"))
        self.horizontalLayout.addWidget(self.cbShowLangBoxes)
        self.label = QtGui.QLabel(self.groupBox_2)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        self.lineEdit = QtGui.QLineEdit(self.groupBox_2)
        self.lineEdit.setObjectName(_fromUtf8("lineEdit"))
        self.horizontalLayout.addWidget(self.lineEdit)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setContentsMargins(-1, 0, -1, -1)
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.label_2 = QtGui.QLabel(self.groupBox_2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalLayout_4.addWidget(self.label_2)
        self.te_pstatus = QtGui.QTextEdit(self.groupBox_2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.te_pstatus.sizePolicy().hasHeightForWidth())
        self.te_pstatus.setSizePolicy(sizePolicy)
        self.te_pstatus.setMaximumSize(QtCore.QSize(16777215, 24))
        self.te_pstatus.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.te_pstatus.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.te_pstatus.setObjectName(_fromUtf8("te_pstatus"))
        self.horizontalLayout_4.addWidget(self.te_pstatus)
        self.verticalLayout_3.addLayout(self.horizontalLayout_4)
        self.groupBox_3 = QtGui.QGroupBox(self.splitter)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_3.sizePolicy().hasHeightForWidth())
        self.groupBox_3.setSizePolicy(sizePolicy)
        self.groupBox_3.setObjectName(_fromUtf8("groupBox_3"))
        self.verticalLayout = QtGui.QVBoxLayout(self.groupBox_3)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.tabWidget = QtGui.QTabWidget(self.groupBox_3)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tab = QtGui.QWidget()
        self.tab.setObjectName(_fromUtf8("tab"))
        self.gridLayout_2 = QtGui.QGridLayout(self.tab)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.graphicsView = QtGui.QGraphicsView(self.tab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.graphicsView.sizePolicy().hasHeightForWidth())
        self.graphicsView.setSizePolicy(sizePolicy)
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(247, 247, 247))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        self.graphicsView.setPalette(palette)
        self.graphicsView.setAutoFillBackground(True)
        self.graphicsView.setObjectName(_fromUtf8("graphicsView"))
        self.gridLayout_2.addWidget(self.graphicsView, 0, 0, 1, 1)
        self.cb_toggle_ws = QtGui.QCheckBox(self.tab)
        self.cb_toggle_ws.setEnabled(True)
        self.cb_toggle_ws.setChecked(False)
        self.cb_toggle_ws.setObjectName(_fromUtf8("cb_toggle_ws"))
        self.gridLayout_2.addWidget(self.cb_toggle_ws, 1, 0, 1, 1)
        self.cb_toggle_ast = QtGui.QCheckBox(self.tab)
        self.cb_toggle_ast.setCheckable(True)
        self.cb_toggle_ast.setChecked(False)
        self.cb_toggle_ast.setObjectName(_fromUtf8("cb_toggle_ast"))
        self.gridLayout_2.addWidget(self.cb_toggle_ast, 2, 0, 1, 1)
        self.cb_fit_ast = QtGui.QCheckBox(self.tab)
        self.cb_fit_ast.setObjectName(_fromUtf8("cb_fit_ast"))
        self.gridLayout_2.addWidget(self.cb_fit_ast, 3, 0, 1, 1)
        self.bt_show_sel_ast = QtGui.QPushButton(self.tab)
        self.bt_show_sel_ast.setObjectName(_fromUtf8("bt_show_sel_ast"))
        self.gridLayout_2.addWidget(self.bt_show_sel_ast, 4, 0, 1, 1)
        self.tabWidget.addTab(self.tab, _fromUtf8(""))
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName(_fromUtf8("tab_2"))
        self.verticalLayout_6 = QtGui.QVBoxLayout(self.tab_2)
        self.verticalLayout_6.setObjectName(_fromUtf8("verticalLayout_6"))
        self.gvStategraph = QtGui.QGraphicsView(self.tab_2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.gvStategraph.sizePolicy().hasHeightForWidth())
        self.gvStategraph.setSizePolicy(sizePolicy)
        self.gvStategraph.setObjectName(_fromUtf8("gvStategraph"))
        self.verticalLayout_6.addWidget(self.gvStategraph)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.btShowWholeGraph = QtGui.QPushButton(self.tab_2)
        self.btShowWholeGraph.setObjectName(_fromUtf8("btShowWholeGraph"))
        self.horizontalLayout_2.addWidget(self.btShowWholeGraph)
        self.leSingleState = QtGui.QLineEdit(self.tab_2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.leSingleState.sizePolicy().hasHeightForWidth())
        self.leSingleState.setSizePolicy(sizePolicy)
        self.leSingleState.setObjectName(_fromUtf8("leSingleState"))
        self.horizontalLayout_2.addWidget(self.leSingleState)
        self.btShowSingleState = QtGui.QPushButton(self.tab_2)
        self.btShowSingleState.setObjectName(_fromUtf8("btShowSingleState"))
        self.horizontalLayout_2.addWidget(self.btShowSingleState)
        self.verticalLayout_6.addLayout(self.horizontalLayout_2)
        self.tabWidget.addTab(self.tab_2, _fromUtf8(""))
        self.tab_3 = QtGui.QWidget()
        self.tab_3.setObjectName(_fromUtf8("tab_3"))
        self.verticalLayout_4 = QtGui.QVBoxLayout(self.tab_3)
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.listWidget = QtGui.QListWidget(self.tab_3)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.listWidget.sizePolicy().hasHeightForWidth())
        self.listWidget.setSizePolicy(sizePolicy)
        self.listWidget.setObjectName(_fromUtf8("listWidget"))
        self.verticalLayout_4.addWidget(self.listWidget)
        self.groupBox = QtGui.QGroupBox(self.tab_3)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.label_4 = QtGui.QLabel(self.groupBox)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.verticalLayout_2.addWidget(self.label_4)
        self.teGrammar = QtGui.QTextEdit(self.groupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.teGrammar.sizePolicy().hasHeightForWidth())
        self.teGrammar.setSizePolicy(sizePolicy)
        self.teGrammar.setObjectName(_fromUtf8("teGrammar"))
        self.verticalLayout_2.addWidget(self.teGrammar)
        self.cb_add_implicit_ws = QtGui.QCheckBox(self.groupBox)
        self.cb_add_implicit_ws.setChecked(True)
        self.cb_add_implicit_ws.setObjectName(_fromUtf8("cb_add_implicit_ws"))
        self.verticalLayout_2.addWidget(self.cb_add_implicit_ws)
        self.label_5 = QtGui.QLabel(self.groupBox)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.verticalLayout_2.addWidget(self.label_5)
        self.tePriorities = QtGui.QTextEdit(self.groupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tePriorities.sizePolicy().hasHeightForWidth())
        self.tePriorities.setSizePolicy(sizePolicy)
        self.tePriorities.setObjectName(_fromUtf8("tePriorities"))
        self.verticalLayout_2.addWidget(self.tePriorities)
        self.btUpdate = QtGui.QPushButton(self.groupBox)
        self.btUpdate.setObjectName(_fromUtf8("btUpdate"))
        self.verticalLayout_2.addWidget(self.btUpdate)
        self.verticalLayout_4.addWidget(self.groupBox)
        self.tabWidget.addTab(self.tab_3, _fromUtf8(""))
        self.verticalLayout.addWidget(self.tabWidget)
        self.horizontalLayout_3.addWidget(self.splitter)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 979, 22))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setObjectName(_fromUtf8("menuFile"))
        self.menuOptions = QtGui.QMenu(self.menubar)
        self.menuOptions.setObjectName(_fromUtf8("menuOptions"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)
        self.actionImport = QtGui.QAction(MainWindow)
        icon = QtGui.QIcon.fromTheme(_fromUtf8("document-import"))
        self.actionImport.setIcon(icon)
        self.actionImport.setObjectName(_fromUtf8("actionImport"))
        self.actionRandomDel = QtGui.QAction(MainWindow)
        self.actionRandomDel.setObjectName(_fromUtf8("actionRandomDel"))
        self.actionUndoRandomDel = QtGui.QAction(MainWindow)
        self.actionUndoRandomDel.setObjectName(_fromUtf8("actionUndoRandomDel"))
        self.actionOpen = QtGui.QAction(MainWindow)
        icon = QtGui.QIcon.fromTheme(_fromUtf8("document-open"))
        self.actionOpen.setIcon(icon)
        self.actionOpen.setObjectName(_fromUtf8("actionOpen"))
        self.actionSave = QtGui.QAction(MainWindow)
        icon = QtGui.QIcon.fromTheme(_fromUtf8("document-save"))
        self.actionSave.setIcon(icon)
        self.actionSave.setObjectName(_fromUtf8("actionSave"))
        self.actionNew = QtGui.QAction(MainWindow)
        icon = QtGui.QIcon.fromTheme(_fromUtf8("document-new"))
        self.actionNew.setIcon(icon)
        self.actionNew.setObjectName(_fromUtf8("actionNew"))
        self.menuFile.addAction(self.actionNew)
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.actionImport)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionSave)
        self.menuOptions.addAction(self.actionRandomDel)
        self.menuOptions.addAction(self.actionUndoRandomDel)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuOptions.menuAction())

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(2)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        self.groupBox_2.setTitle(_translate("MainWindow", "Input", None))
        self.cbShowLangBoxes.setText(_translate("MainWindow", "Show language boxes", None))
        self.label.setText(_translate("MainWindow", "Valid tokens:", None))
        self.label_2.setText(_translate("MainWindow", "Parsing status:", None))
        self.groupBox_3.setTitle(_translate("MainWindow", "Languages", None))
        self.cb_toggle_ws.setText(_translate("MainWindow", "Show whitespace nodes", None))
        self.cb_toggle_ast.setText(_translate("MainWindow", "Show parse tree", None))
        self.cb_fit_ast.setText(_translate("MainWindow", "Fit AST in view", None))
        self.bt_show_sel_ast.setText(_translate("MainWindow", "Show selected text parse tree", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "Parse tree", None))
        self.btShowWholeGraph.setText(_translate("MainWindow", "Show whole graph", None))
        self.btShowSingleState.setText(_translate("MainWindow", "Show single state", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "Stategraph", None))
        self.groupBox.setTitle(_translate("MainWindow", "Language", None))
        self.label_4.setText(_translate("MainWindow", "Grammar:", None))
        self.cb_add_implicit_ws.setText(_translate("MainWindow", "Add implicit whitespaces", None))
        self.label_5.setText(_translate("MainWindow", "Tokenizer rules:", None))
        self.btUpdate.setText(_translate("MainWindow", "Update", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), _translate("MainWindow", "Language", None))
        self.menuFile.setTitle(_translate("MainWindow", "File", None))
        self.menuOptions.setTitle(_translate("MainWindow", "Options", None))
        self.actionImport.setText(_translate("MainWindow", "Import...", None))
        self.actionRandomDel.setText(_translate("MainWindow", "Delete random chars", None))
        self.actionUndoRandomDel.setText(_translate("MainWindow", "Undo random deletion", None))
        self.actionOpen.setText(_translate("MainWindow", "Open...", None))
        self.actionSave.setText(_translate("MainWindow", "Save...", None))
        self.actionNew.setText(_translate("MainWindow", "New", None))

from eco import ScopeScrollArea, NodeEditor