import os
import json
from RF_graph_generator_LangGraph import ReactFlowGenerator

def convert_graph_to_reactflow(input_path: str):
    """
    Convert a graph JSON file to ReactFlow format
    
    Args:
        input_path (str): Path to the input JSON file
    """
    # Initialize the converter with the input file
    converter = ReactFlowGenerator(graph_file=input_path)
    
    # Generate action graph
    action_nodes, action_edges = converter.generate_action_graph_RF()
    
    # Generate component graph
    component_nodes, component_edges = converter.generate_component_graph_RF()
    
    # Combine both graphs into a single structure
    reactflow_data = {
        "action": {
            "nodes": action_nodes,
            "edges": action_edges,
            "viewport": {
                "x": 0,
                "y": 0,
                "zoom": 0.8
            }
        },
        "component": {
            "nodes": component_nodes,
            "edges": component_edges,
            "viewport": {
                "x": 0,
                "y": 0,
                "zoom": 0.8
            }
        }
    }
    
    # Save to output file
    output_path = "./data/output/reactflow_graph_with_jb_new.json"
    with open(output_path, 'w') as f:
        json.dump(reactflow_data, f, indent=2)
    
    print(f"ReactFlow graph data saved to: {output_path}")
    print(f"Action graph: {len(action_nodes)} nodes and {len(action_edges)} edges")
    print(f"Component graph: {len(component_nodes)} nodes and {len(component_edges)} edges")

if __name__ == "__main__":
    # Example usage
    input_file = "./langgraph_detailed_graph_dump.json"  # Updated to use the new langgraph format file
    convert_graph_to_reactflow(input_file) 