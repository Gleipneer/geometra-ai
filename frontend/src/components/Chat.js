import React, { useState, useRef, useEffect } from 'react';
import { Box, Container, TextField, IconButton, Paper, Typography, CircularProgress } from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import { styled } from '@mui/material/styles';

const ChatContainer = styled(Container)(({ theme }) => ({
  height: '100vh',
  display: 'flex',
  flexDirection: 'column',
  padding: theme.spacing(2),
  backgroundColor: '#343541',
  color: '#fff',
}));

const MessageContainer = styled(Box)(({ theme }) => ({
  flex: 1,
  overflowY: 'auto',
  marginBottom: theme.spacing(2),
  '&::-webkit-scrollbar': {
    width: '8px',
  },
  '&::-webkit-scrollbar-track': {
    background: '#2A2B32',
  },
  '&::-webkit-scrollbar-thumb': {
    background: '#565869',
    borderRadius: '4px',
  },
}));

const Message = styled(Paper)(({ theme, isUser }) => ({
  padding: theme.spacing(2),
  marginBottom: theme.spacing(2),
  backgroundColor: isUser ? '#343541' : '#444654',
  color: '#fff',
  borderRadius: '8px',
  maxWidth: '80%',
  marginLeft: isUser ? 'auto' : '0',
  marginRight: isUser ? '0' : 'auto',
}));

const InputContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  gap: theme.spacing(1),
  padding: theme.spacing(2),
  backgroundColor: '#343541',
  borderTop: '1px solid #565869',
}));

const StyledTextField = styled(TextField)(({ theme }) => ({
  '& .MuiOutlinedInput-root': {
    color: '#fff',
    backgroundColor: '#40414F',
    '& fieldset': {
      borderColor: '#565869',
    },
    '&:hover fieldset': {
      borderColor: '#6B6C7B',
    },
    '&.Mui-focused fieldset': {
      borderColor: '#10A37F',
    },
  },
}));

const Chat = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = { text: input, isUser: true };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await fetch('https://geometra-ai-production.up.railway.app/api/ai', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: input }),
      });

      const data = await response.json();
      setMessages(prev => [...prev, { text: data.message, isUser: false }]);
    } catch (error) {
      setMessages(prev => [...prev, { text: 'Error: Could not get response', isUser: false }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <ChatContainer maxWidth={false}>
      <MessageContainer>
        {messages.map((message, index) => (
          <Message key={index} isUser={message.isUser}>
            <Typography variant="body1">{message.text}</Typography>
          </Message>
        ))}
        {loading && (
          <Box display="flex" justifyContent="center" my={2}>
            <CircularProgress size={24} style={{ color: '#10A37F' }} />
          </Box>
        )}
        <div ref={messagesEndRef} />
      </MessageContainer>
      <InputContainer>
        <StyledTextField
          fullWidth
          multiline
          maxRows={4}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type your message..."
          variant="outlined"
        />
        <IconButton 
          onClick={handleSend} 
          disabled={loading || !input.trim()}
          style={{ color: '#10A37F' }}
        >
          <SendIcon />
        </IconButton>
      </InputContainer>
    </ChatContainer>
  );
};

export default Chat; 