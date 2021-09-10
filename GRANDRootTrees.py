# Classes to handle exchange of information between user and ROOT TTrees holding Zhaires simulation data

import ROOT
import numpy as np
import collections
from dataclasses import dataclass, field
from typing import List, Union


# A python list interface to ROOT's std::vector
class StdVectorList(collections.MutableSequence):
    def __init__(self, vec_type, value=[]):
        self.vector = ROOT.vector(vec_type)(value)

    def __len__(self):
        return self.vector.size()

    def __delitem__(self, index):
        self.vector.erase(index)

    def insert(self, index, value):
        self.vector.insert(index, value)

    def __setitem__(self, index, value):
        self.vector[index] = value

    def __getitem__(self, index):
        return self.vector[index]

    def append(self, value):
        # std::vector does not want numpy types for push_back, need to use .item()
        if isinstance(value, np.generic):
            self.vector.push_back(value.item())
        else:
            self.vector.push_back(value)

    def clear(self):
        self.vector.clear()

    def __repr__(self):
        return str(list(self.vector))

# Mother class for GRAND Tree data classes
@dataclass
class GRANDDataTree:
    _file: ROOT.TFile = None
    _tree_name: str = ""
    _tree: ROOT.TTree = ROOT.TTree(_tree_name, _tree_name)

    _run_id: np.ndarray = np.zeros(1, np.uint32)
    _evt_id: np.ndarray = np.zeros(1, np.uint32)

    @property
    def tree(self):
        return self._tree

    @property
    def file(self):
        return self._file

    def __post_init__(self):
        # Work only if _file was specified
        if self._file is None:
            return 0
        # TFile was given
        if type(self._file) is ROOT.TFile:
            # Try to init with the TTree from this file
            try:
                self._tree = self._file.Get(self._tree_name)
            except:
                print(f"No valid {self._tree_name} TTree in the file {self._file.GetName()}")
        # String was given
        elif type(self._file) is str:
            # Check if this is a valid TFile
            try:
                # For now, open in read/only
                # ToDo: How to make secure read/write open?
                self._file = ROOT.TFile(self._file, "read")
                # Try to init with the TTree from this file
                try:
                    self._tree = self._file.Get(self._tree_name)
                except:
                    print(f"No valid {self._tree_name} TTree in the file {self._file}")
            except:
                print(f"The file {self._file} either does not exist or is not a valid ROOT file")

    @property
    def run_id(self):
        return self._run_id[0]

    @run_id.setter
    def run_id(self, val: np.uint32) -> None:
        self._run_id[0] = val

    @property
    def evt_id(self):
        return self._evt_id[0]

    @evt_id.setter
    def evt_id(self, val: np.uint32) -> None:
        self._evt_id[0] = val

    def Fill(self):
        self._tree.Fill()

    def Write(self, *args):
        self._tree.Write(*args)

    def Scan(self, *args):
        self._tree.Scan(*args)

    def GetEvent(self, ev_no):
        self._tree.GetEntry(ev_no)
        # print(self.__dataclass_fields__)
        for field in self.__dataclass_fields__:
            # Skip "tree" and "file" fields, as they are not the part of the stored data
            if field == "_tree" or field == "_file" or field == "_tree_name": continue
            # print(field, self.__dataclass_fields__[field])
            u = getattr(self._tree, field[1:])
            print(self.__dataclass_fields__[field].name, u, type(u))
            setattr(self, field[1:], u)

    def GetEntry(self, ev_no):
        self.GetEvent(ev_no)

    # All three methods below return the number of entries
    def GetEntries(self):
        return self._tree.GetEntries()

    def GetNumberOfEntries(self):
        return self.GetEntries()

    def GetNumberOfEvents(self):
        return self.GetNumberOfEntries()

    def AddFriend(self, value):
        self._tree.AddFriend(value)

    def RemoveFriend(self, value):
        self._tree.RemoveFriend(value)

    def BuildIndex(self, run_id, evt_id):
        self._tree.BuildIndex(run_id, evt_id)

    def SetTreeIndex(self, value):
        self._tree.SetTreeIndex(value)

    # Create branches of the TTree based on the class fields
    def CreateBranches(self):
        # Reset all branch addresses just in case
        self._tree.ResetBranchAddresses()

        # Loop through the class fields
        for field in self.__dataclass_fields__:
            # Skip "tree" and "file" fields, as they are not the part of the stored data
            if field == "_tree" or field == "_file" or field == "_tree_name": continue
            # Create a branch for the field
            self.CreateBranchFromField(self.__dataclass_fields__[field])

    # Create a specific branch of a TTree computing its type from the corresponding class field
    def CreateBranchFromField(self, value):
        # Handle numpy arrays
        if isinstance(value.default, np.ndarray):
            # Generate ROOT TTree data type string

            # Array size or lack of it
            if value.default.ndim == 1:
                val_type = "/"
            else:
                val_type = f"[{value.default.ndim}]/"

            # Data type
            if value.default.dtype == np.int8:
                val_type = "/B"
            elif value.default.dtype == np.uint8:
                val_type = "/b"
            elif value.default.dtype == np.int16:
                val_type = "/S"
            elif value.default.dtype == np.uint16:
                val_type = "/s"
            elif value.default.dtype == np.int32:
                val_type = "/I"
            elif value.default.dtype == np.uint32:
                val_type = "/i"
            elif value.default.dtype == np.int64:
                val_type = "/L"
            elif value.default.dtype == np.uint64:
                val_type = "/l"
            elif value.default.dtype == np.float32:
                val_type = "/F"
            elif value.default.dtype == np.float64:
                val_type = "/D"
            elif value.default.dtype == np.bool_:
                val_type = "/O"

            # Create the branch
            self._tree.Branch(value.name[1:], getattr(self, value.name), value.name[1:] + val_type)
        # ROOT vectors as StdVectorList
        # elif "vector" in str(type(value.default)):
        elif isinstance(value.type, StdVectorList):
            # Create the branch
            self._tree.Branch(value.name[1:], getattr(self, value.name).vector)
        else:
            print(f"Unsupported type {value.type}")
            exit()


@dataclass
class SimShowerTree(GRANDDataTree):
    _tree_name: str = "SimShower"

    _shower_type: StdVectorList("string") = StdVectorList("string")  # shower primary type: If single particle, particle type. If not...tau decay,etc. TODO: Standarize
    _shower_energy: np.ndarray = np.zeros(1, np.float32)  # shower energy (GeV)  Check unit conventions.
    _shower_azimuth: np.ndarray = np.zeros(1, np.float32)  # shower azimuth TODO: Discuss coordinates Cosmic ray convention is bad for neutrinos, but neurtino convention is problematic for round earth. Also, geoid vs sphere problem
    _shower_zenith: np.ndarray = np.zeros(1, np.float32)  # shower zenith  TODO: Discuss coordinates Cosmic ray convention is bad for neutrinos, but neurtino convention is problematic for round earth
    _shower_core_pos: np.ndarray = np.zeros(4, np.float32)  # shower core position TODO: Coordinates in geoid?. Undefined for neutrinos.
    _rnd_seed: np.ndarray = np.zeros(1, np.float64)  # random seed
    _energy_in_neutrinos: np.ndarray = np.zeros(1, np.float32)  # Energy in neutrinos generated in the shower (GeV). Usefull for invisible energy
    _atmos_model: StdVectorList("string") = StdVectorList("string")  # Atmospheric model name TODO:standarize
    _atmos_model_param: np.ndarray = np.zeros(3, np.float32)  # Atmospheric model parameters: TODO: Think about this. Different models and softwares can have different parameters
    _magnetic_field: np.ndarray = np.zeros(3, np.float32)  # Magnetic field parameters: Inclination, Declination, modulus. TODO: Standarize. Check units. Think about coordinates. Shower coordinates make sense.
    _date: StdVectorList("string") = StdVectorList("string")  # Event Date and time. TODO:standarize (date format, time format)
    _site: StdVectorList("string") = StdVectorList("string")  # Event Site: TODO: standarize
    _site_lat_long: np.ndarray = np.zeros(2, np.float32)  # Site latitude and longitude (deg)
    _ground_alt: np.ndarray = np.zeros(1, np.float32)  # Ground Altitude (m)
    _prim_energy: np.ndarray = np.zeros(1, np.float32)  # primary energy (GeV) TODO: Support multiple primaries. Check unit conventions. # LWP: Multiple primaries? I guess, variable count. Thus variable size array or a std::vector
    _prim_type: StdVectorList("string") = StdVectorList("string")  # primary particle type TODO: Support multiple primaries. standarize (PDG?)
    _prim_injpoint_shc: np.ndarray = np.zeros(4, np.float32)  # primary injection point in Shower coordinates TODO: Support multiple primaries
    _prim_inj_alt_shc: np.ndarray = np.zeros(1, np.float32)  # primary injection altitude in Shower Coordinates TODO: Support multiple primaries
    _prim_inj_dir_shc: np.ndarray = np.zeros(3, np.float32)  # primary injection direction in Shower Coordinates  TODO: Support multiple primaries
    _xmax_grams: np.ndarray = np.zeros(1, np.float32)  # shower Xmax depth  (g/cm2 along the shower axis)
    _xmax_pos_shc: np.ndarray = np.zeros(3, np.float64)  # shower Xmax position in shower coordinates
    _xmax_alt: np.ndarray = np.zeros(1, np.float64)  # altitude of Xmax  (m, in the shower simulation earth. Its important for the index of refraction )
    _gh_fit_param: np.ndarray = np.zeros(3, np.float32)  # X0,Xmax,Lambda (g/cm2) (3 parameter GH function fit to the longitudinal development of all particles)
    _hadronic_model: StdVectorList("string") = StdVectorList("string")  # high energy hadronic model (and version) used TODO: standarize
    _low_energy_model: StdVectorList("string") = StdVectorList("string")  # high energy model (and version) used TODO: standarize
    _cpu_time: np.ndarray = np.zeros(3, np.float32)  # Time it took for the simulation. In the case shower and radio are simulated together, use TotalTime/(nant-1) as an approximation

    def __post_init__(self):
        super().__post_init__()

        if self._tree.GetName() == "":
            self._tree.SetName(self._tree_name)
        if self._tree.GetTitle() == "":
            self._tree.SetTitle(self._tree_name)

        self.CreateBranches()

    @property
    def shower_type(self):
        return self._shower_type

    @shower_type.setter
    def shower_type(self, value):
        # Clear the vector before setting
        self._shower_type.clear()

        # A list of strings was given
        if isinstance(value, list):
            self._shower_type += value
        # A vector of strings was given
        elif isinstance(value, ROOT.vector("string")):
            self._shower_type = value
        else:
            exit(f"Incorrect type for shower_type {type(value)}. Either a list or a ROOT.vector of strings required.")

    @property
    def shower_energy(self):
        return self._shower_energy[0]

    @shower_energy.setter
    def shower_energy(self, value):
        self._shower_energy[0] = value

    @property
    def shower_azimuth(self):
        return self._shower_azimuth[0]

    @shower_azimuth.setter
    def shower_azimuth(self, value):
        self._shower_azimuth[0] = value

    @property
    def shower_zenith(self):
        return self._shower_zenith[0]

    @shower_zenith.setter
    def shower_zenith(self, value):
        self._shower_zenith[0] = value

    @property
    def shower_core_pos(self):
        return np.array(self._shower_core_pos)

    @shower_core_pos.setter
    def shower_core_pos(self, value):
        self._shower_core_pos = np.array(value)
        self._tree.SetBranchAddress("shower_core_pos", self._shower_core_pos)

    @property
    def rnd_seed(self):
        return self._rnd_seed[0]

    @rnd_seed.setter
    def rnd_seed(self, value):
        self._rnd_seed[0] = value

    @property
    def energy_in_neutrinos(self):
        return self._energy_in_neutrinos[0]

    @energy_in_neutrinos.setter
    def energy_in_neutrinos(self, value):
        self._energy_in_neutrinos[0] = value

    @property
    def atmos_model(self):
        return self._atmos_model

    @atmos_model.setter
    def atmos_model(self, value):
        # Clear the vector before setting
        self._atmos_model.clear()

        # A list of strings was given
        if isinstance(value, list):
            self._atmos_model += value
        # A vector of strings was given
        elif isinstance(value, ROOT.vector("string")):
            self._atmos_model = value
        else:
            exit(f"Incorrect type for atmos_model {type(value)}. Either a list or a ROOT.vector of strings required.")

    @property
    def atmos_model_param(self):
        return np.array(self._atmos_model_param)

    @atmos_model_param.setter
    def atmos_model_param(self, value):
        self._atmos_model_param = np.array(value)
        self._tree.SetBranchAddress("atmos_model_param", self._atmos_model_param)

    @property
    def magnetic_field(self):
        return np.array(self._magnetic_field)

    @magnetic_field.setter
    def magnetic_field(self, value):
        self._magnetic_field = np.array(value)
        self._tree.SetBranchAddress("magnetic_field", self._magnetic_field)

    @property
    def date(self):
        return self._date

    @date.setter
    def date(self, value):
        # Clear the vector before setting
        self._date.clear()

        # A list of strings was given
        if isinstance(value, list):
            self._date += value
        # A vector of strings was given
        elif isinstance(value, ROOT.vector("string")):
            self._date = value
        else:
            exit(f"Incorrect type for date {type(value)}. Either a list or a ROOT.vector of strings required.")

    @property
    def site(self):
        return self._site

    @site.setter
    def site(self, value):
        # Clear the vector before setting
        self._site.clear()

        # A list of strings was given
        if isinstance(value, list):
            self._site += value
        # A vector of strings was given
        elif isinstance(value, ROOT.vector("string")):
            self._site = value
        else:
            exit(f"Incorrect type for site {type(value)}. Either a list or a ROOT.vector of strings required.")

    @property
    def site_lat_long(self):
        return np.array(self._site_lat_long)

    @site_lat_long.setter
    def site_lat_long(self, value):
        self._site_lat_long = np.array(value)
        self._tree.SetBranchAddress("site_lat_long", self._site_lat_long)

    @property
    def ground_alt(self):
        return self._ground_alt[0]

    @ground_alt.setter
    def ground_alt(self, value):
        self._ground_alt[0] = value

    @property
    def prim_energy(self):
        return self._prim_energy[0]

    @prim_energy.setter
    def prim_energy(self, value):
        self._prim_energy[0] = value

    @property
    def prim_type(self):
        return self._prim_type

    @prim_type.setter
    def prim_type(self, value):
        # Clear the vector before setting
        self._prim_type.clear()

        # A list of strings was given
        if isinstance(value, list):
            self._prim_type += value
        # A vector of strings was given
        elif isinstance(value, ROOT.vector("string")):
            self._prim_type = value
        else:
            exit(f"Incorrect type for prim_type {type(value)}. Either a list or a ROOT.vector of strings required.")

    @property
    def prim_injpoint_shc(self):
        return np.array(self._prim_injpoint_shc)

    @prim_injpoint_shc.setter
    def prim_injpoint_shc(self, value):
        self._prim_injpoint_shc = np.array(value)
        self._tree.SetBranchAddress("prim_injpoint_shc", self._prim_injpoint_shc)

    @property
    def prim_inj_alt_shc(self):
        return self._prim_inj_alt_shc[0]

    @prim_inj_alt_shc.setter
    def prim_inj_alt_shc(self, value):
        self._prim_inj_alt_shc[0] = value

    @property
    def prim_inj_dir_shc(self):
        return np.array(self._prim_inj_dir_shc)

    @prim_inj_dir_shc.setter
    def prim_inj_dir_shc(self, value):
        self._prim_inj_dir_shc = np.array(value)
        self._tree.SetBranchAddress("prim_inj_dir_shc", self._prim_inj_dir_shc)

    @property
    def xmax_grams(self):
        return self._xmax_grams[0]

    @xmax_grams.setter
    def xmax_grams(self, value):
        self._xmax_grams[0] = value

    @property
    def xmax_pos_shc(self):
        return np.array(self._xmax_pos_shc)

    @xmax_pos_shc.setter
    def xmax_pos_shc(self, value):
        self._xmax_pos_shc = np.array(value)
        self._tree.SetBranchAddress("xmax_pos_shc", self._xmax_pos_shc)

    @property
    def xmax_alt(self):
        return self._xmax_alt[0]

    @xmax_alt.setter
    def xmax_alt(self, value):
        self._xmax_alt[0] = value

    @property
    def gh_fit_param(self):
        return np.array(self._gh_fit_param)

    @gh_fit_param.setter
    def gh_fit_param(self, value):
        self._gh_fit_param = np.array(value)
        self._tree.SetBranchAddress("gh_fit_param", self._gh_fit_param)

    @property
    def hadronic_model(self):
        return self._hadronic_model

    @hadronic_model.setter
    def hadronic_model(self, value):
        # Clear the vector before setting
        self._hadronic_model.clear()

        # A list of strings was given
        if isinstance(value, list):
            self._hadronic_model += value
        # A vector of strings was given
        elif isinstance(value, ROOT.vector("string")):
            self._hadronic_model = value
        else:
            exit(f"Incorrect type for hadronic_model {type(value)}. Either a list or a ROOT.vector of strings required.")

    @property
    def low_energy_model(self):
        return self._low_energy_model

    @low_energy_model.setter
    def low_energy_model(self, value):
        # Clear the vector before setting
        self._low_energy_model.clear()

        # A list of strings was given
        if isinstance(value, list):
            self._low_energy_model += value
        # A vector of strings was given
        elif isinstance(value, ROOT.vector("string")):
            self._low_energy_model = value
        else:
            exit(f"Incorrect type for low_energy_model {type(value)}. Either a list or a ROOT.vector of strings required.")

    @property
    def cpu_time(self):
        return np.array(self._cpu_time)

    @cpu_time.setter
    def cpu_time(self, value):
        self._cpu_time = np.array(value)
        self._tree.SetBranchAddress("cpu_time", self._cpu_time)


@dataclass
class SimSignalTree(GRANDDataTree):
    _tree_name: str = "SimSignal"

    # _signal_sim: ROOT.vector("string") = ROOT.vector("string")()
    _signal_sim: StdVectorList("string") = StdVectorList("string")

    _det_id: StdVectorList("int") = StdVectorList("int")
    # TODO: Standarize the ID of antennas. Do we Want a number? A string? both (ID and Name). This will/should be linked to the RunInfo, where some detector configuration should reside.
    _det_type: StdVectorList("vector<string>") = StdVectorList("vector<string>")  # TODO: This is a candidate to be in the SimEfieldRun
    _det_pos_shc: StdVectorList("vector<float>") = StdVectorList("vector<float>")
    # Detector positions in shower coordinates? TODO: How To define shower coordinates?. The only thing common to both neutrinos and cosmic rays is the injection point.
    _t_0: StdVectorList("float") = StdVectorList("float")  # Time window t0
    _p2p: StdVectorList("float") = StdVectorList("float")
    # peak 2 peak amplitudes (x,y,z,modulus). TODO: Hillbert envelope quantities
    _trace_x: StdVectorList("vector<float>") = StdVectorList("vector<float>")  # TODO: I would like to store the three channels
    _trace_y: StdVectorList("vector<float>") = StdVectorList("vector<float>")
    _trace_z: StdVectorList("vector<float>") = StdVectorList("vector<float>")

    def __post_init__(self):
        super().__post_init__()

        if self._tree.GetName()=="":
            self._tree.SetName(self._tree_name)
        if self._tree.GetTitle() == "":
            self._tree.SetTitle(self._tree_name)

        self.CreateBranches()

    @property
    def signal_sim(self):
        return self._signal_sim

    @signal_sim.setter
    def signal_sim(self, value: Union[List[str], ROOT.vector("string")]) -> None:
        # Clear the vector before setting
        self._signal_sim.clear()

        # A list of strings was given
        if isinstance(value, list):
            self._signal_sim += value
        # A vector of strings was given
        elif isinstance(value, ROOT.vector("string")):
            self._signal_sim = StdVectorList("string", value)
        else:
            exit(f"Incorrect type for field_sim {type(value)}. Either a list or a ROOT.vector of strings required.")

    @property
    def det_id(self):
        return self._det_id

    @det_id.setter
    def det_id(self, value):
        # Clear the vector before setting
        self._det_id.clear()

        # A list of strings was given
        if isinstance(value, list) or isinstance(value, np.ndarray):
            self._det_id += value
        # A vector was given
        elif isinstance(value, ROOT.vector("int")):
            self._det_id = value
        else:
            exit(f"Incorrect type for det_id {type(value)}. Either a list, an array or a ROOT.vector of ints required.")

    @property
    def det_type(self):
        return self._det_type

    @det_type.setter
    def det_type(self, value):
        # Clear the vector before setting
        self._det_type.clear()

        # A list of lists of strings was given
        if isinstance(value, list):
            self._det_type += value
        # A vector of vector of strings was given
        elif isinstance(value, ROOT.vector("vector<string>")):
            self._det_type = value
        else:
            exit(f"Incorrect type for det_type {type(value)}. Either a list of lists or a ROOT.vector of vectors of strings required.")

    @property
    def det_pos_shc(self):
        return self._det_pos_shc

    @det_pos_shc.setter
    def det_pos_shc(self, value):
        # Clear the vector before setting
        self._det_pos_shc.clear()

        # A list was given
        if isinstance(value, list) or isinstance(value, np.ndarray):
            self._det_pos_shc += value
        # A vector of strings was given
        elif isinstance(value, ROOT.vector("vector<float>")):
            self._det_pos_shc = value
        else:
            exit(f"Incorrect type for det_pos_shc {type(value)}. Either a list, an array or a ROOT.vector of vector<float> required.")

    @property
    def t_0(self):
        return self._t_0

    @t_0.setter
    def t_0(self, value):
        # Clear the vector before setting
        self._t_0.clear()

        # A list was given
        if isinstance(value, list) or isinstance(value, np.ndarray):
            self._t_0 += value
        # A vector of strings was given
        elif isinstance(value, ROOT.vector("float")):
            self._t_0 = value
        else:
            exit(f"Incorrect type for t_0 {type(value)}. Either a list, an array or a ROOT.vector of float required.")

    @property
    def p2p(self):
        return self._p2p

    @p2p.setter
    def p2p(self, value):
        # Clear the vector before setting
        self._p2p.clear()

        # A list was given
        if isinstance(value, list) or isinstance(value, np.ndarray):
            self._p2p += value
        # A vector of strings was given
        elif isinstance(value, ROOT.vector("float")):
            self._p2p = value
        else:
            exit(f"Incorrect type for p2p {type(value)}. Either a list, an array or a ROOT.vector of float required.")

    @property
    def trace_x(self):
        return self._trace_x

    @trace_x.setter
    def trace_x(self, value):
        # Clear the vector before setting
        self._trace_x.clear()

        # A list was given
        if isinstance(value, list) or isinstance(value, np.ndarray):
            self._trace_x += value
        # A vector of strings was given
        elif isinstance(value, ROOT.vector("vector<float>")):
            self._trace_x = value
        else:
            exit(f"Incorrect type for trace_x {type(value)}. Either a list, an array or a ROOT.vector of vector<float> required.")

    @property
    def trace_y(self):
        return self._trace_y

    @trace_y.setter
    def trace_y(self, value):
        # Clear the vector before setting
        self._trace_y.clear()

        # A list was given
        if isinstance(value, list) or isinstance(value, np.ndarray):
            self._trace_y += value
        # A vector of strings was given
        elif isinstance(value, ROOT.vector("vector<float>")):
            self._trace_y = value
        else:
            exit(f"Incorrect type for trace_y {type(value)}. Either a list, an array or a ROOT.vector of float required.")

    @property
    def trace_z(self):
        return self._trace_z

    @trace_z.setter
    def trace_z(self, value):
        # Clear the vector before setting
        self._trace_z.clear()

        # A list was given
        if isinstance(value, list) or isinstance(value, np.ndarray):
            self._trace_z += value
        # A vector of strings was given
        elif isinstance(value, ROOT.vector("vector<float>")):
            self._trace_z = value
        else:
            exit(f"Incorrect type for trace_z {type(value)}. Either a list, an array or a ROOT.vector of float required.")


@dataclass
class SimEfieldTree(GRANDDataTree):
    _tree_name: str = "SimEfield"

    # Internally they are vectors, but for the user wil be list of strings
    _field_sim: StdVectorList("string") = StdVectorList("string")
    _refractivity_model: StdVectorList("string") = StdVectorList("string")
    _refractivity_param: np.ndarray = np.zeros(2, np.float32)
    _t_pre: np.ndarray = np.zeros(1, np.float32)
    _t_post: np.ndarray = np.zeros(1, np.float32)
    _t_bin_size: np.ndarray = np.zeros(1, np.float32)

    # Detector branches
    _det_id: StdVectorList("int") = StdVectorList("int")
    # TODO: Standarize the ID of antennas. Do we Want a number? A string? both (ID and Name). This will/should be linked to the RunInfo, where some detector configuration should reside.
    _det_type: StdVectorList("vector<string>") = StdVectorList("vector<string>")  # TODO: This is a candidate to be in the SimEfieldRun
    _det_pos_shc: StdVectorList("vector<float>") = StdVectorList("vector<float>")
    # Detector positions in shower coordinates? TODO: How To define shower coordinates?. The only thing common to both neutrinos and cosmic rays is the injection point.
    _t_0: StdVectorList("float") = StdVectorList("float")  # Time window t0
    _p2p: StdVectorList("float") = StdVectorList("float")
    # peak 2 peak amplitudes (x,y,z,modulus). TODO: Hillbert envelope quantities
    _trace_x: StdVectorList("vector<float>") = StdVectorList("vector<float>")  # TODO: I would like to store the three channels
    _trace_y: StdVectorList("vector<float>") = StdVectorList("vector<float>")
    _trace_z: StdVectorList("vector<float>") = StdVectorList("vector<float>")

    def __post_init__(self):
        super().__post_init__()

        if self._tree.GetName() == "":
            self._tree.SetName(self._tree_name)
        if self._tree.GetTitle() == "":
            self._tree.SetTitle(self._tree_name)

        self.CreateBranches()

    @property
    def field_sim(self):
        return self._field_sim

    @field_sim.setter
    def field_sim(self, val: Union[List[str], ROOT.vector("string")]) -> None:
        # Clear the vector before setting
        self._field_sim.clear()

        # A list of strings was given
        if isinstance(val, list):
            self._field_sim += val
        # A vector of strings was given
        elif isinstance(val, ROOT.vector("string")):
            self._field_sim = val
        else:
            exit(f"Incorrect type for field_sim {type(val)}. Either a list or a ROOT.vector of strings required.")

    @property
    def refractivity_model(self):
        return self._refractivity_model

    @refractivity_model.setter
    def refractivity_model(self, val: Union[List[str], ROOT.vector("string")]) -> None:
        # Clear the vector before setting
        self._refractivity_model.clear()

        # A list of strings was given
        if isinstance(val, list):
            self._refractivity_model += val
        # A vector of strings was given
        elif isinstance(val, ROOT.vector("string")):
            self._refractivity_model = val
        else:
            exit(
                f"Incorrect type for refractivity_model {type(val)}. Either a list or a ROOT.vector of strings required.")

    @property
    def refractivity_param(self):
        return np.array(self._refractivity_param)

    @refractivity_param.setter
    def refractivity_param(self, val: np.ndarray) -> None:
        self._refractivity_param = np.array(val)
        self._tree.SetBranchAddress("refractivity_param", self._refractivity_param)

    @property
    def t_pre(self):
        return self._t_pre[0]

    @t_pre.setter
    def t_pre(self, val: np.float32) -> None:
        self._t_pre[0] = val

    @property
    def t_post(self):
        return self._t_post[0]

    @t_post.setter
    def t_post(self, val: np.float32) -> None:
        self._t_post[0] = val

    @property
    def t_bin_size(self):
        return self._t_bin_size[0]

    @t_bin_size.setter
    def t_bin_size(self, val: np.float32) -> None:
        self._t_bin_size[0] = val

    @property
    def det_id(self):
        return self._det_id

    @det_id.setter
    def det_id(self, value):
        # Clear the vector before setting
        self._det_id.clear()

        # A list of strings was given
        if isinstance(value, list) or isinstance(value, np.ndarray):
            self._det_id += value
        # A vector was given
        elif isinstance(value, ROOT.vector("int")):
            self._det_id = value
        else:
            exit(f"Incorrect type for det_id {type(value)}. Either a list, an array or a ROOT.vector of ints required.")

    @property
    def det_type(self):
        return self._det_type

    @det_type.setter
    def det_type(self, value):
        # Clear the vector before setting
        self._det_type.clear()

        # A list of lists of strings was given
        if isinstance(value, list):
            self._det_type += value
        # A vector of vector of strings was given
        elif isinstance(value, ROOT.vector("vector<string>")):
            self._det_type = value
        else:
            exit(f"Incorrect type for det_type {type(value)}. Either a list of lists or a ROOT.vector of vectors of strings required.")

    @property
    def det_pos_shc(self):
        return self._det_pos_shc

    @det_pos_shc.setter
    def det_pos_shc(self, value):
        # Clear the vector before setting
        self._det_pos_shc.clear()

        # A list was given
        if isinstance(value, list) or isinstance(value, np.ndarray):
            self._det_pos_shc += value
        # A vector of strings was given
        elif isinstance(value, ROOT.vector("vector<float>")):
            self._det_pos_shc = value
        else:
            exit(f"Incorrect type for det_pos_shc {type(value)}. Either a list, an array or a ROOT.vector of vector<float> required.")

    @property
    def t_0(self):
        return self._t_0

    @t_0.setter
    def t_0(self, value):
        # Clear the vector before setting
        self._t_0.clear()

        # A list was given
        if isinstance(value, list) or isinstance(value, np.ndarray):
            self._t_0 += value
        # A vector of strings was given
        elif isinstance(value, ROOT.vector("float")):
            self._t_0 = value
        else:
            exit(f"Incorrect type for t_0 {type(value)}. Either a list, an array or a ROOT.vector of float required.")

    @property
    def p2p(self):
        return self._p2p

    @p2p.setter
    def p2p(self, value):
        # Clear the vector before setting
        self._p2p.clear()

        # A list was given
        if isinstance(value, list) or isinstance(value, np.ndarray):
            self._p2p += value
        # A vector of strings was given
        elif isinstance(value, ROOT.vector("float")):
            self._p2p = value
        else:
            exit(f"Incorrect type for p2p {type(value)}. Either a list, an array or a ROOT.vector of float required.")

    @property
    def trace_x(self):
        return self._trace_x

    @trace_x.setter
    def trace_x(self, value):
        # Clear the vector before setting
        self._trace_x.clear()

        # A list was given
        if isinstance(value, list) or isinstance(value, np.ndarray):
            self._trace_x += value
        # A vector of strings was given
        elif isinstance(value, ROOT.vector("vector<float>")):
            self._trace_x = value
        else:
            exit(
                f"Incorrect type for trace_x {type(value)}. Either a list, an array or a ROOT.vector of vector<float> required.")

    @property
    def trace_y(self):
        return self._trace_y

    @trace_y.setter
    def trace_y(self, value):
        # Clear the vector before setting
        self._trace_y.clear()

        # A list was given
        if isinstance(value, list) or isinstance(value, np.ndarray):
            self._trace_y += value
        # A vector of strings was given
        elif isinstance(value, ROOT.vector("vector<float>")):
            self._trace_y = value
        else:
            exit(f"Incorrect type for trace_y {type(value)}. Either a list, an array or a ROOT.vector of float required.")

    @property
    def trace_z(self):
        return self._trace_z

    @trace_z.setter
    def trace_z(self, value):
        # Clear the vector before setting
        self._trace_z.clear()

        # A list was given
        if isinstance(value, list) or isinstance(value, np.ndarray):
            self._trace_z += value
        # A vector of strings was given
        elif isinstance(value, ROOT.vector("vector<float>")):
            self._trace_z = value
        else:
            exit(f"Incorrect type for trace_z {type(value)}. Either a list, an array or a ROOT.vector of float required.")
