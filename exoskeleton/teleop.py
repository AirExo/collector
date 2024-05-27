import os
import time
import json
import logging
import threading
from easydict import EasyDict as edict
from easyrobot.utils.transforms.degree import *
from easyrobot.utils.logger import ColoredLogger
from easyrobot.encoder.angle import AngleEncoder
from exoskeleton.robot.api import get_robot


class SingleArmTeleOperator(object):
    '''
    Tele-operator for single robot arm.
    '''
    def __init__(self, cfgs):
        '''
        Initialization.

        Parameters:
        - cfgs: the path to the configuration file.
        '''
        super(SingleArmTeleOperator, self).__init__()
        if not os.path.exists(cfgs):
            raise AttributeError('Please provide the configuration file {}.'.format(cfgs))
        with open(cfgs, 'r') as f:
            self.cfgs = edict(json.load(f))
        logging.setLoggerClass(ColoredLogger)
        self.logger = logging.getLogger(self.cfgs.get('logger_name', 'TeleOP'))
        self.action_freq = self.cfgs.freq
        self.is_teleop = False
        if not self.cfgs.encoder:
            self.ids = [1, 2, 3, 4, 5, 6, 7, 8]
            self.encoder = None
        else:
            self.encoder = AngleEncoder(**self.cfgs.encoder)
            self.ids = self.encoder.ids
            self.encoder.streaming()
        self.num_ids = len(self.ids)
        self.robot = get_robot(**self.cfgs.robot)
        self.robot.streaming()
    
    def mapping(self, enc, x, num):
        scaling = self.cfgs.mapping[enc].scaling
        emin = self.cfgs.mapping[enc].encoder_min
        emax = self.cfgs.mapping[enc].encoder_max
        edir = self.cfgs.mapping[enc].encoder_direction
        erad = self.cfgs.mapping[enc].encoder_rad
        rmin = self.cfgs.mapping[enc].robot_min
        rmax = self.cfgs.mapping[enc].robot_max
        if erad:
            x = rad_2_deg(x)
        x = deg_clip_in_range(x, emin, emax, edir)
        if scaling:
            return deg_percentile(x, emin, emax, edir) * (rmax - rmin) + rmin
        rdir = self.cfgs.mapping[enc].robot_direction
        me, mr = self.cfgs.mapping[enc].encoder_mapping, self.cfgs.mapping[enc].robot_mapping
        rrad = self.cfgs.mapping[enc].robot_rad
        rzc = self.cfgs.mapping[enc].robot_zero_centered
        fixed = self.cfgs.mapping[enc].fixed
        x = deg_clip_in_range(mr + deg_distance(me, x, edir) * rdir, rmin, rmax, rdir)
        if fixed:
            x = self.cfgs.mapping[enc].fixed_value
        if rzc:
            x = deg_zero_centered(x, rmin, rmax, rdir)
        if rrad:
            x = deg_2_rad(x)
        return x
        
    def transform_action(self, enc_res):
        '''
        Transform the action in encoder field into robot field.
        '''
        action_dict = {}
        action = []
        for i in range(self.num_ids):
            rad = self.mapping("enc{}".format(self.ids[i]), enc_res[i], i)
            action.append(rad)
        action_dict["enc"] = action
        return action_dict

    def initialization(self):
        self.logger.info('[TeleOP-{}] Initialization ... Please remain still.'.format(self.cfgs.name))
        action_dict = {}
        action = []
        for i in range(self.num_ids):
            enc = "enc{}".format(self.ids[i])
            x = self.cfgs.mapping[enc].initial_value
            scaling = self.cfgs.mapping[enc].scaling
            if scaling:
                action.append(x)
                continue
            rmin = self.cfgs.mapping[enc].robot_min
            rmax = self.cfgs.mapping[enc].robot_max
            rdir = self.cfgs.mapping[enc].robot_direction
            rrad = self.cfgs.mapping[enc].robot_rad
            rzc = self.cfgs.mapping[enc].robot_zero_centered
            if rzc:
                x = deg_zero_centered(x, rmin, rmax, rdir)
            if rrad:
                x = deg_2_rad(x)
            action.append(x)
        action_dict["enc"] = action
        action_dict["max_joint_vel"] = [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]
        action_dict["max_joint_acc"] = [0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3]
        self.robot.action(action_dict, wait = True)
        self.logger.info('[TeleOP-{}] Finish initialization.'.format(self.cfgs.name))
    

    def calibration(self):
        '''
        Calibrate the robot with the exoskeleton when starting tele-operation.
        '''
        self.logger.info('[TeleOP-{}] Initially calibrate ... Please remain still.'.format(self.cfgs.name))
        enc_res = self.encoder.fetch_info()
        action_dict = self.transform_action(enc_res)
        action_dict["max_joint_vel"] = [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2]
        action_dict["max_joint_acc"] = [0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3]
        self.robot.action(action_dict, wait = True)
        self.logger.info('[TeleOP-{}] Finish initial calibration.'.format(self.cfgs.name))
        
    def start(self, delay_time = 0.0):
        '''
        Start tele-operation.
        
        Parameters:
        - delay_time: float, optional, default: 0.0, the delay time before collecting data.
        '''
        self.thread = threading.Thread(target = self.teleop_thread, kwargs = {'delay_time': delay_time})
        self.thread.setDaemon(True)
        self.thread.start()
    
    def teleop_thread(self, delay_time = 0.0):
        time.sleep(delay_time)
        self.is_teleop = True
        self.logger.info('[{}] Start tele-operation ...'.format(self.cfgs.name))
        while self.is_teleop:
            enc_res = self.encoder.fetch_info()
            action_dict = self.transform_action(enc_res)
            self.robot.action(action_dict)
            time.sleep(1.0 / self.action_freq)
    
    def stop(self):
        '''
        Stop tele-operation process.
        '''
        self.is_teleop = False
        if self.thread:
            self.thread.join()
        self.logger.info('[{}] Stop tele-operation.'.format(self.cfgs.name))
        if self.encoder:
            self.encoder.stop_streaming()
        self.robot.stop_streaming()
        self.robot.stop()


class DualArmTeleOperator(object):
    '''
    Tele-operator for dual robot arm.
    '''
    def __init__(self, cfgs_left, cfgs_right):
        '''
        Initialization.

        Parameters:
        - cfgs_left: the path to the configuration file of the left arm;
        - cfgs_right: the path to the configuration file of the right arm.
        '''
        super(DualArmTeleOperator, self).__init__()
        self.op_left = SingleArmTeleOperator(cfgs_left)
        self.op_right = SingleArmTeleOperator(cfgs_right)
    
    def initialization(self):
        self.op_left.initialization()
        self.op_right.initialization()
        return
    
    def calibration(self):
        '''
        Calibrate the robot with the exoskeleton when starting tele-operation.
        '''
        self.op_left.calibration()
        self.op_right.calibration()
        return

    def start(self, delay_time = 0.0):
        '''
        Start tele-operation.
        
        Parameters:
        - delay_time: float, optional, default: 0.0, the delay time before collecting data.
        '''
        self.op_left.start(delay_time)
        self.op_right.start(delay_time)

    def stop(self):
        '''
        Stop the tele-operation process.
        '''
        self.op_left.stop()
        self.op_right.stop()


if __name__ == '__main__':
    op = SingleArmTeleOperator('configs/flexiv_left_gather_balls.json')
    op.calibration()
    op.start()
    time.sleep(10)
    op.stop()
    
