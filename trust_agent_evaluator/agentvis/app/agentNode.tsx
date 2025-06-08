import React, { memo } from 'react';
import { Handle, Position } from '@xyflow/react';
import './agentNode.css';

interface AgentNodeData {
  label: string;
  agent_name: string;
  backstory?: string;
  goal?: string;
  model?: string;
}

interface AgentNodeProps {
  data: AgentNodeData;
  isConnectable: boolean;
}

const AgentNode = ({ data, isConnectable }: AgentNodeProps) => {
  return (
    <>
      <Handle
        type="target"
        position={Position.Top}
        isConnectable={isConnectable}
      />
      <div className="agent-node">
        <div className="agent-node-header">
          <div className="agent-node-icon">🤖</div>
          <span className="agent-node-title">{data.label}</span>
        </div>
        {data.model && (
          <div className="agent-node-row">Model: {data.model}</div>
        )}
        {data.backstory && (
          <div className="agent-node-backstory">
            <strong>Backstory:</strong>
            <p>{data.backstory}</p>
          </div>
        )}
        {data.goal && (
          <div className="agent-node-goal">
            <strong>Goal:</strong>
            <p>{data.goal}</p>
          </div>
        )}
      </div>
      <Handle
        type="source"
        position={Position.Bottom}
        isConnectable={isConnectable}
      />
    </>
  );
};

export default memo(AgentNode); 