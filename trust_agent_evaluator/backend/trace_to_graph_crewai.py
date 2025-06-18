import json
import re, ast
from typing import Dict, List, Any
from dataclasses import dataclass
from collections import defaultdict


class TraceGraphFromCrewAI:

    def __init__(self, trace_file: str):
        with open(trace_file, 'r', encoding='utf-8') as f:
            self.trace_data = json.load(f)
        
        self.components = {}
        self.processes = []
        self.agents = []
        self.tools = []
        self.long_term_memory = []
        self.basic_graph = {}        

    # ====================================== 
    # Get CrewAI Spans from MLFlow trace
    # ====================================== 

    def get_crewai_kickoff_span(self) -> Dict[str, Any]:
        
        for span in self.trace_data['data']['spans']:
            span_name = span['name']
            if span_name == "Crew.kickoff":
                return span

        print("Error: Crew.kickoff span not found in trace data.")
        return {}
            
    def get_crewai_agent_spans(self):
        agent_execute_span = []

        for span in self.trace_data['data']['spans']:
            if span['attributes']["mlflow.spanType"] == "\"AGENT\"":
                agent_execute_span.append(span)
        
        return agent_execute_span
    
    def get_crewai_retriever_spans(self):
        retriever_span = []

        for span in self.trace_data['data']['spans']:
            if span['attributes']["mlflow.spanType"] == "\"RETRIEVER\"":
                retriever_span.append(span)
        
        return retriever_span

    def get_crewai_create_long_term_memory_spans(self):
        create_long_term_memory_spans = []
        retriever_spans = self.get_crewai_retriever_spans()

        for cur_retriever in retriever_spans:
            if "CrewAgentExecutor._create_long_term_memory_" in cur_retriever["name"]:
                create_long_term_memory_spans.append(cur_retriever)
        
        return create_long_term_memory_spans

    # ====================================== 
    # extract components from CrewAI trace (spans)
    # ======================================

    def extract_agents(self):
        
        kickoff_span : Dict[str, Any] = {}
        kickoff_span = self.get_crewai_kickoff_span()

        agent_from_kickoff = kickoff_span["attributes"]["agents"]    
        agent_string = agent_from_kickoff.strip('"')

        # Regex to remove everything between 'tools': [ and ]
        agent_string = re.sub(r"'tools':\s*\[.*?\]", "'tools': []", agent_string)
        agent_string = re.sub(r'\\"', '"', agent_string)

        agents_dict = ast.literal_eval(agent_string)
        for i, agent_obj in enumerate(agents_dict):
            # Clean \n from agent_obj["role"]
            agent_name = agent_obj["role"].replace("\\n", "").replace("\n", "").strip()
            # print(agent_name)
            
            self.agents.append({
                "label": f"agent_{i}",
                "name": agent_name,
                "backstory": agent_obj["backstory"],
                "goal": agent_obj["goal"],
                "model": agent_obj["llm"]
            })
        return self.agents

    def extract_tools(self):
        
        agent_spans = self.get_crewai_agent_spans()

        for agent_span in agent_spans:
            cur_agent_name = agent_span["attributes"]["role"]
            tools_string = agent_span["attributes"]["tools"].strip('"')
            tools_string = re.sub(r'\\"', '"', tools_string)

            tool_dict = ast.literal_eval(tools_string)
            
            for tool in tool_dict:
                if not any(existing_tool["name"] == tool["function"]["name"] for existing_tool in self.tools):
                    self.tools.append({
                        "name": tool["function"]["name"],
                        "description": tool["function"]["description"]
                    })
        return self.tools

    def extract_memory(self):
        memory_creation_spans = self.get_crewai_create_long_term_memory_spans()

        for cur_memory_creation_span in memory_creation_spans:
            self.long_term_memory.append({
                "memory" : cur_memory_creation_span["attributes"]["mlflow.spanInputs"]
            })

    def extract_components(self):
        self.extract_agents()
        self.extract_tools()
        self.extract_memory()
        
        self.components = {
            "agents": self.agents,
            "tools": self.tools,
            "memory": self.long_term_memory
        }
        
        return self.agents, self.tools, self.long_term_memory
    
    def extract_process(self):
        """Extract processes from LLM spans"""
        process_idx = 0
        
        for span in self.trace_data['data']['spans']:
            if span['attributes'].get('mlflow.spanType', '').strip('"') == 'LLM':
                # Extract input and output
                input_string = json.loads(span['attributes'].get('mlflow.spanInputs', '{}'))
                output_string = span['attributes'].get('mlflow.spanOutputs', '')
                
                # Get parent span to determine interaction components
                parent_id = span['parent_id']
                parent_span = next((s for s in self.trace_data['data']['spans'] 
                                  if s['context']['span_id'] == parent_id), None)
                
                self.processes.append({
                    "label": f"process_{process_idx}",
                    "input": json.dumps(input_string),
                    "output": output_string,
                })
                process_idx += 1

        return self.processes
    
    def generate_basic_graph(self):
        
        self.extract_components()
        self.extract_process()
        
        return {
            "components": {
                "agents": [
                    {
                        "label": a['label'],
                        "name": a['name'],
                        "backstory": a['backstory'],
                        "goal": a['goal'],
                        "model": a['model']
                    } for a in self.agents
                ],
                "tools": [
                    {
                        "label": f"tool_{i}",
                        "name": t['name'],
                        "description": t['description']
                    } for i, t in enumerate(self.tools)
                ],
                "memory": [
                    {
                        "label": f"memory_{i}",
                        "value": m['memory']
                    } for i, m in enumerate(self.long_term_memory)
                ]
            },
            "processes": [
                {
                    "label": p['label'],
                    "input": p['input'],
                    "output": p['output'],
                }
                for p in self.processes
            ]
        }
    

    def clean_text(self,text):
        # Convert to lowercase and remove special characters
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        # Remove extra whitespace
        text = ' '.join(text.split())
        return text

    def get_ngrams(self, text, n):
        # Split into tokens and generate n-grams
        tokens = text.split()
        return [' '.join(tokens[i:i+n]) for i in range(len(tokens)-n+1)]

    def calculate_similarity_score(self, target, source):
        # Clean both strings
        target = self.clean_text(target)
        source = self.clean_text(source)
        
        # Generate n-grams for both strings
        target_ngrams = set()
        for n in range(1, 4):  # Use 1-3 grams
            target_ngrams.update(self.get_ngrams(target, n))
        
        source_ngrams = set()
        for n in range(1, 4):
            source_ngrams.update(self.get_ngrams(source, n))
        
        # Calculate similarity
        if not target_ngrams or not source_ngrams:
            return 0.0
        
        intersection = len(target_ngrams.intersection(source_ngrams))
        union = len(target_ngrams.union(source_ngrams))
        target_ngrams_len = len(target_ngrams)
        source_ngrams_len = len(source_ngrams)
        
        return intersection / target_ngrams_len if target_ngrams_len > 0 else 0.0

    def is_process_exec_by_agent(self, process, agent_name, agent_backstory, agent_goal):
        """
            Check if the process is executed by the agent
        """

        process_input = json.loads(process['input'])

        # Calculate individual scores
        name_score = self.calculate_similarity_score(agent_name, str(process_input))
        backstory_score = self.calculate_similarity_score(agent_backstory, str(process_input))
        goal_score = self.calculate_similarity_score(agent_goal, str(process_input))
        
        # Calculate average score
        avg_score = (name_score + backstory_score + goal_score) / 3
        
        # print(f"agent: {agent_name}, avg_score: {avg_score}")

        # Return True if average score is above threshold
        return avg_score > 0.9  # Adjust threshold as needed


    def is_use_tool(self, process_string : str, tool_name):

        process_string_clean = self.clean_text(process_string)

        tool_name_str = f"action {self.clean_text(tool_name)}"
        if tool_name_str in process_string_clean:
            return True
        return False
    
    def is_use_memory(self, process_string : str, memory_string : str):

        # Calculate individual scores
        memory_score = self.calculate_similarity_score(memory_string, process_string)
        
        # Return True if average score is above threshold
        return memory_score > 0.6  # Adjust threshold as needed

    def is_process_dependency(self, process, prev_process):
        """
            Check if the process is dependent on the previous process
        """

        cur_process_input = self.clean_text(str(json.loads(process['input'])))
        prev_process_output = self.clean_text(str(json.loads(prev_process['output'])))

        dependency_score = self.calculate_similarity_score(prev_process_output, cur_process_input)
        # print(f"dependency_score, {dependency_score}, prev_process_output: {prev_process_output}")
        return dependency_score > 0.8


    def generate_detailed_knowledge_graph(self):
        """
            Generate the final graph structure
        """
        basic_graph = {}
        basic_graph = self.generate_basic_graph()

        # loop all process to get component relation
        for process_index, process in enumerate(basic_graph['processes']):
                
            # Check each component to find matching agent
            # Initialize agent attributes
            process['agent_label'] = ''
            process['agent_name'] = ''
            process['components_in_input'] = []
            process['components_in_output'] = []
            process['dependency_process'] = []

            # Check each agent to find matching agent
            for agent in basic_graph['components']['agents']:
                cur_agent_name = agent['name']
                cur_agent_backstory = agent['backstory']
                cur_agent_goal = agent['goal']

                if self.is_process_exec_by_agent(process, cur_agent_name, cur_agent_backstory, cur_agent_goal):
                    process['agent_label'] = agent['label']
                    process['agent_name'] = cur_agent_name
                    break

            # Check each tool to find matching tools
            for tool in basic_graph['components']['tools']:
                cur_tool_name = tool['name']

                if self.is_use_tool(str(process['input']), cur_tool_name):
                    process['components_in_input'].append(tool['label'])
                if self.is_use_tool(str(process['output']), cur_tool_name):
                    process['components_in_output'].append(tool['label'])
                            
            # Check each component to find matching memory
            for memory in basic_graph['components']['memory']:
                if self.is_use_memory(str(process['input']), memory['value']):
                    process['components_in_input'].append(memory['label'])
                if self.is_use_memory(str(process['output']), memory['value']):
                    process['components_in_output'].append(memory['label'])

            # Check each previous processs to find matching dependency
            # print(f"cur_process_index: {process['id']}")
            # print(f"cur_process_input: {self.clean_text(str(json.loads(process['input'])))}")
            for cur_previous_process_index in range(process_index-1, -1, -1):

                prev_process = basic_graph['processes'][cur_previous_process_index]

                # a longer dependency process check might be useful for propagation analysis later on
                if self.is_process_dependency(process, prev_process):
                    process['dependency_process'].append(prev_process['label'])
                else:
                    break  # Stop checking only when no dependency is found

                break


        # Initialize edges list
        basic_graph['process_edges'] = []
        
        # Generate edges for process dependency
        for i, cur_process in enumerate(basic_graph['processes']):
            for dependency_process_id in cur_process['dependency_process']:
                # Check if the target process is already in the edges list
                edge = {
                    'source': dependency_process_id,
                    'target': cur_process['label'],
                }
                basic_graph['process_edges'].append(edge)

        # Generate edges for long term memory
        # Iterate through processs to find memory connections
        for i, source_process in enumerate(basic_graph['processes']):
            # Only look at processs after current process
            if len(source_process['components_in_output'])>0:
                for target_process in basic_graph['processes'][i+1:]:
                    # Check if there's any memory connection between processs
                    for memory_idx in source_process['components_in_output']:
                        if memory_idx in target_process['components_in_input']:
                            # Create edge from source to target
                            edge = {
                                'source': source_process['label'],
                                'target': target_process['label'],
                                'memory_index': memory_idx
                            }
                            basic_graph['process_edges'].append(edge)

        
        self.basic_graph = basic_graph
        
        return basic_graph


