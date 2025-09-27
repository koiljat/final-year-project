import { useState } from "react";
import ReactMarkdown from "react-markdown";
import { postProcessText } from "../services/api";
import { showExportOptions } from "../services/exportService";
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
  const [showFeedback, setShowFeedback] = useState(false); // toggle feedback section
  const [feedback, setFeedback] = useState(''); // store user feedback
  const [originalTextInput, setOriginalTextInput] = useState(''); // store original input for regeneration
  const [enhancePrompt, setEnhancePrompt] = useState(false); // checkbox for prompt enhancement

  // Generate summary from API
  const handleGenerate = async () => {
    if (!textInput) return;
    setCurrentOperation('summary');
    setIsLoading(true);
    setOriginalTextInput(textInput); // Store original input for feedback regeneration
    setFeedback(''); // Reset feedback when generating new summary
    setShowFeedback(false); // Hide feedback section for new summary
    setEnhancePrompt(false); // Reset prompt enhancement checkbox
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

  // Toggle feedback section
  const toggleFeedback = () => setShowFeedback(!showFeedback);

  // Handle feedback input change
  const handleFeedbackChange = (e) => {
    setFeedback(e.target.value);
  };

  // Handle prompt enhancement checkbox change
  const handleEnhancePromptChange = (e) => {
    setEnhancePrompt(e.target.checked);
  };

  // Handle regeneration based on feedback
  const handleRegenerate = async () => {
    if (!feedback.trim() || !originalTextInput) return;
    
    setCurrentOperation('regenerating');
    setIsLoading(true);
    
    try {
      // TODO: Implement regeneration with feedback
      // This will be implemented later with the actual regeneration endpoint
      console.log('Regenerating with feedback:', {
        originalInput: originalTextInput,
        feedback: feedback.trim(),
        enhancePrompt: enhancePrompt,
        currentSummary: summaryResult[0],
        model: selectedModel,
        temperature,
        topP
      });
      
      // Placeholder - replace with actual API call
      // const response = await fetch("http://127.0.0.1:8000/regenerate", {
      //   method: "POST",
      //   headers: { "Content-Type": "application/json" },
      //   body: JSON.stringify({
      //     original_text: originalTextInput,
      //     current_summary: summaryResult[0],
      //     feedback: feedback.trim(),
      //     enhance_prompt: enhancePrompt,
      //     model: selectedModel,
      //     temperature,
      //     top_p: topP,
      //   }),
      // });
      // const data = await response.json();
      // setSummaryResult([data.summary]);
      
      // For now, just show an alert
      alert('Regeneration feature will be implemented soon! Check console for logged data.');
      
    } catch (error) {
      console.error("Error regenerating summary:", error);
      alert('Error during regeneration. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  // Handle export
  const handleExport = () => {
    if (!summaryResult.length) return;
    
    const content = summaryResult[0];
    const filename = `ai-summary-${selectedMethod.toLowerCase().replace(/\s+/g, '-')}`;
    
    // Debug: Log feedback and original input (for development)
    if (feedback.trim()) {
      console.log('Feedback available for regeneration:', {
        feedback: feedback.trim(),
        originalInput: originalTextInput,
        currentSummary: summaryResult[0]
      });
    }
    
    showExportOptions(content, filename, (format) => {
      if (format) {
        console.log(`Exported as ${format.toUpperCase()}`);
        // Optionally show a success message
      }
    });
  };

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
              <button 
                onClick={handleExport} 
                className={styles["exportBtn"]}
                title="Export summary in various formats"
              >
                💾 Export
              </button>
              <button 
                onClick={toggleFeedback}
                className={styles["actionBtn"]}
                title="Provide feedback to improve the summary"
              >
                {showFeedback ? "🔽 Hide Feedback" : "💬 Give Feedback"}
              </button>
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

          {/* Feedback Section */}
          {showFeedback && (
            <div className={styles["feedback-section"]}>
              <h4 className={styles["feedback-title"]}>📝 Provide Feedback</h4>
              <p className={styles["feedback-description"]}>
                Help improve the summary by providing specific feedback about what you'd like to see changed or improved.
              </p>
              <textarea
                className={styles["feedback-textarea"]}
                value={feedback}
                onChange={handleFeedbackChange}
                placeholder="Example: Make it shorter, focus more on the main points, use simpler language, add more technical details..."
                rows={4}
              />
              
              {/* Prompt Enhancement Option */}
              <div className={styles["feedback-options"]}>
                <label className={styles["checkbox-label"]}>
                  <input
                    type="checkbox"
                    checked={enhancePrompt}
                    onChange={handleEnhancePromptChange}
                    className={styles["checkbox"]}
                  />
                  <span className={styles["checkbox-text"]}>
                    🚀 Enhance prompt from feedback (AI will improve your feedback before using it)
                  </span>
                </label>
              </div>
              
              <div className={styles["feedback-info"]}>
                <span className={styles["feedback-counter"]}>
                  {feedback.length} characters
                </span>
                <div className={styles["feedback-actions"]}>
                  {feedback.trim() && (
                    <>
                      <span className={styles["feedback-ready"]}>
                        ✓ Ready for regeneration
                      </span>
                      <button
                        onClick={handleRegenerate}
                        disabled={isLoading}
                        className={styles["regenerateBtn"]}
                        title="Regenerate summary based on your feedback"
                      >
                        {isLoading && currentOperation === 'regenerating' ? '⏳ Regenerating...' : '🔄 Regenerate'}
                      </button>
                    </>
                  )}
                </div>
              </div>
            </div>
          )}

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
