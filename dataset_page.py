import os
import math
import random

from PyQt5.QtWidgets import QWidget, QFileDialog, QGridLayout, QVBoxLayout, QHBoxLayout, \
    QPushButton, QTabWidget, QLabel, QFileSystemModel, QTreeView, QToolBox, QScrollArea, \
    QSpacerItem, QSizePolicy, QTableWidget, QTableWidgetItem, QGroupBox, QCheckBox, QSpinBox, \
    QDoubleSpinBox, QLineEdit, QDialog
from PyQt5.QtGui import QPainter, QBrush, QColor, QPixmap, QCursor
from PyQt5.QtCore import Qt, QRect

import glob

from PyQt5.QtGui import QImage
from PIL import Image
from PIL.ImageQt import ImageQt

from data_utils import get_transforms_from_config

import utils

def getFileView(path):
    filemodel = QFileSystemModel()
    filemodel.setRootPath(path)

    tree = QTreeView()
    tree.setModel(filemodel) 
    tree.setRootIndex(filemodel.index(path))

    return tree

def getFilePage(folders, counts, reload_callback=None):
    filepage = QWidget()
    filepage_layout = QGridLayout()
    filepage.setLayout(filepage_layout)

    table = QTableWidget()
    table.setRowCount(len(folders))
    table.setColumnCount(2)
    table.setHorizontalHeaderLabels(['Folder', 'Files'])

    for i, folder in enumerate(folders):
        category_item = QTableWidgetItem(folder)
        value_item = QTableWidgetItem(str(counts[i]))
        table.setItem(i, 0, category_item)
        table.setItem(i, 1, value_item)

    filepage_layout.addWidget(table, 0, 0, 1, 1)
    
    btn_reload = QPushButton("Reload")
    if reload_callback is not None:
        btn_reload.clicked.connect(reload_callback)
    filepage_layout.addWidget(btn_reload, 0, 2, 1, 1)
    return filepage

