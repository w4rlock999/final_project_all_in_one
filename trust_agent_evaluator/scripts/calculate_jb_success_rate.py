import json
import os

def calculate_success_rate(jailbreaks):
    """Calculate success rate from a list of jailbreak judge outputs"""
    success_count = sum(1 for jb in jailbreaks if jb["judge_output"] == "1")
    return success_count / len(jailbreaks)

def main():
    # Read the jailbreak judge results
    with open("data/jailbreak_judge_result.json", "r") as f:
        jb_results = json.load(f)
    
    # Read the agentic graph
    with open("data/agentic_graph.json", "r") as f:
        agentic_graph = json.load(f)
    
    # Create a mapping of node IDs to success rates
    success_rates = {}
    for node in jb_results["nodes"]:
        success_rates[node["id"]] = calculate_success_rate(node["jailbreaks"])
    
    # Add success rates to the agentic graph nodes
    for node in agentic_graph["nodes"]:
        if node["id"] in success_rates:
            node["jailbreak_success_rate"] = success_rates[node["id"]]
    
    # Save the updated graph
    with open("data/agentic_graph_with_jb.json", "w") as f:
        json.dump(agentic_graph, f, indent=2)

if __name__ == "__main__":
    main() 