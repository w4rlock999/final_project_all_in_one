import React, { memo } from 'react';
import { Handle, Position } from '@xyflow/react';

const GenericLLMNode = ({ data, isConnectable }) => {
  return (
    <>
      <Handle
        type="target"
        position={Position.Top}
        isConnectable={isConnectable}
      />
      <div
        style={{
          padding: '10px',
          border: '1px solid #222',
          borderRadius: '5px',
          backgroundColor: '#e3f2fd',
          textAlign: 'center',
          
        }}
      >
        <strong>{data.label}</strong>
        <p>agent id = {data.agent_id}</p>
        <p>ASR = {data.jb_asr}</p>
      </div>
      <Handle
        type="source"
        position={Position.Bottom}
        isConnectable={isConnectable}
      />
    </>
  );
};

export default memo(GenericLLMNode);
