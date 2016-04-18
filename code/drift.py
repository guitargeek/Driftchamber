"""
This script plots drift velocity against field voltage.
"""

from ROOT import (TFile, TGraph, TF1, AddressOf, TH1F, TCanvas, TGraph,
                  gDirectory, TH1F, gROOT, TLegend, gStyle)
from numpy import array, argmin, mean, zeros, float32, uint32, sqrt
import re

#gROOT.SetBatch()

f = TFile("../data.root")

c1 = TCanvas("c1","c1",200,10,500,500)
c1.cd()

hists = []

# Function to calculate a value proportional to the gas amplification for a
# measurement run stored in a tree.
def get_drifttime(treename):
    tree = f.Get(treename)

    hists.append(TH1F("h_{}".format(treename), treename, 15, 600, 1600))
    tree.Draw("Chn3_Time>>h_{}".format(treename), "Chn3_Height>0.02")

    if treename == "drift_4000V":
        hists[-1].Scale(0.1)

    sigma = hists[-1].GetStdDev()

    # TODO: explain why I do this
    width = 2 * sqrt(6) * sigma

    return(width)

# Initialize lists to store data
voltages, drifttimes = [], []

# Get a list of all available tree names
def GetKeyNames( self, dir = "" ):
    self.cd(dir)
    return [key.GetName() for key in gDirectory.GetListOfKeys()]
TFile.GetKeyNames = GetKeyNames

# Calculate the gasamp value for each tree
key_list = f.GetKeyNames("")
for key in key_list:
    numbers = array(re.findall('\d+', key), dtype=int)
    if len(numbers) == 1:
        voltages.append(numbers[0])
        drifttimes.append(get_drifttime(key))

# Plot the histograms if needed
"""
for i, h in enumerate(hists):
    hists[i].SetLineColor(i+1)
    if i == 0:
        hists[i].SetMaximum(20)
        hists[-i].Draw()
    else:
        hists[-i].Draw("same")
"""

# Convert to numpy arrays
voltages = array(voltages, dtype=float)
drifttimes = array(drifttimes, dtype=float)

import matplotlib.pyplot as plt

plt.figure()
plt.title("Drift velocity")
plt.xlabel("Cathode voltage")
plt.ylabel("1/Delta t")
plt.scatter(voltages, 1/drifttimes)
plt.show()

c1.Draw()

f.Close()
