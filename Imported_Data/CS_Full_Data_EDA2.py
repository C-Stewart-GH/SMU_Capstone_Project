import json
import os
from this import d
from elosports.elo import Elo
from collections import Counter
import copy

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
    
#Filter down to Girls and Juniors
#Fix key 'playerProfileIds' to 'playerIds'
vball_data = copy.deepcopy(full_vball_data)

holder=[]
for tournaments in vball_data:
    for divisions in tournaments.get("divisions"):
        if (divisions.get("gender") == "Girls") and (
            divisions.get("ageType") == "Juniors"
        ):
            for matches in divisions.get("matches"):
                if "playerProfileIds" in matches.keys():
                    key_changes.append(matches)
                    matches["playerIds"] = matches.pop("playerProfileIds")
                    holder.append(tournaments.get('tournament')+', MatchId: '+str(matches.get('id')))
len(holder)
holder=list(set(holder))
print(*holder[0:10], sep='\n')


#Check for non-2vs2 games
holder=[]
for tournaments in vball_data:
    for divisions in tournaments.get("divisions"):
        if (divisions.get("gender") == "Girls") and (
            divisions.get("ageType") == "Juniors"
        ):
            for matches in divisions.get("matches"):
                if (
                    len(matches.get("playerIds").get("home")) != 2
                    or len(matches.get("playerIds").get("away")) != 2
                ):
                    holder.append(tournaments.get('tournament')+', MatchId: '+str(matches.get('id')))

len(holder)
holder=list(set(holder))
print(*holder[0:10], sep='\n')
                    
#Check for None Result
holder=[]                  
for tournaments in vball_data:
    for divisions in tournaments.get("divisions"):
        if (divisions.get("gender") == "Girls") and (
            divisions.get("ageType") == "Juniors"
        ):
            for matches in divisions.get("matches"):
                # Remove all games that are not two vs two
                if (
                    len(matches.get("playerIds").get("home")) == 2
                    and len(matches.get("playerIds").get("away")) == 2
                ):
                    for games in matches.get('games'):
                        if games.get('winner')==None:
                            holder.append(tournaments.get('tournament')+', MatchId: '+str(matches.get('id'))+', winner: '+str(games.get('winner')))


len(holder)
holder=list(set(holder))
print(*holder[0:10], sep='\n')  

#Check for unrealistic scores
holder=[]                  
for tournaments in vball_data:
    for divisions in tournaments.get("divisions"):
        if (divisions.get("gender") == "Girls") and (
            divisions.get("ageType") == "Juniors"
        ):
            for matches in divisions.get("matches"):
                # Remove all games that are not two vs two
                if (
                    len(matches.get("playerIds").get("home")) == 2
                    and len(matches.get("playerIds").get("away")) == 2
                ):
                    for games in matches.get('games'):
                        if games.get('winner')!=None and max(games.get('home'),games.get('away'))<10:
                            holder.append(tournaments.get('tournament')+', MatchId: '+str(matches.get('id'))+', winner: '+games.get('winner')+', home: '+str(games.get('home'))+', away: '+str(games.get('away')))


len(holder)
holder=list(set(holder))
print(*holder[0:10], sep='\n')    

#Check for incorrect outcome decisions
holder=[]                  
for tournaments in vball_data:
    for divisions in tournaments.get("divisions"):
        if (divisions.get("gender") == "Girls") and (
            divisions.get("ageType") == "Juniors"
        ):
            for matches in divisions.get("matches"):
                # Remove all games that are not two vs two
                if (
                    len(matches.get("playerIds").get("home")) == 2
                    and len(matches.get("playerIds").get("away")) == 2
                ):
                    for games in matches.get('games'):
                        if games.get('winner')!=None and max(games.get('home'),games.get('away'))>10:
                            if (
                                games.get('winner')=='home' and games.get('home')<games.get('away')
                            )or (
                                games.get('winner')=='away' and games.get('home')>games.get('away')
                            )or (
                                games.get('winner')=='home' and games.get('home')==games.get('away')
                            )or (
                                games.get('winner')=='away' and games.get('home')==games.get('away')
                            ):
                                holder.append(tournaments.get('tournament')+', MatchId: '+str(matches.get('id'))+', winner: '+games.get('winner')+', home: '+str(games.get('home'))+', away: '+str(games.get('away')))


len(holder)
print(*holder[0:10], sep='\n')                 