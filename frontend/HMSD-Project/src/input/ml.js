import React, { useState } from "react";
import { useDropzone } from "react-dropzone";
import "./css/main.css"; // Import external CSS for styling

const Input = () => {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [inflowPrediction, setInflowPrediction] = useState(null);
  const [predictionInputs, setPredictionInputs] = useState({
    evapotranspiration: "",
    storage: "",
    rainfallValue: "",
  });

  const onDrop = (acceptedFiles) => {
    if (acceptedFiles[0]?.type !== "text/csv") {
      alert("Only CSV files are allowed.");
      return;
    }
    setFile(acceptedFiles[0]);
  };

  const { getRootProps, getInputProps } = useDropzone({ onDrop });

  const handlePredictionInputChange = (e) => {
    const { name, value } = e.target;
    setPredictionInputs((prevState) => ({
      ...prevState,
      [name]: value,
    }));
  };

  const handleTrainSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      alert("Please upload a CSV file.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    setLoading(true);
    try {
      const response = await fetch(
        "http://127.0.0.1:5000/api/v1/upload_train_data",
        {
          method: "POST",
          body: formData,
        }
      );

      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`);
      }

      await new Promise((resolve) => setTimeout(resolve, 15));
      alert("Training completed successfully!");
    } catch (error) {
      console.error("Error during training:", error);
      alert("Training failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handlePredictionSubmit = async (e) => {
    e.preventDefault();

    try {
      const response = await fetch(
        "http://127.0.0.1:5000/api/v1/predict_inflow",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(predictionInputs),
        }
      );

      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`);
      }

      const result = await response.json();
      setInflowPrediction(result.predicted_inflow);
    } catch (error) {
      console.error("Error during prediction:", error);
      alert("Prediction failed. Please try again.");
    }
  };

  return (
    <div className="input-container">
      <h2 className="heading">Train Model for Inflow Prediction</h2>
      <p className="description">Upload a CSV file with training data.</p>

      <div {...getRootProps()} className="dropzone">
        <input {...getInputProps()} />
        <p className="dropzone-text">
          {file
            ? file.name
            : "Drag & drop your CSV file here or click to upload"}
        </p>
      </div>

      <form onSubmit={handleTrainSubmit} className="form">
        <button type="submit" className="submit-button" disabled={loading}>
          {loading ? "Training..." : "Train"}
        </button>
      </form>

      <h2 className="heading">Predict Inflow</h2>
      <form onSubmit={handlePredictionSubmit} className="form">
        <input
          type="number"
          name="evapotranspiration"
          placeholder="Evapotranspiration"
          value={predictionInputs.evapotranspiration}
          onChange={handlePredictionInputChange}
          required
        />
        <input
          type="number"
          name="storage"
          placeholder="Storage"
          value={predictionInputs.storage}
          onChange={handlePredictionInputChange}
          required
        />
        <input
          type="number"
          name="rainfallValue"
          placeholder="Rainfall Value"
          value={predictionInputs.rainfallValue}
          onChange={handlePredictionInputChange}
          required
        />
        <button type="submit" className="submit-button">
          Predict
        </button>
      </form>

      {inflowPrediction !== null && (
        <div className="rainfall-inflow-container">
          <h3 className="rainfall-heading">Predicted Inflow</h3>
          <p className="rainfall-value">
            {inflowPrediction} <span className="unit">Inch Acre/Hour</span>
          </p>
        </div>
      )}
    </div>
  );
};

export default Input;
