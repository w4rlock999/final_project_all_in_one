import React, { useRef, useEffect, useState } from 'react';
import './RightPanel.css';

interface RightPanelProps {
  selectedNode: any;
  width: number;
  setWidth: (w: number) => void;
}

interface ProcessInfo {
  id: string;
  input: string;
  output: string;
  agent_index: number;
  agent_name: string;
  tool_in_input: number[];
  tool_in_output: number[];
  memory_in_input: number[];
  memory_in_output: number[];
  dependency_nodes: string[];
  jailbreak_success_rate: number;
}

interface AgentInfo {
  name: string;
  backstory: string;
  goal: string;
  model: string;
  id: string;
}

interface MemoryInfo {
  id: string;
  value: string; // This is a JSON string that needs to be parsed
}

interface ParsedMemoryValue {
  output: {
    thought: string;
    output: string;
    text: string;
  };
}

interface ToolInfo {
  name: string;
  description: string;
  id: string;
}

const MIN_WIDTH = 180;
const MAX_WIDTH = 600;

const RightPanel: React.FC<RightPanelProps> = ({ selectedNode, width, setWidth }) => {
  const panelRef = useRef<HTMLDivElement>(null);
  const [processInfo, setProcessInfo] = useState<ProcessInfo | null>(null);
  const [agentInfo, setAgentInfo] = useState<AgentInfo | null>(null);
  const [memoryInfo, setMemoryInfo] = useState<MemoryInfo | null>(null);
  const [parsedMemoryValue, setParsedMemoryValue] = useState<ParsedMemoryValue | null>(null);
  const [toolInfo, setToolInfo] = useState<ToolInfo | null>(null);

  useEffect(() => {
    const loadInfo = async () => {
      if (selectedNode?.type === 'llm_call_node') {
        try {
          const response = await fetch('/process_info.json');
          const data = await response.json();
          const process = data.process.find((p: ProcessInfo) => p.id === selectedNode.id);
          setProcessInfo(process || null);
          setAgentInfo(null);
          setMemoryInfo(null);
          setParsedMemoryValue(null);
          setToolInfo(null);
        } catch (error) {
          console.error('Failed to load process info:', error);
          setProcessInfo(null);
        }
      } else if (selectedNode?.type === 'agent_node') {
        try {
          const response = await fetch('/component_info.json');
          const data = await response.json();
          const agent = data.agent.find((a: AgentInfo) => a.id === selectedNode.id);
          setAgentInfo(agent || null);
          setProcessInfo(null);
          setMemoryInfo(null);
          setParsedMemoryValue(null);
          setToolInfo(null);
        } catch (error) {
          console.error('Failed to load agent info:', error);
          setAgentInfo(null);
        }
      } else if (selectedNode?.type === 'memory_node') {
        try {
          const response = await fetch('/component_info.json');
          const data = await response.json();
          const memory = data.memory.find((m: MemoryInfo) => m.id === selectedNode.id);
          setMemoryInfo(memory || null);
          if (memory?.value) {
            try {
              const parsed = JSON.parse(memory.value) as ParsedMemoryValue;
              setParsedMemoryValue(parsed);
            } catch (error) {
              console.error('Failed to parse memory value:', error);
              setParsedMemoryValue(null);
            }
          }
          setProcessInfo(null);
          setAgentInfo(null);
          setToolInfo(null);
        } catch (error) {
          console.error('Failed to load memory info:', error);
          setMemoryInfo(null);
          setParsedMemoryValue(null);
        }
      } else if (selectedNode?.type === 'tool_node') {
        try {
          const response = await fetch('/component_info.json');
          const data = await response.json();
          const tool = data.tool.find((t: ToolInfo) => t.id === selectedNode.id);
          setToolInfo(tool || null);
          setProcessInfo(null);
          setAgentInfo(null);
          setMemoryInfo(null);
          setParsedMemoryValue(null);
        } catch (error) {
          console.error('Failed to load tool info:', error);
          setToolInfo(null);
        }
      } else {
        setProcessInfo(null);
        setAgentInfo(null);
        setMemoryInfo(null);
        setParsedMemoryValue(null);
        setToolInfo(null);
      }
    };

    loadInfo();
  }, [selectedNode]);

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

  const formatJsonString = (jsonString: string) => {
    try {
      const parsed = JSON.parse(jsonString);
      return JSON.stringify(parsed, null, 2);
    } catch {
      return jsonString;
    }
  };

  return (
    <div
      className="right-panel"
      ref={panelRef}
      style={{ width }}
    >
      <div className="right-panel-drag-handle" onMouseDown={onMouseDown} role="presentation" />
      <div className="rp-header">{selectedNode ? selectedNode.data.label : ''}</div>
      
      {processInfo && (
        <>
          <div className="rp-section">
            <div className="rp-label">Agent Name:</div>
            <div className="rp-value">{processInfo.agent_name}</div>
            <div className="rp-label">Agent Index:</div>
            <div className="rp-value">{processInfo.agent_index}</div>
            <div className="rp-label">Jailbreak Success Rate:</div>
            <div className="rp-value">{(processInfo.jailbreak_success_rate * 100).toFixed(2)}%</div>
          </div>

          <div className="rp-section">
            <div className="rp-label">Input:</div>
            <div className="rp-box" style={{ minHeight: 100 }}>
              <pre style={{ margin: 0, whiteSpace: 'pre-wrap' }}>
                {formatJsonString(processInfo.input)}
              </pre>
            </div>
            <div className="rp-arrow">▼</div>
            <div className="rp-label">Output:</div>
            <div className="rp-box" style={{ minHeight: 100 }}>
              <pre style={{ margin: 0, whiteSpace: 'pre-wrap' }}>
                {formatJsonString(processInfo.output)}
              </pre>
            </div>
          </div>

          <div className="rp-section">
            <div className="rp-label">Tools in Input:</div>
            <div className="rp-value">{processInfo.tool_in_input.join(', ') || 'None'}</div>
            <div className="rp-label">Tools in Output:</div>
            <div className="rp-value">{processInfo.tool_in_output.join(', ') || 'None'}</div>
            <div className="rp-label">Memory in Input:</div>
            <div className="rp-value">{processInfo.memory_in_input.join(', ') || 'None'}</div>
            <div className="rp-label">Memory in Output:</div>
            <div className="rp-value">{processInfo.memory_in_output.join(', ') || 'None'}</div>
            <div className="rp-label">Dependency Nodes:</div>
            <div className="rp-value">{processInfo.dependency_nodes.join(', ') || 'None'}</div>
          </div>
        </>
      )}

      {agentInfo && (
        <>
          <div className="rp-section">
            <div className="rp-label">Name:</div>
            <div className="rp-value">{agentInfo.name}</div>
            <div className="rp-label">Model:</div>
            <div className="rp-value">{agentInfo.model}</div>
          </div>

          <div className="rp-section">
            <div className="rp-label">Backstory:</div>
            <div className="rp-box" style={{ minHeight: 100 }}>
              <pre style={{ margin: 0, whiteSpace: 'pre-wrap' }}>
                {agentInfo.backstory}
              </pre>
            </div>
          </div>

          <div className="rp-section">
            <div className="rp-label">Goal:</div>
            <div className="rp-box" style={{ minHeight: 100 }}>
              <pre style={{ margin: 0, whiteSpace: 'pre-wrap' }}>
                {agentInfo.goal}
              </pre>
            </div>
          </div>
        </>
      )}

      {parsedMemoryValue && (
        <div className="rp-section">
          <div className="rp-label">Content:</div>
          <div className="rp-box" style={{ minHeight: 100 }}>
            <pre style={{ margin: 0, whiteSpace: 'pre-wrap' }}>
              {parsedMemoryValue.output.output}
            </pre>
          </div>
        </div>
      )}

      {toolInfo && (
        <>
          <div className="rp-section">
            <div className="rp-label">Name:</div>
            <div className="rp-value">{toolInfo.name}</div>
          </div>

          <div className="rp-section">
            <div className="rp-label">Description:</div>
            <div className="rp-box" style={{ minHeight: 100 }}>
              <pre style={{ margin: 0, whiteSpace: 'pre-wrap' }}>
                {toolInfo.description}
              </pre>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default RightPanel; 