from netCDF4 import Dataset      # Read / Write NetCDF4 files
import matplotlib.pyplot as plt
from numpy.core.function_base import linspace  # Plotting library
import cartopy, cartopy.crs as ccrs  # Plot maps
import numpy.ma as ma
import numpy as np
import pandas as pd
import xarray as xr
import datetime
from matplotlib import cm
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
#import goesRequest2 as goes2

# IR Color Tables
def swir():
    num1 = 15
    num2 = 55
    num3 = 40

    top = cm.get_cmap('Blues', num1)
    mid = cm.get_cmap('plasma', num2)
    bot = cm.get_cmap('bone_r', num3)

    newcolors = np.vstack((top(np.linspace(0, 1, num1)),
                           mid(np.linspace(0, 1, num2)),
                           bot(np.linspace(0, 1, num3))))
    newcmp = ListedColormap(newcolors, name='temp')
    return newcmp

def oldspooky():
    num1 = 20
    num2 = 85
    num3 = 30

    top = cm.get_cmap('Greys', num1)
    mid = cm.get_cmap('CMRmap', num2)
    bot = cm.get_cmap('Greys', num3)

    newcolors = np.vstack((top(np.linspace(0, 1, num1)),
                           mid(np.linspace(0, 1, num2)),
                           bot(np.linspace(0, 1, num3))))
    newcmp = ListedColormap(newcolors, name='temp')
    return newcmp

def santa():
    num1 = 20
    num2 = 30
    num3 = 40
    num4 = 50

    top = LinearSegmentedColormap.from_list("", [(0.0, "#cfcfcf"), (1, "#d9c548")])
    mid = cm.get_cmap('PiYG', num2)
    mid2 = cm.get_cmap('Reds_r', num3)
    bot = cm.get_cmap('Greys', num4)

    newcolors = np.vstack((top(np.linspace(0, 1, num1)),
                           mid(np.linspace(0.5, 1, num2)),
                           mid2(np.linspace(0.2, 0.8, num3)),
                           bot(np.linspace(0.1, 0.9, num4))))
    newcmp = ListedColormap(newcolors, name='temp')

    vmax = 40
    vmin = -100

    return newcmp, vmax, vmin

def gay():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/130, '#000000'),
    (20/130, '#cccccc'),
    (20/130, '#1c2a7a'),
    (60/130, "#56db58"), 
    (75/130, "#fcfa68"),
    (90/130, "#ed422f"),
    (95/130, "#c71e75"),
    (100/130, "#170824"),
    (110/130, "#a145ed"),
    (120/130, "#dce6f7"),
    (130/130, "#000000")])

    vmax = 30
    vmin = -100

    return newcmp.reversed(), vmax, vmin

def ca():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/130, '#000000'),
    (19/130, "#626466"),
    (21/130, "#1c2a7a"),
    (30/130, "#0b3a54"),
    (40/130, "#15476b"),
    (60/130, "#098292"),
    (70/130, "#18bc71"),
    (80/130, "#61ec22"),
    (87.5/130, "#e8ed29"),
    (95/130, "#f88d1e"),
    (105/130, "#ce221c"),
    (110/130, "#ac61ce"),
    (115/130, "#563ab4"),
    (120/130, "#cbcbfe"),
    (130/130, "#FFFFFF")])

    vmax = 30
    vmin = -100

    return newcmp.reversed(), vmax, vmin

def ca2():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/130, '#000000'),
    (19/130, "#626466"),
    (21/130, "#1c2a7a"),
    (30/130, "#0b3a54"),
    (40/130, "#15476b"),
    (50/130, "#098292"),
    (60/130, "#18bc71"),
    (70/130, "#61ec22"),
    (80/130, "#e8ed29"),
    (85/130, "#f88d1e"),
    (95/130, "#ce221c"),
    (100/130, "#ac61ce"),
    (105/130, "#563ab4"),
    (117.5/130, "#cbcbfe"),
    (122.5/130, "#FFFFFF"),
    (122.5/130, "#ffd919"),
    (130/130, "#292825")])

    vmax = 30
    vmin = -100

    return newcmp.reversed(), vmax, vmin

def gaytestir():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/150, '#750000'),
    (40/150, "#decbbd"),
    (60/150, "#2c124a"),
    (70/150, "#2b27a3"),
    (80/150, "#65a87f"),
    (90/150, "#e0e64e"),
    (100/150, "#c26915"),
    (110/150, "#752a29"),
    (120/150, "#a60503"),
    (130/150, "#d599f7"),
    (150/150, "#000000")])

    vmax = 50
    vmin = -100

    return newcmp.reversed(), vmax, vmin 

def rainbow():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/145, '#110112'),
    (15/145, '#ff09fd'),
    (32.5/145, '#00007d'),
    (50/145, "#06fefe"), 
    (70/145, "#007d0c"),
    (87/145, "#ffff2d"),
    (123/145, "#7d0706"),
    (135/145, "#ff1a18"),
    (145/145, "#FFFFFF")])

    vmax = 55
    vmin = -90

    return newcmp.reversed(), vmax, vmin

def rainbow2():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/120, '#040257'),
    (10/120, "#524ab0"),
    (20/120, "#b5c1f5"), 
    (20/120, "#04da02"),
    (30/120, "#037904"),
    (45/120, "#ffff2d"),
    (70/120, "#b44c05"),
    (80/120, "#7d0706"),
    (90/120, "#ff1a18"),
    (100/120, "#fc6e6b"),
    (110/120, "#FFFFFF"),
    (110/120, "#000000"),
    (120/120, "#000000")])

    vmax = 20
    vmin = -100

    return newcmp.reversed(), vmax, vmin

def rammb():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/150, "#b55555"),
    (10/150, "#b58555"),
    (25/150, "#000000"),
    (80/150, "#fefefe"),
    (80/150, "#a8fdfd"),
    (100/150, "#545454"),
    (100/150, "#000067"),
    (110/150, "#0000fe"),
    (110/150, "#00600d"),
    (120/150, "#00fc00"),
    (120/150, "#4d0d00"),
    (130/150, "#fb0000"),
    (130/150, "#fcfc00"),
    (140/150, "#000000"),
    (140/150, "#FFFFFF"),
    (150/150, "#040404")])

    vmax = 50
    vmin = -100

    return newcmp.reversed(), vmax, vmin

def avn():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/131, "#000000"),
    (80/131, "#FFFFFF"),
    (80/131, "#0096FF"),
    (100/131, "#006e96"),
    (100/131, "#a0a000"),
    (110/131, "#fafa00"),
    (110/131, "#fafa00"),
    (120/131, "#c87800"),
    (120/131, "#fa0000"),
    (130/131, "#c80000"),
    (131/131, "#585858")])

    vmax = 50
    vmin = -81

    return newcmp.reversed(), vmax, vmin

def funktop():
    newcmp=LinearSegmentedColormap.from_list("",[
    (0/128, "#000000"),
    (1/128, "#141414"),
    (54/128, "#d8d8d8"),
    (55/128, "#646400"),
    (74/128, "#f8f800"),
    (75/128, "#000078"),
    (94/128, "#00fcfc"),
    (95/128, "#540000"),
    (106/128,"#fc0000"),
    (107/128,"#fc5050"),
    (114/128,"#fc8c8c"),
    (115/128,"#00fc00"),
    (127/128,"#fcfcfc"),
    (128/128,"#fcfcfc")])

    vmax = 36
    vmin = -92

    return newcmp.reversed(), vmax, vmin

def jsl():
    newcmp=LinearSegmentedColormap.from_list("",[
    (0/167, "#000000"),
    (1.5/167, "#000000"),
    (2/167, "#1C001C"),
    (3.5/167, "#1C001C"),
    (4/167, "#3C003C"),
    (5.5/167, "#3C003C"),
    (6/167, "#5C005C"),
    (7.5/167, "#5C005C"),
    (8/167, "#7C007C"),
    (9.5/167, "#7C007C"),
    (10/167, "#9C009C"),
    (11.5/167, "#9C009C"),
    (12/167, "#BC00BC"),
    (13.5/167, "#BC00BC"),
    (14/167, "#DC00DC"),
    (15.5/167, "#DC00DC"),
    (16/167, "#FC00FC"),
    (17.5/167, "#FC00FC"),
    (18/167, "#E000EC"),
    (19.5/167, "#E000EC"),
    (20/167, "#C400DC"),
    (21.5/167, "#C400DC"),
    (22/167, "#A800D0"),
    (23.5/167, "#A800D0"),
    (24/167, "#8C00C0"),
    (25.5/167, "#8C00C0"),
    (26/167, "#7000B4"),
    (27.5/167, "#7000B4"),
    (28/167, "#5400A4"),
    (29.5/167, "#5400A4"),
    (30/167, "#380098"),
    (31.5/167, "#380098"),
    (32/167, "#1C0088"),
    (33.5/167, "#1C0088"),
    (34/167, "#00007C"),
    (35.5/167, "#00007C"),
    (36/167, "#001C88"),
    (37.5/167, "#001C88"),
    (38/167, "#003898"),
    (39.5/167, "#003898"),
    (40/167, "#0054A4"),
    (41.5/167, "#0054A4"),
    (42/167, "#0070B4"),
    (43.5/167, "#0070B4"),
    (44/167, "#008CC0"),
    (45.5/167, "#008CC0"),
    (46/167, "#00A8D0"),
    (47.5/167, "#00A8D0"),
    (48/167, "#00C4DC"),
    (49.5/167, "#00C4DC"),
    (50/167, "#00E0EC"),
    (51.5/167, "#00E0EC"),
    (52/167, "#00FCFC"),
    (53.5/167, "#00FCFC"),
    (54/167, "#00ECE0"),
    (55.5/167, "#00ECE0"),
    (56/167, "#00DCC4"),
    (57.5/167, "#00DCC4"),
    (58/167, "#5C5C5C"),
    (65.5/167, "#686868"),
    (66/167, "#707070"),
    (71.5/167, "#787878"),
    (72/167, "#808080"),
    (77.5/167, "#888888"),
    (78/167, "#909090"),
    (83.5/167, "#989898"),
    (84/167, "#A0A0A0"),
    (91/167, "#A8A8A8"),
    (92/167, "#B0B0B0"),
    (95/167, "#B0B0B0"),
    (96/167, "#B8B8B8"),
    (99/167, "#B8B8B8"),
    (100/167, "#C0C0C0"),
    (103/167, "#C0C0C0"),
    (104/167, "#C8C8C8"),
    (107/167, "#C8C8C8"),
    (108/167, "#D0D0D0"),
    (111/167, "#D0D0D0"),
    (112/167, "#D8D8D8"),
    (113/167, "#D8D8D8"),
    (114/167, "#3C0000"),
    (126/167, "#FF3C3C"),
    (127/167, "#FF4747"),
    (137/167, "#FFBEBE"),
    (138/167, "#650065"),
    (157/167, "#DEC9DE"),
    (158/167, "#000000"),
    (167/167, "#000000")])

    vmax = 57
    vmin = -110

    return newcmp.reversed(), vmax, vmin

def bd():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/120, "#a8d1ff"),
    (11/120, "#011a36"), 
    (12/120, "#000000"),
    (12/120, "#1d1d1d"),
    (21/120, "#fafafa"),
    (21/120, "#3a3a3a"),
    (60/120, "#d2d2d2"),
    (60/120, "#5b5b5b"),
    (71/120, "#5b5b5b"),
    (71/120, "#9a9a9a"),
    (83/120, "#9a9a9a"),
    (83/120, "#b7b7b7"),
    (93/120, "#b7b7b7"),
    (93/120, "#000000"),
    (99/120, "#000000"),
    (99/120, "#f9f9f9"),
    (105/120, "#f9f9f9"),
    (105/120, "#9e9e9e"),
    (110/120, "#9e9e9e"),
    (110/120, "#424242"),
    (120/120, "#424242")])

    vmax = 30
    vmin = -90

    return newcmp.reversed(), vmax, vmin

