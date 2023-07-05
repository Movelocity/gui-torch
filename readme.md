## GUI Torch

pytorch 模型训练和预测的界面展示。使用PyQt5实现，目前不具备通用性，仅能使用mobilenet等视觉模型，对一般的图像分类任务进行训练。由于GUI界面至支持在本地训模型，所以本地没显卡就比较难受，易用性不会超过浏览器页面。所以本项目仅提供一种UI展示，代码可直接获取。

![img](./images/main.png)

- [x] 数据加载，预处理可视化
- [x] PyQt5 QTreeView 展示 Pytorch 模型的权重结构
- [x] 模型训练，损失值图片更新
- [x] 使用训练好的图像分类模型，对本地图像进行识别

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

本项目是广东财经大学深度学习与应用的课程设计。
