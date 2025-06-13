# Frontend Minneshantering Implementation

## 1. Skapa Minneshanteringskomponenter

### src/frontend/components/MemoryManager.tsx
```typescript
import React, { useState, useEffect } from 'react';
import { useMemory } from '../hooks/useMemory';
import { Memory } from '../types/memory';
import {
  Paper,
  Typography,
  List,
  ListItem,
  ListItemText,
  IconButton,
  TextField,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import { Delete as DeleteIcon, Search as SearchIcon } from '@mui/icons-material';

export const MemoryManager: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedMemory, setSelectedMemory] = useState<Memory | null>(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const { memories, searchMemories, deleteMemory, isLoading } = useMemory();

  useEffect(() => {
    if (searchQuery) {
      searchMemories(searchQuery);
    }
  }, [searchQuery, searchMemories]);

  const handleDelete = async (memoryId: string) => {
    if (window.confirm('Är du säker på att du vill ta bort detta minne?')) {
      await deleteMemory(memoryId);
    }
  };

  const handleMemoryClick = (memory: Memory) => {
    setSelectedMemory(memory);
    setIsDialogOpen(true);
  };

  return (
    <Paper elevation={3} sx={{ p: 2, height: '100%' }}>
      <Typography variant="h6" gutterBottom>
        Minneshantering
      </Typography>

      <div style={{ marginBottom: '1rem' }}>
        <TextField
          fullWidth
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Sök i minnen..."
          InputProps={{
            endAdornment: <SearchIcon />,
          }}
          variant="outlined"
          size="small"
        />
      </div>

      <List>
        {memories.map((memory) => (
          <ListItem
            key={memory.id}
            secondaryAction={
              <IconButton
                edge="end"
                aria-label="delete"
                onClick={() => handleDelete(memory.id)}
              >
                <DeleteIcon />
              </IconButton>
            }
          >
            <ListItemText
              primary={memory.content.substring(0, 100) + '...'}
              secondary={new Date(memory.created_at).toLocaleString()}
              onClick={() => handleMemoryClick(memory)}
              style={{ cursor: 'pointer' }}
            />
          </ListItem>
        ))}
      </List>

      <Dialog
        open={isDialogOpen}
        onClose={() => setIsDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        {selectedMemory && (
          <>
            <DialogTitle>Minnesdetaljer</DialogTitle>
            <DialogContent>
              <Typography variant="body1" paragraph>
                {selectedMemory.content}
              </Typography>
              <Typography variant="caption" color="textSecondary">
                Skapad: {new Date(selectedMemory.created_at).toLocaleString()}
              </Typography>
              {selectedMemory.metadata && (
                <Typography variant="caption" color="textSecondary" display="block">
                  Metadata: {JSON.stringify(selectedMemory.metadata, null, 2)}
                </Typography>
              )}
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setIsDialogOpen(false)}>Stäng</Button>
            </DialogActions>
          </>
        )}
      </Dialog>
    </Paper>
  );
};
```

### src/frontend/hooks/useMemory.ts
```typescript
import { useState, useCallback } from 'react';
import { useApi } from './useApi';
import { Memory } from '../types/memory';

export const useMemory = () => {
  const [memories, setMemories] = useState<Memory[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const { get, post, delete: del } = useApi();

  const searchMemories = useCallback(async (query: string) => {
    setIsLoading(true);
    try {
      const response = await post('/ai/memory/query', {
        query,
        limit: 10,
      });
      setMemories(response);
    } catch (error) {
      console.error('Error searching memories:', error);
    } finally {
      setIsLoading(false);
    }
  }, [post]);

  const deleteMemory = useCallback(async (memoryId: string) => {
    setIsLoading(true);
    try {
      await del(`/ai/memory/${memoryId}`);
      setMemories((prev) => prev.filter((m) => m.id !== memoryId));
    } catch (error) {
      console.error('Error deleting memory:', error);
    } finally {
      setIsLoading(false);
    }
  }, [del]);

  return {
    memories,
    searchMemories,
    deleteMemory,
    isLoading,
  };
};
```

### src/frontend/types/memory.ts
```typescript
export interface Memory {
  id: string;
  content: string;
  metadata: Record<string, any>;
  created_at: string;
  updated_at: string;
  embedding?: number[];
}
```

## 2. Uppdatera Layout

