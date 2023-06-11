from PyQt5.QtWidgets import QWidget, QFileDialog, QGridLayout, QPushButton, QTreeView
from PyQt5.QtCore import QAbstractItemModel, QModelIndex, Qt

from PyQt5 import QtWidgets
import model_utils
import re
from utils import update_config

class ModelPage(QWidget):
    def __init__(self):
        super(ModelPage, self).__init__()
        self.setStyleSheet("QComboBox { color: gray; } QComboBox:focus { color: #ffd740; } ")
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        # self.setStyleSheet("QComboBox {color: yellow;} ")
        self.model_select = QtWidgets.QComboBox(self)
        self.model_select.addItems(model_utils.models.keys())
        self.layout.addWidget(self.model_select, 0, 0)

        self.load_btn = QtWidgets.QPushButton("Load")
        self.load_btn.setStyleSheet("height: .7em; width: 1.7em; border-radius: .5em")
        self.load_btn.clicked.connect(self.print_selection)
        self.layout.addWidget(self.load_btn, 0, 1)
    
    def print_selection(self):
        selection = self.model_select.currentText()
        print("select model: "+selection)

        model = model_utils.load_cls_model(selection, pretrained=False)
        model_string = str(model)
        del model

        update_config('model', selection)
        # with open('model.txt', 'r', encoding='utf-8') as f:
        #     model_string = f.read()

        self.tree_model = TreeModel(model_string)
        self.tree_view = QTreeView(self)
        self.tree_view.setModel(self.tree_model)

        self.layout.addWidget(self.tree_view, 1, 0, 5, 3)


class TreeNode:
    def __init__(self, data, parent=None, indent=0):
        self.data = data
        self.parent = parent
        self.indent = indent
        self.children = []

    def append_child(self, child):
        self.children.append(child)

class TreeModel(QAbstractItemModel):
    def __init__(self, model_string:str, parent=None):
        super(TreeModel, self).__init__(parent)
        self.root = self.parse_structured_data(model_string)

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            node = parent.internalPointer()
            return len(node.children)
        return len(self.root.children)

    def columnCount(self, parent=QModelIndex()):
        return 1

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        node = index.internalPointer()

        if role == Qt.DisplayRole:
            return node.data
        return None

    def index(self, row, column, parent=QModelIndex()):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            parent_node = self.root
        else:
            parent_node = parent.internalPointer()

        child_node = parent_node.children[row]
        return self.createIndex(row, column, child_node)

    def parent(self, child):
        if not child.isValid():
            return QModelIndex()

        child_node = child.internalPointer()
        parent_node = child_node.parent

        if parent_node == self.root:
            return QModelIndex()

        return self.createIndex(parent_node.children.index(child_node), 0, parent_node)

    def parse_structured_data(self, data):
        lines = data.strip().split("\n")
        stack = []
        root = TreeNode("Root")

        for line in lines:
            data = line.strip()
            if len(data) <= 1:
                continue
            if data.endswith('('):
                data = data[:-1]
            indent = len(line) - len(data)
            node = TreeNode(data=data, indent=indent)

            if not stack:
                root.append_child(node)
                node.parent = root
            elif indent > stack[-1].indent:
                stack[-1].append_child(node)
                node.parent = stack[-1]
            else:
                while len(stack)>1 and indent <= stack[-1].indent:
                    stack.pop()

                stack[-1].append_child(node)
                node.parent = stack[-1]

            stack.append(node)
        return root