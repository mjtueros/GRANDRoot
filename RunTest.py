#!/usr/bin/env python3
import sys
import ZHAireSRawToGRANDROOT as ZHAireS2ROOT
import ComputeVoltageOnGRANDROOT as ComputeVoltage


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