def bd05():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/120, "#000000"),
    (21/120, "#FFFFFF"),

    (21/120, "#6d6d6d"),
    (60/120, "#cacaca"),

    (60/120, "#3c3c3c"),
    (71/120, "#3c3c3c"),

    (71/120, "#6e6e6e"),
    (83/120, "#6e6e6e"),

    (83/120, "#a0a0a0"),
    (93/120, "#a0a0a0"),
    
    (93/120, "#000000"),
    (99/120, "#000000"),

    (99/120, "#FFFFFF"),
    (105/120, "#FFFFFF"),

    (105/120, "#878787"),
    (110/120, "#878787"),

    (110/120, "#555555"),
    (120/120, "#555555")])

    vmax = 30
    vmin = -90

    return newcmp.reversed(), vmax, vmin

def bd2():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/120, "#b58555"),
    (12/120, "#090926"),
    
    (21/120, "#ffffff"),
    (21/120, "#fefefe"),
    (60/120, "#4c8032"), 

    (60/120, "#ffff29"),
    (71/120, "#ffff29"),

    (71/120, "#ff8129"),
    (83/120, "#ff8129"),

    (83/120, "#ff2929"),
    (93/120, "#ff2929"),

    (93/120, "#000000"),
    (99/120, "#000000"),

    (99/120, "#e6dada"),
    (105/120, "#e6dada"),

    (105/120, "#261940"),
    (110/120, "#261940"),

    (110/120, "#990f97"),
    (120/120, "#990f97")])

    vmax = 30
    vmin = -90

    return newcmp.reversed(), vmax, vmin

def bd3():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/130, "#b58555"),
    (22/130, "#090926"),
    (22/130, "#000000"),
    
    (31/130, "#ffffff"),
    (31/130, "#fefefe"),
    (70/130, "#404080"), 

    (70/130, "#ffe329"),
    (81/130, "#ffe329"),

    (81/130, "#de7022"),
    (93/130, "#de7022"),

    (93/130, "#b31b1b"),
    (103/130, "#b31b1b"),

    (103/130, "#2e0202"),
    (109/130, "#2e0202"),

    (109/130, "#e6dada"),
    (115/130, "#e6dada"),

    (115/130, "#bc67b7"),
    (120/130, "#bc67b7"),

    (120/130, "#990f97"),
    (125/130, "#990f97"),

    (125/130, "#601f60"),
    (130/130, "#601f60")])

    vmax = 40
    vmin = -90

    return newcmp.reversed(), vmax, vmin

def ibtracs():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/120, "#000000"),
    (12/120, "#b881a1"), 
    (12/120, "#000000"),
    (12/120, "#1d1d1d"),
    (21/120, "#fafafa"),
    (21/120, "#664848"),
    (60/120, "#ffe1e1"),
    (60/120, "#9f2323"),
    (71/120, "#9f2323"),

    (71/120, "#ff6e1c"),
    (83/120, "#ff6e1c"),
    
    (83/120, "#ffe132"),
    (93/120, "#ffe132"),
    
    (93/120, "#a0d2fe"),
    (99/120, "#a0d2fe"),
    
    (99/120, "#02bffd"),
    (105/120, "#02bffd"),
    
    (105/120, "#4169e1"),
    (110/120, "#4169e1"),
    
    (110/120, "#000096"),
    (115/120, "#000096"),
    
    (115/120, "#FFFFFF"),
    (120/120, "#FFFFFF")])

    vmax = 30
    vmin = -90

    return newcmp.reversed(), vmax, vmin

def ibtracs2():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/120, "#000000"),
    (21/120, "#fafafa"),
    (21/120, "#664848"),
    (60/120, "#ffe1e1"),
    (60/120, "#9f2323"),
    (71/120, "#9f2323"),

    (71/120, "#ff6e1c"),
    (83/120, "#ff6e1c"),
    
    (83/120, "#ffe132"),
    (93/120, "#ffe132"),
    
    (93/120, "#a0d2fe"),
    (99/120, "#a0d2fe"),
    
    (99/120, "#02bffd"),
    (105/120, "#02bffd"),
    
    (105/120, "#4169e1"),
    (110/120, "#4169e1"),
    
    (110/120, "#000096"),
    (115/120, "#000096"),
    
    (115/120, "#FFFFFF"),
    (120/120, "#FFFFFF")])

    vmax = 30
    vmin = -90

    return newcmp.reversed(), vmax, vmin

def lavn():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/150, "#000000"),
    (80/150, "#FFFFFF"),
    (80/150, "#0096FF"),
    (100/150, "#006e96"),
    (100/150, "#a0a000"),
    (110/150, "#fafa00"),
    (110/150, "#fafa00"),
    (120/150, "#c87800"),
    (120/150, "#fa0000"),
    (130/150, "#660000"),
    (130/150, "#585858"),
    (150/150, "#FFFFFF")])

    return newcmp.reversed()

def candy():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0.0, "#000000"), 
    (10/130, "#2a2a2a"),
    (20/130, "#535353"), 
    (30/130, "#7c7c7c"),
    (40/130, "#a3a3a3"),
    (50/130, "#cccccc"),
    (60/130, "#f3f3f3"),
    (70/130, "#96b9e0"),
    (80/130, "#3b7fcd"),
    (90/130, "#868bbc"),
    (95/130, "#ffb8b9"),
    (100/130, "#ff999b"),
    (110/130, "#e43a52"),
    (120/130, "#822049"),
    (130/130, "#250740")])

    vmax = 30
    vmin = -100

    return newcmp.reversed(), vmax, vmin

def candy3():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/130, "#000000"),
    (20/130, "#545454"),
    (40/130, "#ffffff"), 

    (70/130, "#254f80"),
    (75/130, "#298c6d"),
    (80/130, "#6fb334"),
    (85/130, '#cccc3b'),
    (90/130, "#e68743"),
    (100/130, "#ffb8b9"),
    (110/130, "#e43a52"),
    (120/130, "#822049"),
    (130/130, "#250740")])

    return newcmp.reversed() 

def nhc():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/136, "#000000"),   #26C
    (1/136, "#000018"),   #25C
    (16/136, "#0000FC"),  #10C
    (36/136, "#00FC00"),  #-10C
    (56/136, "#FC0000"),  #-30C
    (96/136, "#FCF8F8"),  #-70C
    (96/136, "#D8D8D8"),  #-70C
    (136/136, "#FCFCFC")])#To end

    vmax = 25
    vmin = -110

    return newcmp.reversed(), vmax, vmin

def oldirb():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/130, "#121212"),
    (20/130, "#787878"),
    (25/130, "#d7d9db"),
    (30/130, "#fcfcfc"),
    (45/130, "#2b39a1"),
    (50/130, "#fff957"),
    (55/130, "#e3c024"),
    (85/130, "#a6233f"),
    (85/130, "#a62353"),
    (100/130, "#b075ba"),
    (110/130, "#533c73"),
    (120/130, "#382c4f"),
    (125/130, "#19171c"),
    (130/130, "#000000")])

    return newcmp.reversed()

def irb():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/130, "#121212"),
    (20/130, "#787878"),
    (25/130, "#d7d9db"),
    (30/130, "#fcfcfc"),

    (40/130, "#2b39a1"),
    (50/130, "#3dad8f"),
    (65/130, "#fff957"),
    (70/130, "#e3c024"),
    (85/130, "#a6233f"),
    (90/130, "#4d0d07"),
    (100/130, "#9649c9"),
    (110/130, "#e0e0ff"),
    (130/130, "#000000")])

    vmax = 30
    vmin = -100

    return newcmp.reversed(), vmax, vmin

def irc():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/150, "#b58d65"),
    (15/150, "#9c4c4c"),
    (25/150, "#000000"),
    (30/150, "#333333"),
    (70/150, "#ffffff"),
    (75/150, "#658ba3"),
    (107.5/150, "#112c3d"),
    (112.5/150, "#b53564"),
    (129/150, "#fae1ea"),
    (131/150, "#FFFFFF"),
    (140/150, "#787878"),
    (144/150, "#000000"),
    (145/150, "#2b2b2b"),
    (150/150, "#6f4c9c")])

    vmax = 50
    vmin = -100

    return newcmp.reversed(), vmax, vmin

def oldirc():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/130, "#000000"),
    (15/130, "#2b2b2b"),
    (50/130, "#ffffff"),
    (55/130, "#658ba3"),
    (75/130, "#112c3d"),
    (85/130, "#b53564"),
    (100/130, "#fae1ea"),
    (110/130, "#787878"),
    (130/130, "#0f0303")])

    return newcmp.reversed()

def blcold():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/120, "#000000"),
    (60/120, "#FFFFFF"),
    (60/120, "#666ad6"),
    (70/120, "#949cfd"),
    (70/120, "#0eb7e7"),
    (85/120, "#081a7a"),
    (95/120, "#f6f72b"),
    (100/120, "#fe3518"),
    ((106+(2/3))/120, "#110f0f"),
    ((113+(1/3))/120, "#f5f5f5"),
    (120/120, "#a60aa6")])

    vmax = 40
    vmin = -80

    return newcmp.reversed(), vmax, vmin

def blhot():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/140, "#000000"),
    (80/140, "#FFFFFF"),
    (80/140, "#0eb7e7"),
    (95/140, "#081a7a"),
    (105/140, "#f6f72b"),
    (110/140, "#fe3518"),
    (117.5/140, "#110f0f"),
    (125/140, "#f5f5f5"),
    (135/140, "#a60aa6"),
    (135/140, "#FFFFFF"),
    (140/140, "#FFFFFF")])

    vmax = 40
    vmin = -100

    return newcmp.reversed(), vmax, vmin

def rbtop4():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/150, "#000000"),
    (50/150, "#00c3c3"),
    (70/150, "#04fcfc"),
    (80/150, "#000073"),
    (90/150, "#1cff24"),
    (100/150, "#ffff2d"),
    (110/150, "#ff1a18"),
    (120/150, "#000000"),
    (130/150, "#f1f1f1"),
    (130/150, "#f272c3"),
    (140/150, "#7f027f"),
    (140/150, "#ffff2d"),
    (145/150, "#000000"),
    (145/150, "#ff1a18"),
    (150/150, "#ffffff")])

    vmax = 50
    vmin = -100

    return newcmp.reversed(), vmax, vmin

def rbtop3():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/140, "#000000"),
    (60/140, "#fffdfd"),
    (60/140, "#05fcfe"),
    (70/140, "#010071"),
    (80/140, "#00fe24"),
    (90/140, "#fbff2d"),
    (100/140, "#fd1917"),
    (110/140, "#000300"),
    (120/140, "#e1e4e5"),
    (120/140, "#eb6fc0"),
    (130/140, "#9b1f94"),
    (140/140, "#330f2f")])

    vmax = 40
    vmin = -100

    return newcmp.reversed(), vmax, vmin

def rbtop2():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/160, "#000000"),
    (82.5/160, "#ffffff"),
    (82.5/160, "#00ffff"),
    (95/160, "#001ee1"),
    (109/160, "#4bff00"),
    (115/160, "#e1ff00"),
    (125/160, "#c84d0e"),
    (134/160, "#521f05"),
    (136/160, "#32261E"),
    (140/160, "#908C89"),
    (145/160, "#ffffff"),
    (155/160, "#8D2392"),
    (155/160, "#ffffff"),
    (160/160, "#ffffff")])

    vmax = 57
    vmin = -103

    return newcmp.reversed(), vmax, vmin

def rbtop25():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/160, "#000000"),
    (3.75/160, "#262626"),
    (35/160, "#7f7f7f"),
    (60/160, "#c6c6c6"),
    (78.75/160, "#fbfbfb"),
    (85/160, "#2dbfde"),
    (91.25/160, "#2365b4"),
    (97.5/160, "#36877a"),
    (103.75/160, "#55e039"),
    (110/160, "#9cfc22"),
    (116.25/160, "#e6e91f"),
    (122.5/160, "#f9801f"),
    (128.75/160, "#b44a1f"),
    (135/160, "#4a2b1f"),
    (141.25/160, "#8a8483"),
    (147.5/160, "#eadbe9"),
    (153.75/160, "#ab55ab"),
    (160/160, "#ffffff")])

    vmax = 57
    vmin = -103

    return newcmp.reversed(), vmax, vmin

