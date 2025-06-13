# Bygg Frontend

Detta dokument beskriver hur man bygger och konfigurerar frontend-applikationen för Geometra AI-systemet.

## Översikt

Frontend-applikationen är byggd med:

1. **React & TypeScript**
   - Komponenter
   - Hooks
   - TypeScript-typer

2. **UI-komponenter**
   - Chat-gränssnitt
   - Visualiseringar
   - Formulär

3. **State Management**
   - Redux
   - API-integration
   - Caching

## Installation

1. Skapa React-applikation:
```bash
pnpm create vite frontend --template react-ts
cd frontend
```

2. Installera beroenden:
```bash
pnpm install @mui/material @emotion/react @emotion/styled
pnpm install @reduxjs/toolkit react-redux
pnpm install react-router-dom
pnpm install axios
pnpm install mathjax-react
```

## Konfiguration

### Projektstruktur

1. Skapa mappstruktur:
```bash
mkdir -p src/{components,hooks,store,utils,types,api}
```

2. Konfigurera TypeScript i `tsconfig.json`:
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

### Komponenter

1. Skapa `src/components/Chat/ChatInterface.tsx`:
```typescript
"""Chat interface component."""

import React, { useState, useRef, useEffect } from 'react';
import { Box, TextField, Button, Paper, Typography } from '@mui/material';
import { useDispatch, useSelector } from 'react-redux';
import { sendMessage } from '@/store/chatSlice';
import { Message } from '@/types/chat';
import { MathJax } from 'mathjax-react';

interface ChatInterfaceProps {
  sessionId?: string;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({ sessionId }) => {
  const [message, setMessage] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const dispatch = useDispatch();
  const messages = useSelector((state: RootState) => state.chat.messages);
  
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };
  
  useEffect(() => {
    scrollToBottom();
  }, [messages]);
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim()) return;
    
    dispatch(sendMessage({
      message,
      sessionId,
      timestamp: new Date().toISOString()
    }));
    
    setMessage('');
  };
  
  return (
    <Box sx={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Paper
        elevation={3}
        sx={{
          flex: 1,
          overflow: 'auto',
          p: 2,
          mb: 2
        }}
      >
        {messages.map((msg: Message, index: number) => (
          <Box
            key={index}
            sx={{
              mb: 2,
              p: 2,
              borderRadius: 1,
              bgcolor: msg.isUser ? 'primary.light' : 'grey.100'
            }}
          >
            <Typography variant="body1">
              <MathJax>{msg.content}</MathJax>
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {new Date(msg.timestamp).toLocaleTimeString()}
            </Typography>
          </Box>
        ))}
        <div ref={messagesEndRef} />
      </Paper>
      
      <Box
        component="form"
        onSubmit={handleSubmit}
        sx={{
          display: 'flex',
          gap: 1,
          p: 2
        }}
      >
        <TextField
          fullWidth
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Skriv ditt meddelande..."
          variant="outlined"
        />
        <Button
          type="submit"
          variant="contained"
          disabled={!message.trim()}
        >
          Skicka
        </Button>
      </Box>
    </Box>
  );
};
```

2. Skapa `src/components/Visualization/GeometryCanvas.tsx`:
```typescript
"""Geometry visualization component."""

import React, { useRef, useEffect } from 'react';
import { Box } from '@mui/material';
import { GeometryObject } from '@/types/geometry';

interface GeometryCanvasProps {
  objects: GeometryObject[];
  width?: number;
  height?: number;
}

export const GeometryCanvas: React.FC<GeometryCanvasProps> = ({
  objects,
  width = 800,
  height = 600
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    // Rensa canvas
    ctx.clearRect(0, 0, width, height);
    
    // Rita objekt
    objects.forEach(obj => {
      switch (obj.type) {
        case 'circle':
          drawCircle(ctx, obj);
          break;
        case 'rectangle':
          drawRectangle(ctx, obj);
          break;
        case 'line':
          drawLine(ctx, obj);
          break;
      }
    });
  }, [objects, width, height]);
  
  const drawCircle = (
    ctx: CanvasRenderingContext2D,
    circle: GeometryObject
  ) => {
    ctx.beginPath();
    ctx.arc(
      circle.x,
      circle.y,
      circle.radius,
      0,
      2 * Math.PI
    );
    ctx.stroke();
  };
  
  const drawRectangle = (
    ctx: CanvasRenderingContext2D,
    rect: GeometryObject
  ) => {
    ctx.beginPath();
    ctx.rect(
      rect.x,
      rect.y,
      rect.width,
      rect.height
    );
    ctx.stroke();
  };
  
  const drawLine = (
    ctx: CanvasRenderingContext2D,
    line: GeometryObject
  ) => {
    ctx.beginPath();
    ctx.moveTo(line.x1, line.y1);
    ctx.lineTo(line.x2, line.y2);
    ctx.stroke();
  };
  
  return (
    <Box
      sx={{
        width,
        height,
        border: '1px solid',
        borderColor: 'divider'
      }}
    >
      <canvas
        ref={canvasRef}
        width={width}
        height={height}
      />
    </Box>
  );
};
```

### State Management

1. Skapa `src/store/chatSlice.ts`:
```typescript
"""Chat state management."""

import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { Message } from '@/types/chat';
import { api } from '@/api';

export const sendMessage = createAsyncThunk(
  'chat/sendMessage',
  async (message: Omit<Message, 'id'>) => {
    const response = await api.post('/chat/message', message);
    return response.data;
  }
);

const chatSlice = createSlice({
  name: 'chat',
  initialState: {
    messages: [] as Message[],
    status: 'idle',
    error: null as string | null
  },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(sendMessage.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(sendMessage.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.messages.push(action.payload);
      })
      .addCase(sendMessage.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.error.message || 'Ett fel uppstod';
      });
  }
});

export default chatSlice.reducer;
```

### API-integration

1. Skapa `src/api/index.ts`:
```typescript
"""API client configuration."""

import axios from 'axios';

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

api.interceptors.request.use((config) => {
  const apiKey = localStorage.getItem('apiKey');
  if (apiKey) {
    config.headers['X-API-Key'] = apiKey;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('apiKey');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

## Validering

1. Starta utvecklingsserver:
```bash
pnpm dev
```

2. Kör tester:
```bash
pnpm test
```

3. Bygg för produktion:
```bash
pnpm build
```

## Felsökning

### Frontend-problem

1. **Byggproblem**
   - Kontrollera TypeScript-konfiguration
   - Verifiera beroenden
   - Validera import-sökvägar

2. **Runtime-problem**
   - Kontrollera Redux-state
   - Verifiera API-anrop
   - Validera komponenter

3. **UI-problem**
   - Kontrollera Material-UI-teman
   - Verifiera responsivitet
   - Validera tillgänglighet

## Loggning

1. Konfigurera loggning i `src/utils/logging.ts`:
```typescript
"""Frontend logging configuration."""

import { createLogger, format, transports } from 'winston';

const logger = createLogger({
  level: 'info',
  format: format.combine(
    format.timestamp(),
    format.json()
  ),
  transports: [
    new transports.Console({
      format: format.combine(
        format.colorize(),
        format.simple()
      )
    }),
    new transports.File({
      filename: 'logs/frontend.log'
    })
  ]
});

export default logger;
```

## Nästa steg

1. Implementera [Visualiseringar](08_VISUALISERINGAR.md)
2. Konfigurera [Deployment](09_DEPLOYMENT.md)
3. Skapa [Dokumentation](10_DOKUMENTATION.md) 