class TransformsGroup(QGroupBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Transforms")
        self.setCheckable(False)
        self.setAutoFillBackground(True)
        self.setLayout(QGridLayout())
        self.setStyleSheet("QSpinBox { color: #ffd740; } QSpinBox:disabled { color: black; } QDoubleSpinBox {color: yellow} QDoubleSpinBox:disabled { color: black; }")
        # QSpinBox:focus {  color: rgb(255, 191, 0); }
        self.ckBoxSize = QCheckBox("大小调整")
        self.spinBoxSize = QSpinBox()
        self.spinBoxSize.setRange(4, 1024)
        self.spinBoxSize.setValue(256)
        self.spinBoxSize.setSingleStep(1)
        self.spinBoxSize.setSuffix(" px")
        
        self.ckBoxSize.clicked.connect(lambda checked: self.spinBoxSize.setEnabled(checked))
        self.ckBoxSize.setChecked(True)
        self.layout().addWidget(self.ckBoxSize, 0, 0)
        self.layout().addWidget(self.spinBoxSize, 0, 1)

        self.ckBoxFlip = QCheckBox("随机水平镜像")
        self.layout().addWidget(self.ckBoxFlip, 1, 0)

        self.ckBoxRotate = QCheckBox("随机旋转")
        self.spinBoxRotate = QSpinBox()
        self.spinBoxRotate.setRange(0, 180)
        self.spinBoxRotate.setSingleStep(1)
        self.spinBoxRotate.setValue(10)
        self.spinBoxRotate.setSuffix(" degree")
        self.spinBoxRotate.setEnabled(False)
        self.ckBoxRotate.clicked.connect(lambda checked: self.spinBoxRotate.setEnabled(checked))
        self.layout().addWidget(self.ckBoxRotate, 2, 0)
        self.layout().addWidget(self.spinBoxRotate, 2, 1)

        self.ckBoxJitter = QCheckBox("色彩抖动")
        self.spinBoxJitter = QDoubleSpinBox()
        self.spinBoxJitter.setRange(0, 0.9)
        self.spinBoxJitter.setValue(0.2)
        self.spinBoxJitter.setSingleStep(0.05)
        self.spinBoxJitter.setEnabled(False)
        self.ckBoxJitter.clicked.connect(lambda checked: self.spinBoxJitter.setEnabled(checked))
        self.layout().addWidget(self.ckBoxJitter, 3, 0)
        self.layout().addWidget(self.spinBoxJitter, 3, 1)
    
    def get_state(self):
        state = {}
        state['resize'] = self.ckBoxSize.isChecked()
        state['resize_value'] = (self.spinBoxSize.value(), self.spinBoxSize.value())
        state['random_horizontal_flip'] = self.ckBoxFlip.isChecked()
        state['random_rotation'] = self.spinBoxRotate.value() if self.ckBoxRotate.isChecked() else False
        state['color_jitter'] = self.spinBoxJitter.value() if self.ckBoxJitter.isChecked() else False
        state['to_tensor'] = False

        config = utils.get_config()
        for k, v in state.items():
            config[k] = v
        utils.update_configs(config)
        return state

class ImageViewer(QWidget):
    def __init__(self, get_img_callback=None, process_img_callback=None):
        super().__init__()
        self.get_img_callback = get_img_callback
        self.process_img_callback = process_img_callback
        self.current_path = None
        self.setStyleSheet("background-color: #232629")
        self.image_label = QLabel(self)
        self.image_label.setFixedSize(360, 360)
        self.image_label.setScaledContents(True)
        self.image_label.setCursor(QCursor(Qt.PointingHandCursor))
        self.image_label.mousePressEvent = self.showFullImage

        self.path_label = QLabel("", self)
        # Create the button to update the image
        update_button = QPushButton("Update", self)
        update_button.clicked.connect(self.updateImage)

        pcs_btn = QPushButton("Process", self)
        pcs_btn.clicked.connect(self.processImg)

        # Create the layout and add the widgets
        layout = QGridLayout()
        layout.addWidget(self.image_label, 0, 0, 2, 2)
        layout.addWidget(self.path_label, 2, 0, 1, 2)
        layout.addWidget(update_button, 3, 0, 1, 1)
        layout.addWidget(pcs_btn, 3, 1, 1, 1)
        self.setLayout(layout)

    def showFullImage(self, event):
        if self.image_label.pixmap() is None:
            return

        # Create a new dialog window to display the full image
        dialog = QDialog(self)
        dialog.setWindowTitle("Full Image")

        # Create a label widget to display the full image
        full_image_label = QLabel(dialog)
        full_image_label.setPixmap(QPixmap(self.current_path))

        # Create a scroll area to allow the user to zoom in or out on the image
        scroll_area = QScrollArea(dialog)
        scroll_area.setWidget(full_image_label)
        scroll_area.setWidgetResizable(True)

        # Create a layout and add the widgets
        layout = QHBoxLayout()
        layout.addWidget(scroll_area)
        dialog.setLayout(layout)

        # Show the dialog window
        dialog.exec_()

    def updateImage(self):
        # Get the image path from the input widget

        if self.get_img_callback is None:
            return

        path = self.get_img_callback()
        if path is None or path == "":
            show_warning("没有找到有效图片")
        self.current_path = path

        # Load the image and set it as the pixmap for the image label
        pixmap = QPixmap(path)
        self.path_label.setText(path)
        scaled_pixmap = pixmap.scaled(self.image_label.size(), aspectRatioMode=Qt.KeepAspectRatioByExpanding, transformMode=Qt.SmoothTransformation)
        self.image_label.setPixmap(scaled_pixmap)

    def processImg(self):
        if self.process_img_callback is None:
            return

        qpixmap = self.process_img_callback(self.current_path)
        scaled_pixmap = qpixmap.scaled(self.image_label.size(), aspectRatioMode=Qt.KeepAspectRatioByExpanding, transformMode=Qt.SmoothTransformation)
        # QPixmap.fromImage(ImageQt(pil_image))
        # get_transforms_from_config
        self.image_label.setPixmap(scaled_pixmap)

class DataProcessPage(QWidget):
    def __init__(self, get_img_callback=None):
        super().__init__()
        self.setLayout(QGridLayout())
        self.gBox = TransformsGroup()
        self.layout().addWidget(self.gBox, 0, 0)
        self.imgViewer = ImageViewer(get_img_callback=get_img_callback, process_img_callback=self.process_img)
        self.layout().addWidget(self.imgViewer, 0, 1)

    def process_img(self, path):
        if path is None or path == "":
            return
        pil_img = Image.open(path)

        config = self.gBox.get_state()
        # print(config)

        transforms = get_transforms_from_config(config)
        pil_img = transforms(pil_img)
        return QPixmap.fromImage(ImageQt(pil_img))


class DatasetPage(QWidget):
    def __init__(self):
        super(DatasetPage, self).__init__()

        self.setStyleSheet("margin: 0, 30px")
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.resetPage()

    def resetPage(self):
        # self.folderHelper = FolderHelper()
        img_cls_btn = QPushButton(text="Image Classification Dataset")
        img_cls_btn.clicked.connect(lambda checked, taskname="img_cls": self.loadDataset(taskname))
        img_cls_btn.setStyleSheet("height: 150px;")
        self.layout.addWidget(img_cls_btn, 0, 0, 1, 1)

        img_cls_label = QLabel("*.jpg, *.png files. Each class should be put to a single folder.")
        self.layout.addWidget(img_cls_label, 0, 1, 1, 1)

        txt_cls_btn = QPushButton(text="Text Classification Dataset")
        txt_cls_btn.setEnabled(False)
        txt_cls_btn.clicked.connect(lambda checked, taskname="txt_cls": self.loadDataset(taskname))
        txt_cls_btn.setStyleSheet("height: 150px;")
        self.layout.addWidget(txt_cls_btn, 1, 0, 1, 1)

        txt_cls_label = QLabel("*.txt, utf-8 encoded files. Each class should be put to a single folder.")
        self.layout.addWidget(txt_cls_label, 1, 1, 1, 1)

        self.current_widgets = [img_cls_btn, img_cls_label, txt_cls_btn, txt_cls_label]

    def loadDataset(self, taskname):
        path = QFileDialog.getExistingDirectory(parent=self)
        if path == "":
            return

        if taskname == "img_cls":
            self.valid_suffix = [".png", ".jpg", ".jfif"]
        elif taskname == "txt_cls":
            self.valid_suffix = ['.txt']
        else:
            utils.show_warning(f"unknown type '{taskname}'")
            return

        valid_folders, valid_files = utils.detect_dataset(path, self.valid_suffix)

        if len(valid_folders) == 0:
            utils.show_warning(f"{path}\n未找到数据集，可能有以下原因。\n 1.本程序默认忽略根目录，只看次一级目录\n 2.没有发现 {', '.join(valid_suffix)} 等类型的文件")
            return

        self.valid_folders = valid_folders
        self.valid_files = valid_files
        self.path = path
        utils.update_config('dataset_path', self.path)
        utils.update_config('valid_suffix', self.valid_suffix)
        print(f"using path: '{path}'")

        toolBox = QToolBox()
        toolBox.setCurrentIndex(1)

        filepage = getFilePage(
            self.valid_folders, self.valid_files, reload_callback=lambda :self.loadDataset(taskname))
        toolBox.addItem(filepage, "Files")

        dataProcessPage = DataProcessPage(get_img_callback=self.getRandomData)
        toolBox.addItem(dataProcessPage, "Data preprocess")
        
        # self.load_file_model()
        for widget in self.current_widgets:
            self.layout.removeWidget(widget)
            widget.deleteLater()
        
        self.layout.addWidget(toolBox, 0, 0, 2, 2)
        self.current_widgets = [toolBox]
        
    def getRandomData(self):
        img_folder = "/".join([self.path, random.choice(self.valid_folders)])
        files = []
        for extension in self.valid_suffix:
            files.extend(glob.glob(f"{img_folder}/**/*{extension}", recursive=True))
        # TODO: 检查文件类型是否正确
        return random.choice(files)
