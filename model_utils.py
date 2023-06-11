import torch
import torch.nn.functional as F

import os
from models.mobilenet_v2 import MobileNetV2
from torch.utils.data import DataLoader

models = {"mobilenet_v2": MobileNetV2}

def load_cls_model(name: str, num_classes: int=67, pretrained=False):
    model_class: torch.nn.Module = models.get(name, None)
    if model_class != None:
        model = model_class(num_classes)
        pth_name = name+".pth"
        if pth_name in os.listdir('models') and pretrained:
            model.load_state_dict(torch.load("models/"+pth_name, map_location='cpu'))
            print("pth loaded")
        return model
    
    print(f'"{name}" model not found')
    return None

class TrainingWrapper():
    def __init__(self, model, train_dataset, valid_dataset, optim=None, learning_rate=6e-5, callback=None, verbose=True):

        self.device = torch.device('cuda' if torch.cuda.is_available() else "cpu")
        self.model = model.to(self.device)
        self.train_dataset = train_dataset
        self.valid_dataset = valid_dataset
        self.callback = callback
        
        if optim:
            self.optim = optim
        else:
            self.optim = torch.optim.Adam(model.parameters(), learning_rate)
        self.history = []
        self.verbose = verbose

        self.train_enabled = True 
        self.epoch = 0

    def update_lr(self, lr):
        for param_group in self.optim.param_groups:
            param_group['lr'] = lr

    def training_step(self, batch):
        images, labels = batch[0].to(self.device), batch[1].to(self.device)
        out = self.model(images)              # Generate predictions
        loss = F.cross_entropy(out, labels)   # cross entropy 内部已包含 softmax， 所以外部就不激活了
        return loss
    
    @torch.no_grad()
    def valid_step(self, batch):
        images, labels = batch[0].to(self.device), batch[1].to(self.device) 
        out = self.model(images)              # Generate predictions
        loss = F.cross_entropy(out, labels)   # Calculate loss
        acc = accuracy(out, labels)           # Calculate accuracy
        return {'val_loss': loss.item(), 'val_acc': acc}

    def train_epoch(self, epoch_num=1):
        self.model.train()
        train_losses = []
        for batch in self.train_loader:
            if not self.train_enabled:
                print("pause")
                return
            loss = self.training_step(batch)
            self.optim.zero_grad()
            loss.backward()
            self.optim.step()

            train_losses.append(loss.item())

        # Validation phase
        self.model.eval()
        outputs = [self.valid_step(batch) for batch in self.valid_loader]
        result = {
            'val_loss': np.mean([out['val_loss'] for out in outputs]), 
            'val_acc': np.mean([out['val_acc'] for out in outputs]), 
            'train_loss': np.mean(train_losses)
        }
        if self.verbose:
            print(f"[Epoch {epoch_num+1}] train_loss: {result['train_loss']:.4f}, val_loss: {result['val_loss']:.4f}, val_acc: {result['val_acc']:.4f}")
        self.history.append(result)
        if self.callback:
            self.callback(result)

    def start_training(self, num_epochs=20, lr=None, batch_size=16):
        if lr is not None:
            self.update_lr(lr)

        self.train_loader = DataLoader(self.train_dataset, batch_size=batch_size, shuffle=True)
        self.valid_loader = DataLoader(self.valid_dataset, batch_size=batch_size)
        for i in range(num_epochs):
            if not self.train_enabled:
                return
            self.train_epoch(self.epoch)
            self.epoch += 1
        
        print("训练完毕")
        model_name = utils.get_config("model")
        model_path = f"models/{model_name}-{i}.pth"
        torch.save(self.model.state_dict(), model_path)
        print(f"模型已保存至 {model_path}")

    def pause_training(self):
        self.train_enabled = False