import numpy as np
from collections import Counter
import trueskillthroughtime as ttt
import matplotlib.pyplot as plt
import pickle
import bz2

with open('Pickle_Files/vball_game_data.pbz2', 'rb') as file:
    uncompressed = bz2.BZ2File(file)
    vball = pickle.load(uncompressed)

#Create TrueSkill Through Time Implementation

#Default player parameters
#Player(Gaussian(mu=0.000, sigma=6.000), beta=1.000, gamma=0.030)

#Count number of unique players
len(set(vball['player_id']))

#Count players with at least 5 games
game_counts=[v for k,v in Counter(vball['player_id']).items() if v>=5]
len(game_counts)

#Capture player ids with at least 5 games
common_players=[k for k,v in Counter(vball['player_id']).items() if v>=5]
len(common_players)
common_players[900]

for i in vball[::4]:
    common_player_games=0
    if i['player_id'][i] in common_players and vball['teammate_id'][i] in common_players and vball['opponent1_id'][i] in common_players and vball['opponent2_id'][i] in common_players:
            common_player_games+=1

print(common_player_games)

#Initialize every player into a dictionary
def initialize_players(vball=vball,mu_val=0.0,sigma_val=6.0,beta_val=1.0,gamma_val=0.03):
    unique_players=np.unique(vball['player_id'])
    player_ratings=dict()
    for i in unique_players:
        player_ratings[i]=ttt.Player(ttt.Gaussian(mu=mu_val, sigma=sigma_val),beta=beta_val,gamma=gamma_val)
    return player_ratings


def run_simulation(vball=vball,train_size=20000,mu_val=0.0,sigma_val=6.0,beta_val=1.0,gamma_val=0.03):
    
    player_ratings=initialize_players(vball,mu_val,sigma_val,beta_val,gamma_val)
        
    #Run through every match and update mu and sigma after
    #Looping through every 4th row because the algorithm takes the both teams at once
    loop=0
    prediction=[]
    final_outputs=[]
    for i in vball[::4]:
        outputs=[]
        
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
        
        win_pct_chance=round(g.evidence,5)

        loop+=1
        if loop > train_size:
            if win_pct_chance > .5:
                prediction.append(1)
                outputs.append(1)
            elif win_pct_chance == .5:
                prediction.append(0)
                outputs.append(0)
            else:
                prediction.append(-1)
                outputs.append(-1)

            #append winning team (mu,sigma)
            outputs.append((list(pos[0][0])[0]+list(pos[0][1])[0])/2)

            #append losing team (mu,sigma)
            outputs.append((list(pos[1][0])[0]+list(pos[1][1])[0])/2)
            
            #append skill gap winning team
            outputs.append(abs(list(pos[0][0])[0]-list(pos[0][1])[0]))
            
            #append skill gap losing team
            outputs.append(abs(list(pos[1][0])[0]-list(pos[1][1])[0]))

            #append percentage points won
            if i['ignored_score']==True or i['incomplete_score']==True:
                outputs.append(-1)
            elif i['win']==True:
                outputs.append(i['pct_points_won'])
            elif i['win']==False:
                outputs.append(1-i['pct_points_won'])

            #append percent chance of winning
            outputs.append(round(g.evidence,4))
            
            #Append all of the outputs as one element
            final_outputs.append(list(outputs))

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
    if (hits+misses)!=0:
        acc=hits/(hits+misses)
    else:
        acc=0
    
    #Outputs contain: Binary Outcome, WT avg mu, LT avg mu, WT skill gap, LT skill gap, % points won, and % chance of winning
    return acc,final_outputs

def plot_acc_curve(final_acc,parameter="Input Parameter"):
    max_acc=max(final_acc,key=lambda x:x[1])
    print("Max Acc: ",max_acc[1],'\n',parameter,': ',max_acc[0],sep='')
    plt.plot([x[0] for x in final_acc], [x[1] for x in final_acc])
    plt.xticks([x[0] for x in final_acc])  # add this or the plot api will add extra ticks
    #plt.xticks(rotation=90)
    plt.xlabel(parameter)
    plt.ylabel("Accuracy")
    plt.title(label=str("Accuracy by " + parameter))
    plt.show()
    

#Test multiple training sizes
training_size_test=[x for x in range(0,40001,5000)]
final_acc=[]
for i in training_size_test:
    acc,outputs=run_simulation(vball=vball,train_size=i,mu_val=0.0,sigma_val=6.0,beta_val=1.0,gamma_val=0.03)
    final_acc.append([i,round(acc,4)])

plot_acc_curve(final_acc=final_acc,parameter="Train Size")

#Test multiple sigma sizes (use train_size of 30000)
sigma_size_test=[x/2 for x in range(1,25)]
final_acc=[]
for i in sigma_size_test:
    acc,outputs=run_simulation(vball=vball,train_size=30000,mu_val=0.0,sigma_val=i,beta_val=1.0,gamma_val=0.03)
    final_acc.append([i,round(acc,4)])

plot_acc_curve(final_acc=final_acc,parameter="Sigma Size")

#Test multiple beta sizes (use train_size of 30000 and sigma size of 2.5)
beta_size_test=[x/10 for x in range(0,31)]
final_acc=[]
for i in beta_size_test:
    acc,outputs=run_simulation(vball=vball,train_size=30000,mu_val=0.0,sigma_val=2.5,beta_val=i,gamma_val=0.03)
    final_acc.append([i,round(acc,4)])

plot_acc_curve(final_acc=final_acc,parameter="Beta Size")

#Test multiple mu sizes (use train_size of 30000)
mu_size_test=[x for x in range(0,201,10)]
final_acc=[]
for i in mu_size_test:
    acc,outputs=run_simulation(vball=vball,train_size=30000,mu_val=i,sigma_val=2.5,beta_val=0.5,gamma_val=0.03)
    final_acc.append([i,round(acc,4)])

plot_acc_curve(final_acc=final_acc,parameter="Mu Size")

#Test multiple training sizes
training_size_test=[x for x in range(0,40001,5000)]
final_acc=[]
for i in training_size_test:
    acc,outputs=run_simulation(vball=vball,train_size=i,mu_val=0,sigma_val=2.5,beta_val=0.5,gamma_val=0.03)
    final_acc.append([i,round(acc,4)])

plot_acc_curve(final_acc=final_acc,parameter="Training Size")

#Analyze outputs from optimized model
acc,outputs=run_simulation(vball=vball,train_size=30000,mu_val=0,sigma_val=2.5,beta_val=0.5,gamma_val=0.03)

#Outputs contain: Binary Outcome, WT avg mu, LT avg mu, WT skill gap, LT skill gap, % points won, and % chance of winning
#Understand skill range and gap range
out_array=np.array(outputs)
out_array.shape
out_array[0]

#WT mu
max(out_array[:,1])
min(out_array[:,1])

#LT mu
max(out_array[:,2])
min(out_array[:,2])

#WT skill gap
max(out_array[:,3])
min(out_array[:,3])

#LT skill gap
max(out_array[:,4])
min(out_array[:,4])

#WT % chance of winning
max(out_array[:,6])
min(out_array[:,6])

#Visualize Data
import seaborn as sns
from mpl_toolkits.mplot3d import Axes3D

#3D Plot WT Rating, LT Rating, and WT Win Probability
sns.set_style("whitegrid", {'axes.grid' : False})

fig = plt.figure(figsize=(6,6))

ax = Axes3D(fig)

x = out_array[:,1]
y = out_array[:,2]
z = out_array[:,6]

ax.scatter(x, y, z, c=out_array[:,0],cmap='Paired', marker='o')
ax.set_xlabel('WT Avg Rating')
ax.set_ylabel('LT Avg Rating')
ax.set_zlabel('WT Win Probability')

plt.show()

#WT Rating Histogram
sns.histplot(out_array[:,1])
plt.title('WT Rating')
plt.show()

#LT Rating Histogram
sns.histplot(out_array[:,2])
plt.title('LT Rating')
plt.show()

#Distribution of ratings of winning team when correct vs incorrect
sns.histplot(out_array, x=out_array[:,1], hue=out_array[:,0], element="step",color='blue')
plt.title('WT vs. LT Rating')
plt.show()

#Rating Gap and WT Probability
plt.scatter(out_array[:,1]-out_array[:,2],out_array[:,6])
plt.title('Skill Gap and Win Probability')
plt.xlabel('Skill Gap')
plt.ylabel('Win Probability')
plt.show()


#Outputs contain: Binary Outcome, WT avg mu, LT avg mu, WT skill gap, LT skill gap, % points won, and % chance of winning

#Count of games between winning and losing team
sns.histplot(
    out_array, x=out_array[:,1], y=out_array[:,2],
    bins=30, discrete=(False, False), log_scale=(False, False),
    cbar=True, cbar_kws=dict(shrink=.75),
)
plt.xlabel('WT Rating')
plt.ylabel('LT Rating')
plt.title('Count of LT vs WT Ratings')
plt.show()

#Plot heatmap from array
plt.clf()  # For clearing plot
sns.heatmap(
    all_letter_array,
    cmap="YlOrRd",
    xticklabels=all_letters,
    yticklabels=all_letters,
    linewidth=0.5,
)
plt.xlabel("Probability of To Letter")
plt.ylabel("From Letter")
plt.title("Transition Probabilities")
plt.show()

#
df_X = (out_array[:,6], out_array[:,1]-out_array[:,2], out_array[:,0])
ax = sns.heatmap(df_X)


np_holder=out_array[:,[1,2,0]]
sns.heatmap(out_array[:,1]-out_array[:,2],out_array[:,6])
plt.show()