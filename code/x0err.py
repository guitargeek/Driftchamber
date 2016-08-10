from ROOT import TFile, TH1F, TCanvas, TF1, gStyle, gROOT, gPad, TLegend, TH2F
from numpy import arctan

gROOT.SetBatch()
gStyle.SetOptStat(0)

gStyle.SetPadTickX(1)
gStyle.SetPadTickY(1)

#gStyle.SetTitleOffset(1.5)

f = TFile("../data.root")

tree = f.Get("drift_4000V")

#########################
# Plot a simple histogram
#########################
fontsize = 0.04

c1 = TCanvas("c1","c1",200,10,500,500)
c1.cd()

L = 100
H = 290
z = 110 # von channel 1
c = 0.1
v = 0.14 # mm/ns

h = TH1F("h", "", 30, 0, 15)
n = tree.Draw("X0Err>>h")

h.GetXaxis().SetTitleOffset(1)
h.GetYaxis().SetTitleOffset(1.2)

h.GetXaxis().SetLabelSize(fontsize)
h.GetXaxis().SetTitleSize(fontsize)
h.GetYaxis().SetLabelSize(fontsize)
h.GetYaxis().SetTitleSize(fontsize)
h.SetLineColor(1)

h.GetYaxis().SetTitle("Number of events")
h.GetXaxis().SetTitle("Fitting error of the x_{0} parameter [mm]")

h.Draw("")
#f1.Draw("same")
print h.GetEntries()

c1.Draw()
raw_input("wait")
c1.Print("../plots/x0err.pdf")
