import React, { memo } from 'react';
import { Handle, Position } from '@xyflow/react';
import './memoryNode.css';

interface MemoryNodeData {
  label: string;
  memory_content?: string;
  memory_index?: number;
}

interface MemoryNodeProps {
  data: MemoryNodeData;
  isConnectable: boolean;
}

const MemoryNode = ({ data, isConnectable }: MemoryNodeProps) => {
  const truncateContent = (content: string, maxLength: number = 100) => {
    if (content.length <= maxLength) return content;
    return content.substring(0, maxLength) + '...';
  };

  const formatMemoryContent = (content: string) => {
    try {
      const parsed = JSON.parse(content);
      if (parsed.output && parsed.output.output) {
        return truncateContent(parsed.output.output);
      }
      if (parsed.output) {
        return truncateContent(parsed.output);
      }
      return truncateContent(content);
    } catch {
      return truncateContent(content);
    }
  };

  return (
    <>
      <Handle
        type="target"
        position={Position.Top}
        isConnectable={isConnectable}
      />
      <div className="memory-node">
        <div className="memory-node-header">
          <div className="memory-node-icon">🧠</div>
          <span className="memory-node-title">{data.label}</span>
        </div>
        {data.memory_index !== undefined && (
          <div className="memory-node-row">Index: {data.memory_index}</div>
        )}
        {data.memory_content && (
          <div className="memory-node-content">
            <strong>Content:</strong>
            <p>{formatMemoryContent(data.memory_content)}</p>
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

export default memo(MemoryNode); 