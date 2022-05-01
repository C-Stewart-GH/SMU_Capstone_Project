from asyncio.windows_events import NULL
import numpy as np
from collections import Counter
from datetime import datetime as dt
import pickle
import bz2

with open('Pickle_Files/vball_match_data.pbz2', 'rb') as file:
    uncompressed = bz2.BZ2File(file)
    vball = pickle.load(uncompressed)

np.unique(vball['tournament_name'])[1]


range(len(vball))

# work with only one tournament first
filter_arr = []
for idx, _ in enumerate(vball):
    if vball['tournament_name'][idx] == vball['tournament_name'][10000]:
        filter_arr.append(idx)
newarr = vball[filter_arr]


# In this loop, we are going to loop through every match, then loop through the home and away team.
# If that team is not a key in the team_dict container, add them. Their value is their [win, loss] record
# Finally, update that team's record based off the match outcome
team_dict = dict()
for match in newarr:
    home_ids = (str(match["homePlayer1"]) + "_" + str(match["homePlayer2"]))
    away_ids = (str(match["awayPlayer1"]) + "_" + str(match["awayPlayer2"]))

    for team_id in [home_ids, away_ids]:
        if team_id not in team_dict.keys():
            team_dict.update({team_id: [0, 0]})
        tourn_record = team_dict.get(team_id)

        if team_id == home_ids:
            good_outcome = "Home"
            bad_outcome = "Away"
        elif team_id == away_ids:
            good_outcome = "Away"
            bad_outcome = "Home"  
  
        if match["matchWinner"] == good_outcome:
            team_dict.update({team_id: [tourn_record[0] + 1, tourn_record[1]]})
        elif match["matchWinner"] == bad_outcome:
            team_dict.update({team_id: [tourn_record[0], tourn_record[1] + 1]})

dict(sorted(team_dict.items(), key=lambda item: item[1][0]))

# any players change teams mid way through (e.g. injury)