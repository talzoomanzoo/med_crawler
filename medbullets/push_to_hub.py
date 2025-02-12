import pandas as pd
from datasets import Dataset

# Load the datasets
data_op4 = pd.read_csv('./medbullets_op4.csv')
data_op5 = pd.read_csv('./medbullets_op5.csv')

# Combine datasets using pd.concat
combined_data = pd.concat([data_op4, data_op5], ignore_index=True)
combined_data = combined_data.astype(str)
# Convert DataFrame to list of dictionaries
combined_data_list = combined_data.to_dict('records')

#import pdb;pdb.set_trace()

# Create a Dataset object
dataset = Dataset.from_list(combined_data_list)

# Split the dataset into train and test sets (80:20)
train_test_split = dataset.train_test_split(test_size=0.2)

# Push to Hugging Face hub
train_test_split.push_to_hub("LangAGI-Lab/medbullets")