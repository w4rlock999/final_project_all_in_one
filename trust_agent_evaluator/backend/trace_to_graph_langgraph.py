import json
import re, ast
from typing import Dict, List, Any
from dataclasses import dataclass
from collections import defaultdict


class TraceGraphFromLangGraph:

    def __init__(self, trace_file: str):
        with open(trace_file, 'r', encoding='utf-8') as f:
            self.trace = json.load(f)

        print("trace [data] [span] length:", len(self.trace['data']['spans']))
        
        self.components = {}
        self.actions = []
        self.agents = []
        self.tools = []
        self.long_term_memory = []
        self.short_term_memory = []
        self.basic_graph = {}        

    # ================================================== 
    # extract components from LangGraph trace (spans)
    # ================================================== 

    def extract_agents(self):
        print("extracting agent...")
        print(f"got {len(self.trace['data']['spans'])} number of spans")
        
        spans = self.trace['data']['spans']
        agent_idx = 0
        for cur_span_idx, span in enumerate(spans):
            span_name = span.get('name', '')
            if re.match(r'^(?!path_from).*_agent_main_node.*$', span_name):
                
                # Extract agent name by removing '_main_node' and any trailing digits
                agent_name = re.sub(r"_main_node_\d+$", "", span_name)    

                # Skip if agent_name already exists in self.agents by "name" 
                if any(agent.get("name") == agent_name for agent in self.agents):
                    continue
                
                # searching for system prompt 
                span_id = span.get('span_id')
                agent_system_prompt = ""
                agent_tools = []
                chat_model_span = None
                for idx in range(cur_span_idx, len(spans)):
                    chat_model_span_candidate = spans[idx]

                    if chat_model_span_candidate['attributes']['mlflow.spanType'] == "CHAT_MODEL" and \
                       chat_model_span_candidate['parent_span_id'] == span_id:
                        
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

                # append agent label, agent name, and system prompt
                self.agents.append({
                    "label": f"agent_{agent_idx}",
                    "name": agent_name,
                    "system_prompt": agent_system_prompt,
                    "tools": agent_tools
                })
                agent_idx += 1

        # for agent in self.agents:
        #     print(f"agent name:", agent.get("name"))
            # print(f"agent label:", agent.get("label"))
            # print(f"agent prompt:", agent.get("system_prompt"))
            # print(f"agent tools:", agent.get("tools"))
            # print("--------------------------------")


    def extract_tools(self):

        self.tools = []
        tool_names = set()
        tool_idx=0
        for agent in self.agents:

            for tool in agent.get("tools", []):
                name = tool.get("tool_name")
                desc = tool.get("tool_description")
                if name and name not in tool_names:
                    self.tools.append({
                        "label": f"tool_{tool_idx}",
                        "name": name,
                        "description": desc
                    })
                    tool_names.add(name)
                    tool_idx += 1
        return self.tools

    def extract_memory(self):
        spans = self.trace['data']['spans']

        # self.short_term_memory = []
        memory_keys = set()
        STM_idx=0
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
                if key not in memory_keys:
                    self.short_term_memory.append({
                        "label": f"short_term_memory_{STM_idx}",
                        "agent": agent,
                        "short_term_memory": short_term_memory,
                        "update": update
                    })
                    memory_keys.add(key)
                    STM_idx += 1
                else:
                    # Check if the key already exists in self.short_term_memory
                    for mem in self.short_term_memory:
                        if mem["agent"] == agent and mem["short_term_memory"] == short_term_memory:
                            # Compare the length of the current update with the existing one
                            existing_update = mem.get("update", [])
                            # If either is None, treat as empty list
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
                    
        self.long_term_memory.append({
            "label": "long_term_memory_0",
            "long_term_memory": "knowledge_base_long_term_memory"
        })

        print(f"get {len(self.short_term_memory)} number of short term memory")
        print(f"get {len(self.long_term_memory)} number of long term memory")

        # print("Short Term Memory:", getattr(self, "short_term_memory", []))
        # print("Long Term Memory:", getattr(self, "long_term_memory", []))

    def extract_components(self):
        self.extract_agents()
        self.extract_tools()
        self.extract_memory()
        
        self.components = {
            "agents": self.agents,
            "tools": self.tools,
            "short_term_memory": self.short_term_memory,
            "long_term_memory": self.long_term_memory
        }
    
    def extract_actions(self):
        """Extract actions from LLM spans"""
        self.actions = []
        action_idx = 0
        for span in self.trace['data']['spans']:
            if span['attributes'].get('mlflow.spanType', '') == 'CHAT_MODEL':
                # Find matching agent from parent span
                action_span = span
                action_parent_span_id = action_span.get("parent_span_id")
                action_parent_span = next((s for s in self.trace['data']['spans'] if s.get('span_id') == action_parent_span_id), None)
                agent_main_node_name = action_parent_span["name"] if action_parent_span else None
                agent_name = agent_main_node_name.replace('_main_node', '').rstrip('0123456789_') if agent_main_node_name else None

                # Find agent in self.agents that matches agent_name
                matching_agent = None
                action_agent_label = None
                action_agent_name = None
                for agent in getattr(self, "agents", []):
                    if agent.get('name') == agent_name:
                        matching_agent = agent
                        action_agent_name = matching_agent["name"]
                        action_agent_label = matching_agent["label"]
                        break

                # Skip if agent is not found
                if matching_agent is None:
                    continue

                # Extract input and output
                input = span['attributes']['mlflow.spanInputs'][0]
                output = span['attributes']['mlflow.spanOutputs']
                span_id = span.get('span_id', None)

                self.actions.append({
                    "label": f"action_{action_idx}",
                    "input": input,
                    "output": output,
                    "span_id": span_id,
                    "agent_label": action_agent_label,
                    "agent_name": action_agent_name
                })
                action_idx += 1

        print(f"got {len(self.actions)} number of actions")

        return self.actions
    
    def generate_basic_graph(self):
        
        self.extract_components()
        self.extract_actions()
        
        return {
            "components": {
                "agents": [
                    {
                        "label": a['label'],
                        "name": a['name'],
                        "system_prompt": a['system_prompt'],
                        "tools": a['tools']
  
                    } for a in self.agents
                ],
                "tools": [
                    {
                        "label": t['label'],
                        "name": t['name'],
                        "description": t['description']
                    } for t in self.tools
                ],
                "short_term_memory": [
                    {
                        "label": ms['label'],
                        "short_term_memory": ms['short_term_memory'],
                        "agent": ms['agent'],
                    } for ms in self.short_term_memory
                ],
                "long_term_memory": [
                    {
                        "label": ml['label'],
                        "long_term_memory": ml['long_term_memory'],
                    } for ml in self.long_term_memory
                ]
            },
            "actions": [
                {
                    "label": a['label'],
                    "input": a['input'],
                    "output": a['output'],
                    "span_id": a['span_id'],
                    "agent_label": a['agent_label'],
                    "agent_name": a['agent_name']
                }
                for a in self.actions
            ]
        }

    def generate_detailed_knowledge_graph(self):
        """
            Generate the final graph structure
        """
        basic_graph = {}
        basic_graph = self.generate_basic_graph()
        

        # loop through each action to get component relation
        for action_index, action in enumerate(basic_graph['actions']):
            # print('action label: ', action["label"])    
            # Initialize action attributes
            
            action['components_in_input'] = []
            action['components_in_output'] = []
            action['dependency_action'] = []

            # print("action agent label: ", action["agent_label"])
            # print("action agent name: ", action["agent_name"])
            
            # Check each tool to find matching tools
            # check tool in input's last message
            tool_in_input_labels = []
            if action["input"][-1]["type"] == 'tool':
                tool_in_input_name = action["input"][-1]["name"]
            
                for tool in self.tools:
                    if tool.get('name') == tool_in_input_name:
                        tool_in_input_labels.append(tool["label"])
                        break

            for label in tool_in_input_labels:
                action['components_in_input'].append(label)

            # find tool in output
            tool_in_output = []
            action_output_kwargs = action["output"]["generations"][0][0]["message"]["additional_kwargs"]
            if "tool_calls" in action_output_kwargs:
                tool_calls = action_output_kwargs["tool_calls"]
                for tool_call in tool_calls:
                    cur_tool_name = tool_call["function"]["name"]
                    tool_in_output.append(cur_tool_name)

            # Find matching tools in self.tools for each tool in tool_in_output
            tool_in_output_labels = []
            for tool_name in tool_in_output:
                for tool in self.tools:
                    if tool.get('name') == tool_name:
                        tool_in_output_labels.append(tool["label"])
                        break

            for label in tool_in_output_labels:
                action['components_in_output'].append(label)

            # find short term memory in input and output
            st_memory_in_input_label = []
            # say we have "complete" memory,
            # say memory A have 10 entry, 3 entry is in the current input
            # should we say memory A is IN the input?
            # -> yes
            # why? because in the future, 3 entry can be 5 entry can be 9 entry
            # the point is that memory A have a chance to propagate to current input
            # OR
            # only the current message state should be counted as in input
            # -> according to the agent's memory then?
            # how to tell memory A propagate to memory B then? >>> from memory_in_output
            # more like how a **specific** memory entry could propagate
            action_agent_name = action["agent_name"]
            for memory in self.short_term_memory:
                if memory.get('agent') == action_agent_name:
                    memory_label = memory.get('label')
                    short_term_memory_key = memory.get('short_term_memory')
                    st_memory_in_input_label.append(memory_label)

                    # You can use memory_label and short_term_memory_key as needed

            for label in st_memory_in_input_label:
                action['components_in_input'].append(label)

            st_memory_in_output_label = []
            # need to have a "complete" memory, to check if the current output is in each memory
            action_output_message_id = action["output"]["generations"][0][0]["message"]["id"]
            for short_term_memory in self.short_term_memory:
                # print("length of STM",len(short_term_memory["update"]))
                for short_term_memory_message in short_term_memory["update"]:
                    if short_term_memory_message["id"] == action_output_message_id:
                        st_memory_in_output_label.append(short_term_memory["label"])
                        break
            
            for label in st_memory_in_output_label:
                action['components_in_output'].append(label)

            lt_memory_in_input_label = []
            last_action_message = action["input"][-1]
            if last_action_message["type"] == "tool" and last_action_message["name"] == "get_information_from_knowledge_base":
                lt_memory_in_input_label.append(self.long_term_memory[0]["label"])

            lt_memory_in_output_label = []
            if "save_to_knowledge_base_LTM_tool" in tool_in_output:
                lt_memory_in_output_label.append(self.long_term_memory[0]["label"])

            # print("LTM in input: ", lt_memory_in_input_label)

            for label in lt_memory_in_input_label:
                action['components_in_input'].append(label)

            for label in lt_memory_in_output_label:
                action['components_in_output'].append(label)


            # print("components_in_output: ", action['components_in_output'])

            # print("="*30)


        # Initialize edges list


        # Generate edges for process dependency


        # Generate edges for long term memory
        # Iterate through processs to find memory connections

        self.basic_graph = basic_graph
        
        self.basic_graph["actions_edge"] = []

        # Nested for loop as requested
        for i, source_action in enumerate(self.basic_graph["actions"]):
            for j, target_action in enumerate(self.basic_graph["actions"][i+1:], start=i+1):
                source_action_memory_in_output = [label for label in source_action["components_in_output"] if isinstance(label, str) and label.startswith("short_term_memory_")]
                target_action_memory_in_input = [label for label in target_action["components_in_input"] if isinstance(label, str) and label.startswith("short_term_memory_")]
                
                # print("source memory in output", source_action_memory_in_output)
                # print("target memory in input", target_action_memory_in_input)

                for cur_source_memory in source_action_memory_in_output:
                    if cur_source_memory in target_action_memory_in_input:
                        edge = {
                            'source': source_action['label'],
                            'target': target_action['label'],
                            'memory_label': cur_source_memory
                        }
                        basic_graph["actions_edge"].append(edge)

        # import json
        # with open("langgraph_basic_graph_dump.json", "w", encoding="utf-8") as f:
        #     json.dump(self.basic_graph, f, ensure_ascii=False, indent=2)

        # edge = {
        #     'source': source_action['label'],
        #     'target': target_action['label'],
        #     'memory_index': memory_idx
        # }

        # print(self.basic_graph)

        return basic_graph


