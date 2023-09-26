import os
import time
import json
import argparse
from pynput import keyboard
from easydict import EasyDict as edict
from easyrobot.encoder.angle import AngleEncoder
from exoskeleton.teleop import DualArmTeleOperator


if __name__ == '__main__':
    os.system("kill -9 `ps -ef | grep collector | grep -v grep | awk '{print $2}'`")
    os.system('rm -f /dev/shm/*')
    os.system('udevadm trigger')

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--task', '-t', 
        default = 'gather_balls', 
        help = 'task name', 
        type = str,
        choices = ['gather_balls', 'grasp_from_the_curtained_shelf']
    )
    parser.add_argument(
        '--type',
        default = 'teleop', 
        help = 'type of demonstration collection', 
        type = str,
        choices = ['teleop', 'exoskeleton']
    )
    args = parser.parse_args()

    run_path = 'configs/flexiv_' + str(args.type) + '_' + str(args.task) + '.json'

    if not os.path.exists(run_path):
        raise AttributeError('Please provide the configuration file {}.'.format(run_path))
    with open(run_path, 'r') as f:
        cfgs = edict(json.load(f))
    
    tid = int(input('Task ID: '))
    sid = int(input('Scene ID: '))
    uid = int(input('User ID: '))
    
    if cfgs.mode == 'teleop':
        op = DualArmTeleOperator(cfgs.config.left, cfgs.config.right)
        op.initialization()
        time.sleep(2)
        op.calibration()

        has_start = False
        has_stop = False
        has_record = False

        def _on_press(key):
            global has_start
            global has_stop
            global has_record
            try:
                if key.char == 's':
                    if not has_start:
                        op.start()
                        has_start = True
                    else:
                        pass  
                if key.char == 'q':
                    if not has_start:
                        pass
                    else:
                        op.stop()
                        op.initialization()
                        time.sleep(2)
                        has_stop = True
                if key.char == 'r':
                    if not has_record:
                        os.system('bash collector/collector.sh {} {} {} {} &'.format(run_path, tid, sid, uid))
                        time.sleep(1)
                        has_record = True
                    else:
                        pass     
            except Exception as e:
                print(e)
                pass

        def _on_release(key):
            pass

        listener = keyboard.Listener(on_press = _on_press, on_release = _on_release)
        listener.start()
        while not has_start:
            time.sleep(0.5)
        while not has_stop:
            time.sleep(0.5)
        listener.stop()
    elif cfgs.mode == 'exoskeleton':
        encoder_left = AngleEncoder(**cfgs.encoder_left)
        encoder_left.streaming()
        encoder_right = AngleEncoder(**cfgs.encoder_right)
        encoder_right.streaming()
        has_start = False
        has_stop = False

        def _on_press(key):
            global has_start
            global has_stop
            try:
                if key.char == 'q':
                    if not has_start:
                        pass
                    else:
                        encoder_right.stop_streaming()
                        encoder_left.stop_streaming()
                        has_stop = True
                if key.char == 's':
                    if not has_start:
                        os.system('bash collector/collector.sh {} {} {} {} &'.format(run_path, tid, sid, uid))
                        time.sleep(3)
                        has_start = True
                    else:
                        pass     
            except AttributeError:
                pass

        def _on_release(key):
            pass

        listener = keyboard.Listener(on_press = _on_press, on_release = _on_release)
        listener.start()
        while not has_stop:
            pass
        listener.stop()
        
    else:
        raise AttributeError('Invalid type.')