# -*- coding: utf-8 -*-
"""02-insurance-linear.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1j3SczKlApjIG0N7ajJjQR8dm1p29boTw

# Insurance cost prediction using linear regression


In this project we're going to use information like a person's age, sex, BMI, no. of children and smoking habit to predict the price of yearly medical bills. This kind of model is useful for insurance companies to determine the yearly insurance premium for a person. The dataset for this project is taken from [Kaggle](https://www.kaggle.com/mirichoi0218/insurance).


We will create a model with the following steps:
1. Download and explore the dataset
2. Prepare the dataset for training
3. Create a linear regression model
4. Train the model to fit the data
5. Make predictions using the trained model
"""

# Uncomment and run the appropriate command for your operating system, if required

# Linux / Binder
# !pip install numpy matplotlib pandas torch==1.7.0+cpu torchvision==0.8.1+cpu torchaudio==0.7.0 -f https://download.pytorch.org/whl/torch_stable.html

# Windows
# !pip install numpy matplotlib pandas torch==1.7.0+cpu torchvision==0.8.1+cpu torchaudio==0.7.0 -f https://download.pytorch.org/whl/torch_stable.html

# MacOS
# !pip install numpy matplotlib pandas torch torchvision torchaudio

# Import all the necessary libraries 
import torch
import torchvision
import torch.nn as nn
import pandas as pd
import matplotlib.pyplot as plt
import torch.nn.functional as F
from torchvision.datasets.utils import download_url
from torch.utils.data import DataLoader, TensorDataset, random_split

# Commented out IPython magic to ensure Python compatibility.
import matplotlib.pyplot as plt
# %matplotlib inline
import seaborn as sns
import matplotlib
import plotly.graph_objs as go
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

"""## Step 1: Download and explore the data

Let us begin by downloading the data. We'll use the `download_url` function from PyTorch to get the data as a CSV (comma-separated values) file. 
"""

DATASET_URL = "https://hub.jovian.ml/wp-content/uploads/2020/05/insurance.csv"
DATA_FILENAME = "insurance.csv"
download_url(DATASET_URL, '.')

# read csv we downloaded
dataframe_raw = pd.read_csv(DATA_FILENAME)
dataframe_raw.head()

def customize_dataset(dataframe_raw, rand_str):
    dataframe = dataframe_raw.copy(deep=True)
    # drop some rows
    dataframe = dataframe.sample(int(0.95*len(dataframe)), random_state=int(ord(rand_str[0])))
    # scale input
    dataframe.bmi = dataframe.bmi * ord(rand_str[1])/100.
    # scale target
    dataframe.charges = dataframe.charges * ord(rand_str[2])/100.
    # drop column
    if ord(rand_str[3]) % 2 == 1:
        dataframe = dataframe.drop(['region'], axis=1)
    return dataframe

dataframe = customize_dataset(dataframe_raw, 'vrajesh')
dataframe.head()

num_rows = dataframe.shape[0]
num_cols = dataframe.shape[1]
print("num_rows",num_rows,"num_cols",num_cols)
print("Shape of the DataFrame",dataframe.shape)

# input variables
input_cols = dataframe.drop('charges',axis=1).columns

# input non-numeric or categorial variables
categorical_cols = [x for x in dataframe.columns if type(dataframe[x][1])==str]

# output/target variable(s)
output_cols = [dataframe["charges"].name]

"""**Get the minimum, maximum and average value of the `charges` column and display it on a graph.**"""



#We sore the dataframe using the values in the charges column and store it in a different variable 
data = dataframe.sort_values('charges')
maximum = data.tail(1)
minimum = data.head(1)
average = data.mean(axis=0)
average = average[3]


#We use plotly.express library to represent the data graphically

#We here use the sns library to set the style of the background of the graph
sns.set_style('darkgrid')
fig = px.scatter(dataframe, x=dataframe.index, y=dataframe['charges'],
                  hover_data=[dataframe['charges']])

fig.show()
data2 = dataframe.sort_values('age')
uniq = data2['age'].unique().tolist()
data3 = [data2['age'].loc[data2.age == x].mean() for x in uniq]
#fig1 = plt.plot(x=[data2['age'].loc[data2.age == x]for x in uniq], y = [data2['age'].loc[data2.age == x].mean()for x in uniq])
#fig1.show()

"""## Step 2: Prepare the dataset for training

We need to convert the data from the Pandas dataframe into a PyTorch tensors for training. To do this, the first step is to convert it numpy arrays. If you've filled out `input_cols`, `categorial_cols` and `output_cols` correctly, this following function will perform the conversion to numpy arrays.
"""

def dataframe_to_arrays(dataframe):
    # Make a copy of the original dataframe
    dataframe1 = dataframe.copy(deep=True)
    # Convert non-numeric categorical columns to numbers
    for col in categorical_cols:
        dataframe1[col] = dataframe1[col].astype('category').cat.codes
    # Extract input & outupts as numpy arrays
    inputs_array = dataframe1[input_cols].to_numpy()
    targets_array = dataframe1[output_cols].to_numpy()
    return inputs_array, targets_array

inputs_array, targets_array = dataframe_to_arrays(dataframe)
inputs_array, targets_array

# Convert values to torch.float before we start manupulating the data
inputs = torch.from_numpy(inputs_array).type(torch.float32)
targets = torch.from_numpy(targets_array).type(torch.float32)

inputs.dtype, targets.dtype

# Create a tensor dataset of inputs and targets
dataset = TensorDataset(inputs, targets)

# Splitting our data 
val_percent = 0.1756 # between 0.1 and 0.2
val_size = int(num_rows * val_percent)
train_size = num_rows - val_size


train_ds, val_ds = torch.utils.data.random_split(dataset,[train_size,val_size]) # Use the random_split function to split dataset into 2 parts of the desired length

# Fix a batch size to distribute data
batch_size = 128


train_loader = DataLoader(train_ds, batch_size, shuffle=True)
val_loader = DataLoader(val_ds, batch_size)

for xb, yb in train_loader:
    print("inputs:", xb)
    print("targets:", yb)
    break

"""## Step 3: Create a Linear Regression Model

Our model itself is a fairly straightforward linear regression (we'll build more complex models in the next assignment). 

"""

input_size = len(input_cols)
output_size = len(output_cols)
input_size,output_size

# Main Model for Linear Regression 
# We use nn.Module class and initialize it using super().__init__()
# We calculate loss using F.l1_loss()

class InsuranceModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.linear = nn.Linear(input_size,output_size)                  # fill this (hint: use input_size & output_size defined above)
        
    def forward(self, xb):
        out = self.linear(xb)                          # fill this
        return out
    
    def training_step(self, batch):
        inputs, targets = batch 
        # Generate predictions
        out = self(inputs)          
        # Calcuate loss
        loss = F.l1_loss(out,targets)                          # fill this
        return loss
    
    def validation_step(self, batch):
        inputs, targets = batch
        # Generate predictions
        out = self(inputs)
        # Calculate loss
        loss = F.l1_loss(out,targets)                          # fill this    
        return {'val_loss': loss.detach()}
        
    def validation_epoch_end(self, outputs):
        batch_losses = [x['val_loss'] for x in outputs]
        epoch_loss = torch.stack(batch_losses).mean()   # Combine losses
        return {'val_loss': epoch_loss.item()}
    
    def epoch_end(self, epoch, result, num_epochs):
        # Print result every 20th epoch
        if (epoch+1) % 20 == 0 or epoch == num_epochs-1:
            print("Epoch [{}], val_loss: {:.4f}".format(epoch+1, result['val_loss']))

model = InsuranceModel()

list(model.parameters())

"""## Step 4: Train the model to fit the data

To train our model, we'll use the same `fit` function explained in the lecture. That's the benefit of defining a generic training loop - you can use it for any problem.
"""

def evaluate(model, val_loader):
    outputs = [model.validation_step(batch) for batch in val_loader]
    return model.validation_epoch_end(outputs)

def fit(epochs, lr, model, train_loader, val_loader, opt_func=torch.optim.SGD):
    history = []
    optimizer = opt_func(model.parameters(), lr)
    for epoch in range(epochs):
        # Training Phase 
        for batch in train_loader:
            loss = model.training_step(batch)
            loss.backward()
            optimizer.step()
            optimizer.zero_grad()
        # Validation phase
        result = evaluate(model, val_loader)
        model.epoch_end(epoch, result, epochs)
        history.append(result)
    return history

result = evaluate(model,val_loader) # Use the the evaluate function
print(result)

"""# Lets Train the Model"""

epochs = 1000
lr = 0.18
history1 = fit(epochs, lr, model, train_loader, val_loader)

epochs = 1000
lr = 1
history2 = fit(epochs, lr, model, train_loader, val_loader)

epochs = 2000
lr = 1e-3
history3 = fit(epochs, lr, model, train_loader, val_loader)

epochs = 1000
lr = 3
history4 = fit(epochs, lr, model, train_loader, val_loader)

epochs = 1000
lr = 2.5
history5 = fit(epochs, lr, model, train_loader, val_loader)

import itertools

def seq(start, end, step):
    if step == 0:
        raise ValueError("step must not be 0")
    sample_count = int(abs(end - start) / step)
    return itertools.islice(itertools.count(start, step), sample_count)
lrs = seq(1.0, 0.001, 0.01)

for x in lrs: 
  epochs = 1000
  lr = x
  history5 = fit(epochs, lr, model, train_loader, val_loader)

for x in lrs:
  print(x)

"""**final validation loss of our model?**"""

val_loss = 8066


"""## Step 5: Make predictions using the trained model

"""

def predict_single(input, target, model):
    inputs = input.unsqueeze(0)
    predictions = model(input)                
    prediction = predictions[0].detach()
    print("Input:", input)
    print("Target:", target)
    print("Prediction:", prediction)

input, target = val_ds[0]
predict_single(input, target, model)

input, target = val_ds[10]
predict_single(input, target, model)

input, target = val_ds[23]
predict_single(input, target, model)
