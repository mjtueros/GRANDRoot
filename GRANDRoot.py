import ROOT
import numpy as np

'''
The idea is to have at least 2 TTree per file section. One for event level information, and one for run level information
"Crosstalk" between sections should be minimized

RunLevel information should be in general only lenghty information common to all events, that makes not sense to repeat over and over: Array positions, AntennaModels, MeteoDatabases, etc 


EventLevel information should be as complete as possible to make event

'''
#############################################################################################################################################################################################################
#  SimShower Section
#############################################################################################################################################################################################################

#TODO: Think about what will be common in a run. Do we want to support runs with uneven thining? with uneven cuts? with uneven coordinate systems?. with different arrays? Probabbly not. Different dates, different atmopheres? maybe
#TODO: Should we do, along with the "CreateBranches" functions, a "FillBRanches function", where all variables are passed on the function call? 
#      This would acoomplish  things: 
#      a)make the file structure invisible to the user, and the script producing the files hopefully shorter
#      b)if a change is done on the CreateBranches (adding new, removing some, changing how things are stored), this is handled all inside of the GRANDRoot.py file.
#      c)Adding or removing parameters will change the "FillBranches" function, braking functions using them and forcing to update (which might not always be a happy thing)


# Create or Set rhe TTree branches for SimShower_Run (Simulated Showeer Run Level information )
def Setup_SimShowerRun_Branches(tree,create_branches=True):
    """
    Create or Set rhe TTree branches for SimShower_Run (Simulated Showeer Run Level information )

    Args:
        tree (string): a TTree
        create_branches (bool): toggles the branch creation on and off

    Returns:
        values: the current values for the branches
    """
    t = tree
    # Reset all branch addresses just in case
    t.ResetBranchAddresses()

    values = {"run_id": np.zeros(1, np.uint32),              #runID TODO: datatype. standarize. Do we want also a name or a short description? (so, a number and a string) # LWP: we need hardware/software information, because this can change over time. Looking at the stuff I coded for JEM-EUSO: experiment_name (GP300, GP10k, etc.), experiment_type (real, simulation), antenna_count?, antenna_type? (or more antenna information that can change in time), antenna_layout?, antenna_frequency_window?, firmware_vetsion?, hardware pieces versions, sampling, etc. MJT: Agreed. Some of this will also be duplicated on RawData Part.
              "shower_sim": ROOT.vector("string")(),         #simulation program (and version) used tosimulate the shower TODO: Standarize # LWP: I would move it to the ideas above. This tree will be common for real and simulated data, so specific simualtion field is probably not good . MJT: Not in this particular tree (SimShower)
              "origin_geoid": np.zeros(3, np.float32),       #origin of the coordinate system used for the array TODO: Standarize. Lat, Long, Altitude? smthing else is needed? Geoid?
              #TODO: Think about this. All this below is ZHAIRES specific. How to make it universal? Do we need to make it universal? Or can showers simulated with different simulators have different trees? If need to merge, turn branches off? # LWP: in JEM-EUSO we have a data tree common to simul/real data, an texp tree that contains experiment info common to simul/real, and a tsim which contains only simulator specific data. In case of real data, tsim is not in the file. MJT: Agreed. But again, this is the SimShower Tree.soo...here goes sim information...and some of it is simulator-specific.
              # do we want to have this in the event level instead?
              "rel_thin": np.zeros(1, np.float32),          #relative thinning energy
              "weight_factor": np.zeros(1, np.float32),     #weight factor
              "lowe_cut_e": np.zeros(1, np.float32),        #low energy cut for electrons(GeV) TODO: Check unit conventions
              "lowe_cut_gamma": np.zeros(1, np.float32),    #low energy cut for gammas(GeV) TODO: Check unit conventions
              "lowe_cut_mu": np.zeros(1, np.float32),       #low energy cut for muons(GeV) TODO: Check unit conventions
              "lowe_cut_meson": np.zeros(1, np.float32),    #low energy cut for mesons(GeV) TODO: Check unit conventions
              "lowe_cut_nucleon": np.zeros(1, np.float32)}  #low energy cut for nuceleons(GeV) TODO: Check unit conventions
            
    root_types = {"run_id": "/i",
                  "shower_sim": "/C", 
                  "origin_geoid": "[3]/F",
                  "rel_thin": "/F", 
                  "weight_factor": "/F", 
                  "lowe_cut_e": "/F", 
                  "lowe_cut_gamma": "/F", 
                  "lowe_cut_mu": "/F", 
                  "lowe_cut_meson": "/F", 
                  "lowe_cut_nucleon": "/F"}

    for key,val in values.items():
        if create_branches:
            # Vector branch
            if root_types[key]=="/C":
                t.Branch(key, val)
            # Scalar branch
            else:
                t.Branch(key, val, f"{key}{root_types[key]}")
        # If branches are reaccessed, just set their addresses
        else: 
            t.SetBranchAddress(key, val)
    return values
    
    
# Create or Set the TTree branches for SimShower (Simulated Shower Event Level information)
# TODO: LWP: used also for setting addresses if the tree exists - perhaps the name should be changed?
def Setup_SimShower_Branches(tree, create_branches=True):
    t = tree
    
    # Reset all branch addresses just in case
    t.ResetBranchAddresses()
    
    values = {"run_id": np.zeros(1, np.uint32),                  #runID TODO: datatype. standarize. Do we want also a name or a short description? (so, a number and a string) # LWP: I think this should just be a number, while some names and descriptions, as additional branches should be only in the run ttree MJT: Agreed
              "evt_id": np.zeros(1, np.uint32),                  #eventID TODO: datatype. standarize. Do we want also a name? (so, a number and a string) # LWP: If a name, I would add it also as a separate branch (but I doubt we would need it, more so for runs). MJT: Agreed. naming an event is weird...but i was more thinking if we need a string or an unsigned int. I dont know how we will identify the events yet.
              "shower_type":ROOT.vector("string")(),             #shower primary type: If single particle, particle type. If not...tau decay,etc. TODO: Standarize              
              "shower_energy": np.zeros(1, np.float32),          #shower energy (GeV)  Check unit conventions.
              "shower_azimuth": np.zeros(1, np.float32),         #shower azimuth TODO: Discuss coordinates Cosmic ray convention is bad for neutrinos, but neurtino convention is problematic for round earth. Also, geoid vs sphere problem
              "shower_zenith": np.zeros(1, np.float32),          #shower zenith  TODO: Discuss coordinates Cosmic ray convention is bad for neutrinos, but neurtino convention is problematic for round earth
              "shower_core_pos": np.zeros(4, np.float32),        #shower core position TODO: Coordinates in geoid?. Undefined for neutrinos.
              "rnd_seed": np.zeros(1, np.float64),               #random seed 
              "energy_in_neutrinos": np.zeros(1, np.float32),    #Energy in neutrinos generated in the shower (GeV). Usefull for invisible energy  
              "atmos_model": ROOT.vector("string")(),            #Atmospheric model name TODO:standarize
              "atmos_model_param": np.zeros(3, np.float32),      #Atmospheric model parameters: TODO: Think about this. Different models and softwares can have different parameters
              "magnetic_field": np.zeros(3, np.float32),         #Magnetic field parameters: Inclination, Declination, modulus. TODO: Standarize. Check units. Think about coordinates. Shower coordinates make sense.
              "date": ROOT.vector("string")(),                   #Event Date and time. TODO:standarize (date format, time format)
              "site": ROOT.vector("string")(),                   #Event Site: TODO: standarize
              "site_lat_long": np.zeros(2, np.float32),          #Site latitude and longitude (deg)  
              "ground_alt": np.zeros(1, np.float32),             #Ground Altitude (m)
              "prim_energy":np.zeros(1, np.float32),             #primary energy (GeV) TODO: Support multiple primaries. Check unit conventions. # LWP: Multiple primaries? I guess, variable count. Thus variable size array or a std::vector
              "prim_type": ROOT.vector("string")(),              #primary particle type TODO: Support multiple primaries. standarize (PDG?) 
              "prim_injpoint_shc": np.zeros(4, np.float32),      #primary injection point in Shower coordinates TODO: Support multiple primaries
              "prim_inj_alt_shc": np.zeros(1, np.float32),       #primary injection altitude in Shower Coordinates TODO: Support multiple primaries
              "prim_inj_dir_shc": np.zeros(3, np.float32),       #primary injection direction in Shower Coordinates  TODO: Support multiple primaries
              "xmax_grams": np.zeros(1, np.float32),             #shower Xmax depth  (g/cm2 along the shower axis)
              "xmax_pos_shc": np.zeros(3, np.float64),           #shower Xmax position in shower coordinates 
              "xmax_alt": np.zeros(1, np.float64),               #altitude of Xmax  (m, in the shower simulation earth. Its important for the index of refraction )
              "gh_fit_param": np.zeros(3, np.float32),           #X0,Xmax,Lambda (g/cm2) (3 parameter GH function fit to the longitudinal development of all particles)
              "hadronic_model": ROOT.vector("string")(),         #high energy hadronic model (and version) used TODO: standarize
              "low_energy_model": ROOT.vector("string")(),       #high energy model (and version) used TODO: standarize
              "cpu_time": np.zeros(3, np.float32)                #Time it took for the simulation. In the case shower and radio are simulated together, use TotalTime/(nant-1) as an approximation
             }
    root_types = {"run_id": "/i", 
                  "evt_id": "/i", 
                  "shower_type": "/C", 
                  "shower_energy": "/F",
                  "shower_azimuth": "/F",
                  "shower_zenith": "/F",
                  "shower_core_pos": "[4]/F",                  
                  "rnd_seed": "/D",
                  "energy_in_neutrinos": "/F",
                  "atmos_model": "/C",
                  "atmos_model_param": "[3]/F",
                  "magnetic_field": "[3]/F",
                  "date": "/C",
                  "site": "/C",
                  "site_lat_long": "[2]/F",                  
                  "ground_alt": "/F",
                  "prim_energy": "/F",   
                  "prim_type": "/C",                  
                  "prim_injpoint_shc": "[4]/F",
                  "prim_inj_alt_shc": "/F",
                  "prim_inj_dir_shc": "[3]/F",
                  "xmax_grams": "/F",
                  "xmax_pos_shc": "[3]/D",
                  "xmax_alt": "/D",
                  "gh_fit_param": "[3]/F",
                  "hadronic_model": "/C",
                  "low_energy_model": "/C",
                  "cpu_time": "[3]/F"
                 }
    
    for key,val in values.items():
        # If the branches are created for the first time
        if create_branches:
            # Vector branch
            if root_types[key]=="/C":
                t.Branch(key, val) #TODO: Do we need this? We will be accesing already using SimShower.run_id # LWP: this was only for the initial case of converting from HDF5, where there were several datasets with the same name under Event, and I put them all into the same TTre. If names do not repeat in the TTree, no need.
            # Scalar branch
            else:
                t.Branch(key, val, f"{key}{root_types[key]}")
        # If branches are reaccessed, just set their addresses
        else:
            t.SetBranchAddress(key, val)
    return values    

##################################################################################################################################################################################################################
# SimEfield section
##################################################################################################################################################################################################################
#TODO: Think about what will be common in a run. Do we want to support runs with uneven field simulators? probabbly not? uneven refractivity models? maybe not uneven parameters...probabbly yes!
              
# Create or Set the  TTree branches for SimEfield (Simulated Electric Field Event Level Information)
def Setup_SimEfield_Branches(tree, create_branches=True):
    t = tree
   # Reset all branch addresses just in case
    t.ResetBranchAddresses()


    values = {"run_id": np.zeros(1, np.uint32),                  #runID TODO: datatype. standarize. Do we want also a name or a short description? (so, a number and a string)
              "evt_id": np.zeros(1, np.uint32),                  #eventID TODO: datatype. standarize. Do we want also a name? (so, a number and a string)                                                                         
              "field_sim": ROOT.vector("string")(),              #name and model of the electric field simulator. TODO: Standarize  
              "refractivity_model": ROOT.vector("string")(),     #name of the atmospheric index of refraction model. TODO:Standarize  
              "refractivity_param": np.zeros(2, np.float32),     #parameters of the atmospheric index of refraction model. TODO: Standarize. Think how to support different model needs. 
              "t_pre":np.zeros(1, np.float32),                   #The antenna time window is defined arround a t0 that changes with the antenna, starts on t0+t_pre (thus t_pre is usually negative) and ends on t0+post
              "t_post":np.zeros(1, np.float32),                  #TODO: Should we support different antenna trace sizes? Currently its not posible. If that is the case, should t_pre,t_post and t_bin_size be on SimEfieldRun?
              "t_bin_size":np.zeros(1, np.float32)
             }
    root_types = {"run_id": "/i", 
                  "evt_id": "/i",
                  "field_sim": "/C",
                  "refractivity_model": "/C",
                  "refractivity_param": "[2]/F",
                  "t_pre":"/F",
                  "t_post":"/F",
                  "t_bin_size":"/F", 
                 }

    for key,val in values.items():
     # If the branches are created for the first time
     if create_branches:
       # Vector branch
       if root_types[key]=="/C" or root_types[key]=="vec":
         t.Branch(key, val)
         print("set",key,val)
         # Scalar branch
       else:
         t.Branch(key, val, f"{key}{root_types[key]}")
         print("set2",key,val)
    # If branches are reaccessed, just set their addresses
     else:
       t.SetBranchAddress(key, val)            
    return values    
    
# Create or Set the TTree branches for SimEfield.Detector (Simulated Electric Field Detector level information)
def Setup_SimEfieldDetector_Branches(tree, create_branches=True):
    t = tree

   # Reset all branch addresses just in case
    #t.ResetBranchAddresses()  it was reset in the Setup_SimSignal_Branches call. TODO: Merge both functions

    values = {"det_id": ROOT.vector("int")(),        #TODO: Standarize the ID of antennas. Do we Want a number? A string? both (ID and Name). This will/should be linked to the RunInfo, where some detector configuration should reside.
              "det_type": ROOT.vector("vector<string>")(),             #TODO: This is a candidate to be in the SimEfieldRun
              "det_pos_shc": ROOT.vector("vector<float>")(),   #Detector positions in shower coordinates? TODO: How To define shower coordinates?. The only thing common to both neutrinos and cosmic rays is the injection point.
              "t_0": ROOT.vector("float")(),           #Time window t0
              "p2p": ROOT.vector("float")(),           #peak 2 peak amplitudes (x,y,z,modulus). TODO: Hillbert envelope quantities 
              "trace_x":ROOT.vector("vector<float>")(),        #TODO: I would like to store the three channels
              "trace_y":ROOT.vector("vector<float>")(),
              "trace_z":ROOT.vector("vector<float>")()
              }
    root_types = {"det_id": "vec", 
                  "det_type": "vec", 
                  "det_pos_shc": "vec",                   
                  "t_0": "vec", 
                  "p2p": "vec", 
                  "trace_x":"vec",
                  "trace_y":"vec",
                  "trace_z":"vec"                                    
                  }
    #print("create_branches",create_branches)
    for key,val in values.items():
      # If the branches are created for the first time
      if create_branches:
        # Vector branch        
        if root_types[key]=="/C" or root_types[key]=="vec":
          #print(key,val) 	
          t.Branch("Detectors_"+key, val)
        # Scalar branch
        else:
          #print("key",key,val)
          t.Branch("Detectors_"+key, val, f"{key}{root_types[key]}")
      #If branches are reaccessed, just set their addresses
      else:
        t.SetBranchAddress("Detectors_"+key, val)
    return values 
     


##################################################################################################################################################################################################################
# SimSignal section (The Voltage at the terminals of the antenna)
##################################################################################################################################################################################################################
#TODO: Think about what will be common in a run. Do we want to support runs with uneven field simulators? probabbly not? uneven refractivity models? maybe not uneven parameters...probabbly yes!
              
# Create or Set TTree branches for SimSignal_Run (Simulated Signal Run Level information)
def Setup_SimSignalRun_Branches(tree,create_branches=True):
    t = tree

   # Reset all branch addresses just in case
    t.ResetBranchAddresses()

    values = {"run_id": np.zeros(1, np.uint32)}                 #runID TODO: define datatype. standarize. Do we want also a name or a short description? (so, a number and a string)
    root_types = {"run_id": "/i"}    
    
    for key,val in values.items():
      # If the branches are created for the first time
      if create_branches:
        # Vector branch
        if root_types[key]=="/C":
            t.Branch(key, val)
        # Scalar branch
        else:
            t.Branch(key, val, f"{key}{root_types[key]}")
      #If branches are reaccessed, just set their addresses
      else:
        t.SetBranchAddress(key, val)    
    return values    
    
# Create or Set the TTree branches for SimSignal (Simulated Signal Event Level Information)
def Setup_SimSignal_Branches(tree,create_branches=True):
    t = tree

   # Reset all branch addresses just in case
    t.ResetBranchAddresses()

    values = {"run_id": np.zeros(1, np.uint32),                  #runID TODO: define datatype. standarize. Do we want also a name or a short description? (so, a number and a string)
              "evt_id": np.zeros(1, np.uint32),                  #eventID TODO: define datatype. standarize. Do we want also a name? (so, a number and a string)                                                                         
              "signal_sim": ROOT.vector("string")(),             #name and model of the signal simulator. TODO: Standarize  
             }
    root_types = {"run_id": "/i", 
                  "evt_id": "/i",
                  "signal_sim": "/C",
                 }

    for key,val in values.items():
      # If the branches are created for the first time
      if create_branches:
        # Vector branch
        if root_types[key]=="/C":
            t.Branch(key, val)
        # Scalar branch
        else:
            t.Branch(key, val, f"{key}{root_types[key]}")
      #If branches are reaccessed, just set their addresses
      else:
        t.SetBranchAddress(key, val)
    return values    
    
# Create or Set the TTree branches for SimSignal.Detector (Simulated Signal Detector Level Information)
def Setup_SimSignalDetector_Branches(tree,create_branches=True):                   #TODO: Decide if the "detectorbranches should be standarized (currenlty SimEfield and SimSignal are identical..)"
    t = tree

   # Reset all branch addresses just in case
   # t.ResetBranchAddresses() it was reset in the Setup_SimSignal_Branches call. TODO: Merge both functions
                  

    values = {"det_id": ROOT.vector("int")(),        #TODO: Standarize the ID of antennas. Do we Want a number? A string? both (ID and Name). This will/should be linked to the RunInfo, where some detector configuration should reside.
              "det_type": ROOT.vector("vector<string>")(),             #TODO: This is a candidate to be in the SimEfieldRun
              "det_pos_shc": ROOT.vector("vector<float>")(),   #Detector positions in shower coordinates? TODO: How To define shower coordinates?. The only thing common to both neutrinos and cosmic rays is the injection point.
              "t_0": ROOT.vector("float")(),           #Time window t0
              "p2p": ROOT.vector("float")(),           #peak 2 peak amplitudes (x,y,z,modulus). TODO: Hillbert envelope quantities 
              "trace_x":ROOT.vector("vector<float>")(),        #TODO: I would like to store the three channels
              "trace_y":ROOT.vector("vector<float>")(),
              "trace_z":ROOT.vector("vector<float>")()
              }
    root_types = {"det_id": "vec", 
                  "det_type": "vec", 
                  "det_pos_shc": "vec",                   
                  "t_0": "vec", 
                  "p2p": "vec", 
                  "trace_x":"vec",
                  "trace_y":"vec",
                  "trace_z":"vec"                                    
                  }                  
                  

    for key,val in values.items():
      # If the branches are created for the first time
      if create_branches:
        # Vector branch
        if root_types[key]=="/C" or root_types[key]=="vec":
            t.Branch("Detectors_"+key, val)
        # Scalar branch
        else:
            t.Branch("Detectors_"+key, val, f"{key}{root_types[key]}")
      #If branches are reaccessed, just set their addresses
      else:
        t.SetBranchAddress("Detectors_"+key, val)
    return values
    
