import numpy as np

# Eye number "score"
eyenum = {"CDG" : 6.5,
          "CMG" : 6.5,
          "W"   : 6.0,
          "B"   : 5.5,
          "LG"  : 5.0, 
          "MG"  : 4.5,
          "DG"  : 4.5,
          "OW"  : 4.0,
          "WMG" : np.nan
         }

# Adjustment based on surrounding and/or embedded shade
adjmat = {"OW"  : {"WMG" : 0,   "OW"  : -0.5},
          "DG"  : {"WMG" : 0,   "OW"  : 0    , "DG"  : -0.5},
          "MG"  : {"WMG" : 0,   "OW"  : 0    , "DG"  : -0.5, "MG"  : -0.5},
          "LG"  : {"WMG" : 0.5, "OW"  : 0    , "DG"  : 0,    "MG"  : -0.5, "LG"  : -0.5},
          "B"   : {"WMG" : 1.0, "OW"  : 0.5  , "DG"  : 0,    "MG"  : 0,    "LG"  : -0.5, "B"   : -0.5},
          "W"   : {"WMG" : 1.0, "OW"  : 0.5  , "DG"  : 0.5,  "MG"  : 0,    "LG"  : 0,    "B"   : -1,   "W"   : -1},
          "CMG" : {"WMG" : 1.0, "OW"  : 0.5  , "DG"  : 0.5,  "MG"  : 0,    "LG"  : 0,    "B"   : -0.5, "W"   : -1}
         }

# Calculates the Data T# based on the eye scene
def dvorak(emb, eye, surr):
    if surr.upper() == 'CDG':
        surr = 'CMG'

    if (emb.upper() == 'WMG' or (eyenum[emb.upper()] > eyenum[surr.upper()])) or (emb.upper() == 'MG' and surr.upper() == 'DG'):
        err = 'The embed shade cannot be colder than the surrounding color, and must be colder than WMG.'
    elif (eyenum[eye.upper()] > eyenum[surr.upper()]) or (eyenum[eye.upper()] >= eyenum[emb.upper()]):
        err = 'The eye must be warmer than the convection.'
    else:
        try:
            value = eyenum[emb.upper()] + adjmat[surr.upper()][eye.upper()]
            err = f'{emb.upper()} + {eye.upper()} surr {surr.upper()} is {value}'
        except:
            err = 'This is not possible.'
    return err
