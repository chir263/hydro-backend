import React from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Link,
  useNavigate,
} from "react-router-dom";
import "./App.css";
import "./input/main.js";
import Input from "./input/main.js";
import Inflow from "./input/ml.js";

function Header() {
  return (
    <header
      style={{
        textAlign: "center",
        margin: "20px 0",
        fontSize: "24px",
        fontWeight: "bold",
      }}
    >
      HMSD Project
    </header>
  );
}

function Home() {
  const navigate = useNavigate();

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        marginTop: "50px",
      }}
    >
      <button
        style={{
          padding: "10px 20px",
          margin: "10px",
          backgroundColor: "#007BFF",
          color: "white",
          border: "none",
          borderRadius: "5px",
          cursor: "pointer",
          fontSize: "16px",
        }}
        onClick={() => navigate("/ml")}
      >
        Inflow Prediction
      </button>
      <button
        style={{
          padding: "10px 20px",
          margin: "10px",
          backgroundColor: "#28A745",
          color: "white",
          border: "none",
          borderRadius: "5px",
          cursor: "pointer",
          fontSize: "16px",
        }}
        onClick={() => navigate("/rainfall")}
      >
        Rainfall Prediction
      </button>
    </div>
  );
}

function App() {
  return (
    <Router>
      <Header />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/rainfall" element={<Input />} />
        <Route path="/ml" element={<Inflow />} />
      </Routes>
    </Router>
  );
}

export default App;
