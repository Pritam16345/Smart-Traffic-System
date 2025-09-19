import os
import sys
import pickle
import random
import numpy as np

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

import traci

# --- SETUP ---
sumo_config_file = "bhubaneswar.sumocfg"
sumo_binary = "sumo-gui"
sumo_cmd = [sumo_binary, "-c", sumo_config_file, "--tripinfo-output", "tripinfo_agent.xml", "--quit-on-end"]
MIN_GREEN_TIME = 10

# --- ACTIONS & STATE ---
ACTIONS = [0, 1] # 0 = Continue, 1 = Switch

def get_state(current_phase):
    state = []
    incoming_lanes = ["N_to_C_0", "E_to_C_0", "S_to_C_0", "W_to_C_0"]
    for lane_id in incoming_lanes:
        waiting_cars = traci.lane.getLastStepHaltingNumber(lane_id)
        if waiting_cars == 0: state.append(0)
        elif waiting_cars <= 5: state.append(1)
        else: state.append(2)
    return (tuple(state), current_phase)

def choose_best_action(state, q_table):
    if state not in q_table:
        if 2 in state[0]: return 1
        else: return 0
    return np.argmax(q_table[state])

def run_agent(q_table):
    traci.start(sumo_cmd)
    
    step = 0
    current_phase = 0
    green_time_counter = 0
    traci.trafficlight.setPhase("C", 0)

    while step < 3600 and traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        green_time_counter += 1

        if green_time_counter >= MIN_GREEN_TIME:
            current_state = get_state(current_phase)
            action = choose_best_action(current_state, q_table)

            if action == 1:
                current_phase = (current_phase + 1) % 4
                yellow_phase = (current_phase * 2 - 1 + 8) % 8
                green_phase = current_phase * 2
                
                traci.trafficlight.setPhase("C", yellow_phase)
                for _ in range(3): traci.simulationStep(); step += 1

                traci.trafficlight.setPhase("C", green_phase)
                green_time_counter = 0 # Reset counter
        
        step += 1
            
    traci.close()
    print("Agent simulation finished.")

if __name__ == "__main__":
    try:
        with open('q_table.pkl', 'rb') as f:
            q_table = pickle.load(f)
        print("Q-table loaded successfully.")
    except FileNotFoundError:
        sys.exit("Error: **final_agent_brain.pkl** not found. Please run train.py first.")

    run_agent(q_table)