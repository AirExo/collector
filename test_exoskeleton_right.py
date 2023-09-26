import time
import logging
import argparse
from exoskeleton.teleop import SingleArmTeleOperator


parser = argparse.ArgumentParser()
parser.add_argument(
    '--task', '-t', 
    default = 'gather_balls', 
    help = 'task name', 
    type = str,
    choices = ['gather_balls', 'grasp_from_the_curtained_shelf']
)
args = parser.parse_args()

op = SingleArmTeleOperator('exoskeleton/configs/flexiv_right_' + str(args.task) + '.json')

logger = logging.getLogger("TeleOP-right")
logger.setLevel(logging.INFO)

op.initialization()
time.sleep(5)

op.calibration()

time.sleep(5)

try:
    op.start()
    while True:
        time.sleep(1)
except Exception:
    op.stop()
