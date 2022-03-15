import json
import os
import numpy as np
from elosports.elo import Elo
from collections import Counter
from datetime import datetime as dt
import trueskillthroughtime as ttt
import copy
import matplotlib.pyplot as plt

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

#I am parsing one example to check what is new and what is the same from the update
#No comment means the same
clean_vball_data[0].keys() #tournament, type, and division
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

# 53,851 games for 'Girls' and 'Juniors' that are 2 vs 2
# Warning: matches are missing or unrealistic scores and can be filled in with just a win or loss input
# 215,404 rows recorded (each game appears 4 times)
clean_vball_games = []
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
                    player_holder=[sorted(matches.get('playerProfileIds').get('home')),sorted(matches.get('playerProfileIds').get('away'))]
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


#Create TrueSkill Through Time Implementation

#Default player parameters
#Player(Gaussian(mu=0.000, sigma=6.000), beta=1.000, gamma=0.030)

#Initialize every player into a dictionary

unique_players=np.unique(vball['player_id'])
player_ratings=dict()
for i in unique_players:
    player_ratings[i]=ttt.Player()
    
len(list(player_ratings.items()))

#Run through every match and update mu and sigma after
#Looping through every 4th row because the algorithm takes the both teams at once
loop=0
prediction=[]
for i in vball[::4]:
    ##First step is to store winning and losing team
    if i['win']==True:
        winning_team = [player_ratings[i['player_id']], player_ratings[i['teammate_id']]]
        losing_team = [player_ratings[i['opponent1_id']], player_ratings[i['opponent2_id']]]
    if i['win']==False:
        losing_team = [player_ratings[i['player_id']], player_ratings[i['teammate_id']]]
        winning_team = [player_ratings[i['opponent1_id']], player_ratings[i['opponent2_id']]]    

    #Next step is to generate a new mu and sigma for every player based on the result
    g = ttt.Game([winning_team, losing_team]) #Winning team must go first
    pos=g.posteriors()
    
    loop+=1
    if loop >30000:
        if g.evidence > .5:
            prediction.append(1)
        elif g.evidence == .5:
            prediction.append(0)
        else:
            prediction.append(-1)

    #Next we store the new mu and sigma into the player rating dictionary
    if i['win']==True:
        player_ratings[i['player_id']]=ttt.Player(pos[0][0])
        player_ratings[i['teammate_id']]=ttt.Player(pos[0][1])
        player_ratings[i['opponent1_id']]=ttt.Player(pos[1][0])
        player_ratings[i['opponent2_id']]=ttt.Player(pos[1][1])
    if i['win']==False:
        player_ratings[i['player_id']]=ttt.Player(pos[1][0])
        player_ratings[i['teammate_id']]=ttt.Player(pos[1][1])
        player_ratings[i['opponent1_id']]=ttt.Player(pos[0][0])
        player_ratings[i['opponent2_id']]=ttt.Player(pos[0][1])

hits=len([x for x in prediction if x==1])
misses=len([x for x in prediction if x==-1])
ties=len([x for x in prediction if x==0])
acc=hits/(hits+misses)
round(acc,4)

list(player_ratings.items())[0:5]
g.prior
lhs = g.likelihoods[0][0]
ev = g.evidence
ev = round(ev, 3)
print(ev)
pos = g.posteriors()
print(pos[0][0])
print(lhs[0][0] * player_ratings[i['player_id']].prior)


len(vball)

#Test size of training data needed
final_acc=[]
for train_size in range(30000)[::1000]:
    #Initialize every player into a dictionary
    unique_players=np.unique(vball['player_id'])
    player_ratings=dict()
    for i in unique_players:
        player_ratings[i]=ttt.Player()
        
    #Run through every match and update mu and sigma after
    #Looping through every 4th row because the algorithm takes the both teams at once
    loop=0
    prediction=[]
    for i in vball[::4]:
        ##First step is to store winning and losing team
        if i['win']==True:
            winning_team = [player_ratings[i['player_id']], player_ratings[i['teammate_id']]]
            losing_team = [player_ratings[i['opponent1_id']], player_ratings[i['opponent2_id']]]
        if i['win']==False:
            losing_team = [player_ratings[i['player_id']], player_ratings[i['teammate_id']]]
            winning_team = [player_ratings[i['opponent1_id']], player_ratings[i['opponent2_id']]]    

        #Next step is to generate a new mu and sigma for every player based on the result
        g = ttt.Game([winning_team, losing_team]) #Winning team must go first
        pos=g.posteriors()
        
        loop+=1
        if loop >train_size:
            if g.evidence > .5:
                prediction.append(1)
            elif g.evidence == .5:
                prediction.append(0)
            else:
                prediction.append(-1)

        #Next we store the new mu and sigma into the player rating dictionary
        if i['win']==True:
            player_ratings[i['player_id']]=ttt.Player(pos[0][0])
            player_ratings[i['teammate_id']]=ttt.Player(pos[0][1])
            player_ratings[i['opponent1_id']]=ttt.Player(pos[1][0])
            player_ratings[i['opponent2_id']]=ttt.Player(pos[1][1])
        if i['win']==False:
            player_ratings[i['player_id']]=ttt.Player(pos[1][0])
            player_ratings[i['teammate_id']]=ttt.Player(pos[1][1])
            player_ratings[i['opponent1_id']]=ttt.Player(pos[0][0])
            player_ratings[i['opponent2_id']]=ttt.Player(pos[0][1])

    hits=len([x for x in prediction if x==1])
    misses=len([x for x in prediction if x==-1])
    ties=len([x for x in prediction if x==0])
    acc=hits/(hits+misses)
    final_acc.append([train_size,round(acc,4)])


final_acc

plt.plot([x[0] for x in final_acc], [x[1] for x in final_acc])
plt.xticks([x[0] for x in final_acc])  # add this or the plot api will add extra ticks
plt.xticks(rotation=90)
plt.xlabel("Train Size")
plt.ylabel("Accuracy")
plt.title("Accuracy by Train Size (43270 Matches)")
plt.show() #Max is 0.7331 at 16000

#Default player parameters
#Player(Gaussian(mu=0.000, sigma=6.000), beta=1.000, gamma=0.030)
#Test changing sigma
final_acc=[]
for sigma_size in range(11)[1:]:
    #Initialize every player into a dictionary
    unique_players=np.unique(vball['player_id'])
    player_ratings=dict()
    for i in unique_players:
        player_ratings[i]=ttt.Player(ttt.Gaussian(0.0, sigma_size))
        
    #Run through every match and update mu and sigma after
    #Looping through every 4th row because the algorithm takes the both teams at once
    loop=0
    prediction=[]
    for i in vball[::4]:
        ##First step is to store winning and losing team
        if i['win']==True:
            winning_team = [player_ratings[i['player_id']], player_ratings[i['teammate_id']]]
            losing_team = [player_ratings[i['opponent1_id']], player_ratings[i['opponent2_id']]]
        if i['win']==False:
            losing_team = [player_ratings[i['player_id']], player_ratings[i['teammate_id']]]
            winning_team = [player_ratings[i['opponent1_id']], player_ratings[i['opponent2_id']]]    

        #Next step is to generate a new mu and sigma for every player based on the result
        g = ttt.Game([winning_team, losing_team]) #Winning team must go first
        pos=g.posteriors()
        
        loop+=1
        if loop >16000:
            if g.evidence > .5:
                prediction.append(1)
            elif g.evidence == .5:
                prediction.append(0)
            else:
                prediction.append(-1)

        #Next we store the new mu and sigma into the player rating dictionary
        if i['win']==True:
            player_ratings[i['player_id']]=ttt.Player(pos[0][0])
            player_ratings[i['teammate_id']]=ttt.Player(pos[0][1])
            player_ratings[i['opponent1_id']]=ttt.Player(pos[1][0])
            player_ratings[i['opponent2_id']]=ttt.Player(pos[1][1])
        if i['win']==False:
            player_ratings[i['player_id']]=ttt.Player(pos[1][0])
            player_ratings[i['teammate_id']]=ttt.Player(pos[1][1])
            player_ratings[i['opponent1_id']]=ttt.Player(pos[0][0])
            player_ratings[i['opponent2_id']]=ttt.Player(pos[0][1])

    hits=len([x for x in prediction if x==1])
    misses=len([x for x in prediction if x==-1])
    ties=len([x for x in prediction if x==0])
    acc=hits/(hits+misses)
    final_acc.append([sigma_size,round(acc,4)])


final_acc
#plt.clf()
plt.plot([x[0] for x in final_acc], [x[1] for x in final_acc])
plt.xticks([x[0] for x in final_acc])  # add this or the plot api will add extra ticks
#plt.xticks(rotation=90)
plt.xlabel("Sigma Size")
plt.ylabel("Accuracy")
plt.title("Accuracy by Sigma Size (train=16K Matches=43270 Matches)")
plt.show()
max([x[1] for x in final_acc])


#Default player parameters
#Player(Gaussian(mu=0.000, sigma=6.000), beta=1.000, gamma=0.030)
#Test changing beta
final_acc=[]
beta_size_list=[x*.25 for x in range(13)]
for beta_size in beta_size_list:
    #Initialize every player into a dictionary
    unique_players=np.unique(vball['player_id'])
    player_ratings=dict()
    for i in unique_players:
        player_ratings[i]=ttt.Player(ttt.Gaussian(mu=0.000, sigma=2.000),beta=float(beta_size))
        
    #Run through every match and update mu and sigma after
    #Looping through every 4th row because the algorithm takes the both teams at once
    loop=0
    prediction=[]
    for i in vball[::4]:
        ##First step is to store winning and losing team
        if i['win']==True:
            winning_team = [player_ratings[i['player_id']], player_ratings[i['teammate_id']]]
            losing_team = [player_ratings[i['opponent1_id']], player_ratings[i['opponent2_id']]]
        if i['win']==False:
            losing_team = [player_ratings[i['player_id']], player_ratings[i['teammate_id']]]
            winning_team = [player_ratings[i['opponent1_id']], player_ratings[i['opponent2_id']]]    

        #Next step is to generate a new mu and sigma for every player based on the result
        g = ttt.Game([winning_team, losing_team]) #Winning team must go first
        pos=g.posteriors()
        
        loop+=1
        if loop >16000:
            if g.evidence > .5:
                prediction.append(1)
            elif g.evidence == .5:
                prediction.append(0)
            else:
                prediction.append(-1)

        #Next we store the new mu and sigma into the player rating dictionary
        if i['win']==True:
            player_ratings[i['player_id']]=ttt.Player(pos[0][0])
            player_ratings[i['teammate_id']]=ttt.Player(pos[0][1])
            player_ratings[i['opponent1_id']]=ttt.Player(pos[1][0])
            player_ratings[i['opponent2_id']]=ttt.Player(pos[1][1])
        if i['win']==False:
            player_ratings[i['player_id']]=ttt.Player(pos[1][0])
            player_ratings[i['teammate_id']]=ttt.Player(pos[1][1])
            player_ratings[i['opponent1_id']]=ttt.Player(pos[0][0])
            player_ratings[i['opponent2_id']]=ttt.Player(pos[0][1])

    hits=len([x for x in prediction if x==1])
    misses=len([x for x in prediction if x==-1])
    ties=len([x for x in prediction if x==0])
    acc=hits/(hits+misses)
    final_acc.append([beta_size,round(acc,4)])


final_acc
#plt.clf()
plt.plot([x[0] for x in final_acc], [x[1] for x in final_acc])
plt.xticks([x[0] for x in final_acc])  # add this or the plot api will add extra ticks
#plt.xticks(rotation=90)
plt.xlabel("Beta Size")
plt.ylabel("Accuracy")
plt.title("Accuracy by Beta Size (sigma=2 train=16K Matches=43270 Matches)")
plt.show()
max([x[1] for x in final_acc])

#Default player parameters
#Player(Gaussian(mu=0.000, sigma=6.000), beta=1.000, gamma=0.030)
#Test changing gamma
final_acc=[]
gamma_size_list=[x*.01 for x in range(11)]
for gamma_size in gamma_size_list:
    #Initialize every player into a dictionary
    unique_players=np.unique(vball['player_id'])
    player_ratings=dict()
    for i in unique_players:
        player_ratings[i]=ttt.Player(ttt.Gaussian(mu=0.000, sigma=2.000),beta=.25,gamma=gamma_size)
        
    #Run through every match and update mu and sigma after
    #Looping through every 4th row because the algorithm takes the both teams at once
    loop=0
    prediction=[]
    for i in vball[::4]:
        ##First step is to store winning and losing team
        if i['win']==True:
            winning_team = [player_ratings[i['player_id']], player_ratings[i['teammate_id']]]
            losing_team = [player_ratings[i['opponent1_id']], player_ratings[i['opponent2_id']]]
        if i['win']==False:
            losing_team = [player_ratings[i['player_id']], player_ratings[i['teammate_id']]]
            winning_team = [player_ratings[i['opponent1_id']], player_ratings[i['opponent2_id']]]    

        #Next step is to generate a new mu and sigma for every player based on the result
        g = ttt.Game([winning_team, losing_team]) #Winning team must go first
        pos=g.posteriors()
        
        loop+=1
        if loop >16000:
            if g.evidence > .5:
                prediction.append(1)
            elif g.evidence == .5:
                prediction.append(0)
            else:
                prediction.append(-1)

        #Next we store the new mu and sigma into the player rating dictionary
        if i['win']==True:
            player_ratings[i['player_id']]=ttt.Player(pos[0][0])
            player_ratings[i['teammate_id']]=ttt.Player(pos[0][1])
            player_ratings[i['opponent1_id']]=ttt.Player(pos[1][0])
            player_ratings[i['opponent2_id']]=ttt.Player(pos[1][1])
        if i['win']==False:
            player_ratings[i['player_id']]=ttt.Player(pos[1][0])
            player_ratings[i['teammate_id']]=ttt.Player(pos[1][1])
            player_ratings[i['opponent1_id']]=ttt.Player(pos[0][0])
            player_ratings[i['opponent2_id']]=ttt.Player(pos[0][1])

    hits=len([x for x in prediction if x==1])
    misses=len([x for x in prediction if x==-1])
    ties=len([x for x in prediction if x==0])
    acc=hits/(hits+misses)
    final_acc.append([gamma_size,round(acc,4)])


final_acc
#plt.clf()
plt.plot([x[0] for x in final_acc], [x[1] for x in final_acc])
plt.xticks([x[0] for x in final_acc])  # add this or the plot api will add extra ticks
#plt.xticks(rotation=90)
plt.xlabel("Gamma Size")
plt.ylabel("Accuracy")
plt.title("Accuracy by Gamma Size (beta=.25, sigma=2 train=16K Matches=43270 Matches)")
plt.show()
max([x[1] for x in final_acc])