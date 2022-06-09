import json
import os
import numpy as np
from elosports.elo import Elo
from collections import Counter
from datetime import datetime as dt

# Read in path names into a list
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
import copy
clean_vball_data = copy.deepcopy(full_vball_data)
clean_vball_data[0]["divisions"][0]['googleLocation'][0]
clean_vball_data[0]['tournament']
clean_vball_data[0].keys()
clean_vball_data[0]["divisions"][0]

# Change playerProfileIds to playerIds for consistency and count number of changes
# After filtering for 'Girls' and 'Juniors' there are no changes needed
# 11,893 values with incorrect keys that were changed
key_changes=[]
for tournaments in clean_vball_data:
    for divisions in tournaments.get("divisions"):
        if (divisions.get("gender") == "Girls") and (
            divisions.get("ageType") == "Juniors"
        ):
            for matches in divisions.get("matches"):
                if "playerProfileIds" in matches.keys():
                    key_changes.append(matches)
                    matches["playerIds"] = matches.pop("playerProfileIds")
len(key_changes)

# 36,986 matches for 'Girls' and 'Juniors'
# 36,272 matches that are 2 vs 2
# Warning: 1312 matches are missing scores
# 173,080 rows recorded (each game appears 4 times)
clean_vball_games = []
for tournaments in clean_vball_data:
    for divisions in tournaments.get("divisions"):
        if (divisions.get("gender") == "Girls") and (
            divisions.get("ageType") == "Juniors"
        ):
            for matches in divisions.get("matches"):
                # Remove all games that are not two vs two
                if (
                    len(matches.get("playerIds").get("home")) == 2
                    and len(matches.get("playerIds").get("away")) == 2
                    
                    # Check for missing scores condition removed so we can use results
                    # and max(matches.get('games')[0].get('home'),matches.get('games')[0].get('away'))<10
                ):

                    # Note: The first two values are home and the second two are away
                    # Note: They are sorted to ensure consistency when looking as teams
                    # Set side_check to home beforehand and change to away just before iterating to away team
                    player_holder=[sorted(matches.get('playerIds').get('home')),sorted(matches.get('playerIds').get('away'))]
                    side_check_options=['home','away']
                    game_number=0
                    for games in matches.get('games'):
                        if games.get('winner')!=None:
                            game_number+=1
                            side_check_index=0
                            opponent_check_index=1
                            for side in player_holder:
                                side_check=side_check_options[side_check_index]
                                opponent_check=side_check_options[opponent_check_index]
                                side_check_index+=1
                                opponent_check_index-=1
                                for player in side:
                                    row_holder= []
                                    row_holder.append(tournaments.get('tournament'))    #Tournament Name
                                    row_holder.append(tournaments.get('type'))          #Type (Local or National)
                                    row_holder.append(divisions.get('division'))        #Division
                                    row_holder.append(divisions.get('gender'))          #Gender
                                    row_holder.append(divisions.get('ageType'))         #Age Type
                                    row_holder.append(matches.get('id'))                #Match Id
                                    row_holder.append(game_number)                      #Game Number in Series
                                    row_holder.append(matches.get('type'))              #Match Type (Pool or Bracket)
                                    row_holder.append(matches.get('isMatch'))           #Best of Match (T/F Is the match a best of 3, 5, or 7)
                                    row_holder.append(player)                           #Player ID
                                    if player == side[0]:                               #Teammate ID
                                        row_holder.append(side[1]) 
                                    else:
                                        row_holder.append(side[0])

                                    row_holder.append(str(side[0])+'.'+str(side[1]))    #Team ID (Combined player IDs with '.' in middle)
                                    if opponent_check=='home':
                                        row_holder.append(player_holder[0][0])             #Opponent1 ID
                                        row_holder.append(player_holder[0][1])             #Opponent2 ID
                                        row_holder.append(str(player_holder[0][0])+'.'+str(player_holder[0][1])) #Opponent Team ID
                                    else:
                                        row_holder.append(player_holder[1][0])
                                        row_holder.append(player_holder[1][1])
                                        row_holder.append(str(player_holder[1][0])+'.'+str(player_holder[1][1]))
                                        
                                    row_holder.append(side_check==games.get('winner'))  #Game Win (T/F)
                                    row_holder.append(games.get(side_check))            #Team Score
                                    row_holder.append(games.get(opponent_check))        #Opponent Score
                                    row_holder.append(max(games.get(side_check),games.get(opponent_check))<10) #Incomplete Score
                                    row_holder.append(games.get('to'))                  #Winning Score Required
                                    row_holder.append(games.get(side_check)-games.get(opponent_check))  #Score Differential
                                    row_holder.append(games.get(side_check)/max(games.get(side_check)+games.get(opponent_check),1))  #Percentage of points won
                                    row_holder.append(games.get(games.get('winner')))   #Winning Score
                                    row_holder.append(divisions.get('latitude'))        #Latitude
                                    row_holder.append(divisions.get('longitude'))       #Longitude
                                    row_holder.append(divisions.get('timeZoneName'))    #Time Zone Name
                                    
                                    #Convert datetimes (could be more efficient by moving dt_holder outside of loop)
                                    dt_holder=dt.strptime(matches.get('dateTime'),'%Y-%m-%dT%H:%M:%S%z')
                                    dt_holder = dt_holder.replace(tzinfo=None) #Remove timezone, all are UTC
                                    row_holder.append(dt_holder)               #Datetime
                                    #row_holder.append(dt.date(dt_holder))      #Date
                                    #row_holder.append(dt.time(dt_holder))      #Time
                                    #row_holder.append(divisions.get('googleLocation')) #GoogleLocation
                                    clean_vball_games.append(row_holder)

len(clean_vball_games)

##Covert to list of tuples (for structured array later)
clean_vball_games_tuples=[tuple(clean_vball_games[i]) for i in range(len(clean_vball_games))]

#Find proper datatype for datetime column
np.datetime64(clean_vball_games_tuples[0][26]).dtype

#Set up data structure for structured array
#U200 = string of 200 characters
#i4 = 32 bit integer
#f4 = 32 bit float
#M = datetime format
vball_coltypes=[('tournament_name','U200'), ('type', 'U200'), ('division', 'U200'), ('gender', 'U200'), ('age_type', 'U200'), 
                ('series_number', 'i4'), ('match_type', 'U200'), ('isMatch', '?'), ('match_date', 'U200'), ('player_id', 'i4'), 
                ('teammate_id', 'i4'), ('team_id', 'U200'), ('opponent1_id', 'i4'), ('opponent2_id', 'i4'), ('opponent_team_id', 'U200'), 
                ('win', '?'), ('team_score', 'i4'), ('opponent_score', 'i4'), ('incomplete_score', '?'), ('required_score', 'i4'), 
                ('score_differential', 'i4'), ('pct_points_won', 'f4'), ('winning_score', 'i4'), ('latitude', 'f4'), ('longitude', 'f4'), 
                ('time_zone', 'U200'), ('datetime', '<M8[us]')]

#Store structured array in vball
vball=np.array(clean_vball_games_tuples, dtype=vball_coltypes)

#Sort by date (Final Array)
vball.sort(order='datetime')

#Equivalent output in a structured array
vball['tournament_name'][1]
vball[1]['tournament_name']

#Calling multiple fields
vball[['tournament_name','type']][1]

# #Try out new np array on Michael's Elo algo
# db = Elo(k = 20)

# db.addPlayer(home_team)
# db.addPlayer(away_team)
# db.gameOver(home_team, away_team, True)
# len(db.ratingDict)
# min(db.ratingDict.values())
# sum(db.ratingDict.values())/len(db.ratingDict.values())
# max(db.ratingDict.values())

# db.ratingDict.values()

# if match.get("games")[-1].get("winner") == "home": # -1 bc we assume the last winner listed won the overall match
#     db.gameOver(home_team, away_team, True)
# if match.get("games")[-1].get("winner") == "away":
#     db.gameOver(away_team, home_team, 0)

len(set(vball['tournament_name']))