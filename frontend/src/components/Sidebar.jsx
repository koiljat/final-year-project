import styles from "./Sidebar.module.css";

const Sidebar = ({ 
  selectedModel, setSelectedModel, 
  temperature, setTemperature, 
  topP, setTopP,
  isCollapsed, onToggleCollapse,
  isDarkMode, onToggleDarkMode
}) => {
  return (
    <div className={`${styles.sidebar} ${isCollapsed ? styles.collapsed : ''}`}>
      {/* Toggle Button */}
      <button 
        className={styles.toggleButton}
        onClick={onToggleCollapse}
        aria-label={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
      >
        <span className={styles.toggleIcon}>
          {isCollapsed ? '➤' : '◀'}
        </span>
      </button>

      {/* Sidebar Content */}
      {isCollapsed ? (
        /* Collapsed state - minimal indicators only */
        <div className={styles.collapsedContent}>
          <div className={styles.collapsedLogo}>
            <img src="/assets/selene-logo.png" alt="Selene Logo" />
          </div>
          <div className={styles.collapsedIndicators}>
          </div>
        </div>
      ) : (
        /* Expanded state - full content */
        <div className={styles.sidebarContent}>
          <div className={styles.logoSection}>
            <img src="/assets/selene-logo.png" alt="Selene Logo" />
            <h3>Settings</h3>
          </div>

          <div className={styles.section}>
            <h4>API Provider</h4>
            <select 
              value={selectedModel} 
              onChange={(e) => setSelectedModel(e.target.value)}
              title="API Provider"
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
            <input
              type="number"
              min={0}
              max={1}
              step={0.01}
              value={temperature}
              onChange={(e) => setTemperature(Number(e.target.value))}
              title={`Temperature: ${temperature}`}
            />
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
              title={`Top P: ${topP}`}
            />
          </div>

          <div className={styles.section}>
            <h4>Theme</h4>
            <div className={styles.themeToggle}>
              <button
                className={`${styles.themeButton} ${!isDarkMode ? styles.active : ''}`}
                onClick={() => onToggleDarkMode && onToggleDarkMode()}
                disabled={!isDarkMode}
                title="Light Mode"
              >
                <span className={styles.themeIcon}>☀️</span>
                <span className={styles.themeLabel}>Light</span>
              </button>
              <button
                className={`${styles.themeButton} ${isDarkMode ? styles.active : ''}`}
                onClick={() => onToggleDarkMode && onToggleDarkMode()}
                disabled={isDarkMode}
                title="Dark Mode"
              >
                <span className={styles.themeIcon}>🌙</span>
                <span className={styles.themeLabel}>Dark</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
export default Sidebar;