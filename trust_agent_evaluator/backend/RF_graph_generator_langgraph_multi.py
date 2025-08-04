import json

class ReactFlowGeneratorMulti:
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
        """Get the risk (importance) value for a component"""
        component_id = f"{component_type}_{index}"
        for feature in self.feature_importance.get("feature_importance", []):
            if feature["feature"] == component_id:
                return feature["importance"]
        return 0.0

    def _extract_index_from_label(self, label):
        """Extract the numeric index from a component label"""
        parts = label.split('_')
        return int(parts[-1])

    def generate_action_graph_RF(self):
        """
        Convert the multi-trace graph to ReactFlow format.
        Each trace forms its own tree, positioned from left to right.
        """
        reactflow_nodes = []
        reactflow_edges = []
        processed_edges = set()

        # Calculate base x-offset for each trace
        TRACE_X_OFFSET = 1200  # Horizontal space between traces
        ACTION_X_OFFSET = 150  # Horizontal offset for alternating actions within a trace
        
        # Process each trace's actions
        for trace_idx, trace_actions in enumerate(self.graph.get('actions', [])):
            base_x = trace_idx * TRACE_X_OFFSET  # Base x position for this trace
            
            # Add user input node at the top of the trace
            if trace_actions:  # If trace has actions
                user_input = trace_actions[0]  # First action is user input
                # Position human input node with offset
                HUMAN_INPUT_X_OFFSET = -100  # Move left by 100 units
                HUMAN_INPUT_Y_OFFSET = -50   # Move up by 50 units
                reactflow_nodes.append({
                    "id": user_input['label'],
                    "position": {
                        "x": base_x + HUMAN_INPUT_X_OFFSET,  # Center horizontally
                        "y": HUMAN_INPUT_Y_OFFSET  # Position higher up
                    },
                    "data": {
                        "label": user_input['label'],
                        "time": user_input['time'],
                        "input": user_input['input']
                    },
                    "type": "human_input_node"  # Special node type for user input
                })
            
            # Add action nodes for this trace
            for i, action in enumerate(trace_actions[1:], 1):  # Skip user input in enumeration
                # Alternate x positions for better visualization
                x_offset = (ACTION_X_OFFSET if i % 2 == 1 else -ACTION_X_OFFSET) if len(action.get("components_in_input", [])) > 0 else 0
                
                reactflow_nodes.append({
                    "id": action['label'],
                    "position": {
                        "x": base_x + x_offset,
                        "y": 200 * i  # Vertical spacing between actions
                    },
                    "data": {
                        "label": action['label'],
                        "agent_id": action['agent_label'],
                        "agent_name": action['agent_name'],
                        "input_components": action.get('components_in_input', []),
                        "output_components": action.get('components_in_output', [])
                    },
                    "type": "llm_call_node"
                })

        # Process edges for each trace
        for trace_idx, trace_edges in enumerate(self.graph.get('actions_edge', [])):
            for edge in trace_edges:
                edge_key = f"{edge['source']}-{edge['target']}"
                if edge_key not in processed_edges:
                    edge_style = {"strokeDasharray": "5, 5"} if edge.get('memory_label') else {"strokeDasharray": "none"}
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
        """Generate ReactFlow compatible format for component graph"""
        nodes = []
        edges = []
        processed_edges = set()
        
        # Get components
        agents_data = self.graph.get('components', {}).get('agents', [])
        memory_data = (self.graph.get('components', {}).get('short_term_memory', []) + 
                      self.graph.get('components', {}).get('long_term_memory', []))
        tools_data = self.graph.get('components', {}).get('tools', [])
        
        # Create agent nodes
        for agent in agents_data:
            agent_name = agent.get('name', agent.get('label', '')).strip().replace('\\n', ' ').strip()
            idx = self._extract_index_from_label(agent['label'])
            nodes.append({
                "id": agent['label'],
                "position": {
                    "x": 450 * idx,
                    "y": -150
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
            })
        
        # Create memory nodes
        for i, memory in enumerate(memory_data):
            idx = self._extract_index_from_label(memory['label'])
            memory_content = memory.get('short_term_memory', memory.get('long_term_memory', ''))
            nodes.append({
                "id": memory['label'],
                "position": {
                    "x": -500,
                    "y": 300 * i
                },
                "data": {
                    "label": memory['label'],
                    "memory_content": memory_content[:100] + "..." if len(memory_content) > 100 else memory_content,
                    "memory_index": idx,
                    "risk": self._get_component_risk('memory', idx)
                },
                "type": "memory_node"
            })

        # Create tool nodes
        for tool in tools_data:
            idx = self._extract_index_from_label(tool['label'])
            nodes.append({
                "id": tool['label'],
                "position": {
                    "x": 300 * idx,
                    "y": 300
                },
                "data": {
                    "label": tool['label'],
                    "tool_name": tool.get('name', tool['label']),
                    "description": tool.get('description', ''),
                    "parameters": tool.get('parameters', {}),
                    "risk": self._get_component_risk('tool', idx)
                },
                "type": "tool_node"
            })
        
        # Create edges between agents and components based on all actions across all traces
        for trace_actions in self.graph.get('actions', []):
            for action in trace_actions[1:]:  # Skip user input nodes
                agent_label = action['agent_label']
                
                # Process input components
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
                
                # Process output components
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