def rbtop():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/157, "#000000"),
    (30/157, "#787878"),
    (30.5/157, "#030303"),
    (45/157, "#5A5A5A"),
    (45.5/157, "#5B5B5B"),
    (50/157, "#646464"),
    (50.5/157, "#676767"),
    (72/157, "#F8F8F8"),
    (72.5/157, "#FAFAFA"),
    (77/157, "#BF00FF"),
    (77.5/157, "#BF00FF"),
    (85/157, "#0000FF"),
    (85.5/157, "#000CF2"),
    (102/157, "#00FF00"),
    (103/157, "#19FF00"),
    (112/157, "#FFFF00"),
    (113/157, "#FFE500"),
    (122/157, "#FF0000"),
    (123/157, "#E50000"),
    (132/157, "#000000"),
    (133/157, "#141414"),
    (157/157, "#FFFFFF")])

    vmax = 57
    vmin = -100

    return newcmp.reversed(), vmax, vmin

def copper():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/120, "#07010a"), 
    (20/120, "#4a474a"),
    (40/120, "#FFFFFF"),
    (45/120, "#ebd7f7"),
    (65/120, "#e88c6d"),
    (90/120, "#703030"),
    (100/120, "#79a2d4"),
    (120/120, "#25184a")])

    vmax = 30
    vmin = -90

    return newcmp.reversed(), vmax, vmin

def ire():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/130, "#171717"),
    (50/130, "#ffffff"),
    (69/130, "#3f426b"),
    (71/130, "#711d82"),
    (85/130, "#eb7cbe"),
    (95/130, "#a12a2a"),
    (109/130, "#240404"),
    (111/130, "#16192e"),
    (125/130, "#e1e2e8"),
    (130/130, "#ffffff")])

    vmax = 30
    vmin = -100

    return newcmp.reversed(), vmax, vmin

def irf():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/130, "#000000"),
    (20/130, "#545454"),
    (40/130, "#ffffff"), #white
    (60/130, "#181557"), #blue
    (65/130, "#35db50"), #green
    (70/130, '#ffff29'), #yellow
    (80/130, "#db9335"), #orange
    (85/130, "#ff2929"), #red
    (95/130, "#541c1c"), #brown
    (100/130, "#000000"), #black
    (110/130, "#545454"), #grey
    (120/130, "#ffffff"), #white
    (130/130, "#261940")]) #purple

    vmax = 30
    vmin = -100

    return newcmp.reversed(), vmax, vmin

def irg():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/150, "#b55555"),
    (10/150, "#b58555"),
    (30/150, "#090926"),
    (60/150, "#ffffff"),

    (80/150, "#4c8032"),
    (90/150, "#ffff29"),

    (105/150, "#ff2929"),
    (120/150, "#000000"),
    (130/150, "#e6dada"),
    (140/150, "#261940"),
    (141/150, "#990f97"),
    (150/150, "#e6dada")])

    vmax = 50
    vmin = -100

    return newcmp.reversed(), vmax, vmin

def oldirg():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/130, "#000000"),
    (20/130, "#545454"),
    (40/130, "#ffffff"),

    (60/130, "#4c8032"),
    (70/130, "#ffff29"),

    (85/130, "#ff2929"),
    (100/130, "#000000"),
    (115/130, "#e6dada"),
    (130/130, "#261940")])

    vmax = 30
    vmin = -100

    return newcmp.reversed(), vmax, vmin

def wu():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/130, "#000000"),
    (40/130, "#7a7a7a"),
    (65/130, "#e2dfde"),
    (70/130, "#9febeb"),
    (75/130, "#7c9f9f"),
    (80/130, "#014bb4"),
    (85/130, "#189010"),
    (90/130, "#7abc1b"),
    (95/130, "#d6e026"),
    (100/130, "#d2951b"),
    (105/130, "#ad201d"),
    (110/130, "#7d0553"),
    (115/130, "#9139a4"),
    (120/130, "#b072be"),
    (125/130, "#d1add9"),
    (130/130, "#ece6ed")])

    vmax = 35
    vmin = -95
    
    return newcmp.reversed(), vmax, vmin

def spooky():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/130, "#000000"),
    (20/130, "#545454"),
    (40/130, "#ffffff"),

    (50/130, "#f5e2c1"),
    (70/130, "#eb8415"),
    (95/130, "#590401"),

    (100/130, "#121010"),
    (110/130, "#fcf5f5"),
    (125/130, "#2a084d"),
    (125/130, "#ffffff"),
    (130/130, "#ffffff")])

    vmax = 30
    vmin = -100

    return newcmp.reversed(), vmax, vmin

def testir():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/150, "#bfbf60"),
    (30/150, "#090926"),
    (65/150, "#FFFFFF"),
    (70/150, "#f7e6ff"),
    (80/150, "#a1b8e6"),

    (90/150, "#42a6a6"),
    (100/150, "#1d7339"),
    (120/150, "#1a1a1a"),
    (130/150, "#bf3039"),
    (135/150, "#d19960"),
    (140/150, "#FFFFFF"),
    (145/150, "#d160d1"),
    (150/150, "#2c1f33")])

    vmax = 50
    vmin = -100

    return newcmp.reversed(), vmax, vmin

def irh():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/130, "#000000"),
    (20/130, "#545454"),
    (40/130, "#ffffff"), 
    (60/130, "#216beb"),
    (70/130, "#60c259"),
    (80/130, "#fff88f"),
    (90/130, "#c74c0e"),
    (100/130, "#630505"),
    (110/130, "#edbbbb"),
    (120/130, "#9444c7"),
    (130/130, "#FFFFFF")]) 

    vmax = 30
    vmin = -100

    return newcmp.reversed(), vmax, vmin

def iri():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/130, "#000000"),
    (20/130, "#545454"),
    (40/130, "#ffffff"), 
    (45/130, "#2c5f78"),
    (60/130, "#3e0f4d"),
    (60/130, "#1c4d2e"),
    (80/130, "#cbed5c"),
    (80/130, "#edab9a"),
    (85/130, "#eb4921"),
    (90/130, "#80082c"),
    (100/130, "#240a12"),
    (100/130, "#242424"),
    (130/130, "#FFFFFF")]) 

    vmax = 30
    vmin = -100
    
    return newcmp.reversed(), vmax, vmin

def irk():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/130, "#000000"),
    (20/130, "#4f4f4f"), 
    (40/130, "#ffffff"),
    (60/130, "#397ae3"),
    (75/130, "#193263"),
    (90/130, "#d9c916"),
    (95/130, "#db770b"),
    (100/130, "#8f1111"),
    (110/130, "#db56b5"),
    (120/130, "#ffffff"),
    (127.5/130, "#8556db"),
    (127.5/130, "#e0bb00"),
    (130/130, "#e0bb00")])

    vmax = 30
    vmin = -100
    
    return newcmp.reversed(), vmax, vmin

def irj():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/130, "#000000"),
    (20/130, "#545454"),
    (40/130, "#ffffff"), 
    (60/130, "#7ed1e6"),
    (75/130, "#564ba6"),
    (88.5/130, "#090b3b"),
    (91.5/130, "#3b090a"),
    (100/130, "#801315"),
    (110/130, "#c76f9b"),
    (120/130, "#f7e4e4"),
    (120/130, "#e8e8e8"),
    (125/130, "#b694ff"),
    (130/130, "#2d1c52")]) 

    vmax = 30
    vmin = -100
    
    return newcmp.reversed(), vmax, vmin

def irl():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/140, "#000000"),
    (30/140, "#01c3c3"),
    (40/140, "#22b9b9"),
    (50/140, "#3f8ef6"),
    (60/140, "#2146ba"),
    (75/140, "#002650"),
    (80/140, "#046f0e"),
    (90/140, "#f6f62b"),
    (100/140, "#fe3718"),
    (110/140, "#000000"),
    (120/140, "#818181"),
    (140/140, "#ffffff")]) 

    vmax = 40
    vmin = -100
    
    return newcmp.reversed(), vmax, vmin

def irm():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/140, "#ad4747"),
    (15/140, "#604642"),
    (25/140, "#162c36"),
    (60/140, "#a3becc"),
    (65/140, "#FFFFFF"),
    (70/140, "#dae6cf"),
    (95/140, "#085024"),
    (105/140, "#bf9b30"),
    (110/140, "#cc1414"),
    (115/140, "#e65c5c"),
    (120/140, "#FFFFFF"),
    (130/140, "#323ca8"),
    (140/140, "#1a1a1a")])

    vmax = 40
    vmin = -100

    return newcmp.reversed(), vmax, vmin

def irn():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/130, "#ad4747"),
    (15/130, "#604642"),
    (25/130, "#162c36"),
    (70/130, "#a3becc"),
    (75/130, "#FFFFFF"),
    (80/130, "#dae6cf"),
    (100/130, "#085024"),
    (110/130, "#bf9b30"),
    (115/130, "#cc1414"),
    (120/130, "#e65c5c"),
    (130/130, "#FFFFFF")])

    vmax = 40
    vmin = -90

    return newcmp.reversed(), vmax, vmin


def ryglicki():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/110, "#fafafa"),
    (50/110, "#4f4c53"),
    (50/110, "#a2f5a4"),
    (60/110, "#08520a"),
    (60/110, "#1e1971"),
    (70/110, "#e9fafb"),
    (70/110, "#7a0906"),
    (80/110, "#f3f6dd"),
    (90/110, "#cf615d"),
    (90/110, "#d5bfd5"),
    (100/110, "#9235cb"),
    (100/110, "#04827d"),
    (110/110, "#60f1f0")]) 

    vmax = 20
    vmin = -90

    return newcmp.reversed(), vmax, vmin

def shrek():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/130, "#000000"),
    (20/130, "#545454"),
    (40/130, "#ffffff"), 

    (70/130, "#590a02"),

    (80/130, "#d99d4e"),
    (85/130, "#cfb629"),
    (90/130, "#dbdbdb"),
    (100/130, "#6dab43"),
    (110/130, "#328078"),
    (120/130, "#191d40"),
    (130/130, "#FFFFFF")])

    vmax = 30
    vmin = -100
    
    return newcmp.reversed(), vmax, vmin

def oldcody():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0.0, "#000000"), 
    (10/130, "#2d2e32"),
    (20/130, "#5d5d5d"), 
    (30/130, "#a9abb0"),
    (40/130, "#f2f2f2"),
    (60/130, "#3bc1cc"),
    (70/130, "#e6db02"),
    (80/130, "#d47624"),
    (90/130, "#d14747"),
    (100/130, "#f2f2f2"),
    (110/130, "#82b0ff"),
    (120/130, "#2072ff"),
    (130/130, "#004f6a")])

    vmax = 30
    vmin = -100

    return newcmp.reversed(), vmax, vmin

def cody():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0.0, "#000000"), 
    (10/130, "#091543"),
    (20/130, "#545b7a"), 
    (30/130, "#9fa2b2"),
    (40/130, "#e6e6e7"),
    (50/130, "#29a6d5"),
    (60/130, "#50bb27"),
    (70/130, "#f5fb73"),
    (80/130, "#dc972a"),
    (90/130, "#c9122a"),
    (100/130, "#ffffff"),
    (110/130, "#8baff3"),
    (120/130, "#2675fe"),
    (130/130, "#025172")])

    vmax = 30
    vmin = -100

    return newcmp.reversed(), vmax, vmin

