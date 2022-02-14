import json
import os
from elosports.elo import Elo

#Read in path names into a list
directory = os.fsencode('/Users/cameron/Documents/SMU_DS/Capstone/SMU_Capstone_Project/Raw Data/Match Data/')
file_path_holder=[]
for file in os.listdir(directory):
     filename = os.fsdecode(file)
     if filename.endswith(".json"): 
         file_path_holder.append(str(directory)[2:-1] + str(filename))

#Extend contents of all files into a list
#MUST SORT FILE PATHS OR ORDER COULD CHANGE
file_path_holder=sorted(file_path_holder)
full_vball_data=[]
for path in file_path_holder:
    file=open(path)
    full_vball_data.extend(json.load(file))
    file.close()

#Create Tournaments Table
full_vball_data[0].keys() #Tournament and type are unique to tournament
full_vball_data[0]['divisions'][0].keys()

#Question: Are 'latitude', 'longitude', 'timeZoneName', 'googleLocation' the same within all tournaments
#Answer: Only one division in one tournament doesn't follow this rule West Coast AAU Junior Olympic Games 2019 16 U Girls
#Index: Tournament 21 and division 1

#Loop to find any index that does not match
for i in range(len(full_vball_data)):
    for j in range(len(full_vball_data[i]['divisions'])):
        if (
            full_vball_data[i]['divisions'][j]['latitude'] != full_vball_data[i]['divisions'][0]['latitude'] or
            full_vball_data[i]['divisions'][j]['longitude'] != full_vball_data[i]['divisions'][0]['longitude'] or
            full_vball_data[i]['divisions'][j]['timeZoneName'] != full_vball_data[i]['divisions'][0]['timeZoneName'] or
            full_vball_data[i]['divisions'][j]['googleLocation'] != full_vball_data[i]['divisions'][0]['googleLocation']
        ):
          print('error:',i,j)

#Details on unmatched data
full_vball_data[21]['tournament']
full_vball_data[21]['type']
full_vball_data[21]['divisions'][1].keys()
keys = ['division', 'gender', 'ageType', 'latitude', 'longitude', 'timeZoneName']
for i in range(len(full_vball_data[21]['divisions'])):
    for key in keys:
        full_vball_data[21]['divisions'][i].get(key)
    print('\n')

# Matches
full_vball_data[0]['divisions'][0]['matches'][0].keys()

types=[]
for i in range(len(full_vball_data)):
    for j in range(len(full_vball_data[i]['divisions'])):
        for z in range(len(full_vball_data[i]['divisions'][j]['matches'])):
           types.append(full_vball_data[i]['divisions'][j]['matches'][z]['type'])

set(types)

#Loop to find any index that does not match
for i in range(len(full_vball_data)):
    for j in range(len(full_vball_data[i]['divisions'])):
        for z in range(len(full_vball_data[i]['divisions'][j]['matches'])):
            if (
                full_vball_data[i]['divisions'][j]['matches'][z]['id'] < 1 or
                full_vball_data[i]['divisions'][j]['matches'][z]['type'] not in types or
                len(full_vball_data[i]['divisions'][j]['matches'][z]['dateTime']) < 19 or
                full_vball_data[i]['divisions'][j]['matches'][z]['isMatch'] == ""
            ):
                print('error:',i,j)

divisional_keys=['division', 'gender', 'ageType', 'latitude', 'longitude', 'timeZoneName']
for i in range(len(full_vball_data[0]['divisions'])):
    print("Tournament: ",full_vball_data[0]['tournament'])
    print("Type: ",full_vball_data[0]['type'])
    for k,v in full_vball_data[0]['divisions'][i].items():
        if k in divisional_keys:
            print(k,":",v)
    print("\n")

for i in range(len(full_vball_data[0]['divisions'])):
    print("Tournament: ",full_vball_data[0]['tournament'])
    print("Type: ",full_vball_data[0]['type'])
    for k,v in full_vball_data[0]['divisions'][i]["googleLocation"][0].items():
        print(k,":",v)
    print("\n")
    
for i in range(len(full_vball_data[0]['divisions'])):
    print("Tournament: ",full_vball_data[0]['tournament'])
    print("Type: ",full_vball_data[0]['type'])
    print("\n")
    for j in range(len(full_vball_data[0]['divisions'][i]["matches"])):
        for k,v in full_vball_data[0]['divisions'][i]["matches"][j].items():
            print(k,":",v)
        print("\n")