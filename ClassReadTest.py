import ROOT
from GRANDRootTrees import *

t = SimEfieldTree("sample_trees.root")

t.GetEvent(0)
print(t)
print(t.evt_id)
print(t.refractivity_param)
t.GetEvent(1)
print(t)

t1 = SimShowerTree("sample_trees.root")
t1.GetEvent(0)
print(t1.rnd_seed)

t2 = SimSignalTree("sample_trees.root")
t2.GetEvent(0)
print(t2.signal_sim)