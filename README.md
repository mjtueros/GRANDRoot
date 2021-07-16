# GRANDRoot
Development of the GRAND root file format
This is work in progress. 

Python packages required: os,sys,loogging, numpy,matplotlib,scipy,glob and PyROOT 

#Setting up PyROOT (i had to set this up, your experience might be different)
export LD_LIBRARY_PATH=$ROOTSYS/lib:$PYTHONDIR/lib:$LD_LIBRARY_PATH
export PYTHONPATH=$ROOTSYS/lib:$PYTHONPATH

To test the suite you can do

python3 RunTest.py TestFile.root
python3 PlotEventRoot.py TestFile.root

NOTE: Event2 has no traces ON PURPOSE to test what happens when the trees have different number of entries

Since im not experienced in github, lets follow this simple development scheme, and see how it works.

https://guides.github.com/introduction/flow/

# Documentation

This version features a documentation made using sphinx

## Generating the documentation

### Requirements

Install Sphinx and the documentation theme

``pip install -U Sphinx``

``pip install sphinx-rtd-theme``

### Build the documentation

Enter the ``doc`` directory and run ``make html``
