import { useState } from "react";
import "./App.css";
import FileUpload from "./components/FileUpload";
import MethodSelection from "./components/MethodSelection";
import ResultsSection from "./components/ResultsSection";
import Sidebar from "./components/Sidebar";

function App() {
  const [textInput, setTextInput] = useState("");
  const [summaryResult, setSummaryResult] = useState([]);
  const [selectedMethod, setSelectedMethod] = useState("Default");
  const [selectedModel, setSelectedModel] = useState("gemini-2.5-flash");
  const [temperature, setTemperature] = useState(0.0);
  const [topP, setTopP] = useState(0.05);

  return (
    <div className="app-container">
      <Sidebar 
        selectedModel={selectedModel} 
        setSelectedModel={setSelectedModel}
        temperature={temperature}
        setTemperature={setTemperature}
        topP={topP}
        setTopP={setTopP}
      />
      <div className="content">
        <div className="header">
          <h1>Selene Explains</h1>
          <p>Transform documents into concise summaries</p>
        </div>

        <div className="section card">
          <MethodSelection 
            selectedMethod={selectedMethod} 
            setSelectedMethod={setSelectedMethod} 
          />
        </div>

        <div className="section card">
          <FileUpload 
            textInput={textInput} 
            setTextInput={setTextInput} 
          />
        </div>

        <div className="section card">
          <h1>Results</h1>
          <ResultsSection 
            summaryResult={summaryResult} 
            setSummaryResult={setSummaryResult} 
            textInput={textInput}
            selectedMethod={selectedMethod}
            temperature={temperature}
            topP={topP}
            selectedModel={selectedModel}
          />
        </div>
      </div>
    </div>
  );
}

export default App;
