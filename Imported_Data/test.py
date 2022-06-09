import pickle
import numpy as np
import bz2

with open('Pickle_Files/vball_game_data.pbz2', 'rb') as file:
    uncompressed = bz2.BZ2File(file)
    vball = pickle.load(uncompressed)

len(set(vball['player_id']))

vball.dtype

vball[0]