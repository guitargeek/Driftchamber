#!/usr/bin/env python
"""
Script to convert binary format to root for DRS4 evaluation boards.
http://www.psi.ch/drs/evaluation-board

Jonas Rembser (rembserj@phys.ethz.ch), 2016-04-15 based on work by
Gregor Kasieczka, ETHZ, 2014-01-15
based on decode.C by Dmitry Hits
"""

from sys import argv, exit
from ROOT import TFile, TTree, TTimeStamp, AddressOf
from ROOT.std import vector
from numpy import array, uint32, cumsum, roll, zeros, float32
from struct import unpack

########################################
# Prepare Input
########################################

if not len(argv) == 2:
    print "Wrong number of arguments!"
    print "Usage: python decode.py filename.dat"
    print "Exiting..."
    exit()

input_filename = argv[1]
f = open( input_filename, "rb")

########################################
# Prepare Output
########################################

# File and Trees
outfile = TFile(input_filename.replace(".dat",".root"), 'recreate')
outtree = TTree('tree', 'tree')

# Create board and event serial number and date variables and add to tree
timestamp = TTimeStamp()
outtree.Branch("EventDateTime", "TTimeStamp", AddressOf(timestamp))
board_serials = vector(int)()
outtree.Branch("BoardSerials", board_serials)
event_serial = array([0], dtype=uint32)
outtree.Branch("EventNumber", event_serial, "EventNumber/i")
# more branches will be added dynamically in the first while loop

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

# List of numpy arrays to store the time bin information
timebins = []

while True:
    header = f.read(4)
    # For skipping the initial time header
    if header == "TIME":
        continue
    elif header.startswith("C"):
        n_ch = n_ch + 1
        # Create variables ...
        channels_t.append(zeros(1024, dtype=float32))
        channels_v.append(zeros(1024, dtype=float32))
        # .. And add to tree
        outtree.Branch("chn{}_t".format(n_ch), channels_t[-1], "chn{}_t[1024]/F")
        outtree.Branch("chn{}_v".format(n_ch), channels_v[-1], "chn{}_v[1024]/F")

        # Write timebins to numpy array
        timebins.append(array(unpack('f'*1024, f.read(4*1024))))

    # Increment the number of boards when seeing a new serial number
    # and store the serial numbers in the board serial numbers vector
    elif header.startswith("B#"):
        board_serial = unpack('H', header[2:])[0]
        board_serials.push_back(board_serial)
        n_boards = n_boards + 1

    # End the loop if header is not CXX or a serial number
    elif header == "EHDR":
        break

# This is the main loop One iteration corresponds to reading one channel every
# few channels a new event can start We know that this if the case if we see
# "EHDR" instead of "C00x" (x=1..4) If we have a new event: Fill the tree, reset
# the branches, increment event counter The binary format is described in:
# http://www.psi.ch/drs/DocumentationEN/manual_rev40.pdf (page 24)
# What happens when multiple boards are daisychained: after the C004 voltages of
# the first board, there is the serial number of the next board before it starts
# again with C001.

current_board = 0
tcell = 0 # current trigger cell
t_00 = 0 # time in first cell in first channel for alignment
is_new_event = True

info_string = "Reading in events measurend with {0} channels on {1} board(s)..."
print(info_string.format(n_ch, n_boards))

while True:
    # Sart of Event
    if is_new_event:
        event_serial[0] = unpack("I", f.read(4))[0]
        is_new_event = False

        # Set the timestamp, where the milliseconds need to be converted to
        # nanoseconds to fit the function arguments
        dt_list = unpack("H"*8, f.read(16))
        timestamp_args = list(dt_list[:-2]) + [dt_list[-2]*int(1e6), 1, 0]
        timestamp.Set(*timestamp_args)

        # Fluff the serial number and read in trigger cell
        fluff = f.read(4)
        tcell = unpack('H', f.read(4)[2:])[0]

        # Reset current board number
        current_board = 0
        continue

    # Read the header, this is either
    #  EHDR -> finish event
    #  C00x -> read the data
    #  ""   -> end of file
    header = f.read(4)

    # Handle next board
    if header.startswith("B#"):
        current_board = current_board + 1
        tcell = unpack('H', f.read(4)[2:])[0]
        continue

    # End of Event
    elif header == "EHDR":
        # Fille previous event
        outtree.Fill()
        is_new_event = True

    # Read and store data
    elif header.startswith("C"):
        # the voltage info is 1024 floats with 2-byte precision
        chn_i = int(header[-1]) + current_board * 4

        voltage_ints = unpack('H'*1024, f.read(2*1024))

        # Calculate precise timing using the time bins and trigger cell
        # see p. 23 in the reference
        t = cumsum(roll(timebins[chn_i-1], -tcell))
        t_0 = t[(1024-tcell)%1024] # time of first cell for correction
        if chn_i % 4 == 1:
            t_00 = t_0
        t = t - (t_0 - t_00) # correction
        # Note: it is a bit unclear how to do the correction with
        # multiple boards, so the boards are just corrected independently
        # for now

        for i, x in enumerate(voltage_ints):
            channels_v[chn_i-1][i] = ((x / 65535.) - 0.5)
            channels_t[chn_i-1][i] = t[i]

    # End of File
    elif header == "":
        outtree.Fill()
        break

# Clean up
f.close()
outtree.Write()
outfile.Close()
