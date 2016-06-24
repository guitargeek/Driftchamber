"""
With this script, one can do a monte carlo simulation to see how the
muon tracks are distributed in the wire chamber and compare with measurement.
"""

from numpy import sin, cos, tan, pi, logical_and, greater_equal, less, array
from numpy.random import rand
from ROOT import TH1F

# Dimensions of the driftchamber

h = 290. # height
d = 100. # perpendicular to wire
b = 200. # parallel to wire

# Positions of the wires on the y axis
y = array([110., 130., 170., 180.])

def is_triggering(x, z, theta, phi):
    x2 = x - tan(theta) * h
    z2 = z - tan(phi) * h
    return(logical_and(logical_and(greater_equal(x2, 0), less(x2, d)),
           logical_and(greater_equal(z2, 0), less(z2, b))))

N = 1e6

muons = rand(4, N)
# The positions
muons[0] = muons[0] * d
muons[1] = muons[1] * b
# The angles
muons[2] = (muons[2] - 0.5)*pi
muons[3] = (muons[3] - 0.5)*pi

triggered = is_triggering(*muons)
n = len(triggered[triggered])
print n
print("Fraction triggered: {}".format(n/N))

# We need only the triggered muons now
muons = [muons[i][triggered] for i in range(4)]

hist = TH1F("h", "h", 100, -1, 1)
#hist = TH1F("h", "h", 100, -100, 200)
for i in range(n):
    hist.Fill(muons[2][i])
    #hist.Fill(muons[0][i] - y[3]*tan(muons[2][i]))
hist.SetMinimum(0)

hist.Draw()
raw_input("wait")