### src/frontend/components/Layout.tsx
```typescript
import React, { useState } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  IconButton,
  Box,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Chat as ChatIcon,
  Memory as MemoryIcon,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';

const drawerWidth = 240;

interface LayoutProps {
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  const [mobileOpen, setMobileOpen] = useState(false);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const navigate = useNavigate();
  const location = useLocation();

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const menuItems = [
    { text: 'Chat', icon: <ChatIcon />, path: '/' },
    { text: 'Minneshantering', icon: <MemoryIcon />, path: '/memory' },
  ];

  const drawer = (
    <div>
      <Toolbar />
      <List>
        {menuItems.map((item) => (
          <ListItem
            button
            key={item.text}
            onClick={() => {
              navigate(item.path);
              if (isMobile) {
                setMobileOpen(false);
              }
            }}
            selected={location.pathname === item.path}
          >
            <ListItemIcon>{item.icon}</ListItemIcon>
            <ListItemText primary={item.text} />
          </ListItem>
        ))}
      </List>
    </div>
  );

  return (
    <Box sx={{ display: 'flex' }}>
      <AppBar
        position="fixed"
        sx={{
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          ml: { sm: `${drawerWidth}px` },
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { sm: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap component="div">
            Geometra AI
          </Typography>
        </Toolbar>
      </AppBar>
      <Box
        component="nav"
        sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
      >
        <Drawer
          variant={isMobile ? 'temporary' : 'permanent'}
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true,
          }}
          sx={{
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: drawerWidth,
            },
          }}
        >
          {drawer}
        </Drawer>
      </Box>
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { sm: `calc(100% - ${drawerWidth}px)` },
        }}
      >
        <Toolbar />
        {children}
      </Box>
    </Box>
  );
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
import { MemoryManager } from './components/MemoryManager';
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
          <Route
            path="/memory"
            element={
              <PrivateRoute>
                <Layout>
                  <MemoryManager />
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

## 4. Skapa Tester

### src/frontend/components/__tests__/MemoryManager.test.tsx
```typescript
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryManager } from '../MemoryManager';
import { useMemory } from '../../hooks/useMemory';

// Mock useMemory hook
jest.mock('../../hooks/useMemory');

const mockMemories = [
  {
    id: '1',
    content: 'Test memory 1',
    metadata: { type: 'test' },
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
  {
    id: '2',
    content: 'Test memory 2',
    metadata: { type: 'test' },
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
];

describe('MemoryManager', () => {
  beforeEach(() => {
    (useMemory as jest.Mock).mockReturnValue({
      memories: mockMemories,
      searchMemories: jest.fn(),
      deleteMemory: jest.fn(),
      isLoading: false,
    });
  });

  it('renders memory list', () => {
    render(<MemoryManager />);
    expect(screen.getByText('Minneshantering')).toBeInTheDocument();
    expect(screen.getByText('Test memory 1')).toBeInTheDocument();
    expect(screen.getByText('Test memory 2')).toBeInTheDocument();
  });

  it('handles search', async () => {
    const searchMemories = jest.fn();
    (useMemory as jest.Mock).mockReturnValue({
      memories: mockMemories,
      searchMemories,
      deleteMemory: jest.fn(),
      isLoading: false,
    });

    render(<MemoryManager />);
    const searchInput = screen.getByPlaceholderText('Sök i minnen...');
    fireEvent.change(searchInput, { target: { value: 'test' } });

    await waitFor(() => {
      expect(searchMemories).toHaveBeenCalledWith('test');
    });
  });

  it('handles memory deletion', async () => {
    const deleteMemory = jest.fn();
    (useMemory as jest.Mock).mockReturnValue({
      memories: mockMemories,
      searchMemories: jest.fn(),
      deleteMemory,
      isLoading: false,
    });

    render(<MemoryManager />);
    const deleteButtons = screen.getAllByLabelText('delete');
    fireEvent.click(deleteButtons[0]);

    // Confirm deletion
    const confirmButton = screen.getByText('OK');
    fireEvent.click(confirmButton);

    await waitFor(() => {
      expect(deleteMemory).toHaveBeenCalledWith('1');
    });
  });
});
```

### src/frontend/hooks/__tests__/useMemory.test.ts
```typescript
import { renderHook, act } from '@testing-library/react-hooks';
import { useMemory } from '../useMemory';
import { useApi } from '../useApi';

// Mock useApi hook
jest.mock('../useApi');

describe('useMemory', () => {
  const mockMemories = [
    {
      id: '1',
      content: 'Test memory 1',
      metadata: { type: 'test' },
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    },
  ];

  beforeEach(() => {
    (useApi as jest.Mock).mockReturnValue({
      get: jest.fn(),
      post: jest.fn().mockResolvedValue(mockMemories),
      delete: jest.fn().mockResolvedValue({}),
    });
  });

  it('searches memories', async () => {
    const { result } = renderHook(() => useMemory());

    await act(async () => {
      await result.current.searchMemories('test');
    });

    expect(result.current.memories).toEqual(mockMemories);
  });

  it('deletes memory', async () => {
    const { result } = renderHook(() => useMemory());

    await act(async () => {
      await result.current.deleteMemory('1');
    });

    expect(result.current.memories).toEqual([]);
  });
});
```

## 5. Verifiera Implementation

```bash
# Kör tester
cd frontend
pnpm test

# Starta utvecklingsservern
pnpm dev
```

## 6. Nästa steg

Efter att ha implementerat minneshantering i frontend, kör:

```bash
# Bygg frontend
pnpm build

# Starta hela applikationen
docker-compose up
```

Detta implementerar:
- Minneshanteringsgränssnitt
- Minnesökning och -visning
- Minnesradering
- Responsiv layout
- Tester för komponenter och hooks
- Integration med backend

Nästa steg är att implementera CI/CD och deployment. 