import re
from easyrobot.robot.base import RobotBase
from exoskeleton.robot.flexiv import FlexivInterface


def get_robot(**params):
    name = params.get('name', None)
    try:
        if re.fullmatch('[ -_]*flexiv[ -_]*', str.lower(name)):
            return FlexivInterface(**params)
        else:
            return RobotBase(**params)
    except Exception:
        return RobotBase(**params)
