#!/usr/bin/env python
"""
Script to convert binary format to root
for DRS4 evaluation boards.
http://www.psi.ch/drs/evaluation-board
Jonas Rembser, 2016-04-13 based on work by
Gregor Kasieczka, ETHZ, 2014-01-15
based on decode.C by Dmitry Hits

What this script doesn't do, because really precise timing information was not
necessary for the use case this scrips was written for:
- store event date/time
- calculate precise timing information as described in the DRS manual
"""

from sys import argv, exit
from ROOT import TFile, TTree
from ROOT.std import vector
from struct import unpack
from array import array

########################################
# Prepare Input
########################################

if not len(argv) == 2:
    print "Wrong number of arguments!"
    print "Usage: python test_channels.py filename.dat"
    print "Exiting..."
    exit()

input_filename = argv[1]
f = open( input_filename, "rb")

########################################
# Prepare Output
########################################

# File and Trees
outfile = TFile(input_filename.replace(".dat",".root"), 'recreate')
outtree_t = TTree('tree_t', 'tree_t')
outtree_v = TTree('tree_v', 'tree_v')

# Create event number variable and add to tree
var_n = array('i',[0])
outtree_v.Branch("n", var_n, "n/I")

########################################
# Actual Work
########################################

# Read in effective time width bins in ns and calculate the relative time from
# the effective time bins. This is just a rough calculation, see DRS manual
# p. 24 on how to do this more precise using the trigger cell information.
# The script also gets channel number information from this section to create
# the appropriate number of tree branches.

# To increase to the total number of channels and boards
n_ch = 0
n_boards = 0

# Empty lists for containing the variables connected to the tree branches
channels_t = []
channels_v = []

while True:
    header = f.read(4)
    # For skipping the initial time header
    if header == "TIME":
        continue
    elif header.startswith("C"):
        n_ch = n_ch + 1
        # Create variables ...
        channels_t.append(vector(float)())
        channels_v.append(vector(float)())
        # .. And add to tree
        setattr(outtree_t, "chn{}_t".format(n_ch), channels_t[-1])
        outtree_t.Branch("chn{}_t".format(n_ch), channels_t[-1])
        setattr(outtree_v, "chn{}_v".format(n_ch), channels_v[-1])
        outtree_v.Branch("chn{}_v".format(n_ch), channels_v[-1])
        time_floats = unpack('f'*1024, f.read(4*1024))
        for j, x in enumerate(time_floats):
            if j == 0:
                channels_t[-1].push_back(x)
            else:
                channels_t[-1].push_back(x + channels_t[-1][-1])

    # Increment the number of boards when seeing a new serial number
    elif header.startswith("B#"):
        n_boards = n_boards + 1

    # End the loop if header is not CXX or a serial number
    else:
        break

outtree_t.Fill()

# This is the main loop One iteration corresponds to reading one channel every
# few channels a new event can start We know that this if the case if we see
# "EHDR" instead of "C00x" (x=1..4) If we have a new event: Fill the tree, reset
# the branches, increment event counter The binary format is described in:
# http://www.psi.ch/drs/DocumentationEN/manual_rev40.pdf (page 24)
# What happens when multiple boards are daisychained: after the C004 voltages of
# the first board, there is the serial number of the next board before it starts
# again with C001.

current_board = 0

# Skip the fluff after first EHDR header (serial number and timing info)
fluff = f.read(4*7)

while True:
    # Read the header, this is either
    #  EHDR -> begin new event
    #  C00x -> read the data
    #  ""   -> end of file
    header = f.read(4)

    # Handle next board
    if header.startswith("B#"):
        fluff = f.read(4*1)
        current_board = current_board + 1
        continue

    # End of File
    if header == "":
        outtree_v.Fill()
        break

    # Sart of Event
    elif header == "EHDR":
        # Fille previous event
        outtree_v.Fill()

        # Reset the vector branches
        for chn in channels_v:
            chn.resize(0)

        # Fluff the serial number and timing info
        fluff = f.read(4*7)

        # Increment event counter and reset current board number
        var_n[0] += 1
        current_board = 0
        continue

    # Read and store data
    else:
        # the voltage info is 1024 floats with 2-byte precision
        chn_i = int(header[-1]) + current_board * 4
        voltage_ints = unpack('H'*1024, f.read(2048))
        for x in voltage_ints:
            channels_v[chn_i-1].push_back( ((x / 65535.) - 0.5) * 1000)

# Clean up
f.close()
outtree_t.Write()
outtree_v.Write()
outfile.Close()
