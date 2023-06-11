from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QSpinBox, QDoubleSpinBox, QGroupBox, QComboBox, QGridLayout, QLineEdit
from torchvision.datasets import ImageFolder
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from torch.utils.data import random_split
from torch.utils.data.dataloader import DataLoader

import math

import utils
import model_utils
import data_utils

class FigureTool(QGroupBox):
    def __init__(self):
        super().__init__("Logs")
        self.fig_loss = plt.Figure()
        self.fig_acc = plt.Figure()

        self.ax_loss = self.fig_loss.add_subplot(111)
        self.ax_acc = self.fig_acc.add_subplot(111)
        self.canvas_loss = FigureCanvas(self.fig_loss)
        self.canvas_acc = FigureCanvas(self.fig_acc)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.canvas_loss)
        layout.addWidget(self.canvas_acc)
        self.setLayout(layout)

        self.epochs, self.train_loss, self.val_loss, self.val_acc = [], [], [], []
        self.epoch = 1
        self.demo_mode = False

    def demo(self):
        self.epochs = [i for i in range(1, 21)]
        self.train_loss = [2.7242, 1.5232, 1.0987, 0.8508, 0.6742, 0.5346, 0.4328, 0.3470, 0.2697, 0.2203,
                      0.1790, 0.1481, 0.1190, 0.0950, 0.0823, 0.0656, 0.0618, 0.0531, 0.0531, 0.0450]
        self.val_loss = [1.8789, 1.3625, 1.1306, 1.0211, 0.9465, 0.9108, 0.9318, 0.8633, 0.8630, 0.8796,
                    0.8602, 0.8460, 0.8709, 0.8775, 0.8710, 0.9006, 0.8573, 0.9101, 0.8790, 0.8850]
        self.val_acc = [0.5482, 0.6569, 0.6949, 0.7330, 0.7448, 0.7581, 0.7486, 0.7585, 0.7647, 0.7513,
                   0.7627, 0.7630, 0.7656, 0.7508, 0.7709, 0.7539, 0.7714, 0.7634, 0.7681, 0.7629]    
        self.demo_mode = True
        self.update_fig()
        self.ax_loss.set_title('Demo')
        self.ax_acc.set_title('Demo')

    def update_fig(self):
        self.ax_loss.plot(self.epochs, self.train_loss, label='Train Loss')
        self.ax_loss.plot(self.epochs, self.val_loss, label='Validation Loss')
        self.ax_loss.legend()
        self.ax_loss.set_xlabel('Epochs')
        self.ax_loss.set_ylabel('Loss')

        self.ax_acc.plot(self.epochs, self.val_acc, label='Validation Accuracy')
        self.ax_acc.legend()
        self.ax_acc.set_xlabel('Epochs')
        self.ax_acc.set_ylabel('Accuracy')
    
    def append_data(self, train_loss, valid_loss, valid_acc):
        if self.demo_mode:  # 如果使用了演示数据，先去除演示的数据
            del self.epochs[:]
            del self.train_loss[:]
            del self.val_loss[:]
            del self.val_acc[:]
            self.demo_mode = False

        self.epochs.append(self.epoch)
        self.epoch += 1
        self.train_loss.append(train_loss)
        self.valid_loss.append(valid_loss)
        self.valid_acc.append(valid_acc)
        self.update_fig()


class OptionTools(QGroupBox):
    def __init__(self, parent=None, datasize=0):
        super(OptionTools, self).__init__("Options", parent)

        self.datasize = datasize
        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.batch_size = QSpinBox(self)
        self.batch_size.setValue(16)
        self.learning_rate = QLineEdit(self)
        self.learning_rate.setText("0.0006")
        self.epochs = QSpinBox(self)
        self.epochs.setValue(10)

        self.datasize_label = QLabel(f"dataset left: {datasize}")
        self.train_split = QDoubleSpinBox(self)
        self.train_split.setRange(0, 100)
        self.train_split.setValue(90)
        self.train_split.setSuffix(" %")
        self.train_split.valueChanged.connect(self.split_data)
        self.valid_split = QLabel("0 %")

        self.confirm_btn = QPushButton("Confirm")
        
        self.layout.addWidget(QLabel("batch size: ", self), 0, 0, 1, 1)
        self.layout.addWidget(self.batch_size, 0, 1, 1, 1)
        self.layout.addWidget(QLabel("learning rate", self), 1, 0, 1, 1)
        self.layout.addWidget(self.learning_rate, 1, 1, 1, 1)
        self.layout.addWidget(QLabel("epochs"), 2, 0, 1, 1)
        self.layout.addWidget(self.epochs, 2, 1, 1, 1)

        self.layout.addWidget(self.datasize_label, 3, 0, 1, 2)
        self.layout.addWidget(QLabel("train"), 4, 0, 1, 1)
        self.layout.addWidget(self.train_split, 4, 1, 1, 1)
        self.layout.addWidget(QLabel("validation"), 5, 0, 1, 1)
        self.layout.addWidget(self.valid_split, 5, 1, 1, 1)

    def split_data(self):
        train_split = self.train_split.value()
        # Calculate remaining data size and update label
        remain = 100 - train_split
        self.valid_split.setText(f'{remain} %')

    def freeze_split(self):
        self.train_split.setEnabled(False)

class SelBox(QWidget):
    def __init__(self, selections, confirm_callback):
        super().__init__()
        # self.setStyleSheet("background-color: #232629")
        self.confirm_callback = confirm_callback

        self.setLayout(QGridLayout())
        self.item_select = QComboBox()
        self.item_select.addItems(selections)
        self.item_select.mousePressEvent = self.update_selection
        self.item_select_hint = QLabel("not loaded")
        self.item_select_hint.setStyleSheet("margin-left: 20px")
        self.load_btn = QtWidgets.QPushButton("Load")
        self.load_btn.clicked.connect(self.confirm_selection)
        self.load_btn.setStyleSheet("height: .7em; width: 1em")
        self.layout().addWidget(self.item_select, 0, 0, 1 ,2)
        self.layout().addWidget(self.item_select_hint, 1, 0, 1, 1)
        self.layout().addWidget(self.load_btn, 1, 1, 1, 1)

    def update_selection(self, event):
        pass

    def confirm_selection(self):
        self.item_select_hint.setText("Loaded")
        if self.confirm_callback is not None:
            self.confirm_callback(self.item_select.currentText())

class TrainPage(QWidget):
    def __init__(self):
        super(TrainPage, self).__init__()
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.setStyleSheet("QComboBox { color: gray; } QComboBox:focus { color: #ffd740; } ")

        model_box = SelBox([utils.get_config('model')], confirm_callback=self.update_model)
        data_box = SelBox([utils.get_config('dataset_path')], confirm_callback=self.update_dataset)
        self.log_area = FigureTool()
        self.log_area.demo()

        self.layout.addWidget(model_box, 0, 0, 1, 1)
        self.layout.addWidget(data_box, 1, 0, 1, 1)
        self.layout.addWidget(self.log_area, 0, 1, 4, 2)

        self.dataset_path = None
        self.dataset = None
        self.model = None
        self.transforms = None
        self.train_ds = None

    def update_model(self, text):
        self.model = model_utils.load_cls_model(text, pretrained=False)
        self.ready()

    def update_dataset(self, text):
        self.dataset_path = utils.get_config('dataset_path')
        config = utils.get_config()
        
        self.train_config = OptionTools(self, len(ImageFolder(self.dataset_path)))
        self.layout.addWidget(self.train_config, 2, 0, 3, 1)
        self.ready()

    def ready(self):
        if self.model is None or  self.dataset_path is None:
            return

        if self.transforms is None:
            config = utils.get_config()
            config['to_tensor'] = True
            self.transforms = data_utils.get_transforms_from_config(config)
            self.dataset = ImageFolder(self.dataset_path, transform=self.transforms)

        self.start_btn = QPushButton("Start")
        self.start_btn.clicked.connect(self.start)
        self.layout.addWidget(self.start_btn, 4, 1, 1, 1)

    def start(self):
        lr = eval(self.train_config.learning_rate.text())
        if self.train_ds is None:
            size = self.train_config.datasize
            train_data_size = int(self.train_config.train_split.value()/100 * size // 1)
            valid_data_size = size - train_data_size
            test_data_szie = 0
            self.train_config.freeze_split()

            self.train_ds, self.val_ds, self.test_ds = random_split(
                self.dataset, [train_data_size, valid_data_size, test_data_szie])
            print(f"train_size: {len(self.train_ds)}, validation_size: "+\
                f"{len(self.val_ds)}, test_size: {len(self.test_ds)}")

            self.train_wrapper = model_utils.TrainingWrapper(
                self.model, self.train_ds, self.val_ds, learning_rate=lr, callback=slef.update_logs)

        self.start_btn.setText("Pause")
        self.start_btn.clicked.connect(self.pause)

        batch_size = self.train_config.batch_size.value()
        lr = eval(self.train_config.learning_rate.text())

        epochs = self.train_config.epochs.value()
        self.train_wrapper.start_training(epochs, lr, batch_size)
        
    def pause(self):
        self.train_wrapper.pause_training()
        self.start_btn.setText("Resume")
        self.start_btn.clicked.connect(self.start)
    
    def update_logs(self, data):
        self.log_area.append_data(
            train_loss=data['train_loss'],
            valid_loss=data['val_loss'],
            valid_acc=data['val_acc']
        )
