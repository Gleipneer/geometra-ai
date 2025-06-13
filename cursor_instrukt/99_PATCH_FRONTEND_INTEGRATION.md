# Frontend Integration Implementation

## 1. Skapa AI-komponenter

### src/frontend/components/AIChat.tsx
```typescript
import React, { useState, useRef, useEffect } from 'react';
import { useChat } from '../hooks/useChat';
import { Message } from '../types/chat';
import { Button, TextField, Paper, Typography } from '@mui/material';
import { Send as SendIcon } from '@mui/icons-material';

export const AIChat: React.FC = () => {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { messages, sendMessage, isLoading } = useChat();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    await sendMessage(input);
    setInput('');
  };

  return (
    <Paper elevation={3} sx={{ p: 2, height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Typography variant="h6" gutterBottom>
        AI Assistant
      </Typography>
      
      <div style={{ flex: 1, overflowY: 'auto', marginBottom: '1rem' }}>
        {messages.map((message, index) => (
          <MessageBubble key={index} message={message} />
        ))}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '1rem' }}>
        <TextField
          fullWidth
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Skriv ett meddelande..."
          disabled={isLoading}
          variant="outlined"
          size="small"
        />
        <Button
          type="submit"
          variant="contained"
          disabled={isLoading || !input.trim()}
          endIcon={<SendIcon />}
        >
          Skicka
        </Button>
      </form>
    </Paper>
  );
};

const MessageBubble: React.FC<{ message: Message }> = ({ message }) => {
  const isUser = message.role === 'user';

  return (
    <div
      style={{
        display: 'flex',
        justifyContent: isUser ? 'flex-end' : 'flex-start',
        marginBottom: '0.5rem',
      }}
    >
      <Paper
        elevation={1}
        sx={{
          p: 1,
          maxWidth: '70%',
          backgroundColor: isUser ? 'primary.light' : 'grey.100',
          color: isUser ? 'white' : 'text.primary',
        }}
      >
        <Typography variant="body1">{message.content}</Typography>
      </Paper>
    </div>
  );
};
```

### src/frontend/hooks/useChat.ts
```typescript
import { useState, useCallback } from 'react';
import { Message } from '../types/chat';
import { useApi } from './useApi';

export const useChat = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const { post } = useApi();

  const sendMessage = useCallback(async (content: string) => {
    setIsLoading(true);
    try {
      // Lägg till användarens meddelande
      const userMessage: Message = {
        role: 'user',
        content,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, userMessage]);

      // Skicka till API
      const response = await post('/ai/chat', {
        messages: [...messages, userMessage].map(({ role, content }) => ({
          role,
          content,
        })),
      });

      // Lägg till AI-svar
      const aiMessage: Message = {
        role: 'assistant',
        content: response.content,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, aiMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      // Lägg till felmeddelande
      setMessages((prev) => [
        ...prev,
        {
          role: 'system',
          content: 'Ett fel uppstod vid kommunikation med AI:n. Försök igen senare.',
          timestamp: new Date(),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  }, [messages, post]);

  return {
    messages,
    sendMessage,
    isLoading,
  };
};
```

### src/frontend/types/chat.ts
```typescript
export interface Message {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
}

export interface ChatState {
  messages: Message[];
  isLoading: boolean;
}
```

## 2. Implementera API-hook

### src/frontend/hooks/useApi.ts
```typescript
import { useCallback } from 'react';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const useApi = () => {
  const get = useCallback(async (endpoint: string) => {
    const response = await axios.get(`${API_BASE_URL}${endpoint}`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
    });
    return response.data;
  }, []);

  const post = useCallback(async (endpoint: string, data: any) => {
    const response = await axios.post(`${API_BASE_URL}${endpoint}`, data, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
    });
    return response.data;
  }, []);

  const put = useCallback(async (endpoint: string, data: any) => {
    const response = await axios.put(`${API_BASE_URL}${endpoint}`, data, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
    });
    return response.data;
  }, []);

  const del = useCallback(async (endpoint: string) => {
    const response = await axios.delete(`${API_BASE_URL}${endpoint}`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
    });
    return response.data;
  }, []);

  return {
    get,
    post,
    put,
    delete: del,
  };
};
```

## 3. Uppdatera App.tsx

```typescript
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, CssBaseline } from '@mui/material';
import { theme } from './theme';
import { Layout } from './components/Layout';
import { AIChat } from './components/AIChat';
import { Login } from './components/Login';
import { Register } from './components/Register';
import { PrivateRoute } from './components/PrivateRoute';

export const App: React.FC = () => {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route
            path="/"
            element={
              <PrivateRoute>
                <Layout>
                  <AIChat />
                </Layout>
              </PrivateRoute>
            }
          />
        </Routes>
      </Router>
    </ThemeProvider>
  );
};
```

## 4. Installera Nödvändiga Paket

```bash
cd frontend
pnpm add @mui/material @emotion/react @emotion/styled @mui/icons-material axios react-router-dom
```

## 5. Skapa Tema

### src/frontend/theme.ts
```typescript
import { createTheme } from '@mui/material/styles';

export const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
      light: '#42a5f5',
      dark: '#1565c0',
    },
    secondary: {
      main: '#9c27b0',
      light: '#ba68c8',
      dark: '#7b1fa2',
    },
  },
  typography: {
    fontFamily: [
      '-apple-system',
      'BlinkMacSystemFont',
      '"Segoe UI"',
      'Roboto',
      '"Helvetica Neue"',
      'Arial',
      'sans-serif',
    ].join(','),
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
        },
      },
    },
  },
});
```

## 6. Verifiera Implementation

```bash
# Starta utvecklingsservern
cd frontend
pnpm dev

# Kör tester
pnpm test
```

## 7. Nästa steg

Efter att ha implementerat frontend-integrationen, kör:

```bash
# Bygg frontend
pnpm build

# Starta hela applikationen
docker-compose up
```

Detta implementerar:
- AI-chatgränssnitt med Material-UI
- Realtidsuppdateringar av chatten
- Felhantering och laddningstillstånd
- Responsiv design
- Tema och styling
- API-integration

Nästa steg är att implementera minneshantering i frontend och komplettera testningen. 