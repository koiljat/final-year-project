import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import { showExportOptions } from "../services/exportService";
import { summaryStorage } from "../services/summaryStorage";
import styles from "./HistoryTab.module.css";

const HistoryTab = ({ isActive }) => {
  const [summaries, setSummaries] = useState([]);
  const [expandedId, setExpandedId] = useState(null);

  useEffect(() => {
    // Load summaries when component mounts or becomes active
    const loadSummaries = () => {
      const storedSummaries = summaryStorage.getSummaries();
      setSummaries(storedSummaries);
    };

    if (isActive) {
      loadSummaries();
    }
  }, [isActive]);

  const handleDelete = (id) => {
    if (window.confirm("Are you sure you want to delete this summary?")) {
      summaryStorage.deleteSummary(id);
      setSummaries((prevSummaries) => prevSummaries.filter((s) => s.id !== id));
    }
  };

  const handleClearAll = () => {
    if (
      window.confirm(
        "Are you sure you want to clear all summary history? This action cannot be undone."
      )
    ) {
      summaryStorage.clearAll();
      setSummaries([]);
    }
  };

  const handleExportSummary = (summary) => {
    const content = `# Summary Report\n\n**Generated:** ${formatDate(
      summary.timestamp
    )}\n**Method:** ${summary.method || "Default"}\n**Model:** ${
      summary.model || "Unknown Model"
    }\n\n## Original Text\n\n${
      summary.originalText || "No original text available"
    }\n\n## Summary\n\n${summary.summary}`;

    const filename = `summary-${summary.id}`;

    showExportOptions(content, filename, (format) => {
      if (format) {
        console.log(
          `Exported summary ${summary.id} as ${format.toUpperCase()}`
        );
        // Optionally show a success message
      }
    });
  };

  const toggleExpanded = (id) => {
    setExpandedId(expandedId === id ? null : id);
  };

  const formatDate = (isoString) => {
    const date = new Date(isoString);
    return date.toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const truncateText = (text, maxLength = 150) => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + "...";
  };

  if (summaries.length === 0) {
    return (
      <div className={styles.historyTab}>
        <div className={styles.header}>
          <h2>Summary History</h2>
          <p className={styles.emptyMessage}>
            No summaries yet. Generate your first summary to see it appear here!
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.historyTab}>
      <div className={styles.header}>
        <h2>Summary History</h2>
        <div className={styles.headerActions}>
          <span className={styles.count}>{summaries.length} summaries</span>
          <button onClick={handleClearAll} className={styles.clearAllBtn}>
            Clear All
          </button>
        </div>
      </div>

      <div className={styles.summariesList}>
        {summaries.map((summary) => (
          <div key={summary.id} className={styles.summaryCard}>
            <div className={styles.summaryHeader}>
              <div className={styles.summaryMeta}>
                <span className={styles.timestamp}>
                  {formatDate(summary.timestamp)}
                </span>
                <div className={styles.summaryDetails}>
                  <span className={styles.method}>
                    {summary.method || "Default"}
                  </span>
                  <span className={styles.model}>
                    {summary.model || "Unknown Model"}
                  </span>
                </div>
              </div>
              <div className={styles.summaryActions}>
                <button
                  onClick={() => handleExportSummary(summary)}
                  className={styles.exportBtn}
                  title="Export summary in various formats"
                >
                  💾 Export
                </button>
                <button
                  onClick={() => toggleExpanded(summary.id)}
                  className={styles.expandBtn}
                >
                  {expandedId === summary.id ? "Collapse" : "Expand"}
                </button>
                <button
                  onClick={() => handleDelete(summary.id)}
                  className={styles.deleteBtn}
                >
                  Delete
                </button>
              </div>
            </div>

            <div className={styles.summaryPreview}>
              {expandedId === summary.id ? (
                <div className={styles.fullContent}>
                  <div className={styles.originalText}>
                    <h4>Original Text:</h4>
                    <p>
                      {truncateText(
                        summary.originalText || "No original text available",
                        300
                      )}
                    </p>
                  </div>
                  <div className={styles.summaryResult}>
                    <h4>Summary:</h4>
                    <ReactMarkdown>{summary.summary}</ReactMarkdown>
                  </div>
                </div>
              ) : (
                <p className={styles.previewText}>
                  {truncateText(summary.summary)}
                </p>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default HistoryTab;
