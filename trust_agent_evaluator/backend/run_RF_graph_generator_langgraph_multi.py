import os
import json
from RF_graph_generator_langgraph_multi import ReactFlowGeneratorMulti

def run_RF_graph_generator(input_file: str):
    """
    Generate ReactFlow graph data from the input graph file.
    
    Args:
        input_file (str): Path to the input graph JSON file
    """
    # Create ReactFlow generator instance
    rf_generator = ReactFlowGeneratorMulti(graph_file=input_file)
    
    # Generate action and component graphs
    action_nodes, action_edges = rf_generator.generate_action_graph_RF()
    component_nodes, component_edges = rf_generator.generate_component_graph_RF()
    
    # Prepare output data
    reactflow_data = {
        "action": {
            "nodes": action_nodes,
            "edges": action_edges
        },
        "component": {
            "nodes": component_nodes,
            "edges": component_edges
        }
    }
    
    # Save to file
    current_dir = os.getcwd()
    output_dir = os.path.join(current_dir, 'data', 'output')
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, 'reactflow_graph_with_multi_trace.json')
    with open(output_file, 'w') as f:
        json.dump(reactflow_data, f, indent=2)
    
    print(f"Generated ReactFlow graph data saved to: {output_file}")

if __name__ == "__main__":
    input_file = "./data/output/detailed_graph_langgraph_multi_trace.json"
    run_RF_graph_generator(input_file)