import numpy as np
import pandas as pd
from collections import Counter
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
import bz2
import random


#Pickle in vball data
with open('Pickle_Files/vball_game_data.pbz2', 'rb') as file:
    uncompressed = bz2.BZ2File(file)
    vball = pickle.load(uncompressed)

#Move to data frame
df_vball=pd.DataFrame(vball)

df_vball.info()
df_vball.head()

#Look at game density over time before time filtering
plt.hist(df_vball[['datetime']],bins=80)
plt.title('Games Played by Date')
plt.show()

#Filter for last year of data
max_date=max(df_vball.datetime)
df_recent=df_vball[df_vball.datetime > max_date - pd.offsets.Day(365)]

#Review games lost due to no score (only 1.5%)
len(df_recent)
len(df_recent[df_recent.incomplete_score==True])
len(df_recent[df_recent.ignored_score==True])
len(df_recent[(df_recent.ignored_score==True) | (df_recent.incomplete_score==True)])
len(df_recent[(df_recent.ignored_score==True) & ~(df_recent.incomplete_score==True)])
no_score=df_recent[~(df_recent.ignored_score==True) & (df_recent.incomplete_score==True)]
no_score.iloc[:,20:26]

#Filter out games with no score
df_recent=df_recent[(df_recent.ignored_score==False) & (df_recent.incomplete_score==False)]
df_recent=df_recent.reset_index()
len(df_recent)/4


#Max of player id in array and dataframe for verification (I thought player ID was only 4 values)
vball[:]['player_id'].max()
max(df_recent['player_id'])

#Do not use required score because of win by 2 rule
df_recent.loc[df_recent.required_score!=df_recent.winning_score,['team_score','opponent_score','required_score','winning_score']]

#Get all opponents in one column for group by
df_recent_dup=df_recent.copy()
df_recent_dup.opponent1_id=df_recent_dup.opponent2_id

df_long=df_recent.copy()
df_long=df_long.append(df_recent_dup, ignore_index = True)

len(df_recent)
len(df_long)

#Group players by points played against each opponent which can be used to understand confidence of rating
grp_pts_played=df_long.groupby(['player_id','opponent1_id'])["winning_score"].sum()

#Group players by pct points won average which can be used to understand who is better
grp_pct_pts_won=df_long.groupby(['player_id','opponent1_id'])["pct_points_won"].mean()

#Check every pair is unique in groupings
Counter([str(k[0])+'|'+str(k[1]) for k,v in dict(grp_pts_played).items()]).most_common(10)
Counter([str(k[0])+'|'+str(k[1]) for k,v in dict(grp_pct_pts_won).items()]).most_common(10)

#Create unique player list and set up empty matricies
player_list=sorted(list(df_recent['player_id'].unique()))
points_matrix=np.zeros((len(player_list),len(player_list)))
pct_points_matrix=np.zeros((len(player_list),len(player_list)))

#Create dictionary of sum of points played and avg pct points won
dict_pts_played=dict(grp_pts_played)
dict_pct_pts_won=dict(grp_pct_pts_won)
player_order_dict={k:v for v,k in enumerate(player_list)}

#Fill points matrix (from row to column id)
for k,v in dict_pts_played.items():
  points_matrix[player_order_dict[k[0]],player_order_dict[k[1]]]=v

#Fill pct points won matrix (from row to column id)
#Using 1-v so that the edges point to the better team
for k,v in dict_pct_pts_won.items():
  pct_points_matrix[player_order_dict[k[0]],player_order_dict[k[1]]]=1-v

#Random Walk
holder=[]
for k in range(100000):
  for i in range(1000):
    if i==0:
      random.seed(k)
      start_row = random.randint(0,len(player_list)-1)
      new_row = random.choices(list(range(len(player_list))), weights=list(pct_points_matrix[start_row,:]), k=1)
    else:
      new_row = random.choices(list(range(len(player_list))), weights=list(pct_points_matrix[new_row[0],:]), k=1)  
  holder.append(new_row[0])
  if k%100==0:
    print('cycle',k,'done')

Counter(holder)
len(holder) 

#Article with graph network code I should review later:https://towardsdatascience.com/python-pagerank-meets-sports-analytics-28e4d395af57