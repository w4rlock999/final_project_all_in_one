import json
from reactflow_converter import ReactFlowConverter

def main():
    # Initialize the converter with the graph file containing jailbreak data
    converter = ReactFlowConverter(graph_file='./data/output/detailed_graph_with_jb.json')
    
    # Convert the graph to ReactFlow format with jailbreak data
    initial_nodes, initial_edges = converter.convert_to_reactflow_with_jb()
    
    # Save the ReactFlow data
    reactflow_data = [initial_nodes, initial_edges]
    with open('./data/output/reactflow_graph_with_jb.json', 'w') as f:
        json.dump(reactflow_data, f, indent=2)

if __name__ == "__main__":
    main() 