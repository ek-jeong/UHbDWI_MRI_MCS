Current post-processing software for ultra-high b diffusion MRI (UHb-DWI) runs on MacOS (up to v12.0) with python 3.x. If you face missing package, when launching myMCS.py, the missing modules must be installed via conda or pip. It has been tested on Anaconda python distribution. 

- How to start:
  type python myMCS.py

- Files included:
. myMCS.py
. mcsGlobalVars.py	
. mcsPstProc.py		
. mcsTools.py		
. mcsHelps.py

. myMCS.pdf		


- Sample data folder
(1) intial input data to MCS process (filename:
    C3199_L80D12A4B6_W10kR66_Dm55Da0_2k.dat)
(2) position data for all molecules at all time points (filename:
    C3199_L80D12A4B6_W10kR66_Dm55Da0_2k_TT250.0C1.00S100_P85.100PB1_mcs.dat)
(3) MCS simulation parameters (filename:     
    C3199_L80D12A4B6_W10kR66_Dm55Da0_2k_TT250.0C1.00S100_P85.100PB1_mcs.txt)


- Important MCS parameters are included in the file name of each file:
e.g. C3199_L80D12A4B6_W10kR66_Dm55Da0_2k_TT250.0C1.00S100_P85.100PB1_mcs.dat

- C3199: 3199 axons
- W10k:  10000 molecules
- R66:   g-ratio, i.e. ID/OD
- Dm55:  55 % axons demyelinated with myelin layer removed
- Da0:   0 % demyelinated axons removed
- TT250: total diffusion time of 250 ms 
- C1.00: hopping time 1.0 use
- S100:  saving time 100 used
- P85.100: permeability of myelinated (85 um/s) and demyelinated (100 um/sec) axons

Note that the hopping time needs to be as small as 0.1 used to make a mean displacement close to the grid size, the saving time 10 usec, the total diffusion time 500 sec, and increased number of water molecules, say 20000. However, The size of the generated MCS file will be too large, say ~ 10 GBytes for one simulated MCS data, which is too large for distribution. Therefore, simulation parameters were simplified to reduce the file size. However, the resultant 