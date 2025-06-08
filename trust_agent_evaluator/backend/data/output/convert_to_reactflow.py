import json
from typing import Dict, List, Any

def generate_reactflow_graph(detailed_graph_path: str, output_path: str = None):
    """
    Convert detailed graph JSON to ReactFlow compatible format
    Creates nodes for agents and memory from the detailed graph data
    """
    # Load the detailed graph data
    with open(detailed_graph_path, 'r') as f:
        data = json.load(f)
    
    nodes = []
    edges = []
    
    # Get agents and memory from the components section
    agents_data = data.get('components', {}).get('agents', [])
    memory_data = data.get('components', {}).get('memory', [])
    
    # Create agent nodes
    for i, agent in enumerate(agents_data):
        agent_node = {
            "id": f"agent_{i}",
            "position": {
                "x": 200 * i,
                "y": 100
            },
            "data": {
                "label": f"🤖 {agent.get('name', f'Agent {i}').strip()}",
                "agent_name": agent.get('name', f'Agent {i}').strip(),
                "backstory": agent.get('backstory', ''),
                "goal": agent.get('goal', ''),
                "model": agent.get('model', '')
            },
            "type": "agent_node"
        }
        nodes.append(agent_node)
    
    # Create memory nodes
    for i, memory in enumerate(memory_data):
        memory_node = {
            "id": f"memory_{i}",
            "position": {
                "x": 200 * i,
                "y": 300
            },
            "data": {
                "label": f"🧠 Memory {i}",
                "memory_content": memory.get('value', '')[:100] + "..." if len(memory.get('value', '')) > 100 else memory.get('value', ''),
                "memory_index": i
            },
            "type": "memory_node"
        }
        nodes.append(memory_node)
    
    # Create edges between agents and memory based on execution flow
    execution_nodes = data.get('nodes', [])
    
    # Track which agents use which memory
    agent_memory_connections = {}
    
    for exec_node in execution_nodes:
        agent_name = exec_node.get('agent_name', '').strip()
        memory_in_input = exec_node.get('memory_in_input', [])
        memory_in_output = exec_node.get('memory_in_output', [])
        
        # Find the agent index
        agent_index = None
        for i, agent in enumerate(agents_data):
            if agent.get('name', '').strip() == agent_name:
                agent_index = i
                break
        
        if agent_index is not None:
            # Create connections for memory inputs
            for mem_idx in memory_in_input:
                if mem_idx < len(memory_data):
                    edge_id = f"memory_{mem_idx}_to_agent_{agent_index}"
                    if edge_id not in [edge['id'] for edge in edges]:
                        edges.append({
                            "id": edge_id,
                            "source": f"memory_{mem_idx}",
                            "target": f"agent_{agent_index}",
                            "type": "smoothstep",
                            "style": {"stroke": "#9c27b0", "strokeWidth": 2},
                            "markerEnd": {"type": "arrowclosed", "color": "#9c27b0"},
                            "label": "input"
                        })
            
            # Create connections for memory outputs
            for mem_idx in memory_in_output:
                if mem_idx < len(memory_data):
                    edge_id = f"agent_{agent_index}_to_memory_{mem_idx}"
                    if edge_id not in [edge['id'] for edge in edges]:
                        edges.append({
                            "id": edge_id,
                            "source": f"agent_{agent_index}",
                            "target": f"memory_{mem_idx}",
                            "type": "smoothstep",
                            "style": {"stroke": "#7b1fa2", "strokeWidth": 2},
                            "markerEnd": {"type": "arrowclosed", "color": "#7b1fa2"},
                            "label": "output"
                        })
    
    # Create the final ReactFlow compatible structure
    reactflow_data = {
        "nodes": nodes,
        "edges": edges,
        "viewport": {
            "x": 0,
            "y": 0,
            "zoom": 0.8
        }
    }
    
    # Save to output file
    if output_path is None:
        output_path = detailed_graph_path.replace('.json', '_reactflow.json')
    
    with open(output_path, 'w') as f:
        json.dump(reactflow_data, f, indent=2)
    
    print(f"ReactFlow graph data saved to: {output_path}")
    print(f"Generated {len(nodes)} nodes and {len(edges)} edges")
    print(f"Agents: {len([n for n in nodes if n['type'] == 'agent_node'])}")
    print(f"Memory nodes: {len([n for n in nodes if n['type'] == 'memory_node'])}")
    
    return reactflow_data

if __name__ == "__main__":
    # Convert the detailed graph to ReactFlow format
    input_file = "detailed_graph_with_jb.json"
    output_file = "reactflow_graph_data.json"
    
    try:
        reactflow_data = generate_reactflow_graph(input_file, output_file)
        
        # Print summary
        print("\n=== Conversion Summary ===")
        print(f"Total nodes: {len(reactflow_data['nodes'])}")
        print(f"Total edges: {len(reactflow_data['edges'])}")
        
    except FileNotFoundError:
        print(f"Error: Could not find input file '{input_file}'")
        print("Please make sure the detailed graph JSON file exists in the current directory.")
    except Exception as e:
        print(f"Error during conversion: {str(e)}") 