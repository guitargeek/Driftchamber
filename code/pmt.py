from numpy import array, sqrt, zeros
from ROOT import TGraphErrors, TCanvas, gStyle, gPad, gROOT, TLegend

# This plot shows the dependence of the PMT counting rate on the HV
# in order to find the right HV setting.

##################
# Measurement Data
##################

# Counting time for each hv setting
time = 120.

# PMT 1
v_th_1 = 301 # threshold in mV
hv_1 = array([2400, 2390, 2380, 2370, 2360, 2350, 2340, 2330, 2320, 2310, 2300,
              2290, 2280, 2270, 2260, 2250, 2240, 2230, 2220, 2210, 2200, 2190,
              2180, 2170, 2160, 2150, 2140, 2130, 2120, 2110, 2100],
              dtype=float)
counts_1 = array([2300, 1774, 1365, 1120, 1000, 847, 760, 738, 673, 652, 575,
                   550,  547,  521,  462,  441, 393, 361, 323, 283, 220, 194,
                   171,  120,  102,   91,   72,  61,  40,  47, 26],
                   dtype=float)

# PMT 2
v_th_2 = 522 # threshold in mV
hv_2 = array([2100, 2090, 2080, 2070, 2060, 2050, 2040, 2030, 2020, 2010, 2000,
              1990, 1980, 1970, 1960, 1950, 1940, 1930, 1920, 1910, 1900],
              dtype=float)
counts_2 = array([3160, 2520, 1980, 1730, 1480, 1305, 1118, 960, 804, 750, 711,
                   628,  572,  553,  542,  483,  397,  328, 272, 220, 180],
                   dtype=float)

#############
# Calculation
#############

# counts per seconds
n_1 = counts_1/time
n_err_1 = sqrt(counts_1)/time
n_2 = counts_2/time
n_err_2 = sqrt(counts_2)/time

##########
# Plotting
##########

gROOT.SetBatch()

fontsize = 0.045

# Axis on both sides
gStyle.SetPadTickX(1)
gStyle.SetPadTickY(1)

gStyle.SetTitleOffset(1.5)

c1 = TCanvas("c1","c1",200,10,1000,500);
c1.Divide(2,1,0,0)
gr1 = TGraphErrors(len(n_1),hv_1,n_1,zeros(len(n_1)),n_err_1)
gr2 = TGraphErrors(len(n_2),hv_2,n_2,zeros(len(n_2)),n_err_2)
gr1.SetTitle("")
gr2.SetTitle("")
gr1.SetMaximum(9.8)
gr2.SetMaximum(9.8)
gr1.GetXaxis().SetRangeUser(2090,2380)
gr2.GetXaxis().SetRangeUser(1890,2060)
gr2.GetXaxis().SetTitle("HV [V]")
gr2.GetXaxis().SetTitleOffset(1)
gr2.GetXaxis().SetNdivisions(4, 5, 0)
gr1.GetYaxis().SetTitle("counting rate [s^{-1}]")

gr1.GetXaxis().SetLabelSize(fontsize)
gr1.GetXaxis().SetTitleSize(fontsize)
gr1.GetYaxis().SetLabelSize(fontsize)
gr1.GetYaxis().SetTitleSize(fontsize)

gr2.GetXaxis().SetLabelSize(fontsize)
gr2.GetXaxis().SetTitleSize(fontsize)
gr2.GetYaxis().SetLabelSize(fontsize)
gr2.GetYaxis().SetTitleSize(fontsize)

gr1.SetMarkerStyle(8)
gr2.SetMarkerStyle(8)
gr1.SetMarkerSize(0.7)
gr2.SetMarkerSize(0.7)

c1.cd(1)
gPad.SetTopMargin(0.001)

# Misuse the TLegend class to draw title and v_th
legt1 = TLegend(0.2,0.96,0.53,0.89)
legt1.SetTextFont(62)
legt1.SetHeader("PMT 1")
legt1.SetBorderSize(0)
legt1.SetTextSize(fontsize)

legi1 = TLegend(0.2,0.90,0.53,0.83)
legi1.SetHeader( "V_{th} = " + str(v_th_1) + " mV")
legi1.SetBorderSize(0)
legi1.SetTextSize(fontsize)

gr1.Draw("AP")
legt1.Draw()
legi1.Draw()

c1.cd(2)

legt2 = TLegend(0.12,0.96,0.53,0.89);
legt2.SetTextFont(62);
legt2.SetHeader("PMT 2");
legt2.SetBorderSize(0);
legt2.SetTextSize(fontsize);

legi2 = TLegend(0.12,0.90,0.53,0.83);
legi2.SetHeader( "V_{th} = " + str(v_th_2) + " mV");
legi2.SetBorderSize(0);
legi2.SetTextSize(fontsize);

# Needed to make the right border visible
gPad.SetTopMargin(0.001)
gPad.SetRightMargin(0.001)
gr2.Draw("AP");
legt2.Draw()
legi2.Draw()

c1.Draw()
c1.Print("../plots/pmt.pdf")

# I chose 2300 V for PMT 1 and 1980 V for PMT 2.
# The discriminator pulse  width was tweaked to 30 ns in both cases.
