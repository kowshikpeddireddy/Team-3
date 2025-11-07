import React, { useState, useRef, useEffect } from 'react';
import './Queries.css';
import { sendChatQuery } from '../api/client';
import { Send, Sparkles, X, Table } from 'lucide-react';

function Queries() {
  const [messages, setMessages] = useState([
    {
      type: 'bot',
      text: "Hello! I'm your AI assistant powered by Gemini 2.5 Pro. Ask me anything about your tasks and users in natural language!\n\nTry questions like:\n• How many open tasks do we have?\n• Who has the most tasks?\n• Show me all blocked tasks\n• Which team has the most completed tasks?\n• What are high priority tasks?\n• List all users in Alpha Team\n• Show tasks created this week",
      timestamp: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [modalData, setModalData] = useState(null);
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = {
      type: 'user',
      text: input,
      timestamp: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await sendChatQuery(input);
      const botMessage = {
        type: 'bot',
        text: response.data.response,
        timestamp: response.data.timestamp,
        data: response.data.data,  // Store full data
        columns: response.data.columns,  // Store columns
        count: response.data.count,  // Store count
        question: response.data.question  // Store question
      };
      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Error sending query:', error);
      const errorMessage = {
        type: 'bot',
        text: "Sorry, I'm having trouble processing that request. Please try again.",
        timestamp: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleViewAll = (message) => {
    setModalData(message);
    setShowModal(true);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="queries-page">
      <div className="chat-container">
        <div className="chat-header">
          <div className="header-icon">
            <Sparkles size={24} color="#10b981" />
          </div>
          <div className="header-content">
            <h2>Conversational Query Interface</h2>
            <p>Ask questions about your team's productivity in natural language</p>
          </div>
        </div>

        <div className="chat-messages">
          {messages.map((message, index) => (
            <div key={index} className={`message ${message.type}`}>
              <div className="message-content">
                <p>{message.text}</p>
                {message.type === 'bot' && message.count > 5 && (
                  <button 
                    className="view-all-btn"
                    onClick={() => handleViewAll(message)}
                  >
                    <Table size={16} />
                    View All {message.count} Results
                  </button>
                )}
                <span className="message-time">{message.timestamp}</span>
              </div>
            </div>
          ))}
          
          {loading && (
            <div className="message bot">
              <div className="message-content">
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="chat-input-container">
          <input
            type="text"
            className="chat-input"
            placeholder="Ask me anything about your team's productivity..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
          />
          <button className="send-button" onClick={handleSend} disabled={!input.trim() || loading}>
            <Send size={20} />
            <span>Send</span>
          </button>
        </div>
      </div>

      {/* Results Modal */}
      {showModal && modalData && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div>
                <h3>Query Results</h3>
                <p className="modal-question">{modalData.question}</p>
              </div>
              <button className="modal-close" onClick={() => setShowModal(false)}>
                <X size={24} />
              </button>
            </div>
            
            <div className="modal-body">
              <div className="results-info">
                <span className="results-count">
                  {modalData.count} {modalData.count === 1 ? 'Result' : 'Results'}
                </span>
              </div>

              <div className="results-table-container">
                <table className="results-table">
                  <thead>
                    <tr>
                      {modalData.columns && modalData.columns.map((col, idx) => (
                        <th key={idx}>{col.replace(/_/g, ' ').toUpperCase()}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {modalData.data && modalData.data.map((row, idx) => (
                      <tr key={idx}>
                        {modalData.columns.map((col, colIdx) => (
                          <td key={colIdx}>{row[col] !== null && row[col] !== undefined ? row[col] : 'N/A'}</td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Queries;

