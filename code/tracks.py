from ROOT import TFile, TH1F, TCanvas, TF1, gStyle, gROOT, gPad, TLegend
from numpy import arctan

gROOT.SetBatch()
gStyle.SetOptStat(0)

fontsize = 0.045

gStyle.SetPadTickX(1)
gStyle.SetPadTickY(1)

gStyle.SetTitleOffset(1.5)

f = TFile("../data.root")

tree = f.Get("drift_4000V")

th = 0.02

theta_max = arctan(100/290.)

cut = "Chn1_Height>{0}&&Chn3_Height>{0}&&Chn7_Height>{0}&&Chn8_Height>{0}".format(th)

c1 = TCanvas("c1","c1",200,10,1000,500);
c1.Divide(2,1,0,0)
c1.cd(1)

h_x0 = TH1F("hX0", "", 30, -20, 130)
n_x0 = tree.Draw("X0>>hX0", cut+"&&X0Err<6")

h_theta = TH1F("hTheta", "", 30, -0.35, 0.45)
n_theta = tree.Draw("Theta>>hTheta", cut+"&&ThetaErr<0.04")

f_x0 = TF1("fX0", "{}/(30*100/150)*(x<100)*(x>0)".format(n_x0), -1, 101)
f_theta = TF1("fTheta", "0.8/30*{0}*(-abs((x/{1}))+1)/{1}".format(n_theta, theta_max), -1, 101)

# Style histograms
h_x0.SetLineColor(1)
h_x0.SetFillColor(17)
h_x0.SetLineStyle(1)
h_theta.SetLineColor(1)
h_theta.SetFillColor(17)
h_theta.SetLineStyle(1)

# Style functions
f_x0.SetLineColor(1)
f_x0.SetLineStyle(2)
f_x0.SetLineWidth(1)
f_theta.SetLineColor(1)
f_theta.SetLineStyle(2)
f_theta.SetLineWidth(1)

h_x0.GetXaxis().SetLabelSize(fontsize)
h_x0.GetXaxis().SetTitleSize(fontsize)
h_x0.GetYaxis().SetLabelSize(fontsize)
h_x0.GetYaxis().SetTitleSize(fontsize)

h_theta.GetXaxis().SetLabelSize(fontsize)
h_theta.GetXaxis().SetTitleSize(fontsize)
h_theta.GetYaxis().SetLabelSize(fontsize)
h_theta.GetYaxis().SetTitleSize(fontsize)

h_x0.GetXaxis().SetTitleOffset(1)
h_theta.GetXaxis().SetTitleOffset(1)
h_x0.GetXaxis().CenterTitle()
h_theta.GetXaxis().CenterTitle()

h_x0.SetMaximum(67)
h_theta.SetMaximum(67)

h_x0.GetYaxis().SetTitle("Number of events")
h_x0.GetXaxis().SetTitle("x [mm]")
h_theta.GetXaxis().SetTitle("theta [rad]")

gPad.SetTopMargin(0.001)

h_x0.Draw()
f_x0.Draw("same")

legt1 = TLegend(0.2,0.96,0.53,0.89)
legt1.SetTextFont(62)
legt1.SetHeader("Incident position")
legt1.SetBorderSize(0)
legt1.SetTextSize(fontsize)
legt1.Draw()

legi1 = TLegend(0.2,0.90,0.53,0.73)
legi1.AddEntry("hX0", "Measurement", "F")
legi1.AddEntry("fX0", "Calculation", "L")
legi1.SetBorderSize(0)
legi1.SetTextSize(fontsize)
legi1.Draw()

c1.cd(2)
gPad.SetTopMargin(0.001)
gPad.SetRightMargin(0.001)
h_theta.Draw()
f_theta.Draw("same")

legt2 = TLegend(0.6,0.96,0.93,0.89)
legt2.SetTextFont(62)
legt2.SetHeader("Incident angle")
legt2.SetBorderSize(0)
legt2.SetTextSize(fontsize)
legt2.Draw()

legi2 = TLegend(0.6,0.90,0.93,0.73)
legi2.AddEntry("hTheta", "Measurement", "F")
legi2.AddEntry("fTheta", "Calculation", "L")
legi2.SetBorderSize(0)
legi2.SetTextSize(fontsize)
legi2.Draw()

c1.Draw()
c1.Print("../plots/tracks.pdf")
