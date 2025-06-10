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
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [selectedNode, setSelectedNode] = useState(null);
  const [rightPanelWidth, setRightPanelWidth] = useState(300);

  useEffect(() => {
    const loadInitialData = async () => {
      try {
        const response = await fetch('/initial_flow.json');
        const data = await response.json();
        setNodes(data.component.nodes);
        setEdges(data.component.edges);
      } catch (error) {
        console.error('Failed to load initial flow data:', error);
      }
    };

    loadInitialData();
  }, []);

  const onNodeClick: NodeMouseHandler = useCallback((event, node) => {
    console.log(node.type);
    // setSelectedNode(node);
  }, []);

  return (
    <div style={{ width: '100vw', height: '100vh', display: 'flex' }}>
      <div style={{ flex: 1, height: '100%' }}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onNodeClick={onNodeClick}
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
