import { useState } from "react";
import "./App.css";
import FileUpload from "./components/FileUpload";
import HistoryTab from "./components/HistoryTab";
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
  const [activeTab, setActiveTab] = useState("current");
  const [isLoading, setIsLoading] = useState(false);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);

  return (
    <div className="app-container">
      <Sidebar 
        selectedModel={selectedModel} 
        setSelectedModel={setSelectedModel}
        temperature={temperature}
        setTemperature={setTemperature}
        topP={topP}
        setTopP={setTopP}
        isCollapsed={isSidebarCollapsed}
        onToggleCollapse={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
      />
      <div className="content">
        <div className="header">
          <div className="logo-title">
            <img src="/assets/selene-logo.png" alt="Selene Logo" className="app-logo" />
            <div>
              <h1>Selene</h1>
              <p>Transform documents into concise summaries</p>
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="tab-navigation">
          <button 
            className={`tab-btn ${activeTab === 'current' ? 'active' : ''}`}
            onClick={() => setActiveTab('current')}
          >
            📝 Current Summary {isLoading && '⏳'}
          </button>
          <button 
            className={`tab-btn ${activeTab === 'history' ? 'active' : ''}`}
            onClick={() => setActiveTab('history')}
          >
            📚 History
          </button>
        </div>

        {/* Current Summary Tab Content - Always mounted but conditionally visible */}
        <div style={{ display: activeTab === 'current' ? 'block' : 'none' }}>
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
              isLoading={isLoading}
              setIsLoading={setIsLoading}
            />
          </div>
        </div>

        {/* History Tab Content */}
        {activeTab === 'history' && (
          <div className="section card">
            <HistoryTab isActive={activeTab === 'history'} />
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
