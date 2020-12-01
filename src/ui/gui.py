from PyQt5.QtWidgets import (QApplication, QWidget, QTextEdit, QLineEdit, QPushButton, QHBoxLayout, QShortcut,
                             QVBoxLayout, QGridLayout, QFrame, QToolBar, QTabWidget, QLabel, QAction, QMainWindow)
from PyQt5.QtCore import Qt

from assemtrix import game
from modes import mode, classic
import sys

def run_gui(argv):
    app = QApplication(argv)

    main_window = MainWindow(classic.ClassicMode())
    main_window.show()
    sys.exit(app.exec_())


class MainWindow(QMainWindow):
    def __init__(self, _mode, parent=None):
        QWidget.__init__(self, parent)
        self.mode = _mode
        self.game = None
        self.isGameRunning = False
        self.InitUI()

    def InitUI(self):
        # initialize UI actions
        self.InitAction()

        # initialize window
        self.InitWindow()

    def InitAction(self):
        # Game Start
        self.gameStartAction = QAction("Start", self)
        self.gameStartAction.setShortcut('F3')
        self.gameStartAction.setStatusTip('Start Game')
        self.gameStartAction.triggered.connect(self.onGameStart)

        # Game Shutdown
        self.gameShutdownAction = QAction("Shut Down", self)
        self.gameShutdownAction.setShortcut('F4')
        self.gameShutdownAction.setStatusTip('Shutdown Game')
        self.gameShutdownAction.triggered.connect(self.onGameShutdown)

        # Game Reset
        self.gameResetAction = QAction("Reset", self)
        self.gameResetAction.setShortcut('F5')
        self.gameResetAction.setStatusTip('Restart Game')
        self.gameResetAction.triggered.connect(self.onGameReset)

        # Game proceed until the end
        self.gameRepeatAction = QAction("Run Until...", self)
        self.gameRepeatAction.setShortcut('F9')
        self.gameRepeatAction.setStatusTip('Run until the game ends')

        self.toolbar = self.addToolBar('ToolBar')
        self.toolbar.addActions((self.gameStartAction, self.gameResetAction,
                                 self.gameShutdownAction, self.gameRepeatAction))
        self.statusBar().showMessage('Hi!')


    def InitWindow(self):
        # initialize game window
        self.mainLayout = QHBoxLayout(self)
        self.memoryWindow = MemoryWindow(classic.ClassicMode().default_map, self)
        self.memoryWindow.setEnabled(False)
        self.memoryWindow.setVisible(False)
        self.inputWindow = QVBoxLayout(self)


        # initialize inputWindow
        self.inputText = QLineEdit()
        self.inputText.setPlaceholderText("<op> [addr1] [addr2]")

        self.displayText = QLineEdit()
        self.displayText.setReadOnly(True)

        self.inputButton = QPushButton("input")
        self.inputButton.setShortcut('Return')
        self.inputButton.clicked.connect(self.onInput)

        self.processButton = QPushButton("proceed")
        self.processButton.setShortcut('\\')
        self.processButton.clicked.connect(self.onProcess)

        bbox = QHBoxLayout()
        bbox.addStretch(1)
        bbox.addWidget(self.processButton)
        bbox.addWidget(self.inputButton)


        self.inputWindow.addWidget(self.displayText)
        self.inputWindow.addWidget(self.inputText)
        self.inputWindow.addLayout(bbox)
        self.inputWindow.setEnabled(False)
        self.inputWindow.addStretch(1)

        # assign layout
        self.mainLayout.addWidget(self.memoryWindow, stretch=2)
        self.mainLayout.addLayout(self.inputWindow)
        centralWidget = QWidget()
        centralWidget.setLayout(self.mainLayout)
        self.setCentralWidget(centralWidget)

        # set window geometry
        self.setGeometry(300, 150, 300, 150)
        self.setWindowTitle('Assem-Trix')
        self.show()



    def onGameStart(self):
        if self.isGameRunning:
            return

        self.game = game.AssemTrixGame(self.mode)
        self.memoryWindow.reset(self.game.game_map)
        self.memoryWindow.setEnabled(True)
        self.memoryWindow.setVisible(True)
        self.inputWindow.setEnabled(True)
        self.isGameRunning = True

    def onGameReset(self):
        if not self.isGameRunning:
            return
        self.onGameEnd()
        self.onGameStart()

    def onGameShutdown(self):
        if not self.isGameRunning:
            return

        self.memoryWindow.setEnabled(False)
        self.memoryWindow.setVisible(False)
        self.inputWindow.setEnabled(False)
        self.isGameRunning = False

    def onInputChanged(self):
        pass

    def onInput(self):
        if not self.isGameRunning:
            return

        text = self.inputText.text()
        try:
            result = self.game.inst_input(0, text)
        except Exception as e:
            print(type(e), e)
            return
        self.inputText.clear()
        self.displayText.setText(str(result))
        self.memoryWindow.updateMemory()

    def onProcess(self):
        if not self.isGameRunning:
            return
        self.game.step()

    def onRepetition(self):
        pass


class MemoryWindow(QWidget):
    def __init__(self, _map, parent=None):
        super().__init__(parent)
        self.memoryGrid = QGridLayout(self)
        self.memoryGrid.setSpacing(0)
        self.reset(_map)

        self.show()

    def get_map_size(self):
        return self.x, self.y

    def reset(self, _map: game.MemoryMap):
        self._map = _map
        self.x = _map.x
        self.y = _map.y
        self.memoryFrames = [[self.MemoryFrame(self) for j in range(self.y)] for i in range(self.x)]

        for i in range(self.y):
            for j in range(self.x):
                self.memoryGrid.addWidget(self.memoryFrames[i][j], i, j, Qt.AlignCenter)

        self.updateMemory()

    def updateMemory(self):
        for i in range(self.y):
            for j in range(self.x):
                self.memoryFrames[i][j].setText(str(int(self._map.memory[i][j])))


    class MemoryFrame(QPushButton):
        style_default = "background-color: white;"

        def __init__(self, parent):
            super().__init__(parent)
            self.setContentsMargins(0,0,0,0)
            self.setMaximumSize(50,50)
            self.setStyleSheet(MemoryWindow.MemoryFrame.style_default)



