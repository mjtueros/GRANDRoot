#!/usr/bin/env python3
import sys
import ZHAireSRawToGRANDROOT as ZHAireS2ROOT
import ComputeVoltageOnGRANDROOT as ComputeVoltage
from GRANDRootTrees import *
import numpy as np

# """
t = SimEfieldTree()
# t.Setup_SimEfield_Branches(create_branches=True)
t.tree.Print()
t.Scan()
t.Fill()
t.Scan()
t.evt_id=1
t.field_sim = ["zhacorea"]
t.refractivity_param = np.array([2.1, 1.5], dtype=np.float32)
t.Fill()
t.Scan()
#t.GetEvent(1)
print(t.field_sim)
print(t.evt_id)
exit()
# """

if ( len(sys.argv)<2 ):
    print("usage python RunTest.py outputfile")
    sys.exit(-1)
if ( len(sys.argv)==2 ):
    outputfile=sys.argv[1]

inputfolder="./example-events/event1"
ZHAireS2ROOT.ZHAiresRawToGRANDROOT(outputfile,0,1,inputfolder,	SimEfieldInfo=True, NLongitudinal=False, ELongitudinal=False, NlowLongitudinal=False, ElowLongitudinal=False, EdepLongitudinal=False, LateralDistribution=False, EnergyDistribution=False)

inputfolder="./example-events/event2"
ZHAireS2ROOT.ZHAiresRawToGRANDROOT(outputfile,0,2,inputfolder,	SimEfieldInfo=True, NLongitudinal=False, ELongitudinal=False, NlowLongitudinal=False, ElowLongitudinal=False, EdepLongitudinal=False, LateralDistribution=False, EnergyDistribution=False)

inputfolder="./example-events/event3"
ZHAireS2ROOT.ZHAiresRawToGRANDROOT(outputfile,0,3,inputfolder,	SimEfieldInfo=True, NLongitudinal=False, ELongitudinal=False, NlowLongitudinal=False, ElowLongitudinal=False, EdepLongitudinal=False, LateralDistribution=False, EnergyDistribution=False)


ComputeVoltage.ComputeVoltageOnROOT(outputfile)


#ComputeVoltageOnROOT(inputfile)

