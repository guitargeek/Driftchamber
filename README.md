# Measuring cosmic muons with a driftchamber
## Overview
The driftchamber experiments in advanced practical physics class. The data with the driftchamber events can be found in \[1\].

## Scripts
### decode.py
This script can be used to convert binary data files from the DRS evaluation board \[2\] to ROOT files and is based on an older script which doesn't work with the newest version of the binary data format anymore \[3\].

### pmt.py
Plots the measured count rate vs HV for both photomultipliers for the trigger system. The measurement data is included in the script.

## References
\[2\]: https://polybox.ethz.ch/index.php/s/EKfXl9ODl3joaUA

\[2\]: https://www.psi.ch/drs/evaluation-board

\[3\]: https://github.com/gkasieczka/testbeam/blob/master/decode.py
