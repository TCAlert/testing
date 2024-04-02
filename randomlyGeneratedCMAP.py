import numpy as np 
import random 
from matplotlib.colors import ListedColormap, LinearSegmentedColormap

def temperature():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/200, "#f2bbd4"), 
    (200/200, "#ffd9ee")])

    return newcmp.reversed()

bottom = 0
top = 150

random.randint(bottom, top)