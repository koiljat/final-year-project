import styles from "./MethodSelection.module.css";

const MethodSelection = ({ selectedMethod, setSelectedMethod }) => {
  return (
    <div className={styles.methodSelection}>
      <h3>🔧 Select Summarization Method</h3>
      <select 
        value={selectedMethod} 
        onChange={(e) => setSelectedMethod(e.target.value)}
      >
        <option>Default</option>
        <option>RAG</option>
        <option>MapReduce</option>
      </select>
    </div>
  );
};

export default MethodSelection;
