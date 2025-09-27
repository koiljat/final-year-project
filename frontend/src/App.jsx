import { useEffect, useState } from "react";
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
  const [isDarkMode, setIsDarkMode] = useState(() => {
    // Initialize from localStorage or default to false
    const savedTheme = localStorage.getItem('theme');
    return savedTheme === 'dark';
  });

  // Apply theme to document and persist preference
  useEffect(() => {
    const theme = isDarkMode ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [isDarkMode]);

  return (
    <div className={`app-container ${isDarkMode ? 'dark-theme' : 'light-theme'}`}>
      <Sidebar 
        selectedModel={selectedModel} 
        setSelectedModel={setSelectedModel}
        temperature={temperature}
        setTemperature={setTemperature}
        topP={topP}
        setTopP={setTopP}
        isCollapsed={isSidebarCollapsed}
        onToggleCollapse={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
        isDarkMode={isDarkMode}
        onToggleDarkMode={() => setIsDarkMode(!isDarkMode)}
      />
      <div className="content">
        <div className="header">
          <div className="logo-title">
            <img src="/assets/selene-logo.png" alt="Selene Logo" className="app-logo" />
            <div>
              <h1>SELENExplains</h1>
              <p>Transform documents into concise summaries</p>
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="tab-navigation">
          <button 
            className={`tab-btn ${activeTab === 'current' ? 'active' : ''}`}
            onClick={() => setActiveTab('current')}
            data-text={`📝 Current Summary ${isLoading ? '⏳' : ''}`}
          >
            📝 Current Summary {isLoading && '⏳'}
          </button>
          <button 
            className={`tab-btn ${activeTab === 'history' ? 'active' : ''}`}
            onClick={() => setActiveTab('history')}
            data-text="📚 History"
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
