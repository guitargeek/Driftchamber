"""
This script reads all the rootfiles which were converted datfiles and extracts
meaningful event variables which can be used in the analysis. Those variables
will be saved in a tree for each run und all trees will be saved to one single
rootfile for convenience. The idea is that all other analysis scrips only read
this new rootfile. If some information is missing, this script should be editetd
to save an imporved set of event variables.
"""

from ROOT import TFile, TGraph, TF1, TTree, TTimeStamp, AddressOf, TCanvas
from sys import argv
from numpy import array, argmax, mean, float32, zeros, uint32, diff, argmin, arctan
from scipy.integrate import simps
import os

# The drift velocity in mm/ns which was found by drift.py
v_drift = 0.13781766497 # WARNING! THIS HOLDS ONLY FOR THE 4000V DATA!
# The time at which the first electrons arrive
s = 640

# Getting the driftchanber channel corresponding to a DRS channel
c = [1, 3, 7, 8]

# All the following geometric constants are given in mm
# Distance between photomultipliers
h = 290
# Distance between wires
w = 10
# Calculate the distances of the read out wires from the top scintillator
y = (array(c, dtype=float) - 1) * w + h/2 - 7*w/2

# Method for rebinning. 2^n bins will be combined.
def rebin(array, n):
    for i in range(n):
        if i == 0:
            rebin = (array[:-1:2] + array[1::2])/2
        else:
            rebin = (rebin[:-1:2] + rebin[1::2])/2
    return rebin

# Number of voltage measurements in each channel per event
n = 1024

# Location of the initial rootfiles and filename of the new one
rootfiles_dir = "../rootfiles/"
outfile = TFile("../data.root", 'recreate')

# Variables for the input tree
t = [zeros(n, dtype=float32) for i in range(4)]
v = [zeros(n, dtype=float32) for i in range(4)]
eventn_in = zeros(1, dtype=uint32)
timestamp = TTimeStamp()

# Variables for the output tree
eventn = zeros(1, dtype=uint32)
seconds = zeros(1, dtype=uint32) # seconds passed until the beginning
height = [zeros(1, dtype=float32) for i in range(4)]
time = [zeros(1, dtype=float32) for i in range(4)]

# variables related to the track reconstruction
x0 = zeros(1, dtype=float32)
x0_err = zeros(1, dtype=float32)
theta = zeros(1, dtype=float32)
theta_err = zeros(1, dtype=float32)

# Save event variables for the run stored in 'filename' in a tree called
# 'treename' and save this tree to 'outfile'
def save_event_tree(filename, treename):

    # Read in rootfile and tree
    f = TFile(filename)
    intree = f.Get('tree')
    intree.SetBranchAddress("EventNumber", eventn_in)

    # Create a tree to save the event variables in
    outtree = TTree(treename, treename)

    # Get the number of events
    N = intree.GetEntries()

    # Find out what the number of channels in this run was
    n_ch = 0
    for i in range(1, 5):
        branch = intree.GetBranch("chn{}_t".format(i))
        if branch == None:
            break
        else:
            n_ch = n_ch + 1

    # Initiate branches accorting to the number of channels
    for i in range(n_ch):
        intree.SetBranchAddress("chn{}_t".format(i+1), t[i])
        intree.SetBranchAddress("chn{}_v".format(i+1), v[i])
        intree.SetBranchAddress("EventDateTime", AddressOf(timestamp))

        # Just comment out the branches which are not needed in the final tree
        #outtree.Branch("EventN", eventn, "EventN/i")
        #outtree.Branch("Seconds", seconds, "Seconds/i")
        outtree.Branch("Chn{}_Height".format(c[i]), height[i], "Chn{}_Height/F".format(c[i]))
        outtree.Branch("Chn{}_Time".format(c[i]), time[i], "Chn{}_Time/F".format(c[i]))

        if n_ch > 1 and "4000V" in filename:
            outtree.Branch("X0", x0, "X0/F")
            outtree.Branch("X0Err", x0_err, "X0Err/F")
            outtree.Branch("Theta", theta, "Theta/F")
            outtree.Branch("ThetaErr", theta_err, "ThetaErr/F")


    starting_seconds = 0
    # This loop iterates over each event
    for j in range(N):
        intree.GetEntry(j)
        eventn[0] = eventn_in[0]
        if j == 0:
            starting_seconds = timestamp.GetSec()
        seconds[0] = timestamp.GetSec() - starting_seconds

        # Empty array to write the hit positions in
        x = zeros(4, dtype=float)

        # This loop iterates over each channel
        for i in range(n_ch):

            # Rebin
            t_re = rebin(t[i], 3)
            v_re = rebin(v[i], 3)

            # Calculate noise baseline by averaging the signal in a range
            # before triggering happened
            noise_lvl = mean(v[:30])

            # As the time of the signal we define the minimum of the derivative
            d = diff(v_re)/diff(t_re)
            vd = (v_re[:-1] + v_re[1:])/2
            td = (t_re[:-1] + t_re[1:])/2
            time[i][0] = td[argmin(d)]

            # The height is defined as the maximum in the 10 bins following
            # the signals time position minus the noise level
            height[i][0] = max(-v_re[argmin(d):min(argmin(d) + 10,128)] - noise_lvl)

            # Use the drift velocity to get hit positions for each wire
            x[i] = v_drift * (time[i][0] - s) + 5

        # Fit the track if channel number is greater than 1
        if n_ch > 1:
            gr = TGraph(n_ch, y, x)
            gr.Fit("pol1", "Q")
            fit = gr.GetFunction("pol1")

            x0[0] = fit.GetParameter(0)
            theta[0] = arctan(fit.GetParameter(1))
            theta_err[0] = 1/(1+fit.GetParameter(1)*2)*fit.GetParError(1)
            x0_err[0] = fit.GetParError(0)

        outtree.Fill()

    # Write tree and clean up
    outfile.cd()
    outtree.Write()
    f.Close()

# Process all rootfiles in the rootfiles directory (including subdirectories)
for path, subdirs, files in os.walk(rootfiles_dir):
    for name in files:
        if name.endswith(".root"):
            filename = os.path.join(path, name)
            treename =  filename[len(rootfiles_dir):-5].replace("/", "_")
            print("Processing {}...".format(filename))
            save_event_tree(filename, treename)

# Clean up
outfile.Close()
