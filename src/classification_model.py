import os
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import pandas as pd
from torch.utils.data import Dataset, DataLoader
from huggingface_hub import login
from sklearn.preprocessing import OneHotEncoder
from transformers import TrainingArguments, Trainer
from utils.get_root_dir import get_root_dir
import evaluate
# metric = evaluate.load('accuracy')
# def compute_metrics(eval_pred):
#     logits,labels=eval_pred
#     predictions = np.argmax(logits,axis=-1)
#     return metric.compute(predictions=predictions,references=labels)
    
root = get_root_dir()
root = os.path.dirname(root)
model_path =os.path.join(root,'model','action_classification')
# Model 
class Block(nn.Module):
    def __init__(self,batch_size,hidden_dim,output_dim):
        super().__init__()
        self.block = nn.Sequential(
            nn.BatchNorm1d(batch_size),
            nn.Linear(hidden_dim,output_dim),
            nn.GELU()
        )
    def forward(self,x):
        return self.block(x)
class ClassificationModel(nn.Module):
    def __init__(self,hidden_dim,num_classes,batch_size=1) -> None:
        # input : (B,88) 22 landmark (x,y,z,visibility)
        super().__init__()
        self.in_layers = nn.Sequential(
            nn.Linear(88,hidden_dim), # (B,hidden_dim)
            nn.GELU(), # (B,hidden_dim)
            Block(batch_size,hidden_dim,hidden_dim*2) # (B,hidden_dim*2)
        )
        self.bottleneck = nn.Sequential(
            Block(batch_size,hidden_dim*2,hidden_dim*4), # (B,hidden_dim*4)
        )
        self.output_layers = nn.Sequential(
            Block(batch_size,hidden_dim*4,hidden_dim*2),  # (B,hidden_dim*2)
            Block(batch_size,hidden_dim*2,hidden_dim),  # (B,hidden_dim)
            nn.Linear(hidden_dim,num_classes)  # (B,num_classes)
        )
        for layer in self.modules():
            if isinstance(layer,nn.Linear):
                nn.init.kaiming_uniform_(layer.weight)
    def forward(self,x):
        temp = self.in_layers(x)
        x = self.bottleneck(temp)
        x = self.output_layers[0](x)
        x += temp
        x = self.output_layers[1:](x)
        return x
def trainining(dataset,batch_size=16,lr=2e5,epochs=100):
    model = ClassificationModel(300,3)
    optimizer = optim.Adam(model.parameters(),lr=lr)
    criteria = nn.CrossEntropyLoss()
    trainloader = DataLoader(dataset,batch_size=batch_size,shuffle=True)
    losses = []
    for epoch in range(1,epochs+1):
        total_loss = 0
        for (input,label) in trainloader:
            optimizer.zero_grad()
            model = model(input)
            loss = criteria(model,label)
dataset_path = os.path.join(root,"data","landmark_train.csv")
dataset = pd.read_csv(dataset_path,header=None)
Y = dataset.iloc[:,0]
onehot = OneHotEncoder()
Y = onehot.fit_transform(Y)
print(Y)
X = dataset.iloc[:,1:]
dataset = {
    "X":X,
    "Y":Y
}