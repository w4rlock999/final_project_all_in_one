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
  const [leftPanelWidth, setLeftPanelWidth] = useState(50); // Default width for the left panel
  const [isDragging, setIsDragging] = useState(false);
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
          },
        }));

        // const allNodes = [...processNodes, ...componentNodes];
        
        const processEdges = data.process.edges.map(edge => ({
          ...edge,
          animated: selectedNode != null ? (((edge.source) === selectedNode.data.label) ? true : false) : false,
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
        // Get target nodes of edges that have selectedNode as source
        const targetNodeIds = processEdges
          .filter(edge => edge.source === selectedNode?.id)
          .map(edge => edge.target);

        // Create set of active nodes (selected node + target nodes)
        const activeNodeIds = new Set([selectedNode?.id, ...targetNodeIds]);

        // Update process nodes with opacity changes
        setProcessNodes(nodes => nodes.map(node => ({
          ...node,
          style: {
            ...node.style,
            opacity: selectedNode ? (activeNodeIds.has(node.id) ? 1 : 0.3) : 1,
            transition: 'opacity 0.3s ease',
          },
        })));

        // Update process edges with opacity changes
        // setProcessEdges(edges => edges.map(edge => ({
        //   ...edge,
        //   style: {
        //     ...edge.style,
        //     stroke: selectedNode != null && edge.source === selectedNode.id ? '#0000FF' : '#AFAFAF',
        //     strokeWidth: selectedNode != null && edge.source === selectedNode.id ? 2 : 1,
        //     opacity: selectedNode ? (edge.source === selectedNode.id ? 1 : 0.3) : 1,
        //     transition: 'all 0.3s ease'
        //   },
        // })));
        const processEdges_ = processEdges.map(edge => ({
          ...edge,
          style: {
            ...edge.style,
            stroke: selectedNode != null && edge.source === selectedNode.id ? '#0000FF' : '#AFAFAF',
            strokeWidth: selectedNode != null && edge.source === selectedNode.id ? 2 : 1,
            opacity: selectedNode ? (edge.source === selectedNode.id ? 1 : 0.3) : 1,
            transition: 'stroke 0.3s ease'
          },
        }));

        setProcessEdges(processEdges_);

      } catch (error) {
        console.error('Failed to load initial flow data:', error);
      }
    };

    loadInitialData();
  }, [selectedNode]);

  useEffect(() => {
    const loadInitialData = async () => {
      try {

        const componentNodes_ = componentNodes.map(node => ({
          ...node,
          style: {
            ...node.style,
            opacity: highlightedComponents.length > 0 ? (highlightedComponents.includes(node.id) ? 1 : 0.1) : 1,
            transition: 'opacity 0.3s ease',
          }
        }));

        const componentEdges_ = componentEdges.map(edge => ({
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
        
        setComponentNodes(componentNodes_);
        setComponentEdges(componentEdges_);
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
      setSelectedNode(node);
    } else {
      // Clear highlights when clicking any non-process node
      setHighlightedComponents([]);
      setSelectedNode(null);
    }
  }, []);

  const onEdgeClick = useCallback(() => {
    setHighlightedComponents([]);
    setSelectedNode(null);
  }, []);

  const onPaneClick = useCallback(() => {
    setHighlightedComponents([]);
    setSelectedNode(null);
  }, []);

  const handleMouseDown = (e: React.MouseEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleMouseMove = useCallback((e: MouseEvent) => {
    if (isDragging) {
      const newWidth = (e.clientX / window.innerWidth) * 100;
      setLeftPanelWidth(Math.max(20, Math.min(80, newWidth))); // Limit width between 20% and 80%
    }
  }, [isDragging]);

  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
  }, []);

  useEffect(() => {
    if (isDragging) {
      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', handleMouseUp);
    }
    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging, handleMouseMove, handleMouseUp]);

  return (
    <div style={{ width: '100vw', height: '100vh', display: 'flex' }}>
      <ReactFlowProvider>
        <div style={{ width: `${leftPanelWidth}%`, height: '100%', position: 'relative' }}>
          <ReactFlow
            nodes={[...componentNodes]}
            edges={[...componentEdges]}
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
      </ReactFlowProvider>

      <div
        style={{
          width: '4px',
          height: '100%',
          backgroundColor: '#ccc',
          cursor: 'col-resize',
          position: 'relative',
          zIndex: 10,
        }}
        onMouseDown={handleMouseDown}
      />

      <ReactFlowProvider>
        <div style={{ width: `${100 - leftPanelWidth}%`, height: '100%' }}>
          <ReactFlow
            nodes={[...processNodes]}
            edges={[...processEdges]}
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
      </ReactFlowProvider>
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
