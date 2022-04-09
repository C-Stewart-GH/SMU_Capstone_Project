from asyncio.windows_events import NULL
import json
import os
from pickle import TRUE
from typing_extensions import LiteralString
from unicodedata import numeric
import numpy as np
from elosports.elo import Elo
from collections import Counter
from datetime import datetime as dt

from pyrsistent import v

# Read in path names into a list
directory = os.fsencode(
    "/Users/mmaze/Desktop/GitHub/SMU_Capstone_Project/Raw Data/Match Data/"
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
clean_vball_data[0]["divisions"][0]['timeZoneName']


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




###############################################################################################

# ELO
# https://www.geeksforgeeks.org/elo-rating-algorithm/
import math
from math import log

def KFactor(games_played, k_0_games, k_inf_games, intertia): 
    k_inf_games = k_inf_games - k_0_games
    if k_inf_games <= k_0_games:
        return k_0_games
    else:
        return k_0_games + k_inf_games/(games_played**(1/intertia))

def Probability(rating1, rating2):
    return 1.0 / (1 + (10 ** ((rating2 - rating1) / 400)))

def EloRating(Ra, Rb, K, won):
    # Probability of Player A
    Pa = Probability(Ra, Rb)
    # Case When Player A wins
    if (won) :
        Ra = Ra + K * (1 - Pa)
    # Case When Player A loses
    else :
        Ra = Ra + K * (0 - Pa)
    return(round(Ra, 4))

def LogLoss(outcome, prob):
    if outcome == True:
        result = 1
    else:
        result = 0
    return -1 * ((result * log(prob)) + ((1 - result) * log(1-prob)))

# example:
KFactor(100, 10, 500, 25)
EloRating(1100, 1000, 500, False)
LogLoss(False, .24)

def Simulator(k_0_games, k_inf_games, intertia):
    # elo_db:
    # a dictionary with player id as the key
    # the value is a list of [elo, games_played]
    elo_db = dict()
    # (in)corr_sample_dict:
    # key is list of [games_played, opp_game_played]
    # the value is simply a counter for its respective dictionary
    correct_sample_dict = dict()
    incorr_sample_dict = dict()
    # prob_v_res:
    # This list will be filled with a lists representing each row
    # The first item in this sub list represents a win (1) or loss (0)
    # The following two items hold the Elos
    prob_v_res = []
    max_games_played = 0
    max_opp_game_played = 0
    total_log_loss = 0
    loss_counter = 0

    for index, match in enumerate(vball):
        # add players to database if needed:
        for person in ["player_id", "teammate_id", "opponent1_id", "opponent2_id"]:
            if match[person] not in elo_db.keys():
                elo_db.update({match[person]: [1200, 0]})
        # set parameters     
        avg_oppon = .5 * (elo_db.get(match["opponent1_id"])[0] + elo_db.get(match["opponent2_id"])[0])
        player_elo = elo_db.get(match["player_id"])[0]
        games_played = elo_db.get(match["player_id"])[1] + 1
        opp_game_played = int(.5 * (elo_db.get(match["opponent1_id"])[1] + elo_db.get(match["opponent1_id"])[1]))

        if games_played > max_games_played:
            max_games_played = games_played
        if opp_game_played > max_opp_game_played:
            max_opp_game_played = opp_game_played

        if index >= (len(vball) * .4):

            # skip over situations where both players are unranked or have same elo
            #if player_elo == avg_oppon:
            #    continue

            # compare preds to actual
            prob = Probability(player_elo, avg_oppon)
            total_log_loss += LogLoss(match["win"], prob)
            loss_counter += 1
            if prob > .5:
                pred_win = True
            else:
                pred_win = False
            if pred_win == match["win"]:
                prob_v_res.append([1, player_elo, avg_oppon])
                if str([games_played, opp_game_played]) not in correct_sample_dict.keys():
                    correct_sample_dict.update({str([games_played, opp_game_played]): 1})
                else:
                    correct_sample_dict.update({str([games_played, opp_game_played]): correct_sample_dict.get(str([games_played, opp_game_played])) + 1})
            else:
                prob_v_res.append([0, player_elo, avg_oppon])
                if str([games_played, opp_game_played]) not in incorr_sample_dict.keys():
                    incorr_sample_dict.update({str([games_played, opp_game_played]): 1})
                else:
                    incorr_sample_dict.update({str([games_played, opp_game_played]): incorr_sample_dict.get(str([games_played, opp_game_played])) + 1})
        k = KFactor(games_played, k_0_games, k_inf_games, intertia)

        # perform calculations/updates
        new_elo = EloRating(player_elo, avg_oppon, k, match["win"])
        elo_db.update({match["player_id"]: [new_elo, games_played]})
    log_loss = total_log_loss/loss_counter
    accuracy_dict = {"correct_sample_dict":correct_sample_dict, "incorr_sample_dict":incorr_sample_dict}
    return (accuracy_dict, max_games_played, max_opp_game_played, elo_db, log_loss, prob_v_res)

def ConditionalAcc(accuracy_dict, min_samp_player, max_samp_player, min_samp_opponent, max_samp_opponent):
    correct = []
    incorr = []
    for i in range(min_samp_player, max_samp_player+1):
        for j in range(min_samp_opponent, max_samp_opponent+1):
            if str([i,j]) in accuracy_dict.get("correct_sample_dict").keys():
                correct.append(accuracy_dict.get("correct_sample_dict").get(str([i,j])))
            if str([i,j]) in accuracy_dict.get("incorr_sample_dict").keys():
                incorr.append(accuracy_dict.get("incorr_sample_dict").get(str([i,j])))
    return round(100 * sum(correct)/(sum(correct) + sum(incorr)),3)

def GridSearch(k_0_list, k_inf_list, intertia_list, loss_metric):
    grid_search = dict()
    for k_0 in k_0_list:
            for k_inf in k_inf_list:
                for intert in intertia_list:
                    output = Simulator(k_0_games = k_0, k_inf_games = k_inf, intertia = intert)
                    accuracy_dict, max_games_played, max_opp_game_played, elo_db, log_loss, prob_v_res = output
                    if loss_metric == "log_loss":
                        loss = log_loss
                    elif loss_metric == "acc":
                        loss = ConditionalAcc(accuracy_dict, 0, max_games_played, 0, max_opp_game_played)
                    grid_search.update({str([k_0, k_inf, intert]): loss})
    if loss_metric == "log_loss":
        return min(grid_search.items(), key=lambda x: x[1]) 
    elif loss_metric == "acc":
        return max(grid_search.items(), key=lambda x: x[1]) 

#GridSearch([10, 20, 30, 500], [20, 40, 50, 100, 500], [1, 25, 100], "log_loss")

# best params by "log_loss": non adaptive k value 500
# another time, it returned ('[10, 500, 25]', 0.4141258371136447)
output = Simulator(k_0_games = 10, k_inf_games = 500, intertia = 25)
accuracy_dict, max_games_played, max_opp_game_played, elo_db, log_loss, prob_v_res = output
ConditionalAcc(accuracy_dict, 0, max_games_played, 0, max_opp_game_played)
# the more opponent samples we have the better the accuracy 
# the less player samples we have the better the accuracy 

###############################################################################################
# Compare accuracies across different sample sizes

outer_list=[]
for i in range(1,50):
    inner_list = []
    for j in range(1,50):
        if accuracy_dict.get("correct_sample_dict").get(str([i,j])) == None:
            inner_list.append(NULL)
        elif accuracy_dict.get("incorr_sample_dict").get(str([i,j])) == None:
            inner_list.append(NULL)
        else:
            num_correct = accuracy_dict.get("correct_sample_dict").get(str([i,j]))
            num_incorr = accuracy_dict.get("incorr_sample_dict").get(str([i,j]))
            acc = round(100 * num_correct / (num_correct + num_incorr), 2)
            inner_list.append(acc)
    outer_list.append(inner_list)

import seaborn as sns
import matplotlib.pyplot as plt
ax = sns.heatmap(outer_list)
ax.set_xlabel("opponent samples")
ax.set_ylabel("player samples")
plt.show()

# find min/max elo, along with the matches played and key: 
#min([[val[0], val[1], key] for key, val in elo_db.items()])
#max([[val[0], val[1], key] for key, val in elo_db.items()])

###############################################################################################
# Compare elo win probabilities against proportion of correct predictions

# key holds a tuple of player and opponent elos
# this loop bins matches based off every 100 elo and tracks how many correct v incorrect predictions
bin_dict = dict()
for row in prob_v_res:
    if row[1] < row[2]:
        bin_floor = row[1]
        bin_ceil = row[2]
    else:
        bin_floor = row[2]
        bin_ceil = row[1] 

    bin_floor = int(bin_floor//100 * 100)
    # if residual for bin_ceil % 100, we need to round up to the nearest 100:
    if bin_ceil % 100 > 0:
        bin_ceil = int((bin_ceil//100 + 1) * 100)
    else:
        bin_ceil = int((bin_ceil//100) * 100)

    if (bin_floor, bin_ceil) not in bin_dict.keys():
        bin_dict.update({(bin_floor, bin_ceil): [0, 0]})
    
    #print(row[0])
    # NEED TO CONFIRM WHY THERE AREN'T REPEAT DIGITS BACK-TO-BACK
    # GAMES ARE REPEATED FROM PLAYER AND OPPONENT PERSPECTIVES SO IT SHOULD REPEAT
    win_loss_counter = bin_dict.get((bin_floor, bin_ceil))
    if row[0] == 1:
        bin_dict.update({(bin_floor, bin_ceil): [win_loss_counter[0] + 1, win_loss_counter[1]]})
    else:
        bin_dict.update({(bin_floor, bin_ceil): [win_loss_counter[0], win_loss_counter[1] + 1]})

# need to loop through dict and delete values that arent above a certain sample criteria
keys_to_del = []
for key, val in bin_dict.items():
    #print(key)
    #print(sum(val))
    if sum(val) < 20:
        keys_to_del.append(key)
for key in keys_to_del:
    del bin_dict[key]

prob_v_outcome = dict()
for bin, outcome in bin_dict.items():
    expected = round(100 * Probability(bin[1], bin[0]), 2)
    returned = round(100 * outcome[0] / (outcome[0]+outcome[1]), 2)
    dif = round(expected - returned, 2)
    prob_v_outcome.update({bin: [expected, returned, dif]})

dict(sorted(prob_v_outcome.items(), key=lambda item: item[1][2]))

dif = sorted([x[2] for x in prob_v_outcome.values()])
fig, ax = plt.subplots()
ax.hist(dif, bins = 20)
plt.show()

