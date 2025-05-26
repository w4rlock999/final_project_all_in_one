import os
from trace_to_graph import TraceGraph
import json

def main():
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Construct the path to the MLflow trace JSON file
    trace_file = os.path.join(current_dir, 'data', 'mlflow_trace.json')
    
    # Create TraceGraph instance and process the trace
    trace_graph = TraceGraph(trace_file)
    
    # Generate the basic graph structure
    # basic_graph = trace_graph.generate_basic_graph()
    
    # Generate the detailed graph with relationships
    detailed_graph = trace_graph.generate_graph()
    
    # Convert to ReactFlow format
    reactflow_graph = trace_graph.convert_graph_to_reactflow()
    
    # Save the results
    output_dir = os.path.join(current_dir, 'data', 'output')
    os.makedirs(output_dir, exist_ok=True)
    
    # Save basic graph
    # with open(os.path.join(output_dir, 'basic_graph.json'), 'w') as f:
    #     json.dump(basic_graph, f, indent=2)
    
    # Save detailed graph
    with open(os.path.join(output_dir, 'detailed_graph.json'), 'w') as f:
        json.dump(detailed_graph, f, indent=2)
    
    # Save ReactFlow graph
    with open(os.path.join(output_dir, 'reactflow_graph.json'), 'w') as f:
        json.dump(reactflow_graph, f, indent=2)

if __name__ == "__main__":
    main()
