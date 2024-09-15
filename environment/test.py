import subprocess
import traci
import os
import sys
import traci


if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("Please declare the environment variable 'SUMO_HOME'")


sumoBinary = "sumo-gui"
sumoConfig = "map.sumo.cfg"
sumoCmd = [sumoBinary, "-c", sumoConfig]


traci.start(sumoCmd)


step = 0
while step < 6400:
    traci.simulationStep()
    vehicle_ids = traci.vehicle.getIDList()
    for vehicle_id in vehicle_ids:
        position = traci.vehicle.getPosition(vehicle_id)
        print(f"Vehicle {vehicle_id} at {position}")
    step += 1

traci.close()