def iro():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0.0, "#000000"), 
    (10/130, "#091543"),
    (20/130, "#545b7a"), 
    (30/130, "#9fa2b2"),
    (40/130, "#e6e6e7"),
    (50/130, "#29a6d5"),
    (60/130, "#50bb27"),
    (70/130, "#f5fb73"),
    (80/130, "#dc972a"),
    (90/130, "#c9122a"),
    (100/130, "#2e1748"),
    (110/130, "#6d6486"),
    (120/130, "#b6b1c2"),
    (130/130, "#ffffff")])

    vmax = 30
    vmin = -100

    return newcmp.reversed(), vmax, vmin

def irp():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/150, "#7d3025"),
    (25/150, "#1a1a1a"),
    (60/150, "#ffffff"),
    (90/150, "#804080"),
    (100/150, "#61203f"),
    (110/150, "#bf3030"),
    (120/150, "#261919"),
    (130/150, "#e6e6f2"),
    (135/150, "#79a2d4"),
    (150/150, "#25184a")])

    vmax = 50
    vmin = -100

    return newcmp.reversed(), vmax, vmin

def irq():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/130, "#000000"),
    (40/130, "#ffffff"),
    (50/130, "#c9e1ee"),
    (80/130, "#205c80"),

    (90/130, "#fcd665"),
    (100/130, "#99171b"),

    (100/130, "#3e2080"),
    (110/130, "#FFFFFF"),
    (120/130, "#3030bf"),
    (124/130, "#000000"),
    (125/130, "#400000"),
    (130/130, "#bf6030")])

    vmax = 30
    vmin = -100

    return newcmp.reversed(), vmax, vmin

def irr():
    newcmp = LinearSegmentedColormap.from_list("", [    
    (0/150, "#d97777"),
    (15/150, "#805020"),

    (30/150, "#262626"),
    (60/150, "#ffffff"),

    (70/150, "#55cece"),
    (80/150, "#5555ce"),
    (90/150, "#e6e65e"),
    (110/150, "#ce5555"),

    (120/150, "#482966"),
    (130/150, "#e673e6"),
    (138/150, "#efe6eb"),
    (140/150, "#FFFFFF"),
    (150/150, "#7f5ce6")])

    vmax = 50
    vmin = -100

    return newcmp.reversed(), vmax, vmin

def irs():
    newcmp = LinearSegmentedColormap.from_list("", [    
    (0/130, "#54d3f7"),
    (20/130, "#1818b5"),
    (45/130, "#0c1b70"),
    (60/130, "#358c25"),
    (65/130, "#f6dc2c"),
    (70/130, "#e6fae7"),
    (75/130, "#f7c949"),
    (80/130, "#f79d09"),
    (85/130, "#fee435"),
    (95/130, "#5a3908"),
    (105/130, "#05050a"),
    (105/130, "#def7ef"),
    (130/130, "#feffff")])

    vmax = 40
    vmin = -90

    return newcmp.reversed(), vmax, vmin

def irt():
    newcmp = LinearSegmentedColormap.from_list("",[
    (0/130, "#000000"),
    (15/130, "#0c3336"),
    (60/130, "#FFFFFF"),
    (70/130, "#2e6b35"),
    (90/130, "#e2c657"),
    (95/130, "#f7843c"),
    (100/130, "#fc4226"),
    (110/130, "#f19582"),
    (120/130, "#FFFFFF"),
    (130/130, "#8556db")])

    vmax = 30
    vmin = -100

    return newcmp.reversed(), vmax, vmin

def iru():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/130, "#b58555"),
    (22/130, "#090926"),
    (22/130, "#000000"),
    
    (31/130, "#ffffff"),
    (31/130, "#fefefe"),
    (70/130, "#404080"), 

    (70/130, "#ffe329"),
    (81/130, "#de7022"),
    (93/130, "#b31b1b"),
    (103/130, "#2e0202"),

    (109/130, "#e6dada"),
    (115/130, "#bc67b7"),
    (120/130, "#990f97"),
    (125/130, "#601f60"),
    (130/130, "#000000")])

    vmax = 40
    vmin = -90

    return newcmp.reversed(), vmax, vmin

def irv():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/130, "#000000"),
    (50/130, "#6d6d6d"),
    (60/130, "#5fbf5e"),
    (70/130, "#0e495c"),
    (80/130, "#07544b"),

    (90/130, "#FFFF00"),
    (95/130, "#ddb309"),
    (100/130, "#ea0000"),
    (110/130, "#700000"),
    (120/130, "#000000"),
    (130/130, "#FFFFFF")])

    vmax = 30
    vmin = -100

    return newcmp.reversed(), vmax, vmin

def irw():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/140, "#bea9d4"),
    (10/140, "#604080"),
    (10/140, "#1a1a1a"),
    (60/140, "#e0dfc1"),
    (85/140, "#550080"),
    (95/140, "#668cff"),

    (100/140, "#ffff66"),
    (110/140, "#ff8000"),
    (120/140, "#800000"),

    (125/140, "#ff0080"),
    (135/140, "#ff80ff"),
    (140/140, "#FFFFFF")])
    
    vmax = 40
    vmin = -100

    return newcmp.reversed(), vmax, vmin

def irx():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/140, "#161616"), #330
    (10/140, "#161616"),
    (10/140, "#181818"), #320
    (24/140, "#181818"),
    (24/140, "#1b1b1b"), #306
    (30/140, "#1b1b1b"),
    (30/140, "#333333"), #300
    (36/140, "#333333"),
    (36/140, "#4e4e4e"), #294
    (42/140, "#4e4e4e"),
    (42/140, "#727272"), #288
    (48/140, "#727272"),
    (48/140, "#989898"), #282
    (54/140, "#989898"),
    (54/140, "#b9b9b9"), #276
    (60/140, "#b9b9b9"),
    
    (60/140, "#cacaca"), #270
    (70/140, "#cacaca"),
    
    (70/140, "#d5d5d5"), #260
    (80/140, "#d5d5d5"),
    
    (80/140, "#d9d9d9"), #250
    (90/140, "#d9d9d9"),

    (90/140, "#323232"), #240
    (100/140, "#323232"),

    (100/140, "#a8a8a8"), #230
    (110/140, "#a8a8a8"),

    (110/140, "#161616"), #220
    (120/140, "#161616"), 

    (120/140, "#dfdfdf"), #210
    (130/140, "#dfdfdf"),

    (130/140, "#141414"), #200
    (140/140, "#151515")])
    
    vmax = 62
    vmin = -78

    return newcmp.reversed(), vmax, vmin

def iry():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/140, "#000000"), 
    (50/140, "#FFFFFF"),
    (60/140, "#39556c"),
    (80/140, "#a3c3ca"),
    (95/140, "#e9dd96"),
    (105/140, "#e17105"),
    (110/140, "#d73e0b"),
    (115/140, "#8f0b4e"),
    (120/140, "#000000"),
    (125/140, "#770e8e"),
    (130/140, "#d897e5"),
    (140/140, "#FFFFFF")])
    
    vmax = 30
    vmin = -100

    return newcmp.reversed(), vmax, vmin

def irz():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/130, "#000000"),
    (40/130, "#FFFFFF"),

    (70/130, "#188080"),
    (80/130, "#ebce47"),
    (87.5/130, "#cc7014"),
    (92.5/130, "#bf1313"),
    (95/130, "#800d29"),

    (100/130, "#1a1a1a"),
    (120/130, "#e6e6e6"),
    (130/130, "#FFFFFF")])
    
    vmax = 30
    vmin = -100

    return newcmp.reversed(), vmax, vmin

def ir1():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/130, "#000000"),
    (40/130, "#FFFFFF"),

    (70/130, "#184380"),
    (80/130, "#ebce47"),
    (87.5/130, "#cc7014"),
    (92.5/130, "#bf1313"),
    (95/130, "#800d29"),

    (100/130, "#1a1a1a"),
    (115/130, "#FFFFFF"),
    (130/130, "#ff4da6")])
    
    vmax = 30
    vmin = -100

    return newcmp.reversed(), vmax, vmin

def irvo():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/130, "#000000"),
    (50/130, "#6d6d6d"),
    (60/130, "#5fbf5e"),
    (70/130, "#0e495c"),
    (75/130, "#07544b"),
    (80/130, "#FFFF00"),
    (85/130, "#ddb309"),
    (100/130, "#ea0000"),
    (110/130, "#700000"),
    (120/130, "#000000"),
    (130/130, "#FFFFFF")])

    vmax = 30
    vmin = -100

    return newcmp.reversed(), vmax, vmin


def mean():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/140, "#3b1e27"),
    (7.5/140, "#231423"),
    (12.5/140, "#0d0e23"),
    (50/140, "#8e9cad"),
    (60/140, "#FFFFFF"),
    
    (70/140, "#8a9cb2"),
    (72.5/140, "#739ca3"),
    (75/140, "#49915c"),
    (80/140, "#8a9c78"),
    (90/140, "#e6c72e"),
    (100/140, "#bf6000"),
    (110/140, "#91161a"),    
    (115/140, "#ba69a8"),
    (140/140, "#FFFFFF")])

    vmax = 40
    vmin = -100

    return newcmp.reversed(), vmax, vmin

def trueMean():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/140, "#3b1e27"),
    (7.5/140, "#231423"),
    (15/140, "#0d0e23"),
    (50/140, "#8e9cad"),
    (65/140, "#8a9cb2"),
    (70/140, "#739ca3"),
    (75/140, "#78927f"),
    (80/140, "#8a9c78"),
    (90/140, "#a1a12b"),
    (100/140, "#a93c00"),
    (105/140, "#991e05"),
    (110/140, "#91161a"),
    (115/140, "#c47da5"),
    (120/140, "#ba69a8"),
    (130/140, "#b897b1"),
    (140/140, "#FFFFFF")])

    vmax = 40
    vmin = -100

    return newcmp.reversed(), vmax, vmin

def wind():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/130, "#000000"), 
    (25/130, "#a6a6a6"),
    (25/130, "#4245a6"),
    (60/130, "#29a668"),
    (80/130, "#cccc33"),
    (92.5/130, "#cc3333"),
    (110/130, "#cc7acc"),
    (130/130, "#ffffff")])
    
    vmax = 30
    vmin = -100

    return newcmp.reversed(), vmax, vmin

def wind2():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/130, "#000000"), 
    (25/130, "#a6a6a6"),
    (25/130, "#4245a6"),
    (60/130, "#29a668"),
    (80/130, "#cccc33"),
    (92.5/130, "#cc3333"),
    (100/130, "#cc7acc"),
    (110/130, "#FFFFFF"),
    (120/130, "#d44b35"),
    (130/130, "#552116")])
    
    vmax = 30
    vmin = -100

    return newcmp.reversed(), vmax, vmin

def chasespectral():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/150, "#000000"),
    (15/150, "#030208"),
    (30/150, "#3C3560"),
    (45/150, "#5D74B6"),
    (60/150, "#97C49B"),
    (75/150, "#F7F2B4"),
    (90/150, "#FFA869"),
    (105/150, "#A72C48"),
    (130/150, "#FFA7DF"),
    (150/150, "#420E4E")])

    vmax = 50
    vmin = -100

    return newcmp.reversed(), vmax, vmin

def ncdc():
    newcmp = LinearSegmentedColormap.from_list("", [    
    (0/90, "#525151"),
    (35/90, "#FFFFFF"),
    (42.5/90, "#42bdff"),
    (50/90, "#0000FF"),
    (55/90, "#ffff00"),
    (80/90, "#ff0000"),
    (90/90, "#8d2169")])

    vmax = 20
    vmin = -70

    return newcmp.reversed(), vmax, vmin

def icup():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/140, "#EDEDED"),
    (10/140, "#64BDDF"),
    (20/140, "#156899"),
    (40/140, "#03062F"),
    (50/140, "#D92028"),
    (70/140, "#FBCA0C"),
    (80/140, "#FFFFFF"),
    (100/140, "#000000"),
    (120/140, "#7d20d9"),
    (140/140, "#ff80ff")])

    vmax = 40
    vmin = -100

    return newcmp.reversed(), vmax, vmin
    
