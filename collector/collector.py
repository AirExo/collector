import os
import time
import json
import logging
import argparse
import threading
import numpy as np
from pynput import keyboard
from easydict import EasyDict as edict
from easyrobot.camera.api import get_rgbd_camera
from easyrobot.utils.shared_memory import SharedMemoryManager


def to_type(s):
    if s == "float":
        return np.float64
    elif s == "int":
        return np.int64
    elif s == "uint8":
        return np.uint8
    elif s == "uint16":
        return np.uint16
    else:
        raise AttributeError("Unsupported type name.")


class Collector(object):
    """
    Collector.
    """
    def __init__(self, cfgs, subpath = None, user = 0, **kwargs):
        super(Collector, self).__init__()
        # Data path
        self.path = cfgs.data_path
        if subpath is not None:
            self.path = os.path.join(self.path, subpath)
        if os.path.exists(self.path) == False:
            os.makedirs(self.path)
        # Initialize logger
        self.cfgs = cfgs
        self.logger = logging.getLogger(self.cfgs.get('logger_name', 'Collector'))
        # Initialize cameras
        self.cameras = []
        for cam in cfgs.cameras:
            cam = get_rgbd_camera(**cam)
            cam.streaming()
            self.cameras.append(cam)
        # Initialize data collectors
        self.shm_list = cfgs.shm_data.keys()
        self.shm_managers = []
        for shm_name in self.shm_list:
            self.shm_managers.append(
                SharedMemoryManager(
                    shm_name,
                    1,
                    cfgs.shm_data[shm_name]["shape"],
                    to_type(cfgs.shm_data[shm_name]["type"])
                )
            )
        self.meta = edict()
        self.meta.cfgs = cfgs
        self.meta.user = user
        # Initialize collection
        self.is_collecting = False

    def receive(self):
        '''
        Receive the data.
        '''
        res = {'time': int(time.time() * 1000)}
        for i, shm_name in enumerate(self.shm_list):
            res[shm_name] = self.shm_managers[i].execute()
        return res

    def save(self):
        '''
        Save the collected data to the data path, return the timestamp at collection.
        '''
        res = self.receive()
        timestamp = res['time']

        np.save(os.path.join(self.path, '{}.npy'.format(timestamp)), res, allow_pickle = True)
        return timestamp

    def start(self, delay_time = 0.0):
        '''
        Start collecting data.
        
        Parameters:
        - delay_time: float, optional, default: 0.0, the delay time before collecting data.
        '''
        self.thread = threading.Thread(target = self.collecting_thread, kwargs = {'delay_time': delay_time})
        self.thread.setDaemon(True)
        self.thread.start()
        self.meta.start_time = int(time.time() * 1000)
        self.meta.timestamps = []

    def collecting_thread(self, delay_time = 0.0):
        time.sleep(delay_time)
        self.is_collecting = True
        self.logger.info('[{}] Start collecting data ...'.format(self.cfgs.name))
        while self.is_collecting:
            timestamp = self.save()
            self.meta.timestamps.append(timestamp)

    def stop(self):
        '''
        Stop collecting data.
        '''
        self.meta.stop_time = int(time.time() * 1000)
        self.is_collecting = False
        self.thread.join()
        self.logger.info('[{}] Stop collecting data.'.format(self.cfgs.name))
        for cam in self.cameras:
            cam.stop_streaming()
    
    def save_meta(self):
        '''
        Save metadata.
        '''
        with open(os.path.join(self.path, 'meta.json'), 'w') as f:
            json.dump(self.meta, f)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--cfg', '-c', 
        default = os.path.join('configs', 'flexiv_teleop.yaml'), 
        help = 'path to the configuration file', 
        type = str
    )
    parser.add_argument('--task', '-t', default = 0, help = 'task id', type = int)
    parser.add_argument('--scene', '-s', default = 0, help = 'scene id', type = int)
    parser.add_argument('--user', '-u', default = 0, help = 'user id', type = int)
    args = parser.parse_args()
    if not os.path.exists(args.cfg):
        raise AttributeError('Please provide the configuration file {}.'.format(args.cfg))
    with open(args.cfg, 'r') as f:
        cfgs = edict(json.load(f))
    if cfgs.mode == 'exoskeleton':
        subpath = os.path.join('task{}_itw'.format(args.task), 'scene{}'.format(args.scene))
    else:
        subpath = os.path.join('task{}'.format(args.task), 'scene{}'.format(args.scene))
    collector = Collector(cfgs, subpath, user = args.user)

    has_stop = False

    def _on_press(key):
        global has_stop
        try:
            if key.char == 'q':
                if not has_stop:
                    collector.stop()
                    has_stop = True
        except AttributeError:
            pass

    def _on_release(key):
        pass

    listener = keyboard.Listener(on_press = _on_press, on_release = _on_release)
    collector.start()
    listener.start()
    while not has_stop:
        pass
    listener.stop()
    collector.save_meta()
