source [CONDA ACTIVATE SCRIPT]
conda activate [CONDA ENV]
export DISPLAY=:1
cd [PATH TO THE COLLECTOR]
cfg=$1
tid=$2
sid=$3
uid=$4
python collector/collector.py --cfg $cfg --task $tid --scene $sid --user $uid