def ocody():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0.0, "#000000"), 
    (10/130, "#2d2e32"),
    (20/130, "#5d5d5d"), 
    (30/130, "#a9abb0"),
    (40/130, "#f2f2f2"),
    (50/130, "#27c1cc"),
    (60/130, "#3bc1cc"),
    (70/130, "#e6db02"),
    (80/130, "#d47624"),
    (90/130, "#d14747"),
    (100/130, "#f2f2f2"),
    (110/130, "#82b0ff"),
    (120/130, "#2072ff"),
    (130/130, "#004f6a")])

    return newcmp.reversed()
    
def lava():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/120, '#2e271d'),
    (40/120, '#ffffff'),
    (45/120, '#f09c43'),
    (75/120, '#8a2727'),
    (90/120, '#f26555'),
    (100/120, '#f09246'),
    (110/120, '#eddb82'),
    (120/120, '#7a84cc')])

    vmax = 30
    vmin = -90

    return newcmp.reversed(), vmax, vmin

def ice():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/120, '#d1d8e2'),
    (40/120, '#000000'),
    (45/120, '#0f63bc'),
    (75/120, '#75d8d8'),
    (90/120, '#0d9aaa'),
    (100/120, '#0f6db9'),
    (110/120, '#12247d'),
    (120/120, '#857b33')])

    vmax = 30
    vmin = -90

    return newcmp.reversed(), vmax, vmin

def ice2():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/130, '#000000'),
    (40/130, '#d1d8e2'),

    (45/130, '#0f63bc'),
    (75/130, '#75d8d8'),

    (90/130, '#0d9aaa'),
    (100/130, '#0f6db9'),
    (110/130, '#12247d'),
    (120/130, '#857b33'),
    (125/130, "#b39b24"),
    (130/130, "#FFFFFF")])


    vmax = 30
    vmin = -100

    return newcmp.reversed(), vmax, vmin

def icy():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/120, '#000000'),
    (45/120, '#d1d8e2'),
    (50/120, '#ffffa6'),
    (70/120, '#75d975'),
    (80/120, '#0d9aaa'),
    (90/120, '#0f6db9'),
    (100/120, '#12247d'),
    (120/120, '#FFFFFF')])

    vmax = 30
    vmin = -90

    return newcmp.reversed(), vmax, vmin

def cloudy():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/130, '#12247d'),
    (30/130, "#11597d"),
    (40/130, '#FFFFFF'),
    (70/130, '#bfbfbf'),
    (90/130, "#204010"),
    (95/130, "#ffff80"),
    (100/130, "#ff9f40"),
    (110/130, "#802020"),
    (120/130, "#ff0000"),
    (130/130, "#FFFFFF")])

    vmax = 30
    vmin = -100

    return newcmp.reversed(), vmax, vmin

def oldira():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/120, "#2e3036"), 
    (50/120, '#c3b3f5'), 
    (50/120, '#d6d24f'),
    (62.5/120, '#f07951'),
    (80/120, '#a80295'), 
    (95/120, '#e3ddd8'), 
    (110/120, "#7b80c9"), 
    (120/120, "#3e47c7")])
    return newcmp.reversed()

def ira():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/130, "#000000"),
    (20/130, "#4f4f4f"), 
    (40/130, "#ffffff"),
    (60/130, "#397ae3"),
    (75/130, "#0a6930"),
    (85/130, "#96ad47"),
    (90/130, "#db770b"),
    (100/130, "#8f3d11"),
    (105/130, "#8f1111"),
    (115/130, "#db56b5"),
    (120/130, "#ffffff"),
    (130/130, "#8556db")])

    vmax = 30
    vmin = -100

    return newcmp.reversed(), vmax, vmin

def ird():
    color1 = 'twilight'
    num1 = 110
    color2 = 'Greys' 
    num2 = 40

    top = cm.get_cmap(color1, num1)
    bottom = cm.get_cmap(color2, num2)
    newcolors = np.vstack((top(np.linspace(0, 1, num1)),
                       bottom(np.linspace(0, 1, num2))))
    newcmp = ListedColormap(newcolors, name='temp')

    vmax = 40
    vmin = -110

    return newcmp, vmax, vmin

def ir():
    num1 = 20
    num2 = 60
    num3 = 40
    num4 = 20
    num5 = 10
    top3 = cm.get_cmap('OrRd', num5)
    top2 = cm.get_cmap('BuPu_r', num4)
    top = cm.get_cmap('PuRd', num1)
    mid = cm.get_cmap('Spectral', num2)
    bot = cm.get_cmap('bone_r', num3)

    newcolors = np.vstack((top3(np.linspace(0, 1, num5)), top2(np.linspace(0, 1, num4)), top(np.linspace(0, 1, num1)), mid(np.linspace(0, 1, num2)), bot(np.linspace(0, 1, num3))))
    newcmp = ListedColormap(newcolors, name='temp')

    vmax = 40
    vmin = -110

    return newcmp, vmax, vmin

def blob():
    newcmp = LinearSegmentedColormap.from_list("", [
    
    (0, '#000000'),
    (0.1375, '#303030'),
    (0.421, "#B6B6B6"),
    (0.447, "#FFBBBC"),
    (0.524, "#E37372"),
    (0.55, "#FE4543"),
    (0.576, "#FF1717"),
    (0.627, "#AA0000"),
    (0.653, "#FF8AFF"),
    (0.73, "#FF16FE"),
    (0.756, "#C752C7"),
    (0.782, "#B6B6B6"),
    (0.834, '#ececec'),
    (1, "#FFFFFF")])

    vmax = 50
    vmin = -110

    return newcmp.reversed(), vmax, vmin

def icecream():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/140, "#cece55"),
    (10/140, "#ce5555"),
    (20/140, "#000000"),
    (50/140, "#ffffff"),
    (70/140, "#1faf86"),
    (80/140, "#ffff9c"),
    (90/140, "#edc766"),
    (100/140, "#db502f"),
    (110/140, "#683470"),
    (120/140, "#ffffff"),
    (130/140, "#9a9aff"),
    (140/140, "#13139a")])

    vmax = 40
    vmin = -100

    return newcmp.reversed(), vmax, vmin

def asir():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/140, "#b7b738"),
    (10/140, "#972626"),
    (20/140, "#18183e"),
    (50/140, "#ffffff"),
    (70/140, "#1faf86"),
    (80/140, "#ffff64"),
    (90/140, "#ebc447"),
    (100/140, "#d73729"),
    (110/140, "#5b2a62"),
    (120/140, "#ffffff"),
    (130/140, "#9a9aff"),
    (140/140, "#13139a")])

    vmax = 40
    vmin = -100

    return newcmp.reversed(), vmax, vmin

def volcano():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/140, "#d46c22"),
    (20/140, "#1f0038"),
    (50/140, "#ffffff"),
    (70/140, "#efe47d"),
    (80/140, "#edba4f"),
    (90/140, "#db502f"),
    (100/140, "#6c2727"),
    (110/140, "#000000"),
    (120/140, "#6565ff"),
    (140/140, "#ffffff")])

    vmax = 40
    vmin = -100

    return newcmp.reversed(), vmax, vmin

def ref():
    newcmp = LinearSegmentedColormap.from_list("", [ 
            (0/130, "#000000"),
            (40/130, "#FFFFFF"),
            (60/130, "#005580"),
            (80/130, "#80ff80"),
            (95/130, "#004000"),
            (100/130, "#d9d921"),
            (110/130, "#d95e21"),
            (110/130, "#d92121"),
            (120/130, "#4d1717"),
            (120/130, "#4d1732"),
            (130/130, "#e6b8cf")])

    vmin = -100
    vmax = 30
    
    return newcmp.reversed(), vmax, vmin

def whaticouldvedone():
    num1 = 25
    num2 = 55
    num3 = 40
    num4 = 10
    num5 = 10
    top3 = cm.get_cmap('OrRd', num5)
    top2 = cm.get_cmap('BuPu_r', num4)
    top = cm.get_cmap('PuRd', num1)
    mid = cm.get_cmap('Spectral', num2)
    bot = cm.get_cmap('bone_r', num3)

    newcolors = np.vstack((top3(np.linspace(0, 1, num5)), top2(np.linspace(0, 1, num4)), top(np.linspace(0, 1, num1)), mid(np.linspace(0, 1, num2)), bot(np.linspace(0, 1, num3))))
    newcmp = ListedColormap(newcolors, name='temp')
    return newcmp

def grayir():
    newcmp = LinearSegmentedColormap.from_list("", [
        (0/110, "#000000"),
        (110/110, "#FFFFFF")])

    vmax = 30
    vmin = -80

    return newcmp.reversed(), vmax, vmin

# WV Color Tables

def graywv():
    newcmp = LinearSegmentedColormap.from_list("", [
        (0/60, "#000000"),
        (60/60, "#FFFFFF")])

    vmax = -10
    vmin = -70

    return newcmp.reversed(), vmax, vmin

def msfc():
    newcmp = LinearSegmentedColormap.from_list("", [
        (0/90, "#000000"),
        (5/90, "#6e0505"),
        (15/90, "#c66523"),
        (17.5/90, "#dc9e3d"),
        (20/90, "#997541"),
        (25/90, "#5b4e3e"),
        (27.5/90, "#3f3f3e"),
        (30/90, "#565656"),
        (40/90, "#c7c9ca"),
        (40/90, "#c0cacc"),
        (50/90, "#266775"),
        (55/90, "#6d993d"),
        (60/90, "#d4d925"),
        (62.5/90, "#d9861a"),
        (65/90, "#d51312"),
        (70/90, "#9a0b09"),
        (72.5/90, "#402728"),
        (75/90, "#343132"),
        (90/90, "#dfdfdf")])

    vmax = 0
    vmin = -90

    return newcmp.reversed(), vmax, vmin

def psu():
    newcmp = LinearSegmentedColormap.from_list("", [
        (0/80, "#6e0505"),
        (2.5/80, "#c66523"),
        (5/80, "#c79038"),
        (10/80, "#62441f"),
        (20/80, "#040404"),
        (32.5/80, "#b3b3b3"),
        (35/80, "#c7c9ca"),
        (35/80, "#c0cacc"),

        (45/80, "#266775"),
        (47.5/80, "#6d993d"),
        (50/80, "#d4d925"),
        (55/80, "#d9861a"),
        (60/80, "#d51312"),
        (67.5/80, "#040404"),
        (80/80, "#dfdfdf")])

    vmax = 0
    vmin = -80

    return newcmp.reversed(), vmax, vmin

def wv():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/90, "#696563"),
    (10/90, "#1f1e1c"), 
    (20/90, "#a85432"),
    (30/90, "#e3e1de"),
    (45/90, "#465185"),
    (60/90, "#89d9a7"),
    (80/90, "#30453d"),
    (90/90, '#b3afaf')])

    vmax = 0
    vmin = -90

    return newcmp.reversed(), vmax, vmin

def wv2():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/90, "#bf4351"),
    (5/90, "#a85432"),
    (15/90, "#1f1e1c"), 
    (25/90, "#696563"),
    (35/90, "#e3e1de"),
    (45/90, "#465185"),
    (60/90, "#89d9a7"),
    (80/90, "#30453d"),
    (90/90, '#b3afaf')])

    vmax = 0
    vmin = -90

    return newcmp.reversed(), vmax, vmin

def ssdwv():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/90, "#000000"),
    (7.5/90, "#000000"),
    (8/90, "#FFA05A"),
    (25/90, "#000000"),
    (25.5/90, "#000000"),
    (37/90, "#FFFFFF"),
    (38/90, "#FFFFFF"),
    (52/90, "#005082"),
    (53/90, "#005082"),
    (60/90, "#009696"),
    (61/90, "#A09600"),
    (68/90, "#FA3200"),
    (69/90, "#9600DC"),
    (76/90, "#FA00DC"),
    (77/90, "#0000E2"),
    (84/90, "#000086"),
    (85/90, "#FFFFFF"),
    (90/90, '#FFFFFF')])

    vmax = 0
    vmin = -90

    return newcmp.reversed(), vmax, vmin

