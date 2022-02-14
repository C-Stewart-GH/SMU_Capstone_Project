import json
f = open('/Users/cameron/Documents/SMU_DS/Capstone/SMU_Capstone_Project/Raw Data/Match Data/response_1644436290851.json')
data = json.load(f)
json.dumps(data, indent=4, sort_keys=True)
f.close()

for i in data:
    print (i.keys())

# view all tournament names
for i in data:
    print (i.get('type'), " - ", i.get('tournament'))

for i in data[0].get('divisions'):
    print (i.keys())


data[0].get('divisions')[0].keys()

data[0].get('divisions')[0].get('matches')

len(data[0].get('divisions')[0].get('matches'))

data[0].get('divisions')[0].get('matches')[0]


# experiment with determing team IDs
if data[0].get('divisions')[0].get('matches')[0].get("playerIds").get("home")[0] > data[0].get('divisions')[0].get('matches')[0].get("playerIds").get("home")[1]:
    home_team = str(data[0].get('divisions')[0].get('matches')[0].get("playerIds").get("home")[0]) + "." + str(data[0].get('divisions')[0].get('matches')[0].get("playerIds").get("home")[1])
else:
    home_team = str(data[0].get('divisions')[0].get('matches')[0].get("playerIds").get("home")[1]) + "." + str(data[0].get('divisions')[0].get('matches')[0].get("playerIds").get("home")[0])

if data[0].get('divisions')[0].get('matches')[0].get("playerIds").get("home")[0] > data[0].get('divisions')[0].get('matches')[0].get("playerIds").get("away")[1]:
    away_team = str(data[0].get('divisions')[0].get('matches')[0].get("playerIds").get("away")[0]) + "." + str(data[0].get('divisions')[0].get('matches')[0].get("playerIds").get("away")[1])
else:
    away_team = str(data[0].get('divisions')[0].get('matches')[0].get("playerIds").get("away")[1]) + "." + str(data[0].get('divisions')[0].get('matches')[0].get("playerIds").get("away")[0])

from elosports.elo import Elo
db = Elo(k = 20)

# appending ratingDict with the above IDs
if db.ratingDict.get(home_team) == None:
    db.addPlayer(home_team) # if rating is not entered, defaults to 1500
if db.ratingDict.get(away_team) == None:
    db.addPlayer(away_team) # if rating is not entered, defaults to 1500

db.ratingDict

# submitting results
if data[0].get('divisions')[0].get('matches')[0].get("games")[0].get("winner") == "home":
    db.gameOver(home_team, away_team, True)
if data[0].get('divisions')[0].get('matches')[0].get("games")[0].get("winner") == "away":
    db.gameOver(away_team, home_team, 0)

db.ratingDict


# Loop through every match for the first division/tournament
db = Elo(k = 20)
db.ratingDict
for match in data[0].get('divisions')[0].get('matches'):
    # add teams to the database if needed
    # Each team added to the db will be both player IDs concatenated, with the larger ID first
    if match.get("playerIds").get("home")[0] > match.get("playerIds").get("home")[1]:
        home_team = str(match.get("playerIds").get("home")[0]) + "." + str(match.get("playerIds").get("home")[1])
    else:
        home_team = str(match.get("playerIds").get("home")[1]) + "." + str(match.get("playerIds").get("home")[0])
     # Append dictionary if the player ID does not exist. We don't specify the rating so it defaults to 1500
    if db.ratingDict.get(home_team) == None:
        db.addPlayer(home_team)
    # repeat the same steps for the away team
    if match.get("playerIds").get("away")[0] > match.get("playerIds").get("away")[1]:
        away_team = str(match.get("playerIds").get("away")[0]) + "." + str(match.get("playerIds").get("away")[1])
    else:
        away_team = str(match.get("playerIds").get("away")[1]) + "." + str(match.get("playerIds").get("away")[0])
    if db.ratingDict.get(away_team) == None:
        db.addPlayer(away_team)

    # submitting results
    if match.get("games")[-1].get("winner") == "home": # -1 bc we assume the last winner listed won the overall match
        db.gameOver(home_team, away_team, True)
    if match.get("games")[-1].get("winner") == "away":
        db.gameOver(away_team, home_team, 0)




# view all divisions and genders across the whole data set
for tourn in data:
    for divis in tourn.get("divisions"):
        print(divis.get("division"), divis.get("gender"), divis.get("ageType"))


for tourn in data:
    for divis in tourn.get("divisions"):
        print(divis.keys())


for tourn in data:
    for divis in tourn.get("divisions"):
        if (divis.get("gender") == "Girls") & (divis.get("ageType") == "Juniors"):
            for match in divis.get('matches'):
                pass

# view all tournament names
for i in data:
    print (i.get('type'), " - ", i.get('tournament'))




# Loop through every match of the first data batch
from elosports.elo import Elo
db = Elo(k = 20)
for tourn in data:
    for divis in tourn.get("divisions"):
        if (divis.get("gender") == "Girls") & (divis.get("ageType") == "Juniors"):
            for match in divis.get('matches'):
                
                #debug -> print(tourn.get('tournament'), " - ", match.keys())

                # correct select key names so they are all consistent
                if "playerProfileIds" in match.keys():
                    match["playerIds"] = match.pop("playerProfileIds")

                # at least one match was detected without home player IDs listed. In these cases:
                # skip over the current loop iteration
                if (len(match.get("playerIds").get("home")) == 0) | (len(match.get("playerIds").get("away")) == 0):
                    #print("skipping match from ", tourn.get('tournament'))
                    continue 

                # add teams to the database if needed
                # Each team added to the db will be both player IDs concatenated, with the larger ID first
                if match.get("playerIds").get("home")[0] > match.get("playerIds").get("home")[1]:
                    home_team = str(match.get("playerIds").get("home")[0]) + "." + str(match.get("playerIds").get("home")[1])
                else:
                    home_team = str(match.get("playerIds").get("home")[1]) + "." + str(match.get("playerIds").get("home")[0])
                # Append dictionary if the player ID does not exist. We don't specify the rating so it defaults to 1500
                if db.ratingDict.get(home_team) == None:
                    db.addPlayer(home_team)
                # repeat the same steps for the away team
                if match.get("playerIds").get("away")[0] > match.get("playerIds").get("away")[1]:
                    away_team = str(match.get("playerIds").get("away")[0]) + "." + str(match.get("playerIds").get("away")[1])
                else:
                    away_team = str(match.get("playerIds").get("away")[1]) + "." + str(match.get("playerIds").get("away")[0])
                if db.ratingDict.get(away_team) == None:
                    db.addPlayer(away_team)

                # submitting results
                if match.get("games")[-1].get("winner") == "home": # -1 bc we assume the last winner listed won the overall match
                    db.gameOver(home_team, away_team, True)
                if match.get("games")[-1].get("winner") == "away":
                    db.gameOver(away_team, home_team, 0)
db.ratingDict







# Final Iteration:
import json
# data = []
# files = ("response_1644436290851", "response_1644440709253", "response_1644441792389", "response_1644442447886", 
#         "response_1644442790238", "response_1644443625440", "response_1644443982331", "response_1644444904630",
#         "response_1644445287060", "response_1644501077799", "response_1644506880307", "response_1644513456239",
#         "response_1644518421315", "response_1644520499779")
# for i in files:
#     f = open('C:\\Users\\mmaze\\Desktop\\capstone\\batched_data\\' + i + '.json')
#     data.extend(json.load(f))
#     f.close()

#Read in path names into a list
directory = os.fsencode('/Users/cameron/Documents/SMU_DS/Capstone/SMU_Capstone_Project/Raw Data/Match Data/')
file_path_holder=[]
for file in os.listdir(directory):
     filename = os.fsdecode(file)
     if filename.endswith(".json"): 
         file_path_holder.append(str(directory)[2:-1] + str(filename))

#Extend contents of all files into a list
data=[]
for path in file_path_holder:
    file=open(path)
    data.extend(json.load(file))
    file.close()

from elosports.elo import Elo
db = Elo(k = 20)

for tourn in data:
    for divis in tourn.get("divisions"):
        if (divis.get("gender") == "Girls") & (divis.get("ageType") == "Juniors"):
            for match in divis.get('matches'):
                
                #debug: 
                #print(tourn.get('tournament'), " - ", match.keys())
                #print(match.get("playerIds"))

                # correct select key names so they are all consistent
                if "playerProfileIds" in match.keys():
                    match["playerIds"] = match.pop("playerProfileIds")

                # a few matches list 0 or 1 player IDs. In these cases:
                # skip over the current loop iteration
                if (len(match.get("playerIds").get("home")) != 2) | (len(match.get("playerIds").get("away")) != 2):
                    #print("skipping match from ", tourn.get('tournament'))
                    continue 

                # add teams to the database if needed
                # Each team added to the db will be both player IDs concatenated, with the larger ID first
                if match.get("playerIds").get("home")[0] > match.get("playerIds").get("home")[1]:
                    home_team = str(match.get("playerIds").get("home")[0]) + "." + str(match.get("playerIds").get("home")[1])
                else:
                    home_team = str(match.get("playerIds").get("home")[1]) + "." + str(match.get("playerIds").get("home")[0])
                # Append dictionary if the player ID does not exist. We don't specify the rating so it defaults to 1500
                if db.ratingDict.get(home_team) == None:
                    db.addPlayer(home_team)
                # repeat the same steps for the away team
                if match.get("playerIds").get("away")[0] > match.get("playerIds").get("away")[1]:
                    away_team = str(match.get("playerIds").get("away")[0]) + "." + str(match.get("playerIds").get("away")[1])
                else:
                    away_team = str(match.get("playerIds").get("away")[1]) + "." + str(match.get("playerIds").get("away")[0])
                if db.ratingDict.get(away_team) == None:
                    db.addPlayer(away_team)

                # submitting results
                if match.get("games")[-1].get("winner") == "home": # -1 bc we assume the last winner listed won the overall match
                    db.gameOver(home_team, away_team, True)
                if match.get("games")[-1].get("winner") == "away":
                    db.gameOver(away_team, home_team, 0)

len(db.ratingDict)
min(db.ratingDict.values())
sum(db.ratingDict.values())/len(db.ratingDict.values())
max(db.ratingDict.values())

db.ratingDict.values()
