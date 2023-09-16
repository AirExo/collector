import time
import logging
import argparse
from exoskeleton.teleop import SingleArmTeleOperator


parser = argparse.ArgumentParser()
parser.add_argument(
    '--config', '-c', 
    default = 'grasp_from_the_curtained_shelf', 
    help = 'category of the task', 
    type = str,
    choices = ['gather_balls', 'grasp_from_the_curtained_shelf']
)
args = parser.parse_args()

op = SingleArmTeleOperator('exoskeleton/configs/flexiv_left_'+str(args.config)+'.json')

logger = logging.getLogger("TeleOP-left")
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
