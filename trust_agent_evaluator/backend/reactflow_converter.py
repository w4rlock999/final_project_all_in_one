import json

class ReactFlowConverter:
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

    def convert_to_reactflow(self):
        """
        Convert the graph to ReactFlow format.
        
        Returns:
            tuple: (initial_nodes, initial_edges) in ReactFlow format
        """
        # Convert nodes
        initial_nodes = [
            {
                "id": str(node["id"]),
                "position": {
                    "x": 150 if (len(node["memory_in_input"]) > 0 and i % 2 == 1) else (-150 if (len(node["memory_in_input"]) > 0 and i % 2 == 0) else 0),
                    "y": 100 * i
                },
                "data": {
                    "label": f"Node {node['id']}",
                    "agent_id": f"{node['agent_index']}",
                    "agent_name": f"{node['agent_name']}"
                },
                "type": "llm_call_node"
            }
            for i, node in enumerate(self.graph['nodes'])
        ]

        # Convert edges
        initial_edges = [
            {
                "id": f"e{edge['source']}-{edge['target']}",
                "source": str(edge["source"]),
                "target": str(edge["target"]),
                "data": {
                    "from_memory": str("memory_index" in edge),
                    "memory_index": edge["memory_index"] if "memory_index" in edge else 'None'
                },
                "style": { "strokeDasharray": "5, 5" if "memory_index" in edge else 'none' }
            }
            for edge in self.graph['edges']
        ]

        return initial_nodes, initial_edges

    def convert_to_reactflow_with_jb(self):
        """
        Convert the graph to ReactFlow format with jailbreak success rates.
        
        Returns:
            tuple: (initial_nodes, initial_edges) in ReactFlow format with jailbreak data
        """
        # Convert nodes
        initial_nodes = [
            {
                "id": str(node["id"]),
                "position": {
                    "x": 150 if (len(node["memory_in_input"]) > 0 and i % 2 == 1) else (-150 if (len(node["memory_in_input"]) > 0 and i % 2 == 0) else 0),
                    "y": 100 * i
                },
                "data": {
                    "label": f"Node {node['id']}",
                    "agent_id": f"{node['agent_index']}",
                    "agent_name": f"{node['agent_name']}",
                    "jb_asr": f"{node.get('jailbreak_success_rate', 'N/A')}"
                },
                "type": "llm_call_node"
            }
            for i, node in enumerate(self.graph['nodes'])
        ]

        # Convert edges
        initial_edges = [
            {
                "id": f"e{edge['source']}-{edge['target']}",
                "source": str(edge["source"]),
                "target": str(edge["target"]),
                "data": {
                    "from_memory": str("memory_index" in edge),
                    "memory_index": edge["memory_index"] if "memory_index" in edge else 'None'
                },
                "style": { "strokeDasharray": "5, 5" if "memory_index" in edge else 'none' }
            }
            for edge in self.graph['edges']
        ]

        return initial_nodes, initial_edges 