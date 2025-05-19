import numpy as np
from helper import trapezoidalRule

hgts = np.arange(0, 10.5, .5)
uwnd = np.linspace(0, 10, len(hgts))
vwnd = uwnd**0.5
uMotion = 0
vMotion = 0

duwnd = np.diff(uwnd)
dvwnd = np.diff(vwnd)

sum = []
for x in range(len(duwnd)):
    sum.append(((uwnd[x] - uMotion) * dvwnd[x]) - ((vwnd[x] - vMotion) * duwnd[x]))

helicity = trapezoidalRule(hgts[1:], sum)
