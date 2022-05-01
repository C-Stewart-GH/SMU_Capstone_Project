import json
import os
import numpy as np
from elosports.elo import Elo
from collections import Counter
from datetime import datetime as dt
import copy
import pickle
import bz2

# Read in path names into a list
if os.getlogin() == "mmaze":
    directory = os.fsencode(
        "C:/Users/mmaze/Desktop/GitHub/SMU_Capstone_Project/Raw Data/Match Data/"
    )
else:
    directory = os.fsencode(
        "/Users/cameron/Documents/SMU_DS/Capstone/SMU_Capstone_Project/Raw Data/Match Data/"
    )

file_path_holder = []
for file in os.listdir(directory):
    filename = os.fsdecode(file)
    if filename.endswith(".json"):
        file_path_holder.append(str(directory)[2:-1] + str(filename))

# Extend contents of all files into a list
# MUST SORT FILE PATHS OR ORDER COULD CHANGE
file_path_holder = sorted(file_path_holder)
full_vball_data = []
for path in file_path_holder:
    file = open(path)
    full_vball_data.extend(json.load(file))
    file.close()
    
### Begin Organizing Data

# Copy original data to file that will be cleaned
# IMPORTANT: Need deepcopy due to nested nature of data (copy will cause issues because it is meant for shallow objects)
clean_vball_data = copy.deepcopy(full_vball_data)

#I am parsing one example to check what is new and what is the same from the update
#No comment means the same
clean_vball_data[0].keys() #tournament, type, and division
clean_vball_data[0]['tournamentId'] #Added tournamentId
clean_vball_data[0]['tournament']
clean_vball_data[0]['type']

clean_vball_data[0]["divisions"][0].keys()
clean_vball_data[0]["divisions"][0]['division']
clean_vball_data[0]["divisions"][0]['divisionId'] #Added divisionId
clean_vball_data[0]["divisions"][0]['gender']
clean_vball_data[0]["divisions"][0]['ageType']
clean_vball_data[0]["divisions"][0]['latitude']
clean_vball_data[0]["divisions"][0]['longitude']
clean_vball_data[0]["divisions"][0]['timeZoneName']
clean_vball_data[0]["divisions"][0]['googleLocation'][0] #Need to understand this better if we use location
clean_vball_data[0]["divisions"][0]['matches'][200] #Added roundNumber, matchNumber, matchWinner
clean_vball_data[0]["divisions"][0]['matches'][0]['games'][0] #Added gameNumber, winLoss
clean_vball_data[10]["divisions"][2]['matches'][0]['playerProfileIds']

# Change playerIds to playerProfileIds to  for consistency and count number of changes
# There are no changes needed, all were fixed to playerProfileIds in this update
key_changes=[]
for tournaments in clean_vball_data:
    for divisions in tournaments.get("divisions"):
        if (divisions.get("gender") == "Girls") and (
            divisions.get("ageType") == "Juniors"
        ):
            for matches in divisions.get("matches"):
                if "playerIds" in matches.keys():
                    key_changes.append(matches)
                    matches["playerProfileIds"] = matches.pop("playerIds")
len(key_changes)

#Create dataframe-like set in array
# Warning: matches with missing or unrealistic scores and can be filled in with just a win or loss input
# Each game appears 4 times
clean_vball_matches = []
for tournaments in clean_vball_data:
    for divisions in tournaments.get("divisions"):
        if (divisions.get("gender") == "Girls") and (
            divisions.get("ageType") == "Juniors"
        ):
            for matches in divisions.get("matches"):
                # Remove all games that are not two vs two
                if (
                    len(matches.get("playerProfileIds").get("home")) == 2
                    and len(matches.get("playerProfileIds").get("away")) == 2
                    
                    # Check for missing scores condition removed so we can use results
                    # and max(matches.get('games')[0].get('home'),matches.get('games')[0].get('away'))<10
                ):

                    # Note: The first two values are home and the second two are away
                    # Note: They are sorted to ensure consistency when looking as teams
                    # Set side_check to home beforehand and change to away just before iterating to away team
                    #for games in matches.get('games'):
                    #    if games.get('winner')!=None:
                    home_a = matches.get("playerProfileIds").get("home")[0]
                    home_b = matches.get("playerProfileIds").get("home")[1]
                    away_a = matches.get("playerProfileIds").get("away")[0]
                    away_b = matches.get("playerProfileIds").get("away")[1]
                    if home_a < home_b:
                        home_1 = home_a
                        home_2 = home_b
                    else:
                        home_1 = home_b
                        home_2 = home_a

                    if away_a < away_b:
                        away_1 = away_a
                        away_2 = away_b
                    else:
                        away_1 = away_b
                        away_2 = away_a  

                    row_holder= []
                    row_holder.append(tournaments.get('tournamentId'))  #tournamentId
                    row_holder.append(tournaments.get('tournament'))    #Tournament Name
                    row_holder.append(tournaments.get('type'))          #Type (Local or National)
                    row_holder.append(divisions.get('division'))        #Division
                    row_holder.append(divisions.get('divisionId'))      #divisionId
                    row_holder.append(divisions.get('gender'))          #Gender
                    row_holder.append(divisions.get('ageType'))         #Age Type
                    row_holder.append(matches.get('id'))                #Match Id
                    row_holder.append(matches.get('roundNumber'))       #roundNumber (in tournament)               
                    row_holder.append(matches.get('matchNumber'))       #matchNumber (in round)
                    row_holder.append(matches.get('matchWinner'))       #matchWinner (Match not game winner)
                    row_holder.append(matches.get('type'))              #Match Type (Pool or Bracket)
                    row_holder.append(matches.get('isMatch'))           #Best of Match (T/F Is the match a best of 3, 5, or 7)
                    row_holder.append(home_1)
                    row_holder.append(home_2)
                    row_holder.append(away_1)
                    row_holder.append(away_2)
                    row_holder.append(divisions.get('timeZoneName'))

                    #Convert datetimes (could be more efficient by moving dt_holder outside of loop)
                    dt_holder=dt.strptime(matches.get('dateTime'),'%Y-%m-%dT%H:%M:%S%z')
                    dt_holder = dt_holder.replace(tzinfo=None) #Remove timezone, all are UTC
                    row_holder.append(dt_holder)               #Datetime
                    #row_holder.append(dt.date(dt_holder))      #Date
                    #row_holder.append(dt.time(dt_holder))      #Time
                    #row_holder.append(divisions.get('googleLocation')) #GoogleLocation
                    clean_vball_matches.append(row_holder)


########################################################################################

len(clean_vball_matches)

##Covert to list of tuples (for structured array later)
clean_vball_matches_tuples=[tuple(clean_vball_matches[i]) for i in range(len(clean_vball_matches))]

#Find proper datatype for datetime column
np.datetime64(clean_vball_matches_tuples[0][-1]).dtype

#Set up data structure for structured array
#U200 = string of 200 characters
#i4 = 32 bit integer
#f4 = 32 bit float
#M = datetime format 

vball_coltypes=[('tournamentId', 'i4'), ('tournament_name','U200'), ('type', 'U200'), ('division', 'U200'), ('divisionId', 'U200'), ('gender', 'U200'), 
('age_type', 'U200'), ('match_id', 'i4'),('roundNumber', 'i4'), ('matchNumber', 'i4'), ('matchWinner', 'U200'), ('match_type', 'U200'), 
('isMatch', '?'), ("homePlayer1", 'i4'), ("homePlayer2", 'i4'), ("awayPlayer1", 'i4'), ("awayPlayer2", 'i4'), ('time_zone', 'U200'), ('datetime', '<M8[us]')]

#Store structured array in vball
vball=np.array(clean_vball_matches_tuples, dtype=vball_coltypes)
len(vball)

#Sort by date (Final Array)
vball.sort(order='datetime')

#Remove dates past today
vball=vball[vball['datetime']<dt.now()]
len(vball)

# #Equivalent output in a structured array
# vball['tournament_name'][1] #This is better because multi-input for column must go first
# vball[1]['tournament_name']

# #Calling multiple fields
# vball[['tournament_name','type']][1]

#Total Tournaments in data set
len(set(vball['tournament_name']))
len(set(vball['player_id']))

#Pickle and then use BZ2 compression to reduce to (2.2 MB)
with bz2.BZ2File('Pickle_Files/vball_match_data.pbz2', 'wb') as file:
    pickle.dump(vball, file, protocol=pickle.HIGHEST_PROTOCOL)
    
#Way too large to save to traditional pickle file (>1 GB). DO NOT USE THIS. Kept as an example
# with open('vball_game_data.pickle', 'wb') as handle:
#     pickle.dump(vball, handle, protocol=pickle.HIGHEST_PROTOCOL)

# #Used to track date errors past today. Need to run this function before they are filtered out if you want use the below code
# error_2042=vball[['tournament_name','divisionId','match_id','datetime']][vball['datetime']>dt.now()]
# len(set([t+'//'+id for t,id in error_2042[['tournament_name','divisionId']]]))
# len(set(error_2042['tournament_name']))
# [x for x in error_2042[['tournament_name','divisionId']][0:10]]
# set([t+'//'+id for t,id in error_2042[['tournament_name','divisionId']]])
# error_2042[::200]