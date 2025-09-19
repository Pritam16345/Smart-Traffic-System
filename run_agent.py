import os
import sys
import pickle
import random
import numpy as np

# We need to import python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

import traci

# --- SIMULATION SETUP ---
sumo_config_file = "bhubaneswar.sumocfg"
sumo_binary = "sumo-gui"
sumo_cmd = [sumo_binary, "-c", sumo_config_file, "--tripinfo-output", "tripinfo_agent.xml", "--quit-on-end"]

# --- ACTION & STATE DEFINITIONS ---
ACTIONS = [0, 1] # 0 = Continue, 1 = Switch

def get_state(current_phase):
    queue_state = []
    incoming_lanes = ["N_to_C_0", "E_to_C_0", "S_to_C_0", "W_to_C_0"]
    for lane_id in incoming_lanes:
        waiting_cars = traci.lane.getLastStepHaltingNumber(lane_id)
        if waiting_cars == 0:
            queue_state.append(0)
        elif waiting_cars <= 5:
            queue_state.append(1)
        else:
            queue_state.append(2)
    return (tuple(queue_state), current_phase)

def choose_best_action(state, q_table):
    if state not in q_table:
        # Educated guess for unseen state: if any queues are high, switch.
        if 2 in state[0]:
             return 1 # Switch
        else:
             return 0 # Continue
    return np.argmax(q_table[state])

def run_agent(q_table):
    traci.start(sumo_cmd)
    
    step = 0
    current_phase = 0
    traci.trafficlight.setPhase("C", 0)

    while step < 3600 and traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        current_state = get_state(current_phase)
        action = choose_best_action(current_state, q_table)

        if action == 1:
            current_phase = (current_phase + 1) % 4
            yellow_phase_index = (current_phase * 2 - 1 + 8) % 8
            green_phase_index = current_phase * 2
            
            traci.trafficlight.setPhase("C", yellow_phase_index)
            for _ in range(3):
                traci.simulationStep()
                step += 1

            traci.trafficlight.setPhase("C", green_phase_index)
            for _ in range(5):
                traci.simulationStep()
                step += 1
        
        step += 1
            
    traci.close()
    print("Agent simulation finished.")

if __name__ == "__main__":
    try:
        with open('q_table.pkl', 'rb') as f:
            q_table = pickle.load(f)
        print("Q-table loaded successfully.")
    except FileNotFoundError:
        sys.exit("Error: q_table.pkl not found. Please run train.py first.")

    run_agent(q_table)