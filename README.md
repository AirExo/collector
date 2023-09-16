# superexo-data-collector

## Run

### collecting data

In order to collect data, you need to create the configuration file and then execute the following command:
```
python main.py --type [type of the configuration file] --cfg [category of the task]
```

For example, if you want to record the movement of the exoskeleton alone when doing the task named grasping from the curtained shelf, you may use:
```
python main.py --type exoskeleton --cfg grasp_from_the_curtained_shelf
```

### testing correspondence
If you want to test the correspondence between the exoskeleton and the robot, you may run the following command:
```
python test_exoskeleton.py --cfg [category of the task]
```


