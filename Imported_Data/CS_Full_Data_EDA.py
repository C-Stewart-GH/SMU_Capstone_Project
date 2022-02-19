#I would like to go back through this and do the EDA after filtering for 'Girls' and 'Juniors'
#Currently this includes all data

import json
import os
from this import d
from elosports.elo import Elo
from collections import Counter

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

# Look at tournament info
full_vball_data[0].keys()  # Tournament and type are unique to tournament
full_vball_data[0]["divisions"][0].keys()

# Question: Are 'latitude', 'longitude', 'timeZoneName', 'googleLocation' the same within all tournaments
# Answer: Only one division in one tournament doesn't follow this rule West Coast AAU Junior Olympic Games 2019 16 U Girls
# Index: Tournament 21 and division 1

# Loop to find any index that does not match
for i in range(len(full_vball_data)):
    for j in range(len(full_vball_data[i]["divisions"])):
        if (
            full_vball_data[i]["divisions"][j]["latitude"]
            != full_vball_data[i]["divisions"][0]["latitude"]
            or full_vball_data[i]["divisions"][j]["longitude"]
            != full_vball_data[i]["divisions"][0]["longitude"]
            or full_vball_data[i]["divisions"][j]["timeZoneName"]
            != full_vball_data[i]["divisions"][0]["timeZoneName"]
            or full_vball_data[i]["divisions"][j]["googleLocation"]
            != full_vball_data[i]["divisions"][0]["googleLocation"]
        ):
            print("error:", i, j)

# Details on unmatched data
full_vball_data[21]["tournament"]
full_vball_data[21]["type"]
full_vball_data[21]["divisions"][1].keys()
keys = ["division", "gender", "ageType", "latitude", "longitude", "timeZoneName"]
for i in range(len(full_vball_data[21]["divisions"])):
    for key in keys:
        full_vball_data[21]["divisions"][i].get(key)
    print("\n")

# Look if the keys are consistent within each match
# We find that the players can be listed under playerIds or playerProfileIds
# There are fewer instances of playerProfileIds
full_vball_data[0]["divisions"][0]["matches"][0].keys()

holder = []
for i in range(len(full_vball_data)):
    for j in range(len(full_vball_data[i]["divisions"])):
        for z in range(len(full_vball_data[i]["divisions"][j]["matches"])):
            temp = list(full_vball_data[i]["divisions"][j]["matches"][z].keys())
            holder.extend(temp)

Counter(holder)

# Look at number of games within each match. Consider bracket/pool play and isMatch = T/F

# We find that there can be 1, 2, 3, 4, 5, and 7 games (most are 3 or less)
# There are many more pool play matches and many more isMatch=F
# isMatch=True is 3 games about 98% of the time (weirdly there are 60 1 game matches)
# isMatch=True can apply to both bracket and pool play
# isMatch=False is 1 or 2 games 99.7% of the time (mainly 1)
# Pool games are mainly 1 but sometimes 2 and 3
# Bracket games are mainly 1 but sometimes 3 (Rarely 2 like pool play)
holder = []  # holder is all games
ismatch = []
true_ismatch = []
false_ismatch = []
bracket_or_pool = []
pool_games = []
bracket_games = []
for i in range(len(full_vball_data)):
    for j in range(len(full_vball_data[i]["divisions"])):
        for z in range(len(full_vball_data[i]["divisions"][j]["matches"])):
            temp = len(full_vball_data[i]["divisions"][j]["matches"][z]["games"])
            holder.append(temp)
            bracket_or_pool.append(
                full_vball_data[i]["divisions"][j]["matches"][z]["type"]
            )
            ismatch.append(full_vball_data[i]["divisions"][j]["matches"][z]["isMatch"])
            if full_vball_data[i]["divisions"][j]["matches"][z]["isMatch"] == True:
                true_ismatch.append(temp)
            if full_vball_data[i]["divisions"][j]["matches"][z]["isMatch"] == False:
                false_ismatch.append(temp)
            if full_vball_data[i]["divisions"][j]["matches"][z]["type"] == "Bracket":
                bracket_games.append(temp)
            if full_vball_data[i]["divisions"][j]["matches"][z]["type"] == "Pool":
                pool_games.append(temp)

Counter(holder)
Counter(ismatch)
Counter(true_ismatch)
Counter(false_ismatch)
Counter(bracket_or_pool)
Counter(pool_games)
Counter(bracket_games)

# Check if match ID is unique
# Confirmed it is not but no match ID is used more than twice
# Used example of duplicate ID in this loop to verify that the matches were actually unique
holder = []
for i in range(len(full_vball_data)):
    for j in range(len(full_vball_data[i]["divisions"])):
        for z in range(len(full_vball_data[i]["divisions"][j]["matches"])):
            temp = full_vball_data[i]["divisions"][j]["matches"][z]["id"]
            holder.append(temp)
            if temp == 33654:  # Example of match ID that shows up more than once
                print(full_vball_data[i]["divisions"][j]["matches"][z])

id_count = Counter(holder)
Counter(id_count.values())

# Verify there are two players on every home and away team

# Out of 111328 teams, 97905 have two players
# Team Size: {2: 97905, 4: 9509, 5: 1415, 3: 823, 1: 613, 6: 564, 0: 282, 11: 80, 10: 66, 7: 28, 9: 18, 12: 15, 8: 6, 14: 4})

# Out of 55664 matches 53812 have the same team size on both sides
# Matching: {True: 53812, False: 1852}

# Out of 53812 matches with same team size, 48838 were 2 vs. 2 matches
# Matching by size: {2: 48838, 4: 4063, 3: 323, 1: 216, 6: 160, 5: 121, 0: 77, 11: 8, 10: 6}

holder = []  # holder represents team size
matching = []  # does team size match within a game
matching_by_size = (
    []
)  # size of teams when they match (only show size of one team of match)

for i in range(len(full_vball_data)):
    for j in range(len(full_vball_data[i]["divisions"])):
        for z in range(len(full_vball_data[i]["divisions"][j]["matches"])):
            temp = full_vball_data[i]["divisions"][j]["matches"][z].get(
                "playerIds", "skip"
            )
            if temp == "skip":
                temp = full_vball_data[i]["divisions"][j]["matches"][z].get(
                    "playerProfileIds"
                )
            holder.append(len(temp.get("home")))
            holder.append(len(temp.get("away")))
            matching.append(len(temp.get("home")) == len(temp.get("away")))
            if len(temp.get("home")) == len(temp.get("away")):
                matching_by_size.append(len(temp.get("home")))
            # holder.append(sorted(temp.get('home')))
            # holder.append(sorted(temp.get('away')))
            # if len(temp.get('home'))==14 or len(temp.get('away'))==14: #Example of match ID that shows up more than once
            #     print(full_vball_data[i]['divisions'][j]['matches'][z])
            if len(temp.get("home")) != len(temp.get("away")):
                print(full_vball_data[i]["divisions"][j]["matches"][z])

Counter(holder)
Counter(matching)
Counter(matching_by_size)

# Look at count of game result types
# 92% of matches have a result (all 'no result' games have no home or away scores)
# ~20% of matches with a result have the max home or away score not equal to the 'to' score for the game
# 64% of the above have a max score lower than the 'to' score
# 90% of the above have no scores
# Weirdly 865 games have inputted scores and a result which don't reach the 'to' score
holder = []
holder2 = []
holder3 = []
for i in range(len(full_vball_data)):
    for j in range(len(full_vball_data[i]["divisions"])):
        for z in range(len(full_vball_data[i]["divisions"][j]["matches"])):
            for g in range(
                len(full_vball_data[i]["divisions"][j]["matches"][z]["games"])
            ):
                temp = full_vball_data[i]["divisions"][j]["matches"][z]["games"][g][
                    "winner"
                ]
                holder.append(temp)
                if (
                    full_vball_data[i]["divisions"][j]["matches"][z]["games"][g][
                        "winner"
                    ]
                    == None
                ):
                    holder2.append(
                        full_vball_data[i]["divisions"][j]["matches"][z]["games"][g]
                    )

                game_path = full_vball_data[i]["divisions"][j]["matches"][z]["games"][g]

                # Use comments to pick one of three if statements below
                if (
                    max(game_path["away"], game_path["home"]) != game_path["to"]
                    and full_vball_data[i]["divisions"][j]["matches"][z]["type"] != None
                ):
                    holder3.append(game_path)
                # if max(game_path['away'],game_path['home'])<game_path['to'] and full_vball_data[i]['divisions'][j]['matches'][z]['type']!=None:
                #     holder3.append(game_path)
                # if max(game_path['away'],game_path['home'])!=0 and max(game_path['away'],game_path['home'])<game_path['to'] and full_vball_data[i]['divisions'][j]['matches'][z]['type']!=None:
                #     holder3.append(game_path)


Counter(holder)
holder2[0:10]
holder3[0:10]
len(holder3)

# Look at divisions, gender, and age (I added filter for Juniors only)
# Need to find out what Varsity means
# ~90% of Juniors data is 'Girls'

divisions = []
gender = []
age = []
for i in range(len(full_vball_data)):
    for j in range(len(full_vball_data[i]["divisions"])):
        if full_vball_data[i]["divisions"][j]["ageType"] == "Juniors":
            temp = full_vball_data[i]["divisions"][j]["division"]
            divisions.append(temp)

            temp = full_vball_data[i]["divisions"][j]["gender"]
            gender.append(temp)

            temp = full_vball_data[i]["divisions"][j]["ageType"]
            age.append(temp)

Counter(divisions)
Counter(gender)
Counter(age)



