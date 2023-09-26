import time
import logging
import argparse
from exoskeleton.teleop import DualArmTeleOperator


parser = argparse.ArgumentParser()
parser.add_argument(
    '--task', '-t', 
    default = 'gather_balls', 
    help = 'task name', 
    type = str,
    choices = ['gather_balls', 'grasp_from_the_curtained_shelf']
)
args = parser.parse_args()

op = DualArmTeleOperator(
    'exoskeleton/configs/flexiv_left_' + str(args.task) + '.json', 'exoskeleton/configs/flexiv_right_' + str(args.task) + '.json'
)

logger = logging.getLogger("TeleOP-left")
logger.setLevel(logging.INFO)

logger = logging.getLogger("TeleOP-right")
logger.setLevel(logging.INFO)
 
op.initialization()
time.sleep(10)

op.calibration()

time.sleep(5)

try:
    op.start()
    while True:
        time.sleep(1)
except Exception:
    op.stop()
