import json
import os
from datasets import Dataset
from collections import defaultdict

jama = json.load(open('./jama_raw_updated.json'))
print(set((item["field"]) for item in jama))

jama_full = Dataset.from_list(jama)

train_test_split = jama_full.train_test_split(test_size=0.2)

train_test_split.push_to_hub('LangAGI-Lab/jama_full')

# os.makedirs('jama_files', exist_ok = True)
# grouped_items = defaultdict(list)


# for item in jama:
#     field_name = item['field']
#     grouped_items[field_name].append(item)

# for field_name, items in grouped_items.items():
#     file_name = f'jama_files/jama_{field_name.replace(" ", "_")}.json'
#     print(len(file_name))

#     with open(file_name, 'w') as f:
#         json.dump(items, f)

#     # upload_dataset = Dataset.from_list(items)
    
#     # train_test_split = upload_dataset.train_test_split(test_size=0.2)

#     # train_test_split.push_to_hub(f'LangAGI-Lab/{field_name.replace(" ", "_")}')