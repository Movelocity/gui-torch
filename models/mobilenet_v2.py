import torch
import torchvision
import torch.nn as nn
import torch.nn.functional as F

class MobileNetV2(nn.Module):
    def __init__(self, num_classes=67):
        super().__init__()
        self.network = torchvision.models.mobilenet_v2(weights=None)
        self.network.classifier = nn.Linear(self.network.last_channel, num_classes)
    
    def forward(self, x):
        return self.network(x)
    
    @torch.no_grad()
    def infer(self, x):
        if len(x.shape) < 4:
            x = x.unsqueeze(0)
        return self.network(x)