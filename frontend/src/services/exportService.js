/**
 * Export Service for downloading AI-generated content in various formats
 * Supports TXT, DOCX, and PDF exports with proper UTF-8 encoding and markdown formatting
 */

// Utility function to convert markdown to HTML while preserving structure
const markdownToHTML = (markdown) => {
  return markdown
    .replace(/^### (.*$)/gm, '<h3>$1</h3>') // Level 3 headers
    .replace(/^## (.*$)/gm, '<h2>$1</h2>')  // Level 2 headers  
    .replace(/^# (.*$)/gm, '<h1>$1</h1>')   // Level 1 headers
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') // Bold
    .replace(/\*(.*?)\*/g, '<em>$1</em>')   // Italic
    .replace(/`(.*?)`/g, '<code>$1</code>') // Inline code
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>') // Links
    .replace(/^\* (.+)/gm, '<li>$1</li>')   // List items
    .replace(/(<li>.*<\/li>)/gs, '<ul>$1</ul>') // Wrap list items in ul
    .replace(/^\d+\. (.+)/gm, '<li>$1</li>') // Numbered list items
    .replace(/(<li>.*<\/li>)/gs, (match) => {
      // Check if it's a numbered list (contains digits at start)
      if (match.includes('1. ') || match.includes('2. ')) {
        return '<ol>' + match.replace(/^\d+\. /gm, '') + '</ol>';
      }
      return match;
    })
    .split('\n\n')  // Split by double newlines for paragraphs
    .map(para => para.trim() ? (para.startsWith('<') ? para : `<p>${para.replace(/\n/g, '<br>')}</p>`) : '')
    .join('\n');
};

// Utility function to convert markdown to plain text while preserving structure
const markdownToPlainText = (markdown) => {
  return markdown
    .replace(/^### (.*$)/gm, '$1\n' + '='.repeat(20)) // Level 3 headers with underline
    .replace(/^## (.*$)/gm, '$1\n' + '='.repeat(30))  // Level 2 headers with underline
    .replace(/^# (.*$)/gm, '$1\n' + '='.repeat(40))   // Level 1 headers with underline
    .replace(/\*\*(.*?)\*\*/g, '$1') // Remove bold markdown
    .replace(/\*(.*?)\*/g, '$1')     // Remove italic markdown
    .replace(/`(.*?)`/g, '$1')       // Remove inline code markdown
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '$1 ($2)') // Convert links to plain text
    .replace(/^\* /gm, '• ')         // Convert bullet points
    .replace(/^\d+\. /gm, (match) => match) // Keep numbered lists
    .replace(/\n{3,}/g, '\n\n')      // Limit consecutive newlines
    .trim();
};

// Generate filename with timestamp
const generateFilename = (baseName, extension) => {
  const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
  return `${baseName}_${timestamp}.${extension}`;
};

/**
 * Export as TXT file with proper markdown-to-plain-text conversion
 */
export const exportAsTXT = (content, filename = 'ai-summary') => {
  try {
    const plainTextContent = markdownToPlainText(content);
    const blob = new Blob([plainTextContent], { 
      type: 'text/plain;charset=utf-8' 
    });
    
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = generateFilename(filename, 'txt');
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    // Clean up the URL object
    URL.revokeObjectURL(url);
    
    return true;
  } catch (error) {
    console.error('Error exporting as TXT:', error);
    return false;
  }
};

/**
 * Export as DOCX file with proper HTML formatting from markdown
 */
export const exportAsDOCX = (content, filename = 'ai-summary') => {
  try {
    const htmlContent = markdownToHTML(content);
    
    // Create a comprehensive HTML document with Word-compatible formatting
    const wordDocument = `
      <!DOCTYPE html>
      <html xmlns:o='urn:schemas-microsoft-com:office:office' 
            xmlns:w='urn:schemas-microsoft-com:office:word' 
            xmlns='http://www.w3.org/TR/REC-html40'>
      <head>
        <meta charset="utf-8">
        <title>AI Generated Summary</title>
        <!--[if gte mso 9]>
        <xml>
          <w:WordDocument>
            <w:View>Print</w:View>
            <w:Zoom>90</w:Zoom>
            <w:DoNotPromptForConvert/>
            <w:DoNotShowRevisions/>
            <w:DoNotShowInsertionsAndDeletions/>
            <w:DoNotShowPropertyChanges/>
          </w:WordDocument>
        </xml>
        <![endif]-->
        <style>
          @page { 
            margin: 1in; 
            size: 8.5in 11in;
          }
          body { 
            font-family: 'Times New Roman', serif; 
            font-size: 12pt; 
            line-height: 1.6; 
            margin: 0; 
            padding: 20px;
            color: #333;
          }
          h1 { 
            color: #2c3e50; 
            font-size: 18pt; 
            font-weight: bold; 
            margin-top: 24pt; 
            margin-bottom: 12pt;
            border-bottom: 2px solid #3498db;
            padding-bottom: 6pt;
          }
          h2 { 
            color: #2c3e50; 
            font-size: 16pt; 
            font-weight: bold; 
            margin-top: 20pt; 
            margin-bottom: 10pt;
            border-bottom: 1px solid #bdc3c7;
            padding-bottom: 4pt;
          }
          h3 { 
            color: #34495e; 
            font-size: 14pt; 
            font-weight: bold; 
            margin-top: 16pt; 
            margin-bottom: 8pt;
          }
          p { 
            margin-bottom: 12pt; 
            text-align: justify;
            orphans: 2;
            widows: 2;
          }
          ul, ol {
            margin-left: 20pt;
            margin-bottom: 12pt;
          }
          li {
            margin-bottom: 6pt;
          }
          strong {
            font-weight: bold;
          }
          em {
            font-style: italic;
          }
          code {
            font-family: 'Courier New', monospace;
            background-color: #f8f9fa;
            padding: 2pt 4pt;
            border: 1px solid #e9ecef;
            border-radius: 2pt;
          }
          a {
            color: #3498db;
            text-decoration: underline;
          }
          .document-header {
            text-align: center;
            margin-bottom: 30pt;
            border-bottom: 3px solid #2c3e50;
            padding-bottom: 15pt;
          }
          .meta-info {
            color: #666;
            font-size: 10pt;
            margin-bottom: 20pt;
            padding: 10pt;
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 4pt;
          }
        </style>
      </head>
      <body>
        <div class="document-header">
          <h1>AI Generated Summary</h1>
        </div>
        <div class="meta-info">
          <strong>Generated on:</strong> ${new Date().toLocaleString()}<br>
          <strong>Content Length:</strong> ${content.length} characters<br>
          <strong>Document Type:</strong> AI Summary Report
        </div>
        <div class="content">
          ${htmlContent}
        </div>
      </body>
      </html>
    `;
    
    const blob = new Blob([wordDocument], { 
      type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document;charset=utf-8' 
    });
    
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = generateFilename(filename, 'doc'); // Use .doc for better compatibility
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    URL.revokeObjectURL(url);
    
    return true;
  } catch (error) {
    console.error('Error exporting as DOCX:', error);
    return false;
  }
};

/**
 * Export as PDF file using jsPDF for direct download
 */
export const exportAsPDF = async (content, filename = 'ai-summary') => {
  try {
    // Dynamically load jsPDF if not already loaded
    if (!window.jspdf) {
      await loadJsPDF();
    }
    
    const { jsPDF } = window.jspdf;
    
    const doc = new jsPDF({
      orientation: 'portrait',
      unit: 'mm',
      format: 'a4'
    });
    
    // Set up document properties
    doc.setProperties({
      title: 'AI Generated Summary',
      subject: 'AI Summary Document',
      author: 'Selene AI Summarizer',
      creator: 'Selene Application'
    });
    
    // Document styling
    const pageWidth = doc.internal.pageSize.getWidth();
    const pageHeight = doc.internal.pageSize.getHeight();
    const margin = 20;
    const maxWidth = pageWidth - (margin * 2);
    let yPosition = margin;
    
    // Helper function to add new page if needed
    const checkPageBreak = (neededHeight) => {
      if (yPosition + neededHeight > pageHeight - margin) {
        doc.addPage();
        yPosition = margin;
      }
    };
    
    // Title
    doc.setFontSize(20);
    doc.setFont('helvetica', 'bold');
    doc.text('AI Generated Summary', margin, yPosition);
    yPosition += 15;
    
    // Metadata
    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(100, 100, 100);
    const metaText = `Generated on: ${new Date().toLocaleString()} | Length: ${content.length} characters`;
    doc.text(metaText, margin, yPosition);
    yPosition += 10;
    
    // Separator line
    doc.setDrawColor(52, 73, 94);
    doc.setLineWidth(0.5);
    doc.line(margin, yPosition, pageWidth - margin, yPosition);
    yPosition += 15;
    
    // Process content
    doc.setTextColor(0, 0, 0);
    const lines = content.split('\n');
    
    for (let line of lines) {
      line = line.trim();
      if (!line) {
        yPosition += 5;
        continue;
      }
      
      checkPageBreak(15);
      
      // Handle headers
      if (line.startsWith('### ')) {
        doc.setFontSize(14);
        doc.setFont('helvetica', 'bold');
        doc.setTextColor(52, 73, 94);
        const headerText = line.replace('### ', '');
        const wrappedHeader = doc.splitTextToSize(headerText, maxWidth);
        doc.text(wrappedHeader, margin, yPosition);
        yPosition += wrappedHeader.length * 8 + 5;
      } else if (line.startsWith('## ')) {
        doc.setFontSize(16);
        doc.setFont('helvetica', 'bold');
        doc.setTextColor(52, 73, 94);
        const headerText = line.replace('## ', '');
        const wrappedHeader = doc.splitTextToSize(headerText, maxWidth);
        doc.text(wrappedHeader, margin, yPosition);
        yPosition += wrappedHeader.length * 9 + 6;
      } else if (line.startsWith('# ')) {
        doc.setFontSize(18);
        doc.setFont('helvetica', 'bold');
        doc.setTextColor(52, 73, 94);
        const headerText = line.replace('# ', '');
        const wrappedHeader = doc.splitTextToSize(headerText, maxWidth);
        doc.text(wrappedHeader, margin, yPosition);
        yPosition += wrappedHeader.length * 10 + 8;
      } else {
        // Regular text
        doc.setFontSize(11);
        doc.setFont('helvetica', 'normal');
        doc.setTextColor(0, 0, 0);
        
        // Handle bold and italic (simplified)
        let processedLine = line
          .replace(/\*\*(.*?)\*\*/g, '$1') // Remove bold markers for now
          .replace(/\*(.*?)\*/g, '$1');    // Remove italic markers for now
        
        const wrappedText = doc.splitTextToSize(processedLine, maxWidth);
        doc.text(wrappedText, margin, yPosition);
        yPosition += wrappedText.length * 6 + 3;
      }
    }
    
    // Save the PDF
    doc.save(generateFilename(filename, 'pdf'));
    return true;
    
  } catch (error) {
    console.warn('jsPDF not available, falling back to HTML method:', error);
    return exportAsPDFHTML(content, filename);
  }
};

// Helper function to dynamically load jsPDF
const loadJsPDF = () => {
  return new Promise((resolve, reject) => {
    if (window.jspdf) {
      resolve();
      return;
    }
    
    const script = document.createElement('script');
    script.src = 'https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js';
    script.onload = () => {
      console.log('jsPDF loaded successfully');
      resolve();
    };
    script.onerror = () => {
      console.error('Failed to load jsPDF');
      reject(new Error('Failed to load jsPDF'));
    };
    
    document.head.appendChild(script);
  });
};

/**
 * Fallback PDF export using HTML-to-PDF conversion
 */
const exportAsPDFHTML = (content, filename) => {
  try {
    const htmlContent = markdownToHTML(content);
    
    // Create a temporary container for the content
    const tempContainer = document.createElement('div');
    tempContainer.style.cssText = `
      position: fixed;
      top: -9999px;
      left: -9999px;
      width: 210mm;
      background: white;
      font-family: Arial, sans-serif;
      font-size: 12pt;
      line-height: 1.6;
      padding: 20mm;
      color: #333;
    `;
    
    tempContainer.innerHTML = `
      <style>
        h1 { color: #2c3e50; font-size: 18pt; margin-bottom: 12pt; border-bottom: 2px solid #3498db; padding-bottom: 6pt; }
        h2 { color: #2c3e50; font-size: 16pt; margin-bottom: 10pt; border-bottom: 1px solid #bdc3c7; padding-bottom: 4pt; }
        h3 { color: #34495e; font-size: 14pt; margin-bottom: 8pt; }
        p { margin-bottom: 12pt; text-align: justify; }
        ul, ol { margin-left: 20pt; margin-bottom: 12pt; }
        li { margin-bottom: 6pt; }
        strong { font-weight: bold; }
        em { font-style: italic; }
        code { font-family: monospace; background: #f8f9fa; padding: 2pt; border: 1px solid #e9ecef; }
      </style>
      <h1>AI Generated Summary</h1>
      <p style="color: #666; font-size: 10pt; border: 1px solid #ddd; padding: 10pt; background: #f9f9f9;">
        <strong>Generated on:</strong> ${new Date().toLocaleString()}<br>
        <strong>Content Length:</strong> ${content.length} characters
      </p>
      ${htmlContent}
    `;
    
    document.body.appendChild(tempContainer);
    
    // Use window.print() with specific styling
    const printWindow = window.open('', '_blank');
    printWindow.document.write(`
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="UTF-8">
        <title>${filename}</title>
        <style>
          @media print {
            @page { margin: 0.75in; size: A4; }
            body { margin: 0; }
          }
          ${tempContainer.querySelector('style').textContent}
        </style>
      </head>
      <body>
        ${tempContainer.innerHTML.replace(/<style>.*?<\/style>/s, '')}
        <script>
          window.onload = function() {
            window.print();
            setTimeout(() => window.close(), 1000);
          };
        </script>
      </body>
      </html>
    `);
    
    printWindow.document.close();
    document.body.removeChild(tempContainer);
    
    return true;
  } catch (error) {
    console.error('Error exporting as PDF:', error);
    return false;
  }
};

/**
 * Show export options modal/menu
 */
export const showExportOptions = (content, filename, onComplete) => {
  const modal = document.createElement('div');
  modal.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 10000;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
  `;
  
  const modalContent = document.createElement('div');
  modalContent.style.cssText = `
    background: white;
    padding: 30px;
    border-radius: 12px;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
    max-width: 400px;
    width: 90%;
  `;
  
  modalContent.innerHTML = `
    <h3 style="margin-top: 0; color: #2c3e50; text-align: center;">Export Options</h3>
    <p style="color: #666; text-align: center; margin-bottom: 25px;">Choose your preferred format:</p>
    <div style="display: flex; flex-direction: column; gap: 12px;">
      <button id="exportTXT" style="
        padding: 12px 20px;
        border: 2px solid #3498db;
        background: #3498db;
        color: white;
        border-radius: 8px;
        cursor: pointer;
        font-size: 14px;
        transition: all 0.2s;
      ">📄 Export as TXT</button>
      <button id="exportDOCX" style="
        padding: 12px 20px;
        border: 2px solid #2ecc71;
        background: #2ecc71;
        color: white;
        border-radius: 8px;
        cursor: pointer;
        font-size: 14px;
        transition: all 0.2s;
      ">📝 Export as Word Document</button>
      <button id="exportPDF" style="
        padding: 12px 20px;
        border: 2px solid #e74c3c;
        background: #e74c3c;
        color: white;
        border-radius: 8px;
        cursor: pointer;
        font-size: 14px;
        transition: all 0.2s;
      ">📋 Export as PDF</button>
      <button id="cancelExport" style="
        padding: 12px 20px;
        border: 2px solid #95a5a6;
        background: transparent;
        color: #95a5a6;
        border-radius: 8px;
        cursor: pointer;
        font-size: 14px;
        margin-top: 10px;
        transition: all 0.2s;
      ">Cancel</button>
    </div>
  `;
  
  modal.appendChild(modalContent);
  document.body.appendChild(modal);
  
  // Add hover effects
  const buttons = modalContent.querySelectorAll('button');
  buttons.forEach(button => {
    button.addEventListener('mouseenter', () => {
      if (button.id !== 'cancelExport') {
        button.style.transform = 'translateY(-2px)';
        button.style.boxShadow = '0 4px 12px rgba(0,0,0,0.2)';
      }
    });
    button.addEventListener('mouseleave', () => {
      button.style.transform = 'translateY(0)';
      button.style.boxShadow = 'none';
    });
  });
  
  // Handle button clicks
  modalContent.querySelector('#exportTXT').addEventListener('click', () => {
    exportAsTXT(content, filename);
    document.body.removeChild(modal);
    if (onComplete) onComplete('txt');
  });
  
  modalContent.querySelector('#exportDOCX').addEventListener('click', () => {
    exportAsDOCX(content, filename);
    document.body.removeChild(modal);
    if (onComplete) onComplete('docx');
  });
  
  modalContent.querySelector('#exportPDF').addEventListener('click', () => {
    exportAsPDF(content, filename);
    document.body.removeChild(modal);
    if (onComplete) onComplete('pdf');
  });
  
  modalContent.querySelector('#cancelExport').addEventListener('click', () => {
    document.body.removeChild(modal);
    if (onComplete) onComplete(null);
  });
  
  // Close on background click
  modal.addEventListener('click', (e) => {
    if (e.target === modal) {
      document.body.removeChild(modal);
      if (onComplete) onComplete(null);
    }
  });
  
  // Close on Escape key
  const handleEscape = (e) => {
    if (e.key === 'Escape') {
      document.body.removeChild(modal);
      document.removeEventListener('keydown', handleEscape);
      if (onComplete) onComplete(null);
    }
  };
  document.addEventListener('keydown', handleEscape);
};

/**
 * Quick export functions for direct format export
 */
export const quickExportTXT = (content, filename = 'ai-summary') => exportAsTXT(content, filename);
export const quickExportDOCX = (content, filename = 'ai-summary') => exportAsDOCX(content, filename);
export const quickExportPDF = (content, filename = 'ai-summary') => exportAsPDF(content, filename);