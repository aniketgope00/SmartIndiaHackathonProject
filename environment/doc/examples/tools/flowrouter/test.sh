#!/bin/bash
python "$SUMO_HOME/tools/detector/flowrouter.py" -n input_net.net.xml -d input_detectors.det.xml -f input_flows.txt --verbose