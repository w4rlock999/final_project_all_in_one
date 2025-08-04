import json
import re, ast
import os
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from collections import defaultdict
from datetime import datetime


class TraceGraphFromLangGraph:

    def __init__(self, trace_dir: str):
        if not os.path.exists(trace_dir):
            raise ValueError(f"Directory does not exist: {trace_dir}")
            
        # Get all trace files and sort by timestamp
        self.trace_files = []
        for file in os.listdir(trace_dir):
            if file.endswith('.json'):
                file_path = os.path.join(trace_dir, file)
                # Verify file follows expected format
                if not re.match(r'trace_\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}\.\d{3}\.json$', file):
                    print(f"Warning: Skipping file that doesn't match expected format: {file}")
                    continue
                self.trace_files.append(file_path)
        
        if not self.trace_files:
            raise ValueError(f"No valid trace files found in directory: {trace_dir}")
            
        # Sort files by timestamp in filename
        self.trace_files.sort(key=lambda x: datetime.strptime(
            re.search(r'trace_(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}\.\d{3})', x).group(1),
            '%Y-%m-%d_%H-%M-%S.%f'
        ))

        # Initialize component mappings
        self.name_to_label = {
            'agents': {},
            'tools': {},
            'short_term_memory': {},
            'long_term_memory': {}
        }
        
        # Initialize trace-specific data
        self.traces = []  # List of trace data
        self.actions_per_trace = []  # List of actions for each trace
        self.edges_per_trace = []  # List of edges for each trace
        self.memory_per_trace = []  # List of memory contexts for each trace
        
        # Load all traces
        for trace_file in self.trace_files:
            with open(trace_file, 'r', encoding='utf-8') as f:
                trace_data = json.load(f)
                self.traces.append(trace_data)
                print(f"Loaded trace with {len(trace_data['data']['spans'])} spans from {trace_file}")

        # Shared components across all traces
        self.components = {
            'agents': [],
            'tools': [],
            'short_term_memory': [],
            'long_term_memory': []
        }

        # Initialize action counter for continuous numbering
        self.action_counter = 0

    def extract_user_input_from_trace(self, trace_data: dict, trace_idx: int) -> dict:
        """Extract user input from the first span of a trace"""
        first_span = trace_data['data']['spans'][0]
        user_message = first_span['attributes']['mlflow.spanInputs']['messages'][0]
        assert user_message['type'] == 'human', "First message should be from human"
        
        timestamp = re.search(r'trace_(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}\.\d{3})', 
                            self.trace_files[trace_idx]).group(1)
        
        return {
            "label": f"human_input_{trace_idx}",
            "time": timestamp,
            "input": user_message['content']
        }

    def extract_agents(self, trace_data: dict):
        """Extract agents from a trace, maintaining consistent labels"""
        spans = trace_data['data']['spans']
        
        for cur_span_idx, span in enumerate(spans):
            span_name = span.get('name', '')
            if re.match(r'^(?!path_from).*_agent_main_node.*$', span_name):
                # Extract agent name by removing '_main_node' and any trailing digits
                agent_name = re.sub(r"_main_node_\d+$", "", span_name)    

                # Use existing label if agent already known
                if agent_name in self.name_to_label['agents']:
                    continue
                
                # Create new label if new agent
                new_label = f"agent_{len(self.name_to_label['agents'])}"
                self.name_to_label['agents'][agent_name] = new_label
                
                # Get agent system prompt and tools
                span_id = span.get('span_id')
                agent_system_prompt = ""
                agent_tools = []
                chat_model_span = None
                
                for idx in range(cur_span_idx, len(spans)):
                    chat_model_span_candidate = spans[idx]
                    if (chat_model_span_candidate['attributes']['mlflow.spanType'] == "CHAT_MODEL" and 
                        chat_model_span_candidate['parent_span_id'] == span_id):
                        
                        chat_model_span = chat_model_span_candidate
                        for message in chat_model_span["attributes"]["mlflow.spanInputs"][0]:
                            if message.get('type', '') == "system":
                                agent_system_prompt = message.get('content', '')
                                break

                        for tool in chat_model_span["attributes"]["mlflow.chat.tools"]: 
                            agent_tools.append({
                                "tool_name": tool["function"]["name"],
                                "tool_description": tool["function"]["description"]
                            })
                        break

                # Add to components if new agent
                self.components['agents'].append({
                    "label": new_label,
                    "name": agent_name,
                    "system_prompt": agent_system_prompt,
                    "tools": agent_tools
                })

    def extract_tools(self, trace_data: dict):
        """Extract tools from a trace, maintaining consistent labels"""
        spans = trace_data['data']['spans']
        
        for span in spans:
            if span['attributes'].get('mlflow.spanType', '') == 'CHAT_MODEL':
                for tool in span["attributes"].get("mlflow.chat.tools", []):
                    tool_name = tool["function"]["name"]
                    
                    if tool_name not in self.name_to_label['tools']:
                        new_label = f"tool_{len(self.name_to_label['tools'])}"
                        self.name_to_label['tools'][tool_name] = new_label
                        
                        self.components['tools'].append({
                            "label": new_label,
                            "name": tool_name,
                            "description": tool["function"]["description"]
                        })

    def extract_memory(self, trace_data: dict, trace_idx: int):
        """Extract memory from a trace, maintaining consistent labels but separate contexts"""
        spans = trace_data['data']['spans']
        
        # Initialize memory context for this trace
        trace_memory = {
            'short_term_memory': [],
            'memory_keys': set()  # Track memory keys for this trace only
        }
        
        STM_idx = len(self.name_to_label['short_term_memory'])
        for span in spans:
            span_type = span.get("attributes", {}).get("mlflow.spanType", "")
            if span_type == "SHORT_TERM_MEMORY_UPDATE":
                span_inputs = span.get("attributes", {}).get("mlflow.spanInputs", {})
                span_outputs = span.get("attributes", {}).get("mlflow.spanOutputs", {})
                agent = span_inputs.get("agent")
                short_term_memory = span_inputs.get("short_term_memory")
                update = span_outputs.get("update")

                # Use a tuple of (agent, short_term_memory) as a unique key
                key = (agent, short_term_memory)
                memory_label = None
                
                # Check if memory exists in global mapping
                if key not in self.name_to_label['short_term_memory']:
                    memory_label = f"short_term_memory_{STM_idx}"
                    self.name_to_label['short_term_memory'][key] = memory_label
                    
                    # Add to global components
                    self.components['short_term_memory'].append({
                        "label": memory_label,
                        "agent": agent,
                        "short_term_memory": short_term_memory,
                    })
                    STM_idx += 1
                else:
                    memory_label = self.name_to_label['short_term_memory'][key]

                # Track memory in trace context
                if key not in trace_memory['memory_keys']:
                    trace_memory['short_term_memory'].append({
                        "label": memory_label,
                        "agent": agent,
                        "short_term_memory": short_term_memory,
                        "update": update
                    })
                    trace_memory['memory_keys'].add(key)
                else:
                    # Update existing memory in trace context
                    for mem in trace_memory['short_term_memory']:
                        if mem["label"] == memory_label:
                            existing_update = mem.get("update", [])
                            if existing_update is None:
                                existing_update = []
                            if update is None:
                                update = []
                            if isinstance(existing_update, dict):
                                existing_update = [existing_update]
                            if isinstance(update, dict):
                                update = [update]
                            if len(update) > len(existing_update):
                                mem["update"] = update
                            break

        # Add long-term memory if not already added
        if not self.components['long_term_memory']:
            self.components['long_term_memory'].append({
                "label": "long_term_memory_0",
                "long_term_memory": "knowledge_base_long_term_memory"
            })

        self.memory_per_trace.append(trace_memory)

    def extract_actions(self, trace_data: dict, trace_idx: int):
        """Extract actions from a trace"""
        actions = []
        trace_memory = self.memory_per_trace[trace_idx]
        
        # Add user input as first action
        user_input = self.extract_user_input_from_trace(trace_data, trace_idx)
        actions.append(user_input)
        
        # Process remaining actions
        spans = trace_data['data']['spans']
        for span in spans:
            if span['attributes'].get('mlflow.spanType', '') == 'CHAT_MODEL':
                # Find matching agent
                action_parent_span_id = span.get("parent_span_id")
                action_parent_span = next(
                    (s for s in spans if s.get('span_id') == action_parent_span_id), 
                    None
                )
                agent_main_node_name = action_parent_span["name"] if action_parent_span else None
                agent_name = re.sub(r"_main_node_\d+$", "", agent_main_node_name) if agent_main_node_name else None

                # Get agent label from mapping
                agent_label = self.name_to_label['agents'].get(agent_name)
                if not agent_label:
                    continue

                # Extract input and output
                input_data = span['attributes']['mlflow.spanInputs'][0]
                output_data = span['attributes']['mlflow.spanOutputs']
                span_id = span.get('span_id')

                # Prepare action with components
                action = {
                    "label": f"action_{self.action_counter}",
                    "input": input_data,
                    "output": output_data,
                    "span_id": span_id,
                    "agent_label": agent_label,
                    "agent_name": agent_name,
                    "components_in_input": [],
                    "components_in_output": []
                }

                # Check tools in input
                if input_data[-1]["type"] == 'tool':
                    tool_in_input_name = input_data[-1]["name"]
                    if tool_in_input_name in self.name_to_label['tools']:
                        action['components_in_input'].append(self.name_to_label['tools'][tool_in_input_name])

                # Check tools in output
                output_kwargs = output_data["generations"][0][0]["message"]["additional_kwargs"]
                if "tool_calls" in output_kwargs:
                    for tool_call in output_kwargs["tool_calls"]:
                        tool_name = tool_call["function"]["name"]
                        if tool_name in self.name_to_label['tools']:
                            action['components_in_output'].append(self.name_to_label['tools'][tool_name])

                # Check short term memory in input
                for memory_key, memory_label in self.name_to_label['short_term_memory'].items():
                    if memory_key[0] == agent_name:  # Check if memory belongs to this agent
                        action['components_in_input'].append(memory_label)

                # Check short term memory in output
                output_message_id = output_data["generations"][0][0]["message"]["id"]
                for memory in trace_memory['short_term_memory']:
                    for message in memory.get("update", []):
                        if isinstance(message, dict) and message.get("id") == output_message_id:
                            action['components_in_output'].append(memory["label"])
                            break

                # Check long term memory
                if input_data[-1]["type"] == "tool" and input_data[-1]["name"] == "get_information_from_knowledge_base":
                    action['components_in_input'].append("long_term_memory_0")
                if any(tool.get("function", {}).get("name") == "save_to_knowledge_base_LTM_tool" 
                      for tool in output_kwargs.get("tool_calls", [])):
                    action['components_in_output'].append("long_term_memory_0")

                actions.append(action)
                self.action_counter += 1

        self.actions_per_trace.append(actions)

    def generate_edges_for_trace(self, trace_idx: int):
        """Generate edges for a single trace"""
        actions = self.actions_per_trace[trace_idx]
        trace_memory = self.memory_per_trace[trace_idx]
        edges = []

        # Add edge from user input to first action (if there are actions after user input)
        if len(actions) > 1:
            edges.append({
                'source': actions[0]['label'],  # human_input_N
                'target': actions[1]['label']   # first actual action
            })

        # Process remaining actions (excluding user input)
        for i, source_action in enumerate(actions[1:], start=1):  # Start from first actual action
            for j, target_action in enumerate(actions[i+1:], start=i+1):  # Compare with subsequent actions
                source_action_memory_in_output = [
                    label for label in source_action.get("components_in_output", [])
                    if isinstance(label, str) and label.startswith("short_term_memory_")
                ]
                target_action_memory_in_input = [
                    label for label in target_action.get("components_in_input", [])
                    if isinstance(label, str) and label.startswith("short_term_memory_")
                ]
                
                # Create edge if memory connection exists
                for memory_label in source_action_memory_in_output:
                    if memory_label in target_action_memory_in_input:
                        edges.append({
                            'source': source_action['label'],
                            'target': target_action['label'],
                            'memory_label': memory_label
                        })

        self.edges_per_trace.append(edges)

    def extract_components(self):
        """Extract components from all traces"""
        for trace_idx, trace_data in enumerate(self.traces):
            self.extract_agents(trace_data)
            self.extract_tools(trace_data)
            self.extract_memory(trace_data, trace_idx)
            self.extract_actions(trace_data, trace_idx)
            self.generate_edges_for_trace(trace_idx)

    def generate_detailed_knowledge_graph(self):
        """Generate the final graph structure"""
        self.extract_components()
        
        return {
            "components": self.components,
            "actions": self.actions_per_trace,
            "actions_edge": self.edges_per_trace
        }