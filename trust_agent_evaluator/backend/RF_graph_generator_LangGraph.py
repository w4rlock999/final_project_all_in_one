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
            
        # Load component feature importance data
        try:
            with open('./data/output/component_feature_importance.json', 'r') as f:
                self.feature_importance = json.load(f)
        except FileNotFoundError:
            print("Feature importance file not found")
            self.feature_importance = {"feature_importance": []}

    def _get_component_risk(self, component_type, index):
        """
        Get the risk (importance) value for a component from the feature importance data.
        
        Args:
            component_type (str): Type of component ('agent', 'memory', or 'tool')
            index (int): Index of the component
            
        Returns:
            float: Risk value for the component, 0 if not found
        """
        component_id = f"{component_type}_{index}"
        for feature in self.feature_importance.get("feature_importance", []):
            if feature["feature"] == component_id:
                return feature["importance"]
        return 0.0

    def _extract_index_from_label(self, label):
        """
        Extract the numeric index from a component label.
        
        Args:
            label (str): The component label (e.g., 'agent_0', 'short_term_memory_0', etc.)
            
        Returns:
            int: The extracted index
        """
        parts = label.split('_')
        return int(parts[-1])  # Always take the last part as the index

    def generate_action_graph_RF(self):
        """
        Convert the graph to ReactFlow format.
        Handles both cases with and without jailbreak data.
        
        Returns:
            tuple: (reactflow_nodes, reactflow_edges) in ReactFlow format
        """
        # Convert actions to nodes
        reactflow_nodes = [
            {
                "id": action['label'],
                "position": {
                    "x": (150 if (len(action.get("components_in_input", [])) > 0 and i % 2 == 1) else (-150 if (len(action.get("components_in_input", [])) > 0 and i % 2 == 0) else 0)) + 1900,
                    "y": 200 * i
                },
                "data": {
                    "label": action['label'],
                    "agent_id": action['agent_label'],
                    "agent_name": action['agent_name'],
                    "jb_asr": action.get('jailbreak_success_rate', '0'),
                    "input_components": action.get('components_in_input', []),
                    "output_components": action.get('components_in_output', [])
                },
                "type": "llm_call_node"
            }
            for i, action in enumerate(self.graph.get('actions', []))
        ]

        # Convert edges from actions_edge
        reactflow_edges = []
        processed_edges = set()  # Keep track of processed edge pairs
        
        # Process edges from actions_edge
        for edge in self.graph.get('actions_edge', []):
            edge_key = f"{edge['source']}-{edge['target']}"
            if edge_key not in processed_edges:
                edge_style = { "strokeDasharray": "5, 5" } if edge.get('memory_label') else { "strokeDasharray": "none" }
                reactflow_edges.append({
                    "id": f"e{edge_key}",
                    "source": edge['source'],
                    "target": edge['target'],
                    "data": {
                        "from_memory": "True" if edge.get('memory_label') else "False",
                        "memory_index": edge.get('memory_label', 'None')
                    },
                    "style": edge_style
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
        memory_data = self.graph.get('components', {}).get('short_term_memory', []) + self.graph.get('components', {}).get('long_term_memory', [])
        tools_data = self.graph.get('components', {}).get('tools', [])
        
        # Create agent nodes
        for agent in agents_data:
            agent_name = agent.get('name', agent.get('label', '')).strip().replace('\\n', ' ').strip()
            idx = self._extract_index_from_label(agent['label'])
            agent_node = {
                "id": agent['label'],
                "position": {
                    "x": 450 * idx,
                    "y": - 150
                },
                "data": {
                    "label": agent['label'],
                    "agent_name": agent_name,
                    "backstory": agent.get('system_prompt', ''),
                    "goal": agent.get('goal', ''),
                    "model": agent.get('model', ''),
                    "risk": self._get_component_risk('agent', idx)
                },
                "type": "agent_node"
            }
            nodes.append(agent_node)
        
        # Create memory nodes
        for i, memory in enumerate(memory_data):
            idx = self._extract_index_from_label(memory['label'])
            memory_node = {
                "id": memory['label'],
                "position": {
                    "x": - 500,
                    "y": 300 * i  # Use enumeration index for y-position to avoid overlaps
                },
                "data": {
                    "label": memory['label'],
                    "memory_content": memory.get('short_term_memory', memory.get('long_term_memory', ''))[:100] + "..." if len(memory.get('short_term_memory', memory.get('long_term_memory', ''))) > 100 else memory.get('short_term_memory', memory.get('long_term_memory', '')),
                    "memory_index": idx,
                    "risk": self._get_component_risk('memory', idx)
                },
                "type": "memory_node"
            }
            nodes.append(memory_node)

        # Create tool nodes
        for tool in tools_data:
            idx = self._extract_index_from_label(tool['label'])
            tool_node = {
                "id": tool['label'],
                "position": {
                    "x": 300 * idx,
                    "y": 300  # Position tools below agents
                },
                "data": {
                    "label": tool['label'],
                    "tool_name": tool.get('name', tool['label']),
                    "description": tool.get('description', ''),
                    "parameters": tool.get('parameters', {}),
                    "risk": self._get_component_risk('tool', idx)
                },
                "type": "tool_node"
            }
            nodes.append(tool_node)
        
        # Create edges between agents and components based on actions
        for action in self.graph.get('actions', []):
            agent_label = action['agent_label']
            
            # Create edges for input components
            for component in action.get('components_in_input', []):
                edge_key = f"{agent_label}-{component}"
                if edge_key not in processed_edges:
                    edges.append({
                        "id": f"e{edge_key}",
                        "source": agent_label,
                        "target": component,
                        "data": {
                            "type": "memory_connection" if "memory" in component else "tool_connection"
                        }
                    })
                    processed_edges.add(edge_key)
            
            # Create edges for output components
            for component in action.get('components_in_output', []):
                edge_key = f"{agent_label}-{component}"
                if edge_key not in processed_edges:
                    edges.append({
                        "id": f"e{edge_key}",
                        "source": agent_label,
                        "target": component,
                        "data": {
                            "type": "memory_connection" if "memory" in component else "tool_connection"
                        }
                    })
                    processed_edges.add(edge_key)
        
        return nodes, edges