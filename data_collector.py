import os
import sys
import time

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

import traci

sumo_config_file = "bhubaneswar.sumocfg"
sumo_binary = "sumo"
sumo_cmd = [sumo_binary, "-c", sumo_config_file]

def run_simulation():
    """
    Connects to the SUMO simulation and extracts data for each step.
    """

    print("--- Reading Configuration File ---")
    with open(sumo_config_file, 'r') as f:
        print(f.read())
    print("------------------------------------")
    
    print("Starting SUMO...")
    traci.start(sumo_cmd)
    
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        
        current_time = traci.simulation.getTime()
        waiting_cars_N = traci.lane.getLastStepHaltingNumber("N_to_C_0")
        waiting_cars_S = traci.lane.getLastStepHaltingNumber("S_to_C_0")
        waiting_cars_E = traci.lane.getLastStepHaltingNumber("E_to_C_0")
        waiting_cars_W = traci.lane.getLastStepHaltingNumber("W_to_C_0")
        
        print(f"Time: {current_time:.2f}s | N:{waiting_cars_N} S:{waiting_cars_S} E:{waiting_cars_E} W:{waiting_cars_W}")
        
    traci.close()
    print("Simulation finished.")

if __name__ == "__main__":
    run_simulation()