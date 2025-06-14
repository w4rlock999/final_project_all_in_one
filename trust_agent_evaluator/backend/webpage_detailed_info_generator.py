import json
from typing import Dict, List, Any

class WebpageDetailedInfoGenerator:
    def __init__(self, detailed_graph_with_jb: Dict[str, Any]):
        """
        Initialize the generator with the detailed graph data.
        
        Args:
            detailed_graph_with_jb (Dict[str, Any]): The detailed graph data containing nodes information
        """
        self.detailed_graph = detailed_graph_with_jb
        self.process_info = {"process": []}
        self.component_info = {
            "agent": [],
            "tool": [],
            "memory": []
        }
        
    def generate_process_info(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Generate process information from the detailed graph.
        
        Returns:
            Dict[str, List[Dict[str, Any]]]: Process information in the format {"process": [{}, {}]}
        """
        if "nodes" not in self.detailed_graph:
            raise ValueError("No 'nodes' found in the detailed graph")
            
        for idx, node in enumerate(self.detailed_graph["nodes"], 1):
            # Create a copy of the node data
            process_data = node.copy()
            # Replace the id with process_{idx}
            process_data["id"] = f"process_{idx}"
            self.process_info["process"].append(process_data)
            
        return self.process_info

    def generate_component_info(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Generate component information from the detailed graph.
        
        Returns:
            Dict[str, List[Dict[str, Any]]]: Component information with separate lists for each type
        """
        if "components" not in self.detailed_graph:
            raise ValueError("No 'components' found in the detailed graph")
            
        components = self.detailed_graph["components"]
        
        # Process agents
        if "agents" in components:
            for idx, agent in enumerate(components["agents"]):
                agent_data = agent.copy()
                agent_data["id"] = f"agent_{idx}"
                self.component_info["agent"].append(agent_data)
                
        # Process tools
        if "tools" in components:
            for idx, tool in enumerate(components["tools"]):
                tool_data = tool.copy()
                tool_data["id"] = f"tool_{idx}"
                self.component_info["tool"].append(tool_data)
                
        # Process memory
        if "memory" in components:
            for idx, memory in enumerate(components["memory"]):
                memory_data = memory.copy()
                memory_data["id"] = f"memory_{idx}"
                self.component_info["memory"].append(memory_data)
            
        return self.component_info
    
    def save_process_info(self, output_path: str = "process_info.json") -> None:
        """
        Save the generated process information to a JSON file.
        
        Args:
            output_path (str): Path where the process JSON file will be saved
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.process_info, f, indent=2, ensure_ascii=False)
            
    def save_component_info(self, output_path: str = "component_info.json") -> None:
        """
        Save the generated component information to a JSON file.
        
        Args:
            output_path (str): Path where the component JSON file will be saved
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.component_info, f, indent=2, ensure_ascii=False)
