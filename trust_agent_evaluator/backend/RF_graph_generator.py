import json

class ReactFlowGenerator:
    def __init__(self, graph_data=None, graph_file=None):
        """
        Initialize the ReactFlow converter with either graph data or a graph file.
        
        Args:
            graph_data (dict, optional): The graph data dictionary
            graph_file (str, optional): Path to the graph JSON file
        """
        if graph_file:
            with open(graph_file, 'r') as f:
                self.graph = json.load(f)
        else:
            self.graph = graph_data

    def generate_process_graph_RF(self):
        """
        Convert the graph to ReactFlow format.
        Handles both cases with and without jailbreak data.
        
        Returns:
            tuple: (reactflow_nodes, reactflow_edges) in ReactFlow format
        """
        # Convert nodes
        reactflow_nodes = [
            {
                "id": f"process_{node['id']}",
                "position": {
                    "x": (150 if (len(node["memory_in_input"]) > 0 and i % 2 == 1) else (-150 if (len(node["memory_in_input"]) > 0 and i % 2 == 0) else 0)) + 1900,
                    "y": 200 * i
                },
                "data": {
                    "label": f"process_{node['id']}",
                    "agent_id": f"{node['agent_index']}",
                    "agent_name": f"{node['agent_name']}",
                    "jb_asr": f"{node.get('jailbreak_success_rate', '0')}",
                    "input_components": [
                        f"agent_{node['agent_index']}",
                        *[f"memory_{idx}" for idx in node.get('memory_in_input', [])],
                        *[f"tool_{idx}" for idx in node.get('tool_in_input', [])]
                    ]
                },
                "type": "llm_call_node"
            }
            for i, node in enumerate(self.graph['nodes'])
        ]

        # Convert edges
        # First process non-memory edges
        reactflow_edges = []
        processed_edges = set()  # Keep track of processed edge pairs
        
        # Process non-memory edges first
        for edge in self.graph['edges']:
            edge_key = f"{edge['source']}-{edge['target']}"
            if "memory_index" not in edge and edge_key not in processed_edges:
                reactflow_edges.append({
                    "id": f"e{edge['source']}-{edge['target']}",
                    "source": f"process_"+str(edge["source"]),
                    "target": f"process_"+str(edge["target"]),
                    "data": {
                        "from_memory": "False",
                        "memory_index": 'None'
                    },
                    "style": { "strokeDasharray": "none" }
                })
                processed_edges.add(edge_key)
        
        # Then process memory edges if no non-memory edge exists
        for edge in self.graph['edges']:
            edge_key = f"{edge['source']}-{edge['target']}"
            if "memory_index" in edge and edge_key not in processed_edges:
                reactflow_edges.append({
                    "id": f"e{edge['source']}-{edge['target']}",
                    "source": f"process_"+str(edge["source"]),
                    "target": f"process_"+str(edge["target"]),
                    "data": {
                        "from_memory": "True",
                        "memory_index": edge["memory_index"]
                    },
                    "style": { "strokeDasharray": "5, 5" }
                })
                processed_edges.add(edge_key)

        return reactflow_nodes, reactflow_edges

    def generate_component_graph_RF(self):
        """
        Generate ReactFlow compatible format for component graph
        Creates nodes for agents, memory, and tools from the components section
        Creates edges between agents and tools (agent always as source, tool always as target)
        Creates edges between agents and memory (agent always as source, memory always as target)
        
        Returns:
            dict: ReactFlow compatible graph data
        """
        nodes = []
        edges = []
        processed_edges = set()  # Keep track of processed tool-agent and memory-agent connections
        
        # Get agents, memory, and tools from the components section
        agents_data = self.graph.get('components', {}).get('agents', [])
        memory_data = self.graph.get('components', {}).get('memory', [])
        tools_data = self.graph.get('components', {}).get('tools', [])
        
        # Create agent nodes
        for i, agent in enumerate(agents_data):
            agent_name = agent.get('name', f'Agent {i}').strip().replace('\\n', ' ').strip()
            agent_node = {
                "id": f"agent_{i}",
                "position": {
                    "x": 450 * i,
                    "y": - 150
                },
                "data": {
                    "label": f"agent_{i}",
                    "agent_name": agent_name,
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
                    "x": - 500,
                    "y": 300 * i
                },
                "data": {
                    "label": f"Memory {i}",
                    "memory_content": memory.get('value', '')[:100] + "..." if len(memory.get('value', '')) > 100 else memory.get('value', ''),
                    "memory_index": i
                },
                "type": "memory_node"
            }
            nodes.append(memory_node)

        # Create tool nodes
        for i, tool in enumerate(tools_data):
            tool_node = {
                "id": f"tool_{i}",
                "position": {
                    "x": 300 * i,
                    "y": 300  # Position tools below agents
                },
                "data": {
                    "label": f"Tool {i}",
                    "tool_name": tool.get('name', f'Tool {i}'),
                    "description": tool.get('description', ''),
                    "parameters": tool.get('parameters', {})
                },
                "type": "tool_node"
            }
            nodes.append(tool_node)
        
        # Create edges between agents and tools (agent always as source, tool always as target)
        for node in self.graph.get('nodes', []):
            agent_index = node.get('agent_index')
            if agent_index is not None:
                # Combine both tool inputs and outputs to create edges
                all_tools = set(node.get('tool_in_input', []) + node.get('tool_in_output', []))
                for tool_index in all_tools:
                    edge_key = f"agent_{agent_index}-tool_{tool_index}"
                    if edge_key not in processed_edges:
                        edges.append({
                            "id": f"e{edge_key}",
                            "source": f"agent_{agent_index}",
                            "target": f"tool_{tool_index}",
                            "data": {
                                "type": "tool_connection"
                            }
                        })
                        processed_edges.add(edge_key)
                
                # Combine both memory inputs and outputs to create edges
                all_memories = set(node.get('memory_in_input', []) + node.get('memory_in_output', []))
                for memory_index in all_memories:
                    edge_key = f"agent_{agent_index}-memory_{memory_index}"
                    if edge_key not in processed_edges:
                        edges.append({
                            "id": f"e{edge_key}",
                            "source": f"agent_{agent_index}",
                            "target": f"memory_{memory_index}",
                            "data": {
                                "type": "memory_connection"
                            }
                        })
                        processed_edges.add(edge_key)
        
        return nodes, edges