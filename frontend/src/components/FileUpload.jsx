import { useRef } from "react";
import styles from "./FileUpload.module.css";

const FileUpload = ({ textInput, setTextInput }) => {
  const fileInputRef = useRef(null); // to reset the file input

  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://127.0.0.1:8000/parse_pdf", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      setTextInput(data.parsed_text);
    } catch (error) {
      console.error("Error parsing PDF:", error);
    }
  };

  const handleClear = () => {
    setTextInput(""); // clear the text
    if (fileInputRef.current) {
      fileInputRef.current.value = null; // clear the file input
    }
  };

  return (
    <div className={styles.fileUpload}>
      <h3>📁 Upload Document</h3>
      <div className={styles.fileRow}>
        <input
          ref={fileInputRef}
          className={styles.fileInput}
          type="file"
          accept=".txt,.md,.pdf,.rtf"
          onChange={handleFileChange}
        />
        <button type="button" className={styles.clearBtn} onClick={handleClear}>
          ❌ Remove File
        </button>
      </div>

      <div>
        <textarea
          className={styles.textArea}
          value={textInput}
          onChange={(e) => setTextInput(e.target.value)}
          placeholder="Enter or paste text here..."
        />
      </div>
    </div>
  );
};

export default FileUpload;
