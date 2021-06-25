# GRANDRoot
Development of the GRAND root file format
This is work in progress. To set up, you first need to set up 2 repositories

RADIOSIMUS
https://github.com/grand-mother/radio-simus

(you can skip this if you are not interested in the voltage simulation (that is anyway old and for testing))
In that case, remove all the lines that reference it in ComputeVoltageOnGRANDROOT.py

ZHAIRESPYTHON (the developement branche)
https://github.com/mjtueros/ZHAireS-Python/tree/DevelopmentLeia

and you will need PyROOT installed on your python


you must create the environment variables so that the scripts find this libraries

you can put this on your $HOME .bashrc
#Setting up PyROOT
export LD_LIBRARY_PATH=$ROOTSYS/lib:$PYTHONDIR/lib:$LD_LIBRARY_PATH
export PYTHONPATH=$ROOTSYS/lib:$PYTHONPATH

#directory where the GRAND radio-simus package with

export RADIOSIMUS=/home/mjtueros/GRAND/ComputeVoltage/radio-simus

#directory wheere ZHAireS-Python is located

export ZHAIRESPYTHON=/home/mjtueros/AiresRepository/Dropbox/GitAiresPython/ZHAireS-Python


Finally, to test the suite you can do

python3 RunTest.py TestFile.root
python3 PlotEventRoot.py TestFile.root
