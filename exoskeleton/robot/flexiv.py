"""
Modified flexiv robot interface for exoskeleton tele-operation.
"""
from easyrobot.robot.flexiv import FlexivRobot


class FlexivInterface(FlexivRobot):
    """
    Modified Flexiv Robot Interface.
    """
    def __init__(
        self, 
        robot_ip_address, 
        pc_ip_address, 
        gripper = {}, 
        with_streaming = False,
        streaming_freq = 30,
        shm_name = "robot",
        joint_num = 7,
        min_joint_diff = 0.01,
        **kwargs
    ):
        super(FlexivInterface, self).__init__(
            robot_ip_address = robot_ip_address,
            pc_ip_address = pc_ip_address,
            gripper = gripper,
            with_streaming = with_streaming,
            streaming_freq = streaming_freq,
            shm_name = shm_name,
            **kwargs
        )
        self.joint_num = joint_num
        self.prev_pos = [0.0] * self.DOF
        self.min_joint_diff = min_joint_diff
    
    def action(self, action_dict, wait = False):
        '''
        Perform action in the given action dict.

        Parameters:
        - wait: whether to wait until the robot reach the target position.
        '''
        joint_pos = []
        target_vel = action_dict.get('target_joint_vel', [0.0] * self.DOF)
        target_acc = action_dict.get('target_joint_acc', [0.0] * self.DOF)
        max_vel = action_dict.get('max_joint_vel', [2.0] * self.DOF)
        max_acc = action_dict.get('max_joint_acc', [3.0] * self.DOF)
        joint_pos = action_dict["enc"][:self.joint_num]

        if any(abs(self.prev_pos[i] - joint_pos[i]) > self.min_joint_diff for i in range(self.joint_num)):
            joint_pos = joint_pos
        else:
            joint_pos = self.prev_pos
        self.prev_pos = joint_pos

        self.send_joint_pos(joint_pos, wait, target_vel, target_acc, max_vel, max_acc)
        gripper_action = action_dict["enc"][self.joint_num:]
        self.gripper_action(*gripper_action)