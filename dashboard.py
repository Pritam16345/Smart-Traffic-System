import os
import sys
import pickle
import json
import threading
import time
import numpy as np
from flask import Flask, render_template, jsonify

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")
import traci

app = Flask(__name__)

sumo_config_file = "bhubaneswar.sumocfg"
sumo_binary = "sumo-gui"
sumo_cmd = [sumo_binary, "-c", sumo_config_file, "--tripinfo-output", "tripinfo_agent.xml", "--quit-on-end"]
MIN_GREEN_TIME = 10
ACTIONS = [0, 1]

live_data = {
    "north": 0, "east": 0, "south": 0, "west": 0, "phase": "N"
}
phase_map = {0: "North", 1: "East", 2: "South", 3: "West"}

def get_state(current_phase):
    state = []
    incoming_lanes = ["N_to_C_0", "E_to_C_0", "S_to_C_0", "W_to_C_0"]

    live_data["north"] = traci.lane.getLastStepHaltingNumber("N_to_C_0")
    live_data["east"] = traci.lane.getLastStepHaltingNumber("E_to_C_0")
    live_data["south"] = traci.lane.getLastStepHaltingNumber("S_to_C_0")
    live_data["west"] = traci.lane.getLastStepHaltingNumber("W_to_C_0")
    live_data["phase"] = phase_map[current_phase]
    
    for count in [live_data["north"], live_data["east"], live_data["south"], live_data["west"]]:
        if count == 0: state.append(0)
        elif count <= 5: state.append(1)
        else: state.append(2)
    return (tuple(state), current_phase)

def choose_best_action(state, q_table):
    if state not in q_table:
        if 2 in state[0]: return 1
        else: return 0
    return np.argmax(q_table[state])

def run_simulation_logic():
    """This function contains your agent's logic and will run in a separate thread."""
    try:
        with open('q_table.pkl', 'rb') as f:
            q_table = pickle.load(f)
        print("Q-table loaded successfully for simulation.")
    except FileNotFoundError:
        print("Could not load Q-table. Simulation will not run.")
        return

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
                green_time_counter = 0
        
        get_state(current_phase)
        time.sleep(0.05)
        step += 1
            
    traci.close()
    print("Agent simulation finished.")


@app.route('/')
def index():
    """Serves the main HTML page."""
    return render_template('index.html')

@app.route('/live_data')
def get_live_data():
    """Provides the live traffic data as JSON."""
    return jsonify(live_data)

if __name__ == '__main__':

    simulation_thread = threading.Thread(target=run_simulation_logic)
    simulation_thread.start()
    
    app.run(debug=False)