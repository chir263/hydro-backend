import React, { useState } from "react";
import { useDropzone } from "react-dropzone";
import "./css/main.css"; // Import external CSS for styling

const Input = () => {
  const [rainfallInflow, setRainfallInflow] = useState(null);
  const [file, setFile] = useState(null);
  const [parameters, setParameters] = useState({
    dateRange: "",
    otherParameter: "",
  });

  const onDrop = (acceptedFiles) => {
    if (acceptedFiles[0]?.type !== "image/tiff") {
      alert("Only TIFF files are allowed.");
      return;
    }
    setFile(acceptedFiles[0]);
  };

  const { getRootProps, getInputProps } = useDropzone({ onDrop });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setParameters((prevState) => ({
      ...prevState,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      alert("Please upload rainfall TIFF file.");
      return;
    }
    const formData = new FormData();
    formData.append("file", file);
    formData.append("dateRange", parameters.dateRange);
    formData.append("otherParameter", parameters.otherParameter);

    try {
      const response = await fetch(
        "http://127.0.0.1:5000/api/v1/get_rainfall_inflow",
        {
          method: "POST",
          body: formData,
        }
      );

      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`);
      }

      const result = await response.json();
      console.log("Response from server:", result);
      // alert(`Rainfall Inflow: ${result.rainfall_inflow}`);
      setRainfallInflow(result.rainfall_inflow);
    } catch (error) {
      console.error("Error uploading file:", error);
      alert("Failed to upload file. Please try again.");
    }
  };

  return (
    <div className="input-container">
      <h2 className="heading">Upload Your Rainfall Data</h2>
      <p className="description">Upload a .TIFF file to proceed.</p>

      <div {...getRootProps()} className="dropzone">
        <input {...getInputProps()} />
        <p className="dropzone-text">
          {file
            ? file.name
            : "Drag & drop your .TIFF file here or click to upload"}
        </p>
      </div>

      <form onSubmit={handleSubmit} className="form">
        <button type="submit" className="submit-button">
          Submit
        </button>
      </form>

      {/* Show rainfall inflow if available */}
      {rainfallInflow !== null && (
        <div className="rainfall-inflow-container">
          <h3 className="rainfall-heading">Rainfall Inflow</h3>
          <p className="rainfall-value">
            {rainfallInflow} <span className="unit">Inch Acre/Hour</span>
          </p>
        </div>
      )}
    </div>
  );
};

export default Input;
