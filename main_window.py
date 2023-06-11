
from PyQt5.QtWidgets import QWidget, QMainWindow, QActionGroup, QAction, QGridLayout, QTabWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

from qt_material import apply_stylesheet

from utils import getBtnGroup, getCheckBoxGroup
from dataset_page import DatasetPage
from model_page import ModelPage
from eval_page import EvalPage
from train_page import TrainPage 

class MainWindow(QMainWindow):
    def __init__(self, extra, theme):
        super().__init__()
        self.extra_values = extra
        self.theme = theme
        
        logo = QIcon("./icons/robot2.png")
        self.setWindowIcon(logo)
        self.setWindowTitle("GUI Torch")
        self.setGeometry(500, 100, 800, 800)
        self.setup()

    def setup(self):
        self.centralWidget = QWidget()
        self.mainLayout = QGridLayout()
        self.centralWidget.setLayout(self.mainLayout)

        self.setupMenu()
        self.setupBody()
        self.setCentralWidget(self.centralWidget)

    def setupMenu(self):
        menubar = self.menuBar()
        menubar.setGeometry(0, 0, 1501, 30)

        menuSizes = menubar.addMenu("Size")
        action_group = QActionGroup(menuSizes)
        action_group.setExclusive(True)
        for density in map(str, range(-2, 5)):
            action = QAction(self, text=density)
            action.triggered.connect(lambda checked, density=density: self.update_density(density))
            action.setCheckable(True)
            action.setChecked(density == self.extra_values['density_scale'])
            action.setActionGroup(action_group)
            action_group.addAction(action)
            menuSizes.addAction(action)

        menuHelp = menubar.addMenu("Help")

    def actionCalls(self, arg):
        print(arg)

    def setupBody(self):
        self.tabWidget = QTabWidget()
        self.tabWidget.setTabPosition(QTabWidget.West)
        self.tabWidget.setCurrentIndex(1)
        self.tabWidget.setStyleSheet("QTabBar::tab {margin: 50px, 0} ")

        dataPage = DatasetPage()
        self.tabWidget.addTab(dataPage, "Data")
        
        modelPage = ModelPage()
        self.tabWidget.addTab(modelPage, "Model")

        page3 = TrainPage()
        self.tabWidget.addTab(page3, "Training")

        page4 = EvalPage()
        self.tabWidget.addTab(page4, "Evaluation")

        self.mainLayout.addWidget(self.tabWidget, 0, 0)

    def update_density(self, density: str):
        self.extra_values['density_scale'] = density
        apply_stylesheet(
            self,
            theme=self.theme,
            invert_secondary=self.theme.startswith('light'),
            extra=self.extra_values
        )