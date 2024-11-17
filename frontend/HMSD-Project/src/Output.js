import React, { useState } from "react";

const OutputPage = () => {
  const [modelOutput, setModelOutput] = useState(null);
  const [correlationData, setCorrelationData] = useState([]);
  const [selectedModel, setSelectedModel] = useState("");
  const [loading, setLoading] = useState(false);
  

  // Fetch all outputs
  const fetchOutputs = async () => {
    setLoading(true);
    const response = await fetch("/api/get-all-outputs");
    const result = await response.json();
    setModelOutput(result.modelOutput);
    setCorrelationData(result.correlationData);
    setLoading(false);
  };

  return (
    <div>
      <h1>Model Outputs</h1>
      <button onClick={fetchOutputs}>
        {loading ? "Loading Outputs..." : "Fetch Outputs"}
      </button>

      {modelOutput && (
        <div>
          <h2>Predicted Releases</h2>
          <p>{modelOutput.releases}</p>

          <h2>Environmental Flow (DQT)</h2>
          <p>{modelOutput.dqt}</p>

          <h2>Correlation Visualization</h2>
          <div>
            <img src={modelOutput.correlationGraph} alt="Correlation Graph" />
          </div>

          <h2>Select Submodel Output</h2>
          <select
            value={selectedModel}
            onChange={(e) => setSelectedModel(e.target.value)}
          >
            {modelOutput.submodels.map((model, idx) => (
              <option key={idx} value={model}>
                {model}
              </option>
            ))}
          </select>
          <button
            onClick={async () => {
              const response = await fetch(`/api/get-submodel-output?model=${selectedModel}`);
              const result = await response.json();
              alert(`Output from ${selectedModel}: ${result.output}`);
            }}
          >
            View Submodel Output
          </button>
        </div>
      )}

      {correlationData.length > 0 && (
        <div>
          <h2>Correlation Data</h2>
          <ul>
            {correlationData.map((data, idx) => (
              <li key={idx}>{data}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default OutputPage;
