import { useEffect, useState } from 'react';
import styles from './LoadingIndicator.module.css';

const LoadingIndicator = ({ operation = 'summary' }) => {
  const [messageIndex, setMessageIndex] = useState(0);
  const [dots, setDots] = useState('');

  const loadingMessages = {
    summary: [
      "🤖 Analyzing your document...",
      "🔍 Extracting key insights...", 
      "✨ Crafting the perfect summary...",
      "📝 Polishing the final result...",
      "🎯 Almost there..."
    ],
    shorten: [
      "✂️ Trimming unnecessary words...",
      "🎯 Focusing on the essentials...",
      "📊 Condensing the content..."
    ],
    simplify: [
      "🔧 Making it easier to understand...",
      "💡 Clarifying complex concepts...",
      "📚 Simplifying the language..."
    ],
    rephrase: [
      "🔄 Finding better ways to say it...",
      "✏️ Rephrasing for clarity...",
      "🎨 Crafting a fresh perspective..."
    ]
  };

  const messages = loadingMessages[operation] || loadingMessages.summary;

  useEffect(() => {
    // Cycle through messages every 2 seconds
    const messageInterval = setInterval(() => {
      setMessageIndex((prev) => (prev + 1) % messages.length);
    }, 2000);

    // Animate dots every 500ms
    const dotsInterval = setInterval(() => {
      setDots((prev) => {
        if (prev === '...') return '';
        return prev + '.';
      });
    }, 500);

    return () => {
      clearInterval(messageInterval);
      clearInterval(dotsInterval);
    };
  }, [messages.length]);

  return (
    <div className={styles.loadingContainer}>
      <div className={styles.loadingContent}>
        <div className={styles.spinner}>
          <div className={styles.brain}>
            🧠
          </div>
          <div className={styles.orbit}>
            <div className={styles.particle}></div>
            <div className={styles.particle}></div>
            <div className={styles.particle}></div>
          </div>
        </div>
        
        <div className={styles.messageContainer}>
          <p className={styles.mainMessage}>
            {messages[messageIndex]}
            <span className={styles.dots}>{dots}</span>
          </p>
          <div className={styles.progressBar}>
            <div className={styles.progressFill}></div>
          </div>
          <p className={styles.subMessage}>
            Using <strong>{operation === 'summary' ? 'AI magic' : 'smart algorithms'}</strong> to deliver the best results
          </p>
        </div>
      </div>
      
      <div className={styles.stats}>
        <div className={styles.statItem}>
          <span className={styles.statIcon}>⚡</span>
          <span>Processing...</span>
        </div>
        <div className={styles.statItem}>
          <span className={styles.statIcon}>🎯</span>
          <span>Optimizing</span>
        </div>
        <div className={styles.statItem}>
          <span className={styles.statIcon}>✨</span>
          <span>Finalizing</span>
        </div>
      </div>
    </div>
  );
};

export default LoadingIndicator;