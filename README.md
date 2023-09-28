# AirExo

[[Paper]](https://arxiv.org/pdf/2309.14975.pdf) [[Project Page]](https://airexo.github.io/) [[Sample Demonstration Data]](https://drive.google.com/drive/folders/1f_bmrFPep90aUSBj28TdXRiNvHo7PpxR?usp=drive_link) [[ACT with in-the-Wild Learning]](https://github.com/AirExo/act-in-the-wild)

This repository contains code for teleoperating Flexiv robotic arms using ***AirExo***, as well as code for demonstration data collection, including teleoperated demonstration data and in-the-wild demonstration data.

## Requirements

**Hardware**. ***AirExo***, Intel RealSense D415/D435 camera(s), and two Flexiv Rizon robotic arms. For other types of robots, you can slightly modify the code to adapt them.

**Python Dependencies**.

- numpy
- pynput
- argparse
- [easyrobot](https://github.com/galaxies99/easyrobot)

## Run

### Configurations

There are 3 types of configuration files in this repository, namely

- `exoskeleton/configs/flexiv_[left/right]_[task].json`: the configuration files for teleoperation of a single arm with ***AirExo***, including the robot and gripper specifications, as well as joint mapping parameters obtained from calibration.
- `configs/flexiv_teleop_[task].json`: the configuration files for teleoperated demonstration data collection with ***AirExo***, including the encoder specifications, the data to be collected, and the camera configurations.
- `configs/flexiv_exoskeleton_[task].json`: the configuration files for in-the-wild demonstration data collection with ***AirExo***, including the encoder specifications, the data to be collected, and the camera configurations.

We provide the configuration files for Flexiv robots in our experimental environments. You might need to modify the configurations based on your own settings and calibration results.

### Encoders

Before testing teleoperation, please make sure that your encoders in ***AirExo*** works correctly. You can modify Line 5 in `test_encoder.py` according to your settings and execute the script. The encoder readings should be displayed in the terminal in real time.

### Teleoperation

Use the following command to test the teleoperation function to see if the configurations are set correctly. Before teleoperation begins, the robot will slowly move to the position corresponding to ***AirExo***. After a few seconds, the robot can be controlled in real-time. Please make sure that the operator does not move during the waiting time to prevent unexpected movements of the robot.

```bash
python test_exoskeleton.py
```

You can also test the teleoperation function of a single arm using the following commands.

```bash
python test_exoskeleton_left.py
python test_exoskeleton_right.py
```

### Teleoperated Demonstration Data Collection

Please complete the `collector/collector.sh` file based on your environment first, and we recommend to test the encoder and the teleoperation functions using instructions above before teleoperated demonstration data collection. For teleoperated demonstrations, two Flexiv robotic arms should be connected to the workstation during data collection.

Then, use the following command for data collection. 

```bash
python main.py --type teleop --task [Task Name]
```

Here, for `[Task Name]` we support 2 tasks in our paper: `gather_balls` and `grasp_from_the_curtained_shelf`. Before teleoperation, you will be asked to provide task ID, scene ID and user ID (operator ID) respectively. The collected data will be stored under `[Data Path]/task[Task ID]/scene[Scene ID]/` according to the configuration settings, with the format of:

```text
meta.json
[Timestamp 1].npy
[Timestamp 2].npy
...
[Timestamp T].npy
```

where `[Timestamp i]` denote the timestamp for this data record, and `meta.json` stores all meta information, including all valid timestamps, configurations, *etc.*

### In-the-Wild Demonstration Data Collection

Please complete the `collector/collector.sh` file based on your environment first, and we recommend to test the encoder function using instructions above before in-the-wild demonstration data collection. For in-the-wild demonstrations, no robotic arm is needed during data collection.

Then, use the following command for data collection.

```bash
python main.py --type exoskeleton --task [Task Name]
```

Here, for `[Task Name]` we support 2 tasks in our paper: `gather_balls` and `grasp_from_the_curtained_shelf`. Before data collection, you will be asked to provide task ID, scene ID and user ID (operator ID) respectively. The collected data will be stored under `[Data Path]/task[Task ID]_itw/scene[Scene ID]/` according to the configuration settings, with the same format as the teleoperated demonstrations.

## Citation

If you find ***AirExo*** useful in your research, please consider citing the following paper:

```bibtex
@article{
    fang2023low,
    title = {Low-Cost Exoskeletons for Learning Whole-Arm Manipulation in the Wild},
    author = {Fang, Hongjie and Fang, Hao-Shu and Wang, Yiming and Ren, Jieji and Chen, Jingjing and Zhang, Ruo and Wang, Weiming and Lu, Cewu},
    journal = {arXiv preprint arXiv:2309.14975},
    year = {2023}
}
```