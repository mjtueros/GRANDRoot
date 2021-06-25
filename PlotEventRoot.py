import os
import sys
import logging
import numpy as np
import GRANDRoot 
import ROOT
import matplotlib.pyplot as plt
logging.basicConfig(level=logging.INFO)
logging.getLogger('matplotlib').setLevel(logging.ERROR)


#if no outfilename is given, it will store the table in the same root file, in a separate tree (TODO: handle what happens if it already exists)

#this computes the voltage on all the antennas

def PlotEventOnROOT(inputfilename):

    plt.rc('font', family='serif', size=16)
    width=7.2*3
    height=width/1.45

    #TODO:handle exceptions: input file not vaid,etc
    infilehandle= ROOT.TFile(inputfilename, "READ")

    #preparing input trees #TODO: Handle when something does not exist.
    SimShower= infilehandle.SimShower #this gets the SimShower tree and sets the addresses
    SimEfield= infilehandle.SimEfield #this gets the SimEfield tree and sets the addresses
    SimSignal= infilehandle.SimSignal #this gets the SimSignal tree and sets the addresses


    NumberOfEvents=SimSignal.GetEntries() #TODO: for now, we do it on the first event, quick and dirty until we implement how to write multiple events on the fileSimEfield.Detectors_det_id.size()
    logging.info("Ploting for "+inputfilename+", found "+str(NumberOfEvents)+" events")
     
     
    for idx in range(0,NumberOfEvents):
            
        SimSignal.GetEntry(idx)    #and this reads the whole tree into memmory, into the SimShower object (and its friends!). There are smarter ways to do this (you can disable branches, you can only load the branches you are going to use) 
        #TODO: Check consitency of RunID/EventID

        EventID=SimShower.evt_id
        Zenith=SimShower.shower_zenith
        Azimuth=SimShower.shower_azimuth

        print("EventID",EventID,"Zenith",Zenith,"Azimuth",Azimuth)

        #SimEfield.GetEntry(idx)    #TODO: how to guarantee that SimEfield and SimShower are synchronized (meaning that the same idx represents the same event) # LWP: We create index over run,event. Then we either make simshower a friend of simeefield (or vice versa), GetEntry() on one of them and use branches of the other through the first one, or call GetEntryWithIndex(run,event) or something similar.
        nantennas=SimEfield.Detectors_det_id.size()

        logging.info("Found "+str(nantennas)+" antennas")        

        #SimSignal.GetEntry(idx) 

        etbinsize=SimEfield.t_bin_size
        etpre=SimEfield.t_pre
        etpost=SimEfield.t_post
        print("etpre",etpre,"etpost",etpost,"etbinsize",etbinsize)

        vtbinsize=SimSignal.t_bin_size
        vtpre=SimSignal.t_pre
        vtpost=SimSignal.t_post
        print("vtpre",etpre,"vtpost",etpost,"vtbinsize",etbinsize)
        

        #TODO: Check consistenciy of Det_id and pos in signal and efield        
        Det_id=SimEfield.Detectors_det_id
        Det_pos_shc=SimEfield.Detectors_det_pos_shc

                  
        fig1 = plt.figure(1,figsize=(width,height), facecolor='w', edgecolor='k')
        fig1.suptitle("Event "+ str(EventID))
        ax1=fig1.add_subplot(111)
        ax1.set_xlabel('NS (m) (Shower coordinates)')
        ax1.set_ylabel('EW (m) (Shower coordinates)')        
        xvalues = ([np.asarray(e[0]) for e in Det_pos_shc])
        yvalues = ([np.asarray(e[1]) for e in Det_pos_shc])
        zvalues = ([np.asarray(e[2]) for e in Det_pos_shc])
        im=ax1.scatter(xvalues,yvalues,c=zvalues,cmap=plt.cm.jet,vmin=np.min(zvalues),vmax=np.max(zvalues),s=16)
        for i in range(0,len(Det_id)):
         ax1.annotate(Det_id[i], (xvalues[i],yvalues[i]),fontsize=12)
        plt.tight_layout() 
        plt.show()


        #TODO: Treat the case where no antenna traces were found.
        for i in range(0,int(nantennas)):
            

            DetectorID=SimEfield.Detectors_det_id[i] 

            logging.info("Ploting for antenna "+str(DetectorID)+" ("+str(i+1)+"/"+str(nantennas)+")")

            position=SimEfield.Detectors_det_pos_shc[i]
            #logging.debug("at position"+str(position))
                                    
            efieldx=np.array(SimEfield.Detectors_trace_x[i])
            efieldy=np.array(SimEfield.Detectors_trace_y[i])
            efieldz=np.array(SimEfield.Detectors_trace_z[i])
            t0=SimEfield.Detectors_t_0[i]            
            etime=np.arange(etpre+t0,etpost+t0+10*etbinsize,etbinsize)
            etime=etime[0:(len(efieldx))] 
            
            print("etime[600]",etime[600],"efield[600]",efieldx[600],efieldy[600],efieldz[600])
             
            voltagex=np.array(SimSignal.Detectors_trace_x[i])*5
            voltagey=np.array(SimSignal.Detectors_trace_y[i])*5
            voltagez=np.array(SimSignal.Detectors_trace_z[i])*5                       
            t0=SimSignal.Detectors_t_0[i]
            vtime=np.arange(vtpre+t0,vtpost+t0+10*vtbinsize,vtbinsize)
            vtime=vtime[0:(len(voltagex))]
                        
            print("vtime[600]",vtime[600],"vfield[600]",voltagex[600],voltagey[600],voltagez[600])
                             
            print("efield lenght",len(efieldx),"signal lenght",len(voltagex))
              
            fig2, (ax1, ax2, ax3)  = plt.subplots(1, 3, sharey='row',figsize=(width,height))
            #fig2 = plt.figure(2,figsize=(width,height), facecolor='w', edgecolor='k')
            fig2.suptitle("Antenna "+str(DetectorID))
            #ax1=fig2.add_subplot(131)
            ax1.set_title('NS component',fontsize=12)
            ax1.set_xlabel('time (ns)')
            ax1.set_ylabel('Amplitude (Voltage x5)')                    
            yvalues=efieldx
            im=ax1.plot(etime,yvalues,label="efieldx")
            yvalues=voltagex
            im=ax1.plot(vtime,yvalues,label="voltagex")

            #ax2=fig2.add_subplot(132)
            ax2.set_title('EW component',fontsize=12)            
            ax2.set_xlabel('time (ns)')
            #ax2.set_ylabel('Amplitude')        
            yvalues=efieldy
            im=ax2.plot(etime,yvalues,label="efieldy")
            yvalues=voltagey
            im=ax2.plot(vtime,yvalues,label="voltagey")

            #ax3=fig2.add_subplot(133)
            ax3.set_title('UD component',fontsize=12)
            ax3.set_xlabel('time (ns)')
            #ax3.set_ylabel('Amplitude')                                
            yvalues=efieldz
            im=ax3.plot(etime,yvalues,label="efieldz")
            yvalues=voltagez
            im=ax3.plot(vtime,yvalues,label="voltagez")

            plt.tight_layout() 
            plt.show()
            #end for antennas

        #End for events
    print("About to Close File")    
    infilehandle.Close()
    print("Closed")           


if __name__ == '__main__':

  if ( len(sys.argv)<1 ):
    print("usage PlotEventROOT inputfile])")

  if ( len(sys.argv)==2 ):
   inputfile=sys.argv[1]
   PlotEventOnROOT(inputfile)





