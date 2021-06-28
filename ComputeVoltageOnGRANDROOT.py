import os
import sys
import logging
import numpy as np
# Commented to avoid the dependency on RADIOSIMUS, so that the repository is self contained and easy to do tests.
# now the signal is just the filtered electric field 
#root_dir = os.path.realpath(os.path.join(os.path.split(__file__)[0], "../radio-simus")) # = $PROJECT
#root_dir=os.environ["RADIOSIMUS"] #this requires the radi simus package from grand
#sys.path.append(os.path.join(root_dir, "lib", "python"))
#from radio_simus.in_out import _table_voltage
#from radio_simus.computevoltage import compute_antennaresponse
#from radio_simus.signal_processing import filters
import GRANDRoot 
import ROOT
from copy import deepcopy

logging.basicConfig(level=logging.DEBUG)
logging.getLogger('matplotlib').setLevel(logging.ERROR)

#if no outfilename is given, it will store the table in the same root file, in a separate tree (TODO: handle what happens if it already exists)

#this computes the voltage on all the antennas

def ComputeVoltageOnROOT(inputfilename,RunID=0,outfilename="N/A"):

  #TODO:handle exceptions: input or output file not vaid, RunID not valid,etc

  if os.path.isfile(inputfilename):
    if(outfilename=="N/A"):
      infilehandle= ROOT.TFile(inputfilename, "UPDATE")
      outfilehandle=infilehandle
    else:
      infilehandle= ROOT.TFile(inputfilename, "READ")
      outfilehandle=ROOT.TFile(outfilename, 'UPDATE')

    #preparing input trees #TODO: Handle when something does not exist.
    SimShower=infilehandle.SimShower #this gets the SimShower tree and sets the addresses
    SimEfield=infilehandle.SimEfield #this gets the SimEfield tree and sets the addresses

    NumberOfEvents=SimEfield.GetEntries() #TODO: IMPLEMENT THE FRIENDS SO THAT SIMSHOWER AND SIMEFIELD ARE SYNCHRONIZED
    logging.info("Computing Voltages for "+inputfilename+", found "+str(NumberOfEvents)+" events")
     
    #preparing SimSignal output tree #TODO: handle when it already exists. Check for SimSignalRun existance. Check for RunID consistency
    SimSignal_tree = ROOT.TTree("SimSignal", "SimSignal")
      
    SimSignal=GRANDRoot.Setup_SimSignal_Branches(SimSignal_tree)
    SimSignal_Detector=GRANDRoot.Setup_SimSignalDetector_Branches(SimSignal_tree)
 
    for idx in range(0,NumberOfEvents):
    # for idx in range(0,0):
        #Since SimEfield and SimShower are friends, when i get an entry from SimEfield, the information of SimShower is also loaded
        SimEfield.GetEntry(idx) # #and this reads the whole tree into memmory, into the SimShower object. There are smarter ways to do this (you can disable branches, you can only load the branches you are going to use)
        #TODO: Check consitency of RunID/EventID
        # SimShower.GetEntry(idx)

        # Clear the vectors for the new event
        SimSignal['signal_sim'].clear()
        SimSignal_Detector['det_id'].clear()
        SimSignal_Detector['det_pos_shc'].clear()
        SimSignal_Detector['det_type'].clear()
        SimSignal_Detector['t_0'].clear()
        SimSignal_Detector['trace_x'].clear()
        SimSignal_Detector['trace_y'].clear()
        SimSignal_Detector['trace_z'].clear()

        EventID=SimShower.evt_id
        Zenith=SimShower.shower_zenith
        Azimuth=SimShower.shower_azimuth

        print(type(Zenith),type(Azimuth),Zenith,Azimuth)

        #imEfield.GetEntry(idx)    #TODO: how to guarantee that SimEfield and SimShower are synchronized (meaning that the same idx represents the same event) # LWP: We create index over run,event. Then we either make simshower a friend of simeefield (or vice versa), GetEntry() on one of them and use branches of the other through the first one, or call GetEntryWithIndex(run,event) or something similar.
        nantennas=SimEfield.Detectors_det_id.size()

        logging.info("Found "+str(nantennas)+" antennas")        

        tbinsize=SimEfield.t_bin_size
        tpre=SimEfield.t_pre
        tpost=SimEfield.t_post
        
        SignalSimulator="CompuetVoltageOnGRANDROOT"                       
        #Populate what we can
        SimSignal['run_id'][:]=RunID
        SimSignal['evt_id'][:]=EventID
        SimSignal['signal_sim'].push_back(SignalSimulator)                #TODO: Decide if this goes into the SimEfieldRun Info
         
        #TODO: Treat the case where no antenna traces were found.
        for i in range(0,int(nantennas)):
            

            DetectorID=SimEfield.Detectors_det_id[i] 

            logging.info("computing voltage for antenna "+str(DetectorID)+" ("+str(i+1)+"/"+str(nantennas)+")")

            position=SimEfield.Detectors_det_pos_shc[i]
            #logging.debug("at position"+str(position))
            
            
            efieldx=np.array(SimEfield.Detectors_trace_x[i])
            efieldy=np.array(SimEfield.Detectors_trace_y[i])
            efieldz=np.array(SimEfield.Detectors_trace_z[i])
                        
            efield=np.column_stack((efieldx,efieldy,efieldz))
                        
            t0=SimEfield.Detectors_t_0[i]
              
            time=np.arange(tpre+t0,tpost+t0+10*tbinsize,tbinsize,)
            time=time[0:np.shape(efield)[0]]   

            efield=np.column_stack((time,efield))

            print(" ABOUT TO COMPUTE VOLTAGE ON EFIELD",i)
            print(efield[600])
            #i compute the antenna response using the compute_antennaresponse function
            #A NICE call to the radio-simus library of Anne (which is completely outdated, but is what i have). Configuration and details of the voltage computation unavailable for now!.
            #Configuration should be a little more "present" in the function call,
            #also maybe the library to handle .ini files would be more profesional and robust than current implementation

            #voltage = compute_antennaresponse(efield, Zenith, Azimuth, alpha=0, beta=0)
            fs=1e9/tbinsize #in Hz
            nu_low=1e9*0.03   #in Hz
            nu_high=1e9*0.3   #in Hz            
            voltagex= butter_bandpass_filter(efieldx,nu_low,nu_high,fs) #fs is the sampling frequency i
            voltagey= butter_bandpass_filter(efieldy,nu_low,nu_high,fs)
            voltagez= butter_bandpass_filter(efieldz,nu_low,nu_high,fs)              
            
            
            print("Got VOLTAGE")
            print(voltagex[600],voltagey[600],voltagez[600])
            
            # LWP: push_back is only for std:vector, which can (normally) hold only 1 specific type. I think here we would just have standard TTree branches and thus use the standard something[0]=something convention
            SimSignal_Detector['det_id'].push_back(DetectorID)
            SimSignal_Detector['det_pos_shc'].push_back(position)
            tmp_v = ROOT.vector("string")()
            tmp_v.push_back("HorizonAntenna")                       #TODO: This is hardwaired, and it shouldnt
            SimSignal_Detector['det_type'].push_back(tmp_v)   
            SimSignal_Detector['t_0'].push_back(t0)
            
            #
            #voltagex=deepcopy(voltage[:,1])
            voltagex=np.array(voltagex, dtype=np.float32)
            tmp_trace_x  = ROOT.vector("float")()
            tmp_trace_x.assign(voltagex)
            SimSignal_Detector['trace_x'].push_back(tmp_trace_x)
 
            #voltagey=deepcopy(voltage[:,2])
            voltagey=np.array(voltagey, dtype=np.float32)
            tmp_trace_y  = ROOT.vector("float")()
            tmp_trace_y.assign(voltagey)
            SimSignal_Detector['trace_y'].push_back(tmp_trace_y)            

            #voltagez=deepcopy(voltage[:,3])
            voltagez=np.array(voltagez, dtype=np.float32)            
            tmp_trace_z  = ROOT.vector("float")()
            tmp_trace_z.assign(voltagez)
            SimSignal_Detector['trace_z'].push_back(tmp_trace_z)                
                                                                   #TODO: Fill p2p and Hilbert things
                         
            #end for antennas
        SimSignal_tree.Fill() #put the results in the out_event
        
        #End for events
        #Add SimEfelid as Friend of SimSignal
        #Add SimShower as Friend of SimSignal
        # Need to remove the friend first - it was stored along the TTree in the previous Write() - otherwise AddFriend() crashes
        SimSignal_tree.RemoveFriend(SimEfield)
        SimSignal_tree.RemoveFriend(SimShower)
        #Reset the Index
        SimSignal_tree.SetTreeIndex(ROOT.nullptr)
        #Build a new Index
        SimSignal_tree.BuildIndex("run_id", "evt_id")
        #Add Friends
        SimSignal_tree.AddFriend(SimEfield)
        SimSignal_tree.AddFriend(SimShower)
                         
        #Now save the tree
        SimSignal_tree.Write("", ROOT.TObject.kWriteDelete) #this is to avoid having several copies of the tree in the index of the file
    
    SimEfield.RemoveFriend(SimShower)
    print("*********ABOUT TO CLOSE")
    infilehandle.Close()        
    outfilehandle.Close() #close 
    print("****************CLOSED!")      

  else:

    logging.critical("input file " + inputfilename + " does not exist or is not a directory. ComputeVoltageOnSHDF5 cannot continue")



from scipy.signal import butter, sosfilt, sosfreqz
#taken from https://stackoverflow.com/questions/12093594/how-to-implement-band-pass-butterworth-filter-with-scipy-signal-butter
def butter_bandpass(lowcut, highcut, fs, order=5):
        nyq = 0.5 * fs
        low = lowcut / nyq
        high = highcut / nyq
        sos = butter(order, [low, high], analog=False, btype='band', output='sos')
        return sos

def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
        sos = butter_bandpass(lowcut, highcut, fs, order=order)
        y = sosfilt(sos, data)
        return y


if __name__ == '__main__':

  if ( len(sys.argv)<2 ):
    print("usage ComputVoltagwOnGRANDROOT inputfile (outputfile)")
    print("if outputfile is not specified, voltage is writen on the same file")

  if ( len(sys.argv)==2 ):
   inputfile=sys.argv[1]
   ComputeVoltageOnROOT(inputfile)

  if ( len(sys.argv)==3 ):
   inputfile=sys.argv[1]
   outputfile=sys.argv[2]
   ComputeVoltageOnROOT(inputfile,outfilename=outputfile)




