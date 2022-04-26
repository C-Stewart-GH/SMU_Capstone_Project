from asyncio.windows_events import NULL
import numpy as np
from collections import Counter
from datetime import datetime as dt
import pickle
import bz2


with open('/Users/mmaze/Desktop/vball_game_data.pbz2', 'rb') as file:
    uncompressed = bz2.BZ2File(file)
    vball = pickle.load(uncompressed)

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

