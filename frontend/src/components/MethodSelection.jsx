import { useState } from "react";
import styles from "./MethodSelection.module.css";

const MethodSelection = ({ selectedMethod, setSelectedMethod }) => {
  const [isExpanded, setIsExpanded] = useState(true);
  return (
    <div className={styles.methodSelection}>
      <h2 
        onClick={() => setIsExpanded(!isExpanded)}
        style={{ cursor: 'pointer', userSelect: 'none' }}
      >
        ⚙️ Summarization Settings {isExpanded ? '⬇️' : '➡️'} 
      </h2>
      
      {isExpanded && (
        <div className={styles.settingsGrid}>
          {/* Row 1 */}
          <div className={styles.settingCard}>
            <div className={styles.cardHeader}>
              <span className={styles.cardIcon}>🤖</span>
              <h3>Summarization Method</h3>
            </div>
            <select 
              value={selectedMethod} 
              onChange={(e) => setSelectedMethod(e.target.value)}
              className={styles.cardSelect}
            >
              <option>🤖 Auto</option>
              <option>📚 Retrieval-Augmented Generation (RAG)</option>
              <option>🗂️ Hierarchical Processing</option>
            </select>
          </div>

          <div className={styles.settingCard}>
            <div className={styles.cardHeader}>
              <span className={styles.cardIcon}>👥</span>
              <h3>Intended Audience</h3>
            </div>
            <select className={styles.cardSelect}>
              <option>🌐 General Public</option>
              <option>🧑‍🔬 Experts</option>
              <option>🎓 Students</option>
            </select>
          </div>

          {/* Row 2 */}
          <div className={styles.settingCard}>
            <div className={styles.cardHeader}>
              <span className={styles.cardIcon}>📝</span>
              <h3>Summary Style</h3>
            </div>
            <select className={styles.cardSelect}>
              <option>✂️ Concise</option>
              <option>📄 Detailed</option>
              <option>🔢 Bullet Points</option>
            </select>
          </div>

          <div className={styles.settingCard}>
            <div className={styles.cardHeader}>
              <span className={styles.cardIcon}>🔍</span>
              <h3>PDF Parser</h3>
            </div>
            <select className={styles.cardSelect}>
              <option>📄 PyPDF2</option>
              <option>🔧 PDF Plumber</option>
              <option>👁️ OCR</option>
            </select>
          </div>
        </div>
      )}
    </div>
  );
};

export default MethodSelection;