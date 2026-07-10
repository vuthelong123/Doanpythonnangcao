import React, { Component } from 'react';
import axios from 'axios';
import './Chatbot.css';

class Chatbot extends Component {
  constructor(props) {
    super(props);
    this.state = {
      isOpen: false,
      messages: [{ sender: 'bot', text: 'Xin chào! Tôi là trợ lý ảo Laptop, tôi có thể giúp gì cho bạn?' }],
      inputText: '',
      loading: false
    };
    this.messagesEndRef = React.createRef();
  }

  toggleChat = () => {
    this.setState({ isOpen: !this.state.isOpen });
  };

  handleInputChange = (e) => {
    this.setState({ inputText: e.target.value });
  };

  handleSend = async () => {
    const { inputText, messages } = this.state;
    if (!inputText.trim()) return;

    const userMsg = inputText.trim();
    this.setState({
      messages: [...messages, { sender: 'user', text: userMsg }],
      inputText: '',
      loading: true
    }, this.scrollToBottom);

    try {
      const response = await axios.post('/api/customer/chat', { message: userMsg });
      this.setState(prevState => ({
        messages: [...prevState.messages, { sender: 'bot', text: response.data.reply }],
        loading: false
      }), this.scrollToBottom);
    } catch (error) {
      console.error('Chatbot API error:', error);
      this.setState(prevState => ({
        messages: [...prevState.messages, { sender: 'bot', text: 'Đã có lỗi kết nối. Hãy chắc chắn bạn đã cấu hình API Key ở máy chủ.' }],
        loading: false
      }), this.scrollToBottom);
    }
  };

  handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      this.handleSend();
    }
  };

  scrollToBottom = () => {
    if (this.messagesEndRef.current) {
      this.messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  };

  componentDidUpdate(prevProps, prevState) {
    if (this.state.isOpen && !prevState.isOpen) {
      this.scrollToBottom();
    }
  }

  render() {
    const { isOpen, messages, inputText, loading } = this.state;

    return (
      <div className="chatbot-container">
        {isOpen ? (
          <div className="chatbot-window">
            <div className="chatbot-header">
              <span>Trợ lý Ảo</span>
              <button className="chatbot-close" onClick={this.toggleChat}>&times;</button>
            </div>
            <div className="chatbot-body">
              {messages.map((msg, index) => (
                <div key={index} className={`chatbot-message ${msg.sender}`}>
                  {msg.text}
                </div>
              ))}
              {loading && <div className="chatbot-message bot">Đang trả lời...</div>}
              <div ref={this.messagesEndRef}></div>
            </div>
            <div className="chatbot-footer">
              <input
                type="text"
                className="chatbot-input"
                placeholder="Nhập tin nhắn..."
                value={inputText}
                onChange={this.handleInputChange}
                onKeyPress={this.handleKeyPress}
                disabled={loading}
              />
              <button className="chatbot-send" onClick={this.handleSend} disabled={loading}>
                ➤
              </button>
            </div>
          </div>
        ) : (
          <button className="chatbot-button" onClick={this.toggleChat}>
            💬
          </button>
        )}
      </div>
    );
  }
}

export default Chatbot;
