// Dummy API functions to replace your Streamlit logic

export const generateSummary = async (text, method) => {
  console.log("Generating summary...", { text, method });
  // Replace with actual API call later
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve(
        "This is a dummy summary. Replace with API call result later."
      );
    }, 1500);
  });
};

export const postProcessText = async (operation, text) => {
  console.log("Post-processing...", { operation, text });
  // Replace with actual API call later
  return new Promise((resolve) => {
    setTimeout(() => resolve(text + ` [${operation} applied]`), 500);
  });
};
