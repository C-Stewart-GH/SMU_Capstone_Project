import json
import os

directory = os.fsencode('/Users/cameron/Documents/SMU_DS/Capstone/SMU_Capstone_Project/Raw Data/Match Data/')
file_path_holder=[]
for file in os.listdir(directory):
     filename = os.fsdecode(file)
     if filename.endswith(".json"): 
         file_path_holder.append(str(directory)[2:] + filename)
     else:
         continue

file=open("/Users/cameron/Documents/SMU_DS/Capstone/Volleyball Data/Sample Data.json")
vball=json.load(file)