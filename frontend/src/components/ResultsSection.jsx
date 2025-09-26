import { useState } from "react";
import ReactMarkdown from "react-markdown";
import { postProcessText } from "../services/api";
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
}) => {
  const [loading, setLoading] = useState(false);
  const [showMarkdown, setShowMarkdown] = useState(true);
  const [paragraphMode, setParagraphMode] = useState(false); // paragraph-wise editing toggle

  // Generate summary from API
  const handleGenerate = async () => {
    if (!textInput) return;
    setLoading(true);
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
    } catch (error) {
      console.error("Error fetching summary:", error);
    } finally {
      setLoading(false);
    }
  };

  // Post-process (Simplify, Shorten, Rephrase)
  const handlePostProcess = async (operation) => {
    if (!summaryResult.length) return;
    let processed;

    const operationsMap = {
      "Shorten": "/shorten",
      "Simplify": "/simplify",
      "Rephrase": "/rephrase"
    };

    if (operation in operationsMap) {
      // Call your FastAPI /shorten endpoint
      try {
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
      } catch (error) {
        console.error("Error processing text:", error);
        return;
      }
    } else {
      // Use existing postProcessText for Simplify/Rephrase
      processed = await postProcessText(operation, summaryResult[0]);
    }

    setSummaryResult([processed]);
    setShowMarkdown(false); // stay editable
  };

  // Toggle markdown view
  const toggleMarkdown = () => setShowMarkdown(!showMarkdown);

  return (
    <div className={styles["results-section"]}>
      <button
        className={styles["generate-btn"]}
        onClick={handleGenerate}
        disabled={loading}
      >
        {loading ? "⏳ Generating..." : "🚀 Generate Summary"}
      </button>
      {loading && <p>Loading summary, please wait...</p>}

      {summaryResult.length > 0 && !loading && (
        <div className={styles["results-container"]}>
          <div className={styles["results-header"]}>
            <h3 className={styles["results-title"]}>Results</h3>
            <div>
              <button onClick={toggleMarkdown} className={styles["action-btn"]}>
                {showMarkdown ? "Show Plain Text" : "Show Markdown"}
              </button>
              {!showMarkdown && (
                <button
                  onClick={() => setParagraphMode(!paragraphMode)}
                  className={styles["action-btn"]}
                >
                  {paragraphMode ? "Single Block Edit" : "Paragraph-wise Edit"}
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
                    className={styles["action-btn"]}
                    onClick={() => handlePostProcess("Simplify")}
                  >
                    Simplify
                  </button>
                  <button
                    className={styles["action-btn"]}
                    onClick={() => handlePostProcess("Shorten")}
                  >
                    Shorten
                  </button>
                  <button
                    className={styles["action-btn"]}
                    onClick={() => handlePostProcess("Rephrase")}
                  >
                    Rephrase
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
