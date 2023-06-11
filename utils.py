
import os
from PyQt5.QtWidgets import QGroupBox, QGridLayout, QPushButton, QCheckBox, QSpacerItem, QVBoxLayout, QTabBar
import json

def load_config(file_path="tmp.config"):
    if not os.path.exists(file_path):
        config = {
            "model": "",
            "scale": 256,
            "valid_suffix": [".png", ".jpg", ".gif", ".jfif"],
            "dataset_path": "."
        }
    else:
        with open(file_path, 'r', encoding="utf-8") as f:
            config = json.load(f)
    return config

def update_configs(dict, file_path="tmp.config"):
    config = load_config(file_path)

    for k, v in dict.items():
        config[k] = v
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=0)

def update_config(key, value, file_path="tmp.config"):
    config = load_config(file_path)
    config[key] = value

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=0)

def get_config(key=None, file_path="tmp.config"):
    config = load_config(file_path)
    if key is not None:
        return config[key]
    else:
        return config

def getBtnGroup():
    btnGroup = QGroupBox(title="Buttons")
    btnGroup.setCheckable(False)

    layout = QGridLayout()
    btnGroup.setLayout(layout)

    btn1 = QPushButton(text="Push Button")
    layout.addWidget(btn1, 0, 0)

    btn2 = QPushButton(text="Push Button")
    layout.addWidget(btn2, 1, 0)

    btn3 = QPushButton(text="Check")
    btn3.setCheckable(True)
    btn3.setChecked(True)
    layout.addWidget(btn3, 0, 1)

    return btnGroup

def getCheckBoxGroup():
    ckGroup = QGroupBox(title="CheckBoxes")
    ckGroup.setCheckable(False)
    ckGroup.setAutoFillBackground(True)

    names = ["Ckeck 1", "Check 2", "Check 3"]
    layout = QVBoxLayout()
    ckGroup.setLayout(layout)
    
    for name in names:
        ck = QCheckBox(text=name)
        layout.addWidget(ck)

        spacer = QSpacerItem(20, 40)
        layout.addItem(spacer)
    return ckGroup


class HorizontalTab(QTabBar):
    """
    Usage:
        tabWidget = QTabWidget()
        tabWidget.setTabBar(HorizontalTab())
        tabWidget.setTabPosition(QTabWidget.West)
    """
    def tabSizeHint(self, index):
        hint = super().tabSizeHint(index).transposed()
        return QSize(max(hint.width(), 120), max(hint.height(), 80))

    def paintEvent(self, event):
        painter = QtWidgets.QStylePainter(self)
        opt = QtWidgets.QStyleOptionTab()

        currentIdx = self.currentIndex()
        ids = list(range(self.count()))
        ids.pop(currentIdx)
        ids.append(currentIdx)  # the current tab is always painted above the others

        for i in ids:
            self.initStyleOption(opt, i)
            opt.shape = QTabBar.RoundedWest
            painter.drawControl(QtWidgets.QStyle.CE_TabBarTabShape, opt)
            opt.shape = QTabBar.RoundedNorth
            painter.drawControl(QtWidgets.QStyle.CE_TabBarTabLabel, opt)


from PyQt5.QtWidgets import QMessageBox

def show_warning(message):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)
    msg.setText(message)
    msg.setWindowTitle("Warning")
    msg.setStandardButtons(QMessageBox.Ok)
    return msg.exec_()

def detect_dataset(root_dir, suffix=[]):
    """
    >>> detect_dataset(root_dir, suffix=['.jpg', '.png'])
    (['doll', 'grape4', 'outputs'], [24, 25, 28])

    返回指定目录下的一级子目录，和各自的有效文件(指定后缀)个数
    """
    valid_folders = []
    valid_files_cnt = []
    for path_ in os.listdir(root_dir):
        valid_files = 0
        if os.path.isfile(path_):
            continue

        folder = os.path.join(root_dir, path_)

        folder_valid = False
        for dirpath, dirnames, filenames in os.walk(folder):
            for f in filenames:
                if any([f.endswith(s) for s in suffix]):
                    folder_valid = True
                    valid_files += 1
        if folder_valid:
            valid_folders.append(path_)
            valid_files_cnt.append(valid_files)
    tmp_cnt = valid_files_cnt
    tmp_dict = {number:name for name, number in zip(valid_folders, valid_files_cnt)}
    # Sort
    valid_folders = sorted(valid_folders)
    valid_files_cnt = sorted(valid_files_cnt, key=tmp_dict.get)
    return valid_folders, valid_files_cnt

def convert_bytes(num):
    """
    this function will convert bytes to MB.... GB... etc
    """
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return f"{num:.2f} {x}"
        num /= 1024.0