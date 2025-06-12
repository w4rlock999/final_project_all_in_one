import React, { memo } from 'react';
import { Handle, Position } from '@xyflow/react';
import './agentNode.css';

interface AgentNodeData {
  agent_id: string;
  agent_name: string;
  label: string;
}

interface AgentNodeProps {
  data: AgentNodeData;
  isConnectable: boolean;
  isHighlighted?: boolean;
}

const AgentNode = ({ data, isConnectable, isHighlighted }: AgentNodeProps) => {
  return (
    <>
      <Handle
        type="target"
        position={Position.Top}
        isConnectable={isConnectable}
      />
      <div className={`agent-node ${isHighlighted ? 'highlighted' : ''}`}>
        <div className="agent-node-header">
          <span className="agent-node-label">{data.label}</span>
        </div>
        <div className="agent-node-content">
          <span className="agent-node-name">{data.agent_name}</span>
        </div>
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