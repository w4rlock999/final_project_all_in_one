'use client';
import React, { useState, useCallback } from 'react';
import {
  ReactFlow,
  ReactFlowProvider,
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  useReactFlow,
  Panel,
  Node,
  ReactFlowInstance,
  BackgroundVariant,
  Connection,
  Edge,
  NodeMouseHandler,
  OnNodesChange,
  OnEdgesChange,
  OnInit
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import genericLLMNode from './genericLLMNode';

interface CustomNodeData extends Record<string, unknown> {
  label: string;
  agent_id: string;
  agent_name: string;
  jb_asr: string;
}

interface CustomEdgeData extends Record<string, unknown> {
  from_memory: string;
  memory_index: string | number;
}

type CustomNode = Node<CustomNodeData>;
type CustomEdge = Edge<CustomEdgeData>;

const flowKey = 'example-flow';

// [{'id': '1', 'position': {'x': 0, 'y': 0}, 'data': {'label': 'Node 1', 'agent_id': '0', 'agent_name': 'Candidate and Job Analyst for tech industry hiring\\n'}, 'type': 'llm_call_node'}, {'id': '2', 'position': {'x': 0, 'y': 100}, 'data': {'label': 'Node 2', 'agent_id': '0', 'agent_name': 'Candidate and Job Analyst for tech industry hiring\\n'}, 'type': 'llm_call_node'}, {'id': '3', 'position': {'x': -150, 'y': 200}, 'data': {'label': 'Node 3', 'agent_id': '0', 'agent_name': 'Candidate and Job Analyst for tech industry hiring\\n'}, 'type': 'llm_call_node'}, {'id': '4', 'position': {'x': 150, 'y': 300}, 'data': {'label': 'Node 4', 'agent_id': '0', 'agent_name': 'Candidate and Job Analyst for tech industry hiring\\n'}, 'type': 'llm_call_node'}, {'id': '5', 'position': {'x': -150, 'y': 400}, 'data': {'label': 'Node 5', 'agent_id': '1', 'agent_name': 'Job Profiler for tech industry hiring\\n'}, 'type': 'llm_call_node'}, {'id': '6', 'position': {'x': 150, 'y': 500}, 'data': {'label': 'Node 6', 'agent_id': '1', 'agent_name': 'Job Profiler for tech industry hiring\\n'}, 'type': 'llm_call_node'}, {'id': '7', 'position': {'x': -150, 'y': 600}, 'data': {'label': 'Node 7', 'agent_id': '0', 'agent_name': 'Candidate and Job Analyst for tech industry hiring\\n'}, 'type': 'llm_call_node'}, {'id': '8', 'position': {'x': 150, 'y': 700}, 'data': {'label': 'Node 8', 'agent_id': '0', 'agent_name': 'Candidate and Job Analyst for tech industry hiring\\n'}, 'type': 'llm_call_node'}, {'id': '9', 'position': {'x': -150, 'y': 800}, 'data': {'label': 'Node 9', 'agent_id': '0', 'agent_name': 'Candidate and Job Analyst for tech industry hiring\\n'}, 'type': 'llm_call_node'}, {'id': '10', 'position': {'x': 150, 'y': 900}, 'data': {'label': 'Node 10', 'agent_id': '0', 'agent_name': 'Candidate and Job Analyst for tech industry hiring\\n'}, 'type': 'llm_call_node'}, {'id': '11', 'position': {'x': -150, 'y': 1000}, 'data': {'label': 'Node 11', 'agent_id': '0', 'agent_name': 'Candidate and Job Analyst for tech industry hiring\\n'}, 'type': 'llm_call_node'}, {'id': '12', 'position': {'x': 150, 'y': 1100}, 'data': {'label': 'Node 12', 'agent_id': '0', 'agent_name': 'Candidate and Job Analyst for tech industry hiring\\n'}, 'type': 'llm_call_node'}, {'id': '13', 'position': {'x': -150, 'y': 1200}, 'data': {'label': 'Node 13', 'agent_id': '2', 'agent_name': 'Hiring Candidate Evaluator for tech industry hiring\\n'}, 'type': 'llm_call_node'}, {'id': '14', 'position': {'x': 150, 'y': 1300}, 'data': {'label': 'Node 14', 'agent_id': '3', 'agent_name': 'Tech Company Communication Department\\n'}, 'type': 'llm_call_node'}, {'id': '15', 'position': {'x': -150, 'y': 1400}, 'data': {'label': 'Node 15', 'agent_id': '3', 'agent_name': 'Tech Company Communication Department\\n'}, 'type': 'llm_call_node'}, {'id': '16', 'position': {'x': 150, 'y': 1500}, 'data': {'label': 'Node 16', 'agent_id': '3', 'agent_name': 'Tech Company Communication Department\\n'}, 'type': 'llm_call_node'}]
// [{'id': 'e1-2', 'source': '1', 'target': '2', 'data': {'from_memory': False, 'memory_index': None}}, {'id': 'e2-3', 'source': '2', 'target': '3', 'data': {'from_memory': False, 'memory_index': None}}, {'id': 'e3-4', 'source': '3', 'target': '4', 'data': {'from_memory': False, 'memory_index': None}}, {'id': 'e4-5', 'source': '4', 'target': '5', 'data': {'from_memory': False, 'memory_index': None}}, {'id': 'e5-6', 'source': '5', 'target': '6', 'data': {'from_memory': False, 'memory_index': None}}, {'id': 'e6-7', 'source': '6', 'target': '7', 'data': {'from_memory': False, 'memory_index': None}}, {'id': 'e7-8', 'source': '7', 'target': '8', 'data': {'from_memory': False, 'memory_index': None}}, {'id': 'e8-9', 'source': '8', 'target': '9', 'data': {'from_memory': False, 'memory_index': None}}, {'id': 'e11-12', 'source': '11', 'target': '12', 'data': {'from_memory': False, 'memory_index': None}}, {'id': 'e13-14', 'source': '13', 'target': '14', 'data': {'from_memory': False, 'memory_index': None}}, {'id': 'e14-15', 'source': '14', 'target': '15', 'data': {'from_memory': False, 'memory_index': None}}, {'id': 'e15-16', 'source': '15', 'target': '16', 'data': {'from_memory': False, 'memory_index': None}}, {'id': 'e2-3', 'source': '2', 'target': '3', 'data': {'from_memory': True, 'memory_index': 0}}, {'id': 'e2-4', 'source': '2', 'target': '4', 'data': {'from_memory': True, 'memory_index': 0}}, {'id': 'e2-7', 'source': '2', 'target': '7', 'data': {'from_memory': True, 'memory_index': 0}}, {'id': 'e2-8', 'source': '2', 'target': '8', 'data': {'from_memory': True, 'memory_index': 0}}, {'id': 'e2-9', 'source': '2', 'target': '9', 'data': {'from_memory': True, 'memory_index': 0}}, {'id': 'e2-10', 'source': '2', 'target': '10', 'data': {'from_memory': True, 'memory_index': 0}}, {'id': 'e4-5', 'source': '4', 'target': '5', 'data': {'from_memory': True, 'memory_index': 1}}, {'id': 'e4-6', 'source': '4', 'target': '6', 'data': {'from_memory': True, 'memory_index': 1}}, {'id': 'e4-7', 'source': '4', 'target': '7', 'data': {'from_memory': True, 'memory_index': 1}}, {'id': 'e4-8', 'source': '4', 'target': '8', 'data': {'from_memory': True, 'memory_index': 1}}, {'id': 'e4-9', 'source': '4', 'target': '9', 'data': {'from_memory': True, 'memory_index': 1}}, {'id': 'e4-10', 'source': '4', 'target': '10', 'data': {'from_memory': True, 'memory_index': 1}}, {'id': 'e4-11', 'source': '4', 'target': '11', 'data': {'from_memory': True, 'memory_index': 1}}, {'id': 'e4-12', 'source': '4', 'target': '12', 'data': {'from_memory': True, 'memory_index': 1}}, {'id': 'e6-7', 'source': '6', 'target': '7', 'data': {'from_memory': True, 'memory_index': 2}}, {'id': 'e6-8', 'source': '6', 'target': '8', 'data': {'from_memory': True, 'memory_index': 2}}, {'id': 'e6-9', 'source': '6', 'target': '9', 'data': {'from_memory': True, 'memory_index': 2}}, {'id': 'e6-10', 'source': '6', 'target': '10', 'data': {'from_memory': True, 'memory_index': 2}}, {'id': 'e6-11', 'source': '6', 'target': '11', 'data': {'from_memory': True, 'memory_index': 2}}, {'id': 'e6-12', 'source': '6', 'target': '12', 'data': {'from_memory': True, 'memory_index': 2}}, {'id': 'e10-13', 'source': '10', 'target': '13', 'data': {'from_memory': True, 'memory_index': 3}}, {'id': 'e12-13', 'source': '12', 'target': '13', 'data': {'from_memory': True, 'memory_index': 4}}, {'id': 'e13-14', 'source': '13', 'target': '14', 'data': {'from_memory': True, 'memory_index': 5}}, {'id': 'e13-15', 'source': '13', 'target': '15', 'data': {'from_memory': True, 'memory_index': 5}}, {'id': 'e13-16', 'source': '13', 'target': '16', 'data': {'from_memory': True, 'memory_index': 5}}, {'id': 'e15-16', 'source': '15', 'target': '16', 'data': {'from_memory': True, 'memory_index': 6}}]

// [{'id': 'e1-2', 'source': '1', 'target': '2', 'data': {'from_memory': 'False', 'memory_index': None}}, {'id': 'e2-3', 'source': '2', 'target': '3', 'data': {'from_memory': 'False', 'memory_index': None}}, {'id': 'e3-4', 'source': '3', 'target': '4', 'data': {'from_memory': 'False', 'memory_index': None}}, {'id': 'e4-5', 'source': '4', 'target': '5', 'data': {'from_memory': 'False', 'memory_index': None}}, {'id': 'e5-6', 'source': '5', 'target': '6', 'data': {'from_memory': 'False', 'memory_index': None}}, {'id': 'e6-7', 'source': '6', 'target': '7', 'data': {'from_memory': 'False', 'memory_index': None}}, {'id': 'e7-8', 'source': '7', 'target': '8', 'data': {'from_memory': 'False', 'memory_index': None}}, {'id': 'e8-9', 'source': '8', 'target': '9', 'data': {'from_memory': 'False', 'memory_index': None}}, {'id': 'e11-12', 'source': '11', 'target': '12', 'data': {'from_memory': 'False', 'memory_index': None}}, {'id': 'e13-14', 'source': '13', 'target': '14', 'data': {'from_memory': 'False', 'memory_index': None}}, {'id': 'e14-15', 'source': '14', 'target': '15', 'data': {'from_memory': 'False', 'memory_index': None}}, {'id': 'e15-16', 'source': '15', 'target': '16', 'data': {'from_memory': 'False', 'memory_index': None}}, {'id': 'e2-3', 'source': '2', 'target': '3', 'data': {'from_memory': 'True', 'memory_index': 0}}, {'id': 'e2-4', 'source': '2', 'target': '4', 'data': {'from_memory': 'True', 'memory_index': 0}}, {'id': 'e2-7', 'source': '2', 'target': '7', 'data': {'from_memory': 'True', 'memory_index': 0}}, {'id': 'e2-8', 'source': '2', 'target': '8', 'data': {'from_memory': 'True', 'memory_index': 0}}, {'id': 'e2-9', 'source': '2', 'target': '9', 'data': {'from_memory': 'True', 'memory_index': 0}}, {'id': 'e2-10', 'source': '2', 'target': '10', 'data': {'from_memory': 'True', 'memory_index': 0}}, {'id': 'e4-5', 'source': '4', 'target': '5', 'data': {'from_memory': 'True', 'memory_index': 1}}, {'id': 'e4-6', 'source': '4', 'target': '6', 'data': {'from_memory': 'True', 'memory_index': 1}}, {'id': 'e4-7', 'source': '4', 'target': '7', 'data': {'from_memory': 'True', 'memory_index': 1}}, {'id': 'e4-8', 'source': '4', 'target': '8', 'data': {'from_memory': 'True', 'memory_index': 1}}, {'id': 'e4-9', 'source': '4', 'target': '9', 'data': {'from_memory': 'True', 'memory_index': 1}}, {'id': 'e4-10', 'source': '4', 'target': '10', 'data': {'from_memory': 'True', 'memory_index': 1}}, {'id': 'e4-11', 'source': '4', 'target': '11', 'data': {'from_memory': 'True', 'memory_index': 1}}, {'id': 'e4-12', 'source': '4', 'target': '12', 'data': {'from_memory': 'True', 'memory_index': 1}}, {'id': 'e6-7', 'source': '6', 'target': '7', 'data': {'from_memory': 'True', 'memory_index': 2}}, {'id': 'e6-8', 'source': '6', 'target': '8', 'data': {'from_memory': 'True', 'memory_index': 2}}, {'id': 'e6-9', 'source': '6', 'target': '9', 'data': {'from_memory': 'True', 'memory_index': 2}}, {'id': 'e6-10', 'source': '6', 'target': '10', 'data': {'from_memory': 'True', 'memory_index': 2}}, {'id': 'e6-11', 'source': '6', 'target': '11', 'data': {'from_memory': 'True', 'memory_index': 2}}, {'id': 'e6-12', 'source': '6', 'target': '12', 'data': {'from_memory': 'True', 'memory_index': 2}}, {'id': 'e10-13', 'source': '10', 'target': '13', 'data': {'from_memory': 'True', 'memory_index': 3}}, {'id': 'e12-13', 'source': '12', 'target': '13', 'data': {'from_memory': 'True', 'memory_index': 4}}, {'id': 'e13-14', 'source': '13', 'target': '14', 'data': {'from_memory': 'True', 'memory_index': 5}}, {'id': 'e13-15', 'source': '13', 'target': '15', 'data': {'from_memory': 'True', 'memory_index': 5}}, {'id': 'e13-16', 'source': '13', 'target': '16', 'data': {'from_memory': 'True', 'memory_index': 5}}, {'id': 'e15-16', 'source': '15', 'target': '16', 'data': {'from_memory': 'True', 'memory_index': 6}}]

const initialNodes = [{'id': '1', 'position': {'x': 0, 'y': 0}, 'data': {'label': 'Node 1', 'agent_id': '0', 'agent_name': 'Candidate and Job Analyst for tech industry hiring\\n', 'jb_asr': '0.16666666666666666'}, 'type': 'llm_call_node'}, {'id': '2', 'position': {'x': 0, 'y': 100}, 'data': {'label': 'Node 2', 'agent_id': '0', 'agent_name': 'Candidate and Job Analyst for tech industry hiring\\n', 'jb_asr': '0.23333333333333334'}, 'type': 'llm_call_node'}, {'id': '3', 'position': {'x': -150, 'y': 200}, 'data': {'label': 'Node 3', 'agent_id': '0', 'agent_name': 'Candidate and Job Analyst for tech industry hiring\\n', 'jb_asr': '0.13333333333333333'}, 'type': 'llm_call_node'}, {'id': '4', 'position': {'x': 150, 'y': 300}, 'data': {'label': 'Node 4', 'agent_id': '0', 'agent_name': 'Candidate and Job Analyst for tech industry hiring\\n', 'jb_asr': '0.43333333333333335'}, 'type': 'llm_call_node'}, {'id': '5', 'position': {'x': -150, 'y': 400}, 'data': {'label': 'Node 5', 'agent_id': '1', 'agent_name': 'Job Profiler for tech industry hiring\\n', 'jb_asr': '0.23333333333333334'}, 'type': 'llm_call_node'}, {'id': '6', 'position': {'x': 150, 'y': 500}, 'data': {'label': 'Node 6', 'agent_id': '1', 'agent_name': 'Job Profiler for tech industry hiring\\n', 'jb_asr': '0.3'}, 'type': 'llm_call_node'}, {'id': '7', 'position': {'x': -150, 'y': 600}, 'data': {'label': 'Node 7', 'agent_id': '0', 'agent_name': 'Candidate and Job Analyst for tech industry hiring\\n', 'jb_asr': '0.3'}, 'type': 'llm_call_node'}, {'id': '8', 'position': {'x': 150, 'y': 700}, 'data': {'label': 'Node 8', 'agent_id': '0', 'agent_name': 'Candidate and Job Analyst for tech industry hiring\\n', 'jb_asr': '0.4666666666666667'}, 'type': 'llm_call_node'}, {'id': '9', 'position': {'x': -150, 'y': 800}, 'data': {'label': 'Node 9', 'agent_id': '0', 'agent_name': 'Candidate and Job Analyst for tech industry hiring\\n', 'jb_asr': '0.5'}, 'type': 'llm_call_node'}, {'id': '10', 'position': {'x': 150, 'y': 900}, 'data': {'label': 'Node 10', 'agent_id': '0', 'agent_name': 'Candidate and Job Analyst for tech industry hiring\\n', 'jb_asr': '0.16666666666666666'}, 'type': 'llm_call_node'}, {'id': '11', 'position': {'x': -150, 'y': 1000}, 'data': {'label': 'Node 11', 'agent_id': '0', 'agent_name': 'Candidate and Job Analyst for tech industry hiring\\n', 'jb_asr': '0.3333333333333333'}, 'type': 'llm_call_node'}, {'id': '12', 'position': {'x': 150, 'y': 1100}, 'data': {'label': 'Node 12', 'agent_id': '2', 'agent_name': 'Hiring Candidate Evaluator for tech industry hiring\\n', 'jb_asr': '0.06666666666666667'}, 'type': 'llm_call_node'}, {'id': '13', 'position': {'x': -150, 'y': 1200}, 'data': {'label': 'Node 13', 'agent_id': '3', 'agent_name': 'Tech Company Communication Department\\n', 'jb_asr': '0.26666666666666666'}, 'type': 'llm_call_node'}, {'id': '14', 'position': {'x': 150, 'y': 1300}, 'data': {'label': 'Node 14', 'agent_id': '3', 'agent_name': 'Tech Company Communication Department\\n', 'jb_asr': '0.13333333333333333'}, 'type': 'llm_call_node'}, {'id': '15', 'position': {'x': -150, 'y': 1400}, 'data': {'label': 'Node 15', 'agent_id': '3', 'agent_name': 'Tech Company Communication Department\\n', 'jb_asr': '0.6'}, 'type': 'llm_call_node'}, {'id': '16', 'position': {'x': 150, 'y': 1500}, 'data': {'label': 'Node 16', 'agent_id': '3', 'agent_name': 'Tech Company Communication Department\\n', 'jb_asr': '0.3333333333333333'}, 'type': 'llm_call_node'}];
const initialEdges = [{'id': 'e1-2', 'source': '1', 'target': '2', 'data': {'from_memory': 'False', 'memory_index': 'None'}, 'style': {'strokeDasharray': 'none'}}, {'id': 'e2-3', 'source': '2', 'target': '3', 'data': {'from_memory': 'False', 'memory_index': 'None'}, 'style': {'strokeDasharray': 'none'}}, {'id': 'e3-4', 'source': '3', 'target': '4', 'data': {'from_memory': 'False', 'memory_index': 'None'}, 'style': {'strokeDasharray': 'none'}}, {'id': 'e4-5', 'source': '4', 'target': '5', 'data': {'from_memory': 'False', 'memory_index': 'None'}, 'style': {'strokeDasharray': 'none'}}, {'id': 'e5-6', 'source': '5', 'target': '6', 'data': {'from_memory': 'False', 'memory_index': 'None'}, 'style': {'strokeDasharray': 'none'}}, {'id': 'e6-7', 'source': '6', 'target': '7', 'data': {'from_memory': 'False', 'memory_index': 'None'}, 'style': {'strokeDasharray': 'none'}}, {'id': 'e7-8', 'source': '7', 'target': '8', 'data': {'from_memory': 'False', 'memory_index': 'None'}, 'style': {'strokeDasharray': 'none'}}, {'id': 'e8-9', 'source': '8', 'target': '9', 'data': {'from_memory': 'False', 'memory_index': 'None'}, 'style': {'strokeDasharray': 'none'}}, {'id': 'e10-11', 'source': '10', 'target': '11', 'data': {'from_memory': 'False', 'memory_index': 'None'}, 'style': {'strokeDasharray': 'none'}}, {'id': 'e11-12', 'source': '11', 'target': '12', 'data': {'from_memory': 'False', 'memory_index': 'None'}, 'style': {'strokeDasharray': 'none'}}, {'id': 'e12-13', 'source': '12', 'target': '13', 'data': {'from_memory': 'False', 'memory_index': 'None'}, 'style': {'strokeDasharray': 'none'}}, {'id': 'e13-14', 'source': '13', 'target': '14', 'data': {'from_memory': 'False', 'memory_index': 'None'}, 'style': {'strokeDasharray': 'none'}}, {'id': 'e15-16', 'source': '15', 'target': '16', 'data': {'from_memory': 'False', 'memory_index': 'None'}, 'style': {'strokeDasharray': 'none'}}, {'id': 'e2-3', 'source': '2', 'target': '3', 'data': {'from_memory': 'True', 'memory_index': 0}, 'style': {'strokeDasharray': '5, 5'}}, {'id': 'e2-4', 'source': '2', 'target': '4', 'data': {'from_memory': 'True', 'memory_index': 0}, 'style': {'strokeDasharray': '5, 5'}}, {'id': 'e2-7', 'source': '2', 'target': '7', 'data': {'from_memory': 'True', 'memory_index': 0}, 'style': {'strokeDasharray': '5, 5'}}, {'id': 'e2-8', 'source': '2', 'target': '8', 'data': {'from_memory': 'True', 'memory_index': 0}, 'style': {'strokeDasharray': '5, 5'}}, {'id': 'e2-9', 'source': '2', 'target': '9', 'data': {'from_memory': 'True', 'memory_index': 0}, 'style': {'strokeDasharray': '5, 5'}}, {'id': 'e4-5', 'source': '4', 'target': '5', 'data': {'from_memory': 'True', 'memory_index': 1}, 'style': {'strokeDasharray': '5, 5'}}, {'id': 'e4-6', 'source': '4', 'target': '6', 'data': {'from_memory': 'True', 'memory_index': 1}, 'style': {'strokeDasharray': '5, 5'}}, {'id': 'e4-7', 'source': '4', 'target': '7', 'data': {'from_memory': 'True', 'memory_index': 1}, 'style': {'strokeDasharray': '5, 5'}}, {'id': 'e4-8', 'source': '4', 'target': '8', 'data': {'from_memory': 'True', 'memory_index': 1}, 'style': {'strokeDasharray': '5, 5'}}, {'id': 'e4-9', 'source': '4', 'target': '9', 'data': {'from_memory': 'True', 'memory_index': 1}, 'style': {'strokeDasharray': '5, 5'}}, {'id': 'e4-10', 'source': '4', 'target': '10', 'data': {'from_memory': 'True', 'memory_index': 1}, 'style': {'strokeDasharray': '5, 5'}}, {'id': 'e4-11', 'source': '4', 'target': '11', 'data': {'from_memory': 'True', 'memory_index': 1}, 'style': {'strokeDasharray': '5, 5'}}, {'id': 'e6-7', 'source': '6', 'target': '7', 'data': {'from_memory': 'True', 'memory_index': 2}, 'style': {'strokeDasharray': '5, 5'}}, {'id': 'e6-8', 'source': '6', 'target': '8', 'data': {'from_memory': 'True', 'memory_index': 2}, 'style': {'strokeDasharray': '5, 5'}}, {'id': 'e6-9', 'source': '6', 'target': '9', 'data': {'from_memory': 'True', 'memory_index': 2}, 'style': {'strokeDasharray': '5, 5'}}, {'id': 'e6-10', 'source': '6', 'target': '10', 'data': {'from_memory': 'True', 'memory_index': 2}, 'style': {'strokeDasharray': '5, 5'}}, {'id': 'e6-11', 'source': '6', 'target': '11', 'data': {'from_memory': 'True', 'memory_index': 2}, 'style': {'strokeDasharray': '5, 5'}}, {'id': 'e9-12', 'source': '9', 'target': '12', 'data': {'from_memory': 'True', 'memory_index': 3}, 'style': {'strokeDasharray': '5, 5'}}, {'id': 'e11-12', 'source': '11', 'target': '12', 'data': {'from_memory': 'True', 'memory_index': 4}, 'style': {'strokeDasharray': '5, 5'}}, {'id': 'e12-13', 'source': '12', 'target': '13', 'data': {'from_memory': 'True', 'memory_index': 5}, 'style': {'strokeDasharray': '5, 5'}}, {'id': 'e12-14', 'source': '12', 'target': '14', 'data': {'from_memory': 'True', 'memory_index': 5}, 'style': {'strokeDasharray': '5, 5'}}, {'id': 'e12-15', 'source': '12', 'target': '15', 'data': {'from_memory': 'True', 'memory_index': 5}, 'style': {'strokeDasharray': '5, 5'}}, {'id': 'e12-16', 'source': '12', 'target': '16', 'data': {'from_memory': 'True', 'memory_index': 5}, 'style': {'strokeDasharray': '5, 5'}}];

let id = 3;
const getId = () => `${id++}`;

function Flow() {
  const [nodes, setNodes, onNodesChange] = useNodesState<CustomNode>(initialNodes as CustomNode[]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<CustomEdge>(initialEdges as CustomEdge[]);
  const [nodeType, setNodeType] = useState('agent');
  const { screenToFlowPosition } = useReactFlow();
  const [rfInstance, setRfInstance] = useState<ReactFlowInstance<CustomNode, CustomEdge> | null>(null);
  const [selectedNode, setSelectedNode] = useState<CustomNode | null>(null);

  const onNodeClick: NodeMouseHandler = useCallback((event, node) => {
    setSelectedNode(node as unknown as CustomNode);
  }, []);

  const onConnect = useCallback((params: Connection) => {
    setEdges((eds) => addEdge(params, eds) as CustomEdge[]);
  }, [setEdges]);

  const onConnectEnd = useCallback(
    (event, connectionState) => {
      if (!connectionState || !connectionState.fromNode) return;

      const { fromNode, toNode } = connectionState;

      if (toNode) return;

      const { clientX, clientY } =
        'changedTouches' in event ? event.changedTouches[0] : event;

      const newNode: CustomNode = {
        id: getId(),
        position: screenToFlowPosition({ x: clientX, y: clientY }),
        data: { 
          label: `${nodeType.charAt(0).toUpperCase() + nodeType.slice(1)} Node`,
          agent_id: '0',
          agent_name: 'New Agent',
          jb_asr: '0'
        },
        type: nodeType,
      };

      setNodes((nds) => nds.concat(newNode));

      const newEdge: CustomEdge = connectionState.fromHandle.type === 'target'
        ? { 
            id: `e${newNode.id}-${fromNode.id}`, 
            source: newNode.id, 
            target: fromNode.id,
            data: {
              from_memory: 'False',
              memory_index: 'None'
            }
          }
        : { 
            id: `e${fromNode.id}-${newNode.id}`, 
            source: fromNode.id, 
            target: newNode.id,
            data: {
              from_memory: 'False',
              memory_index: 'None'
            }
          };

      setEdges((eds) => eds.concat(newEdge));
    },
    [nodeType, screenToFlowPosition, setNodes]
  );

  const onSave = useCallback(() => {
    if (rfInstance) {
      const flow = rfInstance.toObject();
      console.log(flow)
      // localStorage.setItem(flowKey, JSON.stringify(flow));
    }
  }, [rfInstance]);

  return (
    <div style={{ width: '100vw', height: '100vh', display: 'flex' }}>
      <div style={{ flex: 1, height: '100%' }}>
        <ReactFlow<CustomNode, CustomEdge>
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onInit={setRfInstance}
          onConnectEnd={onConnectEnd}
          onNodeClick={onNodeClick}
          fitView
          nodeTypes={{ llm_call_node: genericLLMNode}}
          style={{ backgroundColor: '#F7F9FB' }}
        >
          <Controls />
          <MiniMap />
          <Background variant={BackgroundVariant.Dots} gap={12} size={1} />
        </ReactFlow>
      </div>
      
      <div style={{ 
        width: '300px', 
        height: '100%', 
        backgroundColor: 'white',
        borderLeft: '1px solid #eee',
        padding: '20px',
        overflowY: 'auto'
      }}>
        {selectedNode ? (
          <div>
            <h3>Node Details</h3>
            <p><strong>ID:</strong> {selectedNode.id}</p>
            <p><strong>Label:</strong> {selectedNode.data.label}</p>
            <p><strong>Agent ID:</strong> {selectedNode.data.agent_id}</p>
            <p><strong>Agent Name:</strong> {selectedNode.data.agent_name}</p>
            <p><strong>JB ASR:</strong> {selectedNode.data.jb_asr}</p>
          </div>
        ) : (
          <div>
            <h3>No Node Selected</h3>
            <p>Click on a node to view its details</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default function Page() {
  return (
    <ReactFlowProvider>
      <Flow />
    </ReactFlowProvider>
  );
}
