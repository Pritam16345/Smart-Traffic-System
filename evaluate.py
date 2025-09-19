import xml.etree.ElementTree as ET

def calculate_average_duration(xml_file):
    """
    Parses a tripinfo XML file and calculates the average trip duration.
    """
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    total_duration = 0
    vehicle_count = 0
    
    for tripinfo in root.findall('tripinfo'):
        duration = float(tripinfo.get('duration'))
        total_duration += duration
        vehicle_count += 1
        
    if vehicle_count == 0:
        return 0
        
    return total_duration / vehicle_count

if __name__ == "__main__":
    baseline_file = 'tripinfo_baseline.xml'
    agent_file = 'tripinfo_agent.xml'
    
    try:
        baseline_avg_time = calculate_average_duration(baseline_file)
        agent_avg_time = calculate_average_duration(agent_file)
        
        print("\n--- PERFORMANCE EVALUATION ---")
        print(f"Baseline Average Commute Time: {baseline_avg_time:.2f} seconds")
        print(f"AI Agent Average Commute Time: {agent_avg_time:.2f} seconds")
        
        if baseline_avg_time > 0:
            improvement = ((baseline_avg_time - agent_avg_time) / baseline_avg_time) * 100
            print(f"\nImprovement: {improvement:.2f}%")
            if improvement > 10:
                print("🏆 GOAL ACHIEVED! Commute time reduced by over 10%.")
            else:
                print("Good progress, but goal not met. Consider training for more episodes.")
        else:
            print("Could not calculate improvement (baseline time is zero).")
            
    except FileNotFoundError as e:
        print(f"Error: Could not find a required file. {e}")
        print("Please make sure you have run the baseline simulation and the agent simulation first.")