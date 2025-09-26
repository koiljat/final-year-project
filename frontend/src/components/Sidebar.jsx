import styles from "./Sidebar.module.css";

const Sidebar = ({ 
  selectedModel, setSelectedModel, 
  temperature, setTemperature, 
  topP, setTopP 
}) => {
  return (
    <div className={styles.sidebar}>
      <img src="/assets/logo.png" alt="Logo" />

      <div className={styles.section}>
        <h4>API Provider</h4>
        <select 
          value={selectedModel} 
          onChange={(e) => setSelectedModel(e.target.value)}
        >
          <option value="gpt-5">GPT-5</option>
          <option value="gpt-4.1">GPT-4.1</option>
          <option value="gpt-4o">GPT-4o</option>
          <option value="gpt-4">GPT-4</option>
          <option value="o4-mini">O4-mini</option>
          <option value="gemini-2.5-flash">Gemini 2.5 Flash</option>
          <option value="sonar">Sonar</option>
        </select>
      </div>

      <div className={styles.section}>
        <h4>Temperature</h4>
        <div className={styles["flex-row"]}>
          <input
            type="range"
            min={0}
            max={1}
            step={0.01}
            value={temperature}
            onChange={(e) => setTemperature(Number(e.target.value))}
          />
          <input
            type="number"
            min={0}
            max={1}
            step={0.01}
            value={temperature}
            onChange={(e) => setTemperature(Number(e.target.value))}
            className={styles["input-small"]}
          />
        </div>
      </div>

      <div className={styles.section}>
        <h4>Top P</h4>
        <input
          type="number"
          min={0}
          max={1}
          step={0.01}
          value={topP}
          onChange={(e) => setTopP(Number(e.target.value))}
        />
      </div>
    </div>
  );
};
export default Sidebar;