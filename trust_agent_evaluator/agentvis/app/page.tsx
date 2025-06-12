'use client';
import React, { useState, useCallback, useEffect } from 'react';
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
import AgentNode from './agentNode';
import MemoryNode from './memoryNode';
import ToolNode from './toolNode';
import RightPanel from './RightPanel';

const flowKey = 'example-flow';

let id = 3;
const getId = () => `${id++}`;

function Flow() {
  const [processNodes, setProcessNodes, onProcessNodesChange] = useNodesState<Node<Record<string, unknown>, string>>([]);
  const [processEdges, setProcessEdges, onProcessEdgesChange] = useEdgesState<Edge<Record<string, unknown>>>([]);
  
  const [componentNodes, setComponentNodes, onComponentNodesChange] = useNodesState<Node<Record<string, unknown>, string>>([]);
  const [componentEdges, setComponentEdges, onComponentEdgesChange] = useEdgesState<Edge<Record<string, unknown>>>([]);
  const [selectedNode, setSelectedNode] = useState<Node<Record<string, unknown>, string> | null>(null);
  const [rightPanelWidth, setRightPanelWidth] = useState(300);
  const [highlightedComponents, setHighlightedComponents] = useState<string[]>([]);

  useEffect(() => {
    const loadInitialData = async () => {
      try {
        const response = await fetch('/initial_flow.json');
        const data = await response.json();
        // Combine nodes and edges from both component and process
        const processNodes = data.process.nodes

        const componentNodes = data.component.nodes.map(node => ({
          ...node,
          style: {
            ...node.style,
            opacity: highlightedComponents.length > 0 ? (highlightedComponents.includes(node.id) ? 1 : 0.1) : 1,
            transition: 'opacity 0.3s ease',
          }
        }));

        // const allNodes = [...processNodes, ...componentNodes];
        
        const processEdges = data.process.edges
        const componentEdges = data.component.edges.map(edge => ({
          ...edge,
          style: {
            ...edge.style,
            opacity: highlightedComponents.length > 0 ? (highlightedComponents.includes(edge.source) && highlightedComponents.includes(edge.target)) ? 1 : 0.2 : 1,
            stroke: highlightedComponents.length > 0 ? (highlightedComponents.includes(edge.source) && highlightedComponents.includes(edge.target)) ? '#0000FF' : '#AFAFAF' : '#AFAFAF',
            strokeWidth: highlightedComponents.length > 0 ? (highlightedComponents.includes(edge.source) && highlightedComponents.includes(edge.target)) ? 2 : 1 : 1,
            transition: 'stroke 0.3s ease'
          },
          animated: highlightedComponents.length > 0 ? (highlightedComponents.includes(edge.source) && highlightedComponents.includes(edge.target)) ? true : false : false,
        }));

        // const allEdges = [...componentEdges, ...processEdges];
        
        setProcessNodes(processNodes);
        setProcessEdges(processEdges);
        setComponentNodes(componentNodes);
        setComponentEdges(componentEdges);
      } catch (error) {
        console.error('Failed to load initial flow data:', error);
      }
    };

    loadInitialData();
  }, []);

  useEffect(() => {
    const loadInitialData = async () => {
      try {
        const response = await fetch('/initial_flow.json');
        const data = await response.json();


        const componentNodes = data.component.nodes.map(node => ({
          ...node,
          style: {
            ...node.style,
            opacity: highlightedComponents.length > 0 ? (highlightedComponents.includes(node.id) ? 1 : 0.1) : 1,
            transition: 'opacity 0.3s ease',
          }
        }));

        const componentEdges = data.component.edges.map(edge => ({
          ...edge,
          style: {
            ...edge.style,
            opacity: highlightedComponents.length > 0 ? (highlightedComponents.includes(edge.source) && highlightedComponents.includes(edge.target)) ? 1 : 0.2 : 1,
            stroke: highlightedComponents.length > 0 ? (highlightedComponents.includes(edge.source) && highlightedComponents.includes(edge.target)) ? '#0000FF' : '#AFAFAF' : '#AFAFAF',
            strokeWidth: highlightedComponents.length > 0 ? (highlightedComponents.includes(edge.source) && highlightedComponents.includes(edge.target)) ? 2 : 1 : 1,
            transition: 'stroke 0.3s ease'
          },
          animated: highlightedComponents.length > 0 ? (highlightedComponents.includes(edge.source) && highlightedComponents.includes(edge.target)) ? true : false : false,
        }));
        
        setComponentNodes(componentNodes);
        setComponentEdges(componentEdges);
      } catch (error) {
        console.error('Failed to load initial flow data:', error);
      }
    };

    loadInitialData();
  }, [highlightedComponents]);

  const onNodeClick: NodeMouseHandler = useCallback((event, node) => {
    if (node.type === 'llm_call_node') {
      const inputComponents = (node.data.input_components as string[]) || [];
      setHighlightedComponents(inputComponents);
    } else {
      // Clear highlights when clicking any non-process node
      setHighlightedComponents([]);
    }
  }, []);

  const onEdgeClick = useCallback(() => {
    setHighlightedComponents([]);
  }, []);

  const onPaneClick = useCallback(() => {
    setHighlightedComponents([]);
  }, []);

  return (
    <div style={{ width: '100vw', height: '100vh', display: 'flex' }}>
      <div style={{ flex: 1, height: '100%' }}>
        <ReactFlow
          nodes={[...processNodes, ...componentNodes]}
          edges={[...processEdges, ...componentEdges]}
          onNodesChange={(changes) => {
            onProcessNodesChange(changes);
            onComponentNodesChange(changes);
          }}
          onEdgesChange={(changes) => {
            onProcessEdgesChange(changes);
            onComponentEdgesChange(changes);
          }}
          onNodeClick={onNodeClick}
          onEdgeClick={onEdgeClick}
          onPaneClick={onPaneClick}
          fitView
          minZoom={0.05}
          nodeTypes={{ 
            llm_call_node: genericLLMNode,
            agent_node: AgentNode,
            memory_node: MemoryNode,
            tool_node: ToolNode
          }}
          style={{ backgroundColor: '#ffffff' }}
        >
          <Controls />
          <MiniMap />
          <Background variant={BackgroundVariant.Dots} gap={12} size={1} />
        </ReactFlow>
      </div>
      <RightPanel selectedNode={selectedNode} width={rightPanelWidth} setWidth={setRightPanelWidth} />
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
