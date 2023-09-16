source /home/ubuntu/anaconda3/etc/profile.d/conda.sh
conda activate py38
export DISPLAY=:1
cd /home/ubuntu/hongjie/DARM/
cfg=$1
tid=$2
sid=$3
uid=$4
python collector/collector.py --cfg $cfg --task $tid --scene $sid --user $uid
