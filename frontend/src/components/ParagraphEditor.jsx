import styles from "./ResultsSection.module.css";

const ParagraphEditor = ({ paragraph, index, summaryResult, setSummaryResult, selectedModel}) => {
  const handleChange = (e) => {
    const updated = [...summaryResult];
    const paragraphs = updated[0].split("###");
    paragraphs[index] = e.target.value;
    updated[0] = paragraphs.join("###");
    setSummaryResult(updated);
  };

  const handlePostProcess = async (operation) => {
    const paragraphs = summaryResult[0].split("###");
    let processed;

    const operationsMap = {
      "Shorten": "/shorten",
      "Simplify": "/simplify",
      "Rephrase": "/rephrase"
    };

    if (operation in operationsMap) {
      const response = await fetch(`http://127.0.0.1:8000${operationsMap[operation]}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: paragraphs[index], model: selectedModel}), // add temperature/top_p if needed
      });
      const data = await response.json();
      processed = data.summary;
    } else {
      console.error("Unknown operation:", operation);
      return;
    }

    paragraphs[index] = processed;
    const updated = [...summaryResult];
    updated[0] = paragraphs.join("###");
    setSummaryResult(updated);
  };

  return (
    <div className={styles["paragraph-editor"]}>
      <textarea
        className={styles["plain-text-block"]}
        value={paragraph}
        onChange={handleChange}
        placeholder="Enter paragraph content..."
      />
      <div className={styles["actions"]}>
        <button
          className={styles["actionBtn"]}
          onClick={() => handlePostProcess("Simplify")}
        >
          💡 Simplify
        </button>
        <button
          className={styles["actionBtn"]}
          onClick={() => handlePostProcess("Shorten")}
        >
          ✂️ Shorten
        </button>
        <button
          className={styles["actionBtn"]}
          onClick={() => handlePostProcess("Rephrase")}
        >
          🔄 Rephrase
        </button>
      </div>
    </div>
  );
};

export default ParagraphEditor;
