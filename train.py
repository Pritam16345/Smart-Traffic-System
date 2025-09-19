import os
import sys
import pickle
import random
import numpy as np
import traci

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

ALPHA = 0.2
GAMMA = 0.9
EPSILON_START = 1.0
EPSILON_DECAY = 0.99
MIN_EPSILON = 0.01

sumo_config_file = "bhubaneswar.sumocfg"
sumo_binary = "sumo"
sumo_cmd = [sumo_binary, "-c", sumo_config_file]

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

def choose_action(state, q_table, epsilon):
    if random.uniform(0, 1) < epsilon:
        return random.choice(ACTIONS)
    else:
        if state not in q_table:
            q_table[state] = np.zeros(len(ACTIONS))
        return np.argmax(q_table[state])

def run_training(episodes):
    q_table = {}
    epsilon = EPSILON_START

    for episode in range(episodes):
        traci.start(sumo_cmd)
        
        step = 0
        current_phase = 0
        traci.trafficlight.setPhase("C", 0)

        while step < 3600 and traci.simulation.getMinExpectedNumber() > 0:
            current_state = get_state(current_phase)
            if current_state not in q_table:
                q_table[current_state] = np.zeros(len(ACTIONS))


            old_waiting_cars = sum(traci.lane.getLastStepHaltingNumber(lane) for lane in ["N_to_C_0", "E_to_C_0", "S_to_C_0", "W_to_C_0"])

            action = choose_action(current_state, q_table, epsilon)

            if action == 1:
                current_phase = (current_phase + 1) % 4
                yellow_phase_index = (current_phase * 2 - 1 + 8) % 8
                green_phase_index = current_phase * 2
                
                traci.trafficlight.setPhase("C", yellow_phase_index)
                for _ in range(3): traci.simulationStep(); step += 1
                
                traci.trafficlight.setPhase("C", green_phase_index)
                for _ in range(5): traci.simulationStep(); step += 1
            else: # Continue phase
                traci.simulationStep()
                step += 1

            # Get waiting cars AFTER the action to calculate reward
            new_waiting_cars = sum(traci.lane.getLastStepHaltingNumber(lane) for lane in ["N_to_C_0", "E_to_C_0", "S_to_C_0", "W_to_C_0"])
            
            reward = old_waiting_cars - new_waiting_cars

            new_state = get_state(current_phase)
            if new_state not in q_table:
                q_table[new_state] = np.zeros(len(ACTIONS))
            

            old_value = q_table[current_state][action]
            next_max = np.max(q_table[new_state])
            new_value = old_value + ALPHA * (reward + GAMMA * next_max - old_value)
            q_table[current_state][action] = new_value
            
        traci.close()
        epsilon = max(MIN_EPSILON, epsilon * EPSILON_DECAY)
        print(f"Episode {episode+1}/{episodes} finished. Epsilon: {epsilon:.4f}")

    with open('q_table.pkl', 'wb') as f:
        pickle.dump(q_table, f)
    
    print("\nTraining complete! Q-table saved.")
    return q_table

if __name__ == "__main__":
    trained_q_table = run_training(300)