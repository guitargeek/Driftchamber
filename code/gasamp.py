"""
This script generates a plot where one can read off the gas amplification for
different preassures and anode voltages.
"""

from ROOT import (TFile, TF1, AddressOf, TH1F, TCanvas, TGraph,
                  gDirectory, TH1F, gROOT, TLegend, gStyle)
from ROOT.std import vector
from numpy import array, argmin, mean, zeros, float32, uint32
import re

gROOT.SetBatch()

f = TFile("../data.root")

c1 = TCanvas("c1","c1",200,10,500,500)
c1.cd()

# Function to calculate a value proportional to the gas amplification for a
# measurement run stored in a tree.
def get_gasamp(treename):
    tree = f.Get(treename)

    h = TH1F("h_{}".format(treename), "h_{}".format(treename), 1000, 0, 0.5)
    tree.Draw("Chn1_Height>>h_{0}".format(treename))
    h.Fit("landau", "Q")

    fit = h.GetFunction("landau")

    mpv = fit.GetParameter(1) # most propable value
    mean = h.GetMean()

    # One can also change this to mpv, but the results are better fittable
    # and explainable if one takes just the average of pulse heights
    return(mean)

# Initialize lists to store data
preassures, gasamps,voltages = [], [], []

# Get a list of all available tree names
def GetKeyNames( self, dir = "" ):
    self.cd(dir)
    return [key.GetName() for key in gDirectory.GetListOfKeys()]
TFile.GetKeyNames = GetKeyNames

# Calculate the gasamp value for each tree
key_list = f.GetKeyNames("")
for key in key_list:
    numbers = array(re.findall('\d+', key), dtype=int)
    if len(numbers) == 2:
        if numbers[0] not in preassures:
            preassures.append(numbers[0])
            gasamps.append([])
            voltages.append([])
        voltages[-1].append(numbers[1])
        gasamps[-1].append(get_gasamp(key))

# Convert to numpy arrays
preassures = array(preassures, dtype=float)
gasamps = [array(x, dtype=float)*1000 for x in gasamps]
voltages = [array(x, dtype=float)/1000 for x in voltages]

##########
# Plotting
##########

# Axis on both sides
gStyle.SetPadTickX(1)
gStyle.SetPadTickY(1)

fontsize = 0.04

c1.SetLogy()

n = len(preassures)
graphs = [TGraph(len(voltages[i]), voltages[i], gasamps[i]) for i in range(n)]

# Voltage ranges where the fit should be done, because the for small voltages
# the result is meaningless as many events fall below trigger lever. For too
# high voltages, the DRS is clipping.
x_min = [2.150, 1.850, 1.750, 1.950, 2.050]
x_max = [2.550, 2.550, 2.550, 2.550, 2.450]

for i in range(n):
    graphs[i].Fit("expo", "Q", "", x_min[i], x_max[i])
    fit = graphs[i].GetFunction("expo")
    fit.SetLineColor(1)
    fit.SetLineStyle(i+1)
    fit.SetRange(1.650, 2.625)
    graphs[i].GetXaxis().SetLimits(1.650,2.625)
    graphs[i].SetMaximum(210)
    graphs[i].SetMinimum(4)
    graphs[i].SetName("gr{}".format(i+1))
    if i == 0:
        graphs[i].GetYaxis().SetTitleOffset(1.25)
        graphs[i].GetXaxis().SetLabelSize(fontsize)
        graphs[i].GetXaxis().SetTitleSize(fontsize)
        graphs[i].GetYaxis().SetLabelSize(fontsize)
        graphs[i].GetYaxis().SetTitleSize(fontsize)
        graphs[i].SetMarkerStyle(i+33)
        graphs[i].GetXaxis().SetTitle("Anode voltage [kV]")
        graphs[i].GetYaxis().SetTitle("Average peak height [mV]")
        graphs[i].SetTitle("Gas amplification")
        graphs[i].Draw("AP")
    else:
        graphs[i].SetMarkerStyle(i+19)
        graphs[i].Draw("P")

leg = TLegend(0.67,0.13,0.87,0.45)
leg.SetBorderSize(0)
leg.SetTextSize(fontsize)

leg.AddEntry("gr3","{} bar".format(preassures[2]/1000),"p")
leg.AddEntry("gr2","{} bar".format(preassures[1]/1000),"p")
leg.AddEntry("gr4","{} bar".format(preassures[3]/1000),"p")
leg.AddEntry("gr5","{} bar".format(preassures[4]/1000),"p")
leg.AddEntry("gr1","{} bar".format(preassures[0]/1000),"p")

leg.Draw()

c1.Draw()
c1.Print("../plots/gasamp.pdf")

f.Close()
