import React, { useRef } from 'react';
import './RightPanel.css';

interface RightPanelProps {
  selectedNode: any;
  width: number;
  setWidth: (w: number) => void;
}

const MIN_WIDTH = 180;
const MAX_WIDTH = 600;

const RightPanel: React.FC<RightPanelProps> = ({ selectedNode, width, setWidth }) => {
  const panelRef = useRef<HTMLDivElement>(null);

  const onMouseDown = (e: React.MouseEvent) => {
    if (e.button !== 0) return;
    const startX = e.clientX;
    const startWidth = width;

    const onMouseMove = (moveEvent: MouseEvent) => {
      const newWidth = Math.min(
        Math.max(startWidth - (moveEvent.clientX - startX), MIN_WIDTH),
        MAX_WIDTH
      );
      setWidth(newWidth);
    };

    const onMouseUp = () => {
      window.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('mouseup', onMouseUp);
    };

    window.addEventListener('mousemove', onMouseMove);
    window.addEventListener('mouseup', onMouseUp);
  };

  // Example placeholders for input/output/memory fields
  const agentName = selectedNode?.data?.agent_name || '';
  const agentIndex = selectedNode?.data?.agent_id || '';
  const model = selectedNode?.data?.model || '';
  const input = selectedNode?.data?.input || '';
  const output = selectedNode?.data?.output || '';
  const memoryInInput = selectedNode?.data?.memory_in_input || '';
  const memoryInOutput = selectedNode?.data?.memory_in_output || '';
  const prevNodeOutput = selectedNode?.data?.prev_node_output || '';
  const jbAsr = selectedNode?.data?.jb_asr || '';

  return (
    <div
      className="right-panel"
      ref={panelRef}
      style={{ width }}
    >
      <div className="right-panel-drag-handle" onMouseDown={onMouseDown} role="presentation" />
      <div className="rp-header">{selectedNode ? selectedNode.data.label : ''}</div>
      <div className="rp-section">
        <div className="rp-label">Agent Name:</div>
        <div className="rp-value">{agentName}</div>
        <div className="rp-label">Agent Index:</div>
        <div className="rp-value">{agentIndex}</div>
        <div className="rp-label">Model:</div>
        <div className="rp-value">{model}</div>
      </div>
      <div className="rp-section">
        <div className="rp-label">Input:</div>
        <div className="rp-box" style={{ minHeight: 100 }}>{input}</div>
        <div className="rp-arrow">▼</div>
        <div className="rp-label">Output:</div>
        <div className="rp-box" style={{ minHeight: 100 }}>{output}</div>
        <div className="rp-arrow">▼</div>
      </div>
      <div className="rp-section">
        <div className="rp-label">Memory in input:</div>
        <div className="rp-value">{memoryInInput}</div>
        <div className="rp-label">Memory in output:</div>
        <div className="rp-value">{memoryInOutput}</div>
        <div className="rp-label">Previous node output:</div>
        <div className="rp-value">{prevNodeOutput}</div>
      </div>
      <div className="rp-section">
        <div className="rp-label">Jailbreaking ASR:</div>
        <div className="rp-value">{jbAsr}</div>
      </div>
    </div>
  );
};

export default RightPanel; 