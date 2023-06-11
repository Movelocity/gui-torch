## GUI Torch

本项目是广东财经大学深度学习与应用的课程设计。

![img](./images/main.png)

## 1. 使用方法
```
$ python main.py  # 使用 python3 运行 main.py 文件
```
在数据页面中选择数据集目录后，即可直接到推理页面使用训练好的模型进行测试。默认模型使用 MobileNetV2，模型权重已包含在项目中。

## 2. 部分依赖环境
```
torch==1.7.0
torchvision==0.8.1
PyQt5
qt-material
```
缺少对应的库可以使用 pip install 包名==版本 进行安装，没有注明版本号即为默认版本

## 3. 注意事项
本项目GUI界面包含模型训练功能，但不建议在没有显卡的个人电脑上训练模型。本项目的模型文件也是使用云平台的GPU进行训练的，预训练好的模型文件在 models 文件夹下。

## 4. 部分界面截图

![model](./images/model.png)

![evaluate](./images/evaluate.png)


