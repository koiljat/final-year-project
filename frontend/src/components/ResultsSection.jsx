import { useState } from "react";
import ReactMarkdown from "react-markdown";
import { postProcessText } from "../services/api";
import { summaryStorage } from "../services/summaryStorage";
import LoadingIndicator from "./LoadingIndicator";
import ParagraphEditor from "./ParagraphEditor";
import styles from "./ResultsSection.module.css";

const ResultsSection = ({
  summaryResult,
  setSummaryResult,
  textInput,
  selectedMethod,
  temperature,
  topP,
  selectedModel,
  isLoading,
  setIsLoading,
}) => {
  const [showMarkdown, setShowMarkdown] = useState(true);
  const [paragraphMode, setParagraphMode] = useState(false); // paragraph-wise editing toggle
  const [currentOperation, setCurrentOperation] = useState('summary'); // track what operation is loading

  // Generate summary from API
  const handleGenerate = async () => {
    if (!textInput) return;
    setCurrentOperation('summary');
    setIsLoading(true);
    try {
      const response = await fetch("http://127.0.0.1:8000/summarize", {
        method: "POST", 
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text: textInput,
          model: selectedModel,
          temperature,
          top_p: topP,
        }),
      });
      const data = await response.json();
      setSummaryResult([data.summary]);
      setShowMarkdown(false); // default to editable after generation
      
      // Save to localStorage
      summaryStorage.saveSummary({
        summary: data.summary,
        originalText: textInput,
        method: selectedMethod,
        model: selectedModel,
        temperature,
        topP,
      });
      
    } catch (error) {
      console.error("Error fetching summary:", error);
    } finally {
      setIsLoading(false);
    }
  };

  // Post-process (Simplify, Shorten, Rephrase)
  const handlePostProcess = async (operation) => {
    if (!summaryResult.length) return;
    setCurrentOperation(operation.toLowerCase());
    setIsLoading(true);
    let processed;

    const operationsMap = {
      "Shorten": "/shorten",
      "Simplify": "/simplify",
      "Rephrase": "/rephrase"
    };

    try {
      if (operation in operationsMap) {
        // Call your FastAPI endpoint
        const response = await fetch(`http://127.0.0.1:8000${operationsMap[operation]}`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            text: summaryResult[0],
            model: selectedModel,
            temperature,
            top_p: topP,
          }),
        });
        const data = await response.json();
        processed = data.summary;
      } else {
        // Use existing postProcessText for fallback
        processed = await postProcessText(operation, summaryResult[0]);
      }
      
      setSummaryResult([processed]);
      setShowMarkdown(false); // stay editable
    } catch (error) {
      console.error("Error processing text:", error);
    } finally {
      setIsLoading(false);
    }
  };

  // Toggle markdown view
  const toggleMarkdown = () => setShowMarkdown(!showMarkdown);

  return (
    <div className={styles["results-section"]}>
      <button
        className={styles["generateBtn"]}
        onClick={handleGenerate}
        disabled={isLoading}
      >
        {isLoading ? "⏳ Generating..." : "🚀 Generate Summary"}
      </button>
      
      {isLoading && <LoadingIndicator operation={currentOperation} />}

      {summaryResult.length > 0 && !isLoading && (
        <div className={styles["results-container"]}>
          <div className={styles["results-header"]}>
            <h3 className={styles["results-title"]}>Results</h3>
            <div className={styles.buttonGroup}>
              <button onClick={toggleMarkdown} className={styles["actionBtn"]}>
                {showMarkdown ? "📝 Show Plain Text" : "👁️ Show Markdown"}
              </button>
              {!showMarkdown && (
                <button
                  onClick={() => setParagraphMode(!paragraphMode)}
                  className={styles["actionBtn"]}
                >
                  {paragraphMode ? "📄 Single Block Edit" : "📋 Paragraph-wise Edit"}
                </button>
              )}
            </div>
          </div>

          <div className={styles["results-text"]}>
            {showMarkdown ? (
              <ReactMarkdown>{summaryResult[0]}</ReactMarkdown>
            ) : paragraphMode ? (
              // Paragraph mode: each paragraph gets its own textarea + buttons
              summaryResult[0]
                .split("###")
                .map((para, idx) => (
                  <ParagraphEditor
                    key={idx}
                    paragraph={para}
                    index={idx}
                    summaryResult={summaryResult}
                    setSummaryResult={setSummaryResult}
                    selectedModel={selectedModel}
                  />
                ))
            ) : (
              // Single block editable + buttons
              <div>
                <div
                  className={styles["plain-text-block"]}
                  contentEditable
                  suppressContentEditableWarning={true}
                  onInput={(e) => {
                    const updated = [...summaryResult];
                    updated[0] = e.currentTarget.textContent;
                    setSummaryResult(updated);
                  }}
                >
                  {summaryResult[0]}
                </div>
                <div className={styles["actions"]}>
                  <button
                    className={styles["actionBtn"]}
                    onClick={() => handlePostProcess("Simplify")}
                    disabled={isLoading}
                  >
                    💡 Simplify
                  </button>
                  <button
                    className={styles["actionBtn"]}
                    onClick={() => handlePostProcess("Shorten")}
                    disabled={isLoading}
                  >
                    ✂️ Shorten
                  </button>
                  <button
                    className={styles["actionBtn"]}
                    onClick={() => handlePostProcess("Rephrase")}
                    disabled={isLoading}
                  >
                    🔄 Rephrase
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ResultsSection;