def wv5():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/90, "#ff8f40"), 
    (10/90, "#d9bf00"),
    (25/90, "#171717"),
    (40/90, "#ffffff"),
    (57.5/90, "#3f426b"),
    (60/90, "#711d82"),
    (70/90, "#eb7cbe"),
    (80/90, "#a12a2a"),
    (90/90, "#240404")])

    vmax = 0
    vmin = -90

    return newcmp.reversed(), vmax, vmin

def wv4():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0.0, "#ffdf00"), 
    (10/80, "#807000"),
    (20/80, "#000000"), 
    (30/80, "#777776"),
    (40/80, "#ffffff"),
    (50/80, "#5d73c5"),
    (60/80, "#222777"),
    (70/80, "#5f2f90"),
    (75/80, "#6d3d96"),
    (80/80, "#c32787")])

    vmax = 0
    vmin = -80

    return newcmp.reversed(), vmax, vmin

def codywv():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0.0, "#FCD100"), 
    (10/90, "#534A37"),
    (20/90, "#070704"), 
    (25/90, "#7A7A7A"),
    (30/90, "#EDEDED"),
    (40/90, "#64BDDF"),
    (50/90, "#156899"),
    (60/90, "#03062F"),
    (70/90, "#D92028"),
    (80/90, "#FBCA0C"),
    (90/90, "#FFFFFF")])

    vmax = 0
    vmin = -90

    return newcmp.reversed(), vmax, vmin

def mikewv():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0.0, "#1b1a17"), 
    (10/90, "#fdbf20"),
    (17.5/90, "#f36631"),
    (20/90, "#d2352c"),
    (32.5/90, "#f2f1f6"),
    (40/90, "#44b8cf"),
    (50/90, "#307584"),
    (60/90, "#223b48"),
    (70/90, "#274397"),
    (90/90, "#8927f4")])

    vmax = 0
    vmin = -90

    return newcmp.reversed(), vmax, vmin

def wv3():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/90, "#804080"),
    (5/90, "#1a000d"),
    (10/90, "#661a1a"),
    (15/90, "#8f5d3c"), 
    (20/90, "#000000"),
    (40/90, "#FFFFFF"),
    (50/90, "#a9c4de"),
    (55/90, "#8e9ac8"),
    (65/90, "#88439e"),
    (70/90, "#4d014b"),
    (70/90, "#67041f"),
    (80/90, "#d1145b"),
    (90/90, "#f7f4f9")])

    vmax = 0
    vmin = -90

    return newcmp.reversed(), vmax, vmin

def codywv2():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0.0, "#ffdf00"), 
    (10/85, "#807000"),
    (20/85, "#000000"), 
    (30/85, "#777776"),
    (40/85, "#ffffff"),
    (45/85, "#f3f3f3"),
    (50/85, "#96b9e0"),
    (55/85, "#254f80"),
    (60/85, "#868bbc"),
    (65/85, "#ffb8b9"),
    (70/85, "#ff999b"),
    (75/85, "#e43a52"),
    (80/85, "#822049"),
    (85/85, "#250740")])

    return newcmp.reversed()

def wv6():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/90, "#992660"),
    (10/90, "#802020"),
    (15/90, "#000000"),
    (22.5/90, "#413D3E"),
    (30/90, "#FFFFFF"),
    (55/90, "#3d3d99"),
    (60/90, "#d96cd9"),
    (70/90, "#663d52"),
    (72.5/90, "#bf3030"),
    (75/90, "#bf4830"),
    (90/90, "#FFFFFF")])

    vmax = 0
    vmin = -90

    return newcmp.reversed(), vmax, vmin

def darkwv():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/90, "#FFFFFF"),
    (10/90, "#000000"),
    (10/90, "#FFFFFF"), 
    (30/90, "#000000"),
    (45/90, "#a66441"),
    (60/90, "#61a641"),
    (70/90, "#90e8cb"),
    (90/90, "#000000")])

    vmax = 0
    vmin = -90

    return newcmp.reversed(), vmax, vmin

# def handwv():
#     newcmp = LinearSegmentedColormap.from_list("", [
#     (0/90, "#5d5e7f"),
#     (17.5/90, "#07080c"),
#     (25/90, "#061d47"),
#     (40/90, "#6b81b7"),
#     (50/90, "#ffe374"),
#     (75/90, "#7f3c1e"),
#     (80/90, "#27140d"),
#     (85/90, "#8c1612"),
#     (90/90, "#fa9e29")])

#     vmax = 0
#     vmin = -90

#     return newcmp.reversed(), vmax, vmin

def handwv():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/90, "#5d5e7f"),
    (17.5/90, "#07080c"),
    (25/90, "#061d47"),
    (40/90, "#6b81b7"),
    (50/90, "#ffe374"),
    (65/90, "#7f3c1e"),
    (70/90, "#27140d"),
    (75/90, "#8c1612"),
    (82.5/90, "#fa9e29"),
    (90/90, "#f0fdf4")])

    vmax = 0
    vmin = -90

    return newcmp.reversed(), vmax, vmin

def handir():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/130, "#07080c"),
    (10/130, "#061d47"),
    (32.5/130, "#6b81b7"),
    (60/130, "#FFFFFF"),

    (70/130, "#ffe374"),
    (95/130, "#7f3c1e"),
    (100/130, "#27140d"),
    (110/130, "#8c1612"),
    (120/130, "#fa9e29"),
    (130/130, "#f0fdf4")])

    vmax = 30
    vmin = -100

    return newcmp.reversed(), vmax, vmin

def wv7():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/90, "#5d5e7f"),
    (17.5/90, "#07080c"),
    (25/90, "#061d47"),
    (35/90, "#6b81b7"),
    (40/90, "#e6e6e6"),
    (70/90, "#27140d"),
    (75/90, "#8c1612"),
    (82.5/90, "#fa9e29"),
    (90/90, "#f0fdf4")])

    vmax = 0
    vmin = -90

    return newcmp.reversed(), vmax, vmin

def wv8():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/90, "#debfff"),
    (10/90, "#000000"),
    (20/90, "#4040ff"),
    (30/90, "#004040"),
    (35/90, "#40ff40"),
    (40/90, "#806b00"),
    (45/90, "#ffd500"),
    (60/90, "#804000"),
    (70/90, "#ff0000"),
    (80/90, "#ffbfdf"),
    (90/90, '#400040')])

    vmax = 0
    vmin = -90

    return newcmp.reversed(), vmax, vmin

def wv9():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/90, "#ff4040"),
    (5/90, "#994736"),
    (10/90, "#593c2d"),
    (17.5/90, "#000000"),
    (30/90, "#ffffff"),
    (35/90, "#c9e1ee"),
    (45/90, "#205c80"),

    (50/90, "#fcd665"),
    (62.5/90, "#bf1d22"),
    (67.5/90, "#400000"),
    (70/90, "#000000"),
    (72.5/90, "#3e2080"),
    (80/90, "#8080ff"),
    (90/90, "#FFFFFF")])

    vmax = 0
    vmin = -90

    return newcmp.reversed(), vmax, vmin

def wv95():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/90, "#ff4040"),
    (5/90, "#994736"),
    (10/90, "#593c2d"),
    (17.5/90, "#000000"),
    (35/90, "#ffffff"),
    (45/90, "#205c80"),

    (50/90, "#fcd665"),
    (60/90, "#d96c00"),
    (65/90, "#bf0000"),
    (70/90, "#000000"),
    (72.5/90, "#3e2080"),
    (80/90, "#8080ff"),
    (90/90, "#FFFFFF")])

    vmax = 0
    vmin = -90

    return newcmp.reversed(), vmax, vmin

def wv11():
    newcmp = LinearSegmentedColormap.from_list("", [    
    (0/90, "#d97777"),
    (7.5/90, "#805020"),
    (15/90, "#262626"),
    (30/90, "#ffffff"),

    (35/90, "#55cece"),
    (40/90, "#5555ce"),
    (47.5/90, "#e6e65e"),
    (60/90, "#ce5555"),
    (70/90, "#482966"),
    (80/90, "#e673e6"),
    (90/90, "#efe6eb")])

    vmax = 0
    vmin = -90

    return newcmp.reversed(), vmax, vmin

def wv12():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/90, "#b55555"),
    (10/90, "#b58555"),
    (20/90, "#001540"),
    (30/90, "#405580"),
    (40/90, "#FFFFFF"),

    (50/90, "#53994d"),
    (55/90, "#ffff40"),
    (65/90, "#ff1919"),
    (75/90, "#000000"),
    (85/90, "#e6e6e6"),
    (90/90, "#FFFFFF")])
    
    vmax = 0
    vmin = -90

    return newcmp.reversed(), vmax, vmin

def wv13():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/90, "#b58555"),
    (15/90, "#1a1a1a"),
    (25/90, "#405580"),
    (40/90, "#FFFFFF"),

    (50/90, "#188080"),
    (60/90, "#ebce47"),
    (65/90, "#cc7014"),
    (70/90, "#bf1313"),
    (75/90, "#800d29"),
    (80/90, "#1a1a1a"),
    (87.5/90, "#e6e6e6"),
    (90/90, "#FFFFFF")])
    
    vmax = 0
    vmin = -90

    return newcmp.reversed(), vmax, vmin

def wv135():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/90, "#b58555"),
    (15/90, "#1a1a1a"),
    (25/90, "#405580"),
    (40/90, "#FFFFFF"),

    (50/90, "#188080"),
    (60/90, "#ebce47"),
    (65/90, "#cc7014"),
    (70/90, "#bf1313"),
    (75/90, "#800d29"),
    (77.5/90, "#1a1a1a"),
    (87.5/90, "#e6e6e6"),
    (90/90, "#FFFFFF")])
    
    vmax = 0
    vmin = -90

    return newcmp.reversed(), vmax, vmin

def halloween():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/90, "#8a36e1"),
    (7.5/90, "#6b81b7"),
    (17.5/90, "#061d47"),
    (25/90, "#07080c"),
    (40/90, "#5d5e7f"),
    (60/90, "#1a1a1a"),
    (70/90, "#D92028"),
    (80/90, "#FBCA0C"),
    (90/90, "#FFFFFF")])
    
    vmax = 0
    vmin = -90

    return newcmp.reversed(), vmax, vmin

def wv14():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/90, "#FBCA0C"),
    (10/90, "#bf303a"),
    (20/90, "#1a1a1a"),
    
    (40/90, "#FFFFFF"),
    (50/90, "#a1a1e6"),
    (60/90, "#0f5499"),
    (70/90, "#12b3b3"),
    (80/90, "#7ee67e"),
    (85/90, "#e6e6a1"),
    (90/90, "#FFFFFF")])
    
    vmax = 0
    vmin = -90

    return newcmp.reversed(), vmax, vmin


def wv15():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/90, "#ffff00"),
    (30/90, "#000080"),
    (45/90, "#ffffff"),
    (70/90, "#333333"),
    (80/90, "#7830bf"),
    (90/90, "#FFFFFF")])
    
    vmax = 0
    vmin = -90

    return newcmp.reversed(), vmax, vmin

def simple():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/90, "#545454"),
    (15/90, "#000000"),
    (30/90, "#6060bf"),
    (45/90, "#ffffff"),
    (67.5/90, "#ff0000"),
    (90/90, "#000000")])
    
    vmax = 0
    vmin = -90

    return newcmp.reversed(), vmax, vmin

def simple2():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/90, "#ffdd00"),
    (15/90, "#000000"),
    (45/90, "#ffffff"),
    (67.5/90, "#6060bf"),
    (75/90, "#402080"),
    (80/90, "#201040"),
    (90/90, "#30bfbf")])
    
    vmax = 0
    vmin = -90

    return newcmp.reversed(), vmax, vmin

def testwv():
    newcmp = LinearSegmentedColormap.from_list("", [    
    (0/90, "#b55555"),
    (7.5/90, "#b58555"),
    (15/90, "#090926"),
    (35/90, "#ffffff"),

    (45/90, "#4c8032"),
    (50/90, "#ffff29"),

    (60/90, "#ff2929"),
    (70/90, "#000000"),
    (72.5/90, "#482966"),
    (80/90, "#e673e6"),
    (90/90, "#efe6eb")])

    vmax = 0
    vmin = -90

    return newcmp.reversed(), vmax, vmin

def wv16():
    newcmp = LinearSegmentedColormap.from_list("", [    
    (0.0, "#ceac55"), 
    (10/90, "#bf5858"),
    (20/90, "#070704"), 

    (30/90, "#b3b3b3"),

    (40/90, "#156899"),
    (50/90, "#64BDDF"),
    
    (60/90, "#FFFFFF"),
    (70/90, "#FBCA0C"),
    (80/90, "#D92028"),
    (90/90, "#03062F")])

    vmax = 0
    vmin = -90

    return newcmp.reversed(), vmax, vmin

def wv17():
    newcmp = LinearSegmentedColormap.from_list("", [    
    (0.0, "#ceac55"), 
    (20/90, "#070704"), 

    (40/90, "#FFFFFF"),
    (55/90, "#4d2e4d"),
    (60/90, "#800d29"),
    (70/90, "#e64545"),
    (80/90, "#e6d4a1"),
    (90/90, "#FFFFFF")])

    vmax = 0
    vmin = -90

    return newcmp.reversed(), vmax, vmin


def wv18():
    newcmp = LinearSegmentedColormap.from_list("", [    
    (0/90, "#a4a4a4"), 
    (25/90, "#000000"),
    (30/90, "#123524"),
    (50/90, "#e6e6a1"),
    (60/90, "#e68a2e"),
    (70/90, "#ff0000"),
    (80/90, "#000000"),
    (90/90, "#FFFFFF")])

    vmax = 0
    vmin = -90

    return newcmp.reversed(), vmax, vmin

def wv19():
    newcmp = LinearSegmentedColormap.from_list("", [    
    (0/90, "#ceac55"),
    (15/90, "#000000"), 
    (30/90, "#FFFFFF"),
    (40/90, "#ed77b0"),
    (60/90, "#191a5f"),
    (70/90, "#1975d1"),
    (85/90, "#06ffff"),
    (90/90, "#FFFFFF")])

    vmax = 0
    vmin = -90

    return newcmp.reversed(), vmax, vmin

def wv20():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/90, "#ffff00"),
    (30/90, "#000080"),
    (45/90, "#ffffff"),
    (60/90, "#008000"),
    (90/90, "#00ffff")])
    
    vmax = 0
    vmin = -90

    return newcmp.reversed(), vmax, vmin

def wv21():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/90, "#000000"),
    (12.5/90, "#FFFFFF"),
    (12.5/90, "#6d6d6d"),

    (30/90, "#cacaca"),
    (30/90, "#3c3c3c"),
    (45/90, "#3c3c3c"),

    (45/90, "#6e6e6e"),
    (54/90, "#6e6e6e"),
    
    (54/90, "#a0a0a0"),
    (64/90, "#a0a0a0"),

    (64/90, "#000000"),
    (70/90, "#000000"),

    (70/90, "#FFFFFF"),
    (75/90, "#FFFFFF"),

    (75/90, "#888888"),
    (80/90, "#888888"),
    
    (80/90, "#555555"),
    (90/90, "#555555")])
    
    vmin = -90
    vmax = 0

    return newcmp.reversed(), vmax, vmin

def wv22():
    newcmp = LinearSegmentedColormap.from_list("", [    
    (0/90, "#ceac55"),
    (15/90, "#000000"), 
    (35/90, "#FFFFFF"),
    (45/90, "#D23819"),
    (60/90, "#191a5f"),
    (70/90, "#1975d1"),
    (85/90, "#06ffff"),
    (90/90, "#FFFFFF")])

    vmax = 0
    vmin = -90

    return newcmp.reversed(), vmax, vmin

def wv23():
    newcmp = LinearSegmentedColormap.from_list("", [    
    (0.0, "#ceac55"), 
    (20/90, "#070704"), 
    (25/90, "#4d4d4d"),
    (30/90, "#FFFFFF"),
    (40/90, "#60bf60"),
    (60/90, "#191a5f"),
    (70/90, "#1975d1"),
    (85/90, "#06ffff"),
    (90/90, "#FFFFFF")])

    vmax = 0
    vmin = -90

    return newcmp.reversed(), vmax, vmin

def wv24():
    newcmp = LinearSegmentedColormap.from_list("", [    
    (0/90, "#ceac55"),
    (20/90, "#000000"), 
    (45/90, "#FFFFFF"),
    (60/90, "#60bf60"),
    (90/90, "#000000")])

    vmax = 0
    vmin = -90

    return newcmp.reversed(), vmax, vmin

def wv25():
    newcmp = LinearSegmentedColormap.from_list("", [    
    (0.0, "#cccccc"),
    (10/90, "#000000"),
    (15/90, "#BF9381"),
    (20/90, "#B27C66"),
    (30/90, "#230C33"),
    (40/90, "#592E83"),
    (50/90, "#9984D4"),
    (55/90, "#CAA8F5"),
    (60/90, "#FFFFFF"),
    (67.5/90, "#6F87BB"),
    (75/90, "#2E426D"),
    (82.5/90, "#52B3B1"),
    (90/90, "#FFFFFF")])

    vmax = 0
    vmin = -90

    return newcmp.reversed(), vmax, vmin

def wv26():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/90, "#b55555"),
    (5/90, "#b58555"),
    (20/90, "#001540"),
    (30/90, "#405580"),
    (40/90, "#FFFFFF"),
    (45/90, "#ffe374"),
    (60/90, '#7f3c1e'),
    (70/90, '#f26555'),
    (75/90, '#f09246'),
    (80/90, '#eddb82'),
    (90/90, "#FFFFFF")])
    
    vmax = 0
    vmin = -90

    return newcmp.reversed(), vmax, vmin

def wv27():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/90, "#d9c750"),
    (20/90, "#000000"),

    (40/90, "#FFFFFF"),
    (50/90, "#62a68b"),
    (70/90, "#1d004d"),
    (85/90, "#bfbfbf"),
    (90/90, "#FFFFFF")])
    
    vmax = 0
    vmin = -90

    return newcmp.reversed(), vmax, vmin

def wv28():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/90, "#807540"),
    (10/90, "#000000"),
    (20/90, "#202040"),
    (40/90, "#bfbfbf"),
    (50/90, "#FFFFFF"),
    (60/90, "#ebb3ff"),
    (70/90, "#ff40cf"),
    (75/90, "#ff0000"),
    (80/90, "#990000"),
    (90/90, "#000000")])
    
    vmax = 0
    vmin = -90

    return newcmp.reversed(), vmax, vmin

def wv29():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/90, "#b55555"),
    (10/90, "#b58555"),
    (20/90, "#1a1a1a"),
    (45/90, "#FFFFFF"),
    (65/90, "#3030bf"),
    (70/90, "#1a661a"),
    (90/90, "#FFFFFF")])
    
    vmax = 0
    vmin = -90

    return newcmp.reversed(), vmax, vmin

def watermelon():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/90, "#FFFFFF"),
    (10/90, "#5d5e7f"),
    (20/90, "#07080c"),
    (25/90, "#061d47"),
    (45/90, "#61a641"),
    (55/90, "#90e8cb"),
    (60/90, "#FFFFFF"),
    (65/90, "#E890AD"),
    (75/90, "#a62929"),
    (85/90, "#000000"),
    (90/90, "#666666")])

    vmax = 0
    vmin = -90

    return newcmp.reversed(), vmax, vmin

def aswvold():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/90, "#cece55"),
    (10/90, "#ce5555"),
    (20/90, "#262626"),
    (35/90, "#ffffff"),
    (45/90, "#4dcb4d"),
    (55/90, "#169898"),
    (65/90, "#123781"),
    (70/90, "#6a5dac"),
    (80/90, "#4a146b"),
    (90/90, "#efe6eb")])

    vmax = 0
    vmin = -90

    return newcmp.reversed(), vmax, vmin

def aswv():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/90, "#972626"),
    (10/90, "#a67b3f"),
    (20/90, "#131330"),
    (35/90, "#ffffff"),
    (45/90, "#1973b3"),
    (55/90, "#ebcf47"),
    (65/90, "#ca652c"),
    (72/90, "#b31919"),
    (80/90, "#1c161d"),
    (90/90, "#f7edf7")])

    vmax = 0
    vmin = -90

    return newcmp.reversed(), vmax, vmin

def wv10():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/90, "#cece55"),
    (10/90, "#ce5555"),
    (20/90, "#262626"),
    (35/90, "#ffffff"),
    (45/90, "#55cece"),
    (60/90, "#5555ce"),
    (70/90, "#4d3366"),
    (80/90, "#e673e6"),
    (90/90, "#efe6eb")])

    vmax = 0
    vmin = -90

    return newcmp.reversed(), vmax, vmin

def irgwv():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/90, "#b55555"),
    (10/90, "#b58555"),
    (20/90, "#090926"),
    (35/90, "#ffffff"),

    (50/90, "#4c8032"),
    (55/90, "#ffff29"),

    (63/90, "#ff2929"),
    (70/90, "#000000"),
    (80/90, "#e6dada"),
    (84/90, "#261940"),
    (85/90, "#990f97"),
    (90/90, "#e6dada")])

    vmax = 0
    vmin = -90

    return newcmp.reversed(), vmax, vmin

def oldwv():
    num1 = 20
    num2 = 40
    num3 = 30
    top = cm.get_cmap('PuRd', num1)
    mid = cm.get_cmap('BuPu_r', num2)
    bot = cm.get_cmap('Greys', num3)

    newcolors = np.vstack((top(np.linspace(0, 1, num1)), mid(np.linspace(0, 1, num2)), bot(np.linspace(0, 1, num3))))
    newcmp = ListedColormap(newcolors, name='temp')
    
    vmax = 0
    vmin = -90

    return newcmp, vmax, vmin

def ref1():
    newcmp = LinearSegmentedColormap.from_list("", [ 
            (0/80, "#000000"),
            (10/80, "#000000"),
            (20/80, "#005580"),
            (30/80, "#80ff80"),
            (45/80, "#004000"),
            (50/80, "#d9d921"),
            (60/80, "#d95e21"),
            (60/80, "#d92121"),
            (70/80, "#4d1717"),
            (70/80, "#4d1732"),
            (80/80, "#e6b8cf")])

    vmin = -10
    vmax = 70
    
    return newcmp, vmin, vmax

def cold():
    newcmp = LinearSegmentedColormap.from_list("", [ 
            (0/80, "#000000"),
            (20/80, "#FFFFFF"),
            (40/80, "#0000ff"),
            (50/80, "#00ffff"),
            (60/80, "#FFFFFF"),
            (70/80, "#FF0000"),
            (80/80, "#000000")])

    vmin = -10
    vmax = 70
    
    return newcmp, vmin, vmax

def ref2():
    newcmp = LinearSegmentedColormap.from_list("", [ 
            (0/80, "#000000"),
            (25/80, "#545454"),
            (30/80, "#FFFFFF"),
            (40/80, "#408040"),
            (50/80, "#e6e673"),
            (60/80, "#ff2626"),
            (70/80, "#e673e6"),
            (80/80, "#000000")])

    vmin = -10
    vmax = 70
    
    return newcmp, vmin, vmax

def ref3():
    newcmp = LinearSegmentedColormap.from_list("", [ 
            (0/50, "#000000"),
            (30/80, "#c4c4c4"),
            (40/80, "#4287f5"),
            (50/80, "#13124d"),

            (50/80, "#124d12"),
            (60/80, "#ded228"),
            (65/80, "#de6528"),
            (70/80, "#ff0000"),

            (75/80, "#800040"),
            (80/80, "#FFFFFF")])

    vmin = -10
    vmax = 70
    
    return newcmp, vmin, vmax

def ref4():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/130, "#bea9d4"),
    (10/130, "#604080"),
    (20/130, "#1a1a1a"),
    (30/130, "#405580"),
    (50/130, "#FFFFFF"),

    (60/130, "#53994d"),
    (80/130, "#e6e62e"),
    (95/130, "#ff1919"),
    (115/130, "#000000"),
    (130/130, "#FFFFFF")])
    
    vmin = -20
    vmax = 80

    return newcmp, vmin, vmax

def ref5():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/100, "#000000"),
    (20/100, "#FFFFFF"),
    (20/100, "#6d6d6d"),
    (40/100, "#cacaca"),
    (40/100, "#3c3c3c"),
    (50/100, "#3c3c3c"),
    (50/100, "#6e6e6e"),
    (60/100, "#6e6e6e"),
    (60/100, "#a0a0a0"),
    (70/100, "#a0a0a0"),
    (70/100, "#000000"),
    (75/100, "#000000"),
    (75/100, "#FFFFFF"),
    (80/100, "#FFFFFF"),
    (80/100, "#888888"),
    (85/100, "#888888"),
    (85/100, "#555555"),
    (100/100, "#555555")])
    
    vmin = -20
    vmax = 80

    return newcmp, vmin, vmax

def ref6():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/100, "#bea9d4"),
    (10/100, "#604080"),
    (20/100, "#1a1a1a"),
    (30/100, "#e0dfc1"),
    (50/100, "#550080"),
    (60/100, "#668cff"),
    (60/100, "#ffff66"),
    (70/100, "#ff8000"),
    (80/100, "#800000"),
    (80/100, "#ff0080"),
    (90/100, "#ff80ff"),
    (100/100, "#FFFFFF")])
    
    vmin = -20
    vmax = 80

    return newcmp, vmin, vmax

def ref7():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/100, "#604080"),
    (10/100, "#bea9d4"),
    (20/100, "#e6e6e6"),

    (30/100, "#80ffff"),
    (40/100, "#0000ff"),
    (40/100, "#004020"),
    (60/100, "#80ff80"),
    (60/100, "#ffff00"),
    (70/100, "#ff9f40"),
    (80/100, "#ff4040"),
    (80/100, "#ffbfdf"),
    (90/100, "#ff0080"),
    (90/100, "#800080"),
    (100/100, "#FFFFFF")])
    
    vmin = -20
    vmax = 80

    return newcmp, vmin, vmax

def ref8():
    newcmp = LinearSegmentedColormap.from_list("", [ 
            (0/80, "#000000"),
            (4.999/80, "#000000"),
            (5/80, "#00FFFF"),
            (19.999/80, "#0000FF"),
            (20/80, "#00FF00"),
            (34.999/80, "#007F00"),
            (35/80, "#FFFF00"),
            (49.999/80, "#FF7F00"),
            (50/80, "#FF0000"),
            (65.999/80, "#7F0000"),
            (70/80, "#FF00FF"),
            (80/80, "#7F00FF")])

    vmin = 0
    vmax = 80
    
    return newcmp, vmin, vmax

def ref9():
    newcmp = LinearSegmentedColormap.from_list("", [ 
            (0/80, "#663366"),
            (10/80, "#c7c7c7"),
            (15/80, "#4d97ff"),
            (20/80, "#a3bf86"),
            (35/80, "#125918"),
            (40/80, "#e6cb45"),
            (50/80, "#bf5b13"),
            (55/80, "#801006"),
            (60/80, "#a6295d"),
            (65/80, "#c449aa"),
            (70/80, "#FFFFFF"),
            (80/80, "#4c1313")])

    vmin = -10
    vmax = 70
    
    return newcmp, vmin, vmax

def cod1():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/100, "#3a3a48"),
    (13/100, "#646482"),
    (13/100, "#1f2a68"),
    (30/100, "#4f76ec"),
    (30/100, "#02621e"),
    (52/100, "#50f545"),
    (52/100, "#fffb27"),
    (65/100, "#ff8214"),
    (85/100, "#be0000"),
    (85/100, "#e601c8"),
    (95/100, "#fd84fa"),
    (100/100, "#00ebe6"),
    (100/100, "#000000")])
    
    vmin = -20
    vmax = 80

    return newcmp, vmin, vmax

def cod2():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/100, "#000000"),
    (20/100, "#FFFFFF"),
    (37/100, "#04461b"),
    (52/100, "#04e91c"),
    (52/100, "#fcee04"),
    (68/100, "#ea8405"),
    (68/100, "#f42e04"),
    (80/100, "#7b0504"),
    (80/100, "#fc02fc"),
    (90/100, "#838584"),
    (100/100, "#FFFFFF")])
    
    vmin = -20
    vmax = 80

    return newcmp, vmin, vmax

def pivotal():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/65, "#FFFFFF"),
    (15/65, "#1450b4"),
    (15/65, "#0f505f"),
    (25/65, "#fff371"),
    (35/65, "#db7417"),
    (40/65, "#cc0000"),
    (47.5/65, "#76030a"),
    (47.5/65, "#a037af"),
    (55/65, "#611293"),
    (55/65, "#828282"),
    (65/65, "#FFFFFF")])
    
    vmin = 10
    vmax = 75

    return newcmp, vmin, vmax

def tc1():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/110, "#1a1a1a"),
    (10/110, "#405580"),
    (30/110, "#FFFFFF"),

    (40/110, "#53994d"),
    (60/110, "#e6e62e"),
    (75/110, "#ff1919"),
    (95/110, "#404040"),
    (110/110, "#000000")])
    
    vmin = -10
    vmax = 65

    return newcmp, vmin, vmax

def mn():
    newcmp = LinearSegmentedColormap.from_list("", [
    (0/80, "#000000"),
    (10/80, "#e0e7c7"),
    (20/80, "#2a51a9"),
    (28/80, "#6aeaf3"),
    (32/80, "#14e722"),
    (45/80, "#045a06"),
    (50/80, "#feeb00"),
    (60/80, "#fd8900"),
    (60/80, "#ff0000"),
    (70/80, "#650100"),
    (70/80, "#ffffff"),
    (80/80, "#e806ef")])
    
    vmin = -10
    vmax = 70

    return newcmp, vmin, vmax

def gsref():
    newcmp = LinearSegmentedColormap.from_list("", [ 
            (0/55, "#545454"),
            (5/55, "#000000"),
            (20/55, "#000000"),
            (55/55, "#FFFFFF")])

    vmin = -5
    vmax = 50
    
    return newcmp, vmin, vmax

wvtables = {
    'msfc'  : msfc(),
    'psu'   : psu(),
    'wv'    : wv(),
    'wv2'   : wv2(),
    'wv3'   : wv3(),
    'wv4'   : wv4(),
    'wv5'   : wv5(),    
    'wv6'   : wv6(),
    'wv7'   : wv7(),
    'wv8'   : wv8(),
    'wv9'   : wv9(),
    'wv9.5' : wv95(),
    'wv10'  : wv10(),
    'wv11'  : wv11(),
    'wv12'  : wv12(),
    'wv13'  : wv13(),
    'wv13.5'  : wv135(),
    'wv14'  : wv14(),
    'wv15'  : wv15(),
    'wv16'  : wv16(),
    'wv17'  : wv17(),
    'wv18'  : wv18(),
    'wv19'  : wv19(),
    'wv20'  : wv20(),
    'wv21'  : wv21(),
    'wv22'  : wv22(),
    'wv23'  : wv23(),
    'wv24'  : wv24(),
    'wv25'  : wv25(),
    'wv26'  : wv26(),
    'wv27'  : wv27(),
    'wv28'  : wv28(),
    'wv29'  : wv29(),
    'simple': simple(),
    'simple2': simple2(),
    'test'  : testwv(),
    'watermelon'   : watermelon(),
    'halloween'    : halloween(),
    'irg'   : irgwv(),
    'ssd'   : ssdwv(),
    'mikewv': mikewv(),
    'codywv': codywv(),
    'aswv'  : aswv(),
    'aswvold'  : aswvold(),
    'gs'    : graywv(),
    'hand'  : handwv(),
    'dark'  : darkwv(),
    'oldwv' : oldwv()}

irtables = {
    'gs'      :grayir(),
    'avn'     :avn(),
    'funktop' :funktop(),
    'jsl'     :jsl(),
    'rainbow' :rainbow(),
    'rainbow2':rainbow2(),
    'rbtop'   :rbtop(),
    'rbtop2'  :rbtop2(),
    'rbtop2.5':rbtop25(),
    'rbtop3'  :rbtop3(),
    'rbtop4'  :rbtop4(),
    'bd'      :bd(),
    'bd.5'    :bd05(),
    'bd2'     :bd2(),
    'bd3'     :bd3(),
    'ibtracs' :ibtracs(),
    'ibtracs2':ibtracs2(),
    'rammb'   :rammb(),
    'nhc'     :nhc(),
    'wu'      :wu(),
    'shrek'   :shrek(),
    'hand'    :handir(),
    'ryglicki':ryglicki(),
    'candy'   :candy(),
    'bl'      :blhot(),
    'blcold'  :blcold(),
    'spooky'  :spooky(),
    'lava'    :lava(),
    'ice'     :ice(),
    'icy'     :icy(),
    'ice2'    :ice2(),
    'santa'   :santa(),
    'gay'     :gay(),
    'test'    :testir(),
    'cu'      :copper(),
    'oldcody' :oldcody(),
    'cody'    :cody(),
    'icecream':icecream(),
    'asir'    :asir(),
    'volcano' :volcano(),
    'blob'    :blob(),
    'ir'      :ir(),
    'ira'     :ira(),
    'irb'     :irb(),
    'irc'     :irc(),
    'ird'     :ird(),
    'ire'     :ire(),
    'irf'     :irf(),
    'irg'     :irg(),
    'oldirg'  :oldirg(),
    'irh'     :irh(),
    'iri'     :ca2(),
    'irj'     :irj(),
    'irk'     :irk(),
    'irl'     :irl(),
    'irm'     :irm(),
    'irn'     :irn(),
    'iro'     :iro(),
    'irp'     :irp(),
    'irq'     :irq(),
    'irr'     :irr(),
    'irs'     :irs(),
    'irt'     :irt(),
    'iru'     :iru(),
    'irv'     :irv(),
    'irw'     :irw(),
    'irx'     :irx(),
    'iry'     :iry(),
    'irz'     :irz(),
    'ir1'     :ir1(),
    'mean'    :mean(),
    'wind'    :wind(),
    'wind2'   :wind2(),
    'icup'    :icup(),
    'cloudy'  :cloudy(),
    'cs'      :chasespectral(),
    'ncdc'    :ncdc(),
    'ref'     :ref(),
    'irca'    :ca()}

radtables = {
    'ref'    : ref1(),
    'ref2'   : ref2(),
    'ref3'   : ref3(),
    'ref4'   : ref4(),
    'ref5'   : ref5(),
    'ref6'   : ref6(),
    'ref7'   : ref7(),
    'ref8'   : ref8(), 
    'ref9'   : ref9(), 
    'cod1'   : cod1(),
    'cod2'   : cod2(),
    'tc1'    : tc1(),
    'mn'     : mn(),
    'gs'     : gsref(),
    'pivotal': pivotal(),
    'cold'   : cold()
}

# import numpy as np
# import matplotlib.pyplot as plt

# X, Y = np.meshgrid(np.arange(0, 100), np.arange(0, 100))

# cmaps: list = wvtables.values()  # TODO list of colormaps. Please set!
# names: list = list(wvtables.keys())
# fig, axs = plt.subplots(len(cmaps), 1, figsize=(10, len(cmaps)), dpi=200, constrained_layout=True)
# for i, cmap in enumerate(cmaps):
#     axs[i].pcolormesh(X, Y, X, cmap=cmap[0])
#     axs[i].set_xticks([])
#     axs[i].set_yticks([])
#     axs[i].set_ylabel(names[i])

# plt.savefig(r"C:\Users\deela\Downloads\wvcolormaps.png", dpi=200)