from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton, QLabel, QComboBox, QFileDialog, QSizePolicy, QGroupBox, QVBoxLayout, QProgressBar
from PyQt5.QtCore import QAbstractItemModel, QModelIndex, Qt
from PyQt5.QtGui import QPixmap
from PyQt5 import QtWidgets

import model_utils
import data_utils
import utils

import re
import random 
import glob
import math

from PIL import Image

class ClassificationViewer(QGroupBox):
    def __init__(self, parent=None, topk=5):
        super().__init__("Result", parent)
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.topk = topk

        self.labels = [QLabel("Class", self) for _ in range(topk)]
        self.pg_bars = [QProgressBar(self) for _ in range(topk)]
        self.probs = [QLabel("0") for _ in range(topk)]

        for i in range(topk):
            self.layout.addWidget(self.labels[i], i, 0)
            self.layout.addWidget(self.pg_bars[i], i, 1)
            self.layout.addWidget(self.probs[i], i, 2)
    
    def display_topk(self, cls_result:dict):
        for i, (k, v) in enumerate(cls_result.items()):
            if i >= self.topk:
                break
            self.labels[i].setText(k)
            self.probs[i].setText(str(round(v, 5)))
            self.pg_bars[i].setValue(int(v*100//1))

class ImageViewer(QGroupBox):
    def __init__(self, get_img_callback=None, model_infer_callback=None):
        super().__init__("ImageView")
        self.current_path = None
        self.get_img_callback = get_img_callback
        self.model_infer_callback = model_infer_callback
        # self.setStyleSheet("background-color: yellow;")

        self.image_label = QLabel(self)
        self.image_label.setFixedSize(360, 360)
        self.image_label.setStyleSheet("background-color: #232629")
        self.image_label.setScaledContents(True)

        self.current_path = ""
        self.path_label = QLabel(self.current_path, self)
        self.path_label.setWordWrap(True)
        self.path_label.setAlignment(Qt.AlignTop)
        self.path_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.path_label.setMinimumHeight(self.path_label.fontMetrics().height())

        self.result_display = ClassificationViewer(self)
        
        in_btn = QPushButton("Select", self)
        in_btn.setEnabled(False)
        in_btn.clicked.connect(self.load_from_dataset)

        out_btn = QPushButton("Open", self)
        out_btn.setEnabled(False)
        out_btn.clicked.connect(self.load_from_outside)

        pred_btn = QPushButton("Predict", self)
        pred_btn.setEnabled(False)
        pred_btn.clicked.connect(self.model_infer)
        self.btns = [in_btn, out_btn, pred_btn]
        # Create the layout and add the widgets
        layout = QGridLayout()
        layout.addWidget(self.image_label, 0, 0, 2, 2)
        layout.addWidget(self.path_label, 2, 0, 1, 2)
        layout.addWidget(self.result_display, 0, 2, 2, 1)
        layout.addWidget(in_btn, 3, 0, 1, 1)
        layout.addWidget(out_btn, 3, 1, 1, 1)
        layout.addWidget(pred_btn, 3, 2, 1, 1)
        self.setLayout(layout)
        self.adjustSize()

    def display_topk(self, data):
        self.result_display.display_topk(data)

    def activate(self):
        for btn in self.btns:
            btn.setEnabled(True)

    def model_infer(self):
        self.model_infer_callback(self.current_path)

    def load_from_dataset(self):
        if self.get_img_callback is None:
            return
        path = self.get_img_callback()
        self.current_path = path
        self.update_img()

    def load_from_outside(self):
        path, _ = QFileDialog.getOpenFileName(parent=self)
        valid_suffix = [".png", ".jpg", ".gif", ".jfif"]
        if not any([path.endswith(suffix) for suffix in valid_suffix]):
            print(f'"{path}" is not a vaild image file. try using {valid_suffix}')
        self.current_path = path
        self.update_img()

    def update_img(self):
        pixmap = QPixmap(self.current_path)
        self.path_label.setText(self.current_path)
        scaled_pixmap = pixmap.scaled(self.image_label.size(), aspectRatioMode=Qt.KeepAspectRatioByExpanding, transformMode=Qt.SmoothTransformation)
        self.image_label.setPixmap(scaled_pixmap)

class EvalPage(QWidget):
    def __init__(self):
        super(EvalPage, self).__init__()
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.setStyleSheet("QComboBox { color: gray; } QComboBox:focus { color: #ffd740; } ")

        model_box = QWidget()
        model_box.setStyleSheet("background-color: #232629")
        model_box.setLayout(QGridLayout())
        self.model_select = QComboBox()
        self.model_select.addItems([utils.get_config('model')])
        self.model_select.mousePressEvent = self.update_selection
        self.model_select_hint = QLabel("not loaded")
        self.model_select_hint.setStyleSheet("margin-left: 20px")
        self.load_btn = QtWidgets.QPushButton("Load")
        self.load_btn.setStyleSheet("height: .7em; width: 1.7em; border-radius: .5em")
        
        self.load_btn.clicked.connect(self.update_content)
        model_box.layout().addWidget(self.model_select, 0, 0, 1 ,2)
        model_box.layout().addWidget(self.model_select_hint, 1, 0, 1, 1)
        model_box.layout().addWidget(self.load_btn, 1, 1, 1, 1)
        self.layout.addWidget(model_box, 0, 0, 1, 1)

        self.img_viewer = ImageViewer(get_img_callback=self.getRandomData, model_infer_callback=self.model_infer)
        self.layout.addWidget(self.img_viewer, 0, 1, 3, 2)
        self.path = None
        self.model = None
        self.transforms = None

    def model_infer(self, img_path):
        if self.transforms is None:
            self.transforms = data_utils.get_transforms_from_config({
                'resize': utils.get_config('scale'),
                'to_tensor': True
            })
        img = Image.open(img_path)
        img = self.transforms(img)
        if img_path.endswith('.png'):
            img = img[:3, :, :]

        self.model.eval()  # eval很重要, 不然归一化的时候会乱套
        output = self.model.infer(img).softmax(-1)
        top_probs, top_indices = output.topk(k=5, sorted=True)
        id_to_name = {i:name for i, name in enumerate(self.valid_folders)}
        top_classes = {}
        for i in range(5):
            class_index = top_indices[0][i].item()
            class_prob = top_probs[0][i].item()
            class_name = id_to_name[class_index]
            top_classes[class_name] = class_prob
        self.img_viewer.display_topk(top_classes)

    def update_selection(self, event):
        self.model_select.setItemText(0, utils.get_config('model'))

    def update_content(self):
        currentText = self.model_select.currentText()
        config = utils.get_config()
        self.path, self.valid_suffix = config['dataset_path'], config['valid_suffix']
        self.valid_folders, valid_files = utils.detect_dataset(self.path, self.valid_suffix)
        self.img_viewer.activate()

        self.model = model_utils.load_cls_model(currentText, pretrained=True)
        self.model_select_hint.setText("model loaded")

    def getRandomData(self):
        if self.path is None:
            config = utils.get_config()
            self.path, self.valid_suffix = config['dataset_path'], config['valid_suffix']
        img_folder = "/".join([self.path, random.choice(self.valid_folders)])
        files = []
        for extension in self.valid_suffix:
            files.extend(glob.glob(f"{img_folder}/**/*{extension}", recursive=True))
        # TODO: 检查文件类型是否正确
        return random.choice(files)