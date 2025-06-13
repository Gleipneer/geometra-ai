# Frontend-testtäckning

## 1. Skapa frontend-teststruktur
```bash
# Skapa testkataloger
mkdir -p tests/unit/frontend/{components,pages,services}
mkdir -p tests/integration/frontend
mkdir -p tests/e2e
```

## 2. Implementera komponenttester
```typescript
// tests/unit/frontend/components/Button.test.tsx
import { render, fireEvent } from '@testing-library/react';
import Button from '../../../src/frontend/components/Button';

describe('Button Component', () => {
  it('renders correctly', () => {
    const { getByText } = render(<Button>Click me</Button>);
    expect(getByText('Click me')).toBeInTheDocument();
  });

  it('handles click events', () => {
    const handleClick = jest.fn();
    const { getByText } = render(
      <Button onClick={handleClick}>Click me</Button>
    );
    fireEvent.click(getByText('Click me'));
    expect(handleClick).toHaveBeenCalled();
  });
});
```

## 3. Implementera sidtester
```typescript
// tests/unit/frontend/pages/Chat.test.tsx
import { render, screen } from '@testing-library/react';
import Chat from '../../../src/frontend/pages/Chat';

describe('Chat Page', () => {
  it('renders chat interface', () => {
    render(<Chat />);
    expect(screen.getByPlaceholderText('Type your message...')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Send' })).toBeInTheDocument();
  });

  it('displays messages', () => {
    const messages = [
      { id: 1, text: 'Hello', sender: 'user' },
      { id: 2, text: 'Hi there!', sender: 'assistant' }
    ];
    render(<Chat initialMessages={messages} />);
    expect(screen.getByText('Hello')).toBeInTheDocument();
    expect(screen.getByText('Hi there!')).toBeInTheDocument();
  });
});
```

## 4. Implementera servicetester
```typescript
// tests/unit/frontend/services/api.test.ts
import { api } from '../../../src/frontend/services/api';

describe('API Service', () => {
  it('sends messages to backend', async () => {
    const message = { text: 'Hello', type: 'text' };
    const response = await api.sendMessage(message);
    expect(response).toHaveProperty('id');
    expect(response).toHaveProperty('text');
  });

  it('handles errors gracefully', async () => {
    const message = { text: '', type: 'text' };
    await expect(api.sendMessage(message)).rejects.toThrow();
  });
});
```

## 5. Implementera integrationstester
```typescript
// tests/integration/frontend/Chat.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import Chat from '../../../src/frontend/pages/Chat';
import { api } from '../../../src/frontend/services/api';

jest.mock('../../../src/frontend/services/api');

describe('Chat Integration', () => {
  it('sends and receives messages', async () => {
    render(<Chat />);
    
    // Type and send message
    const input = screen.getByPlaceholderText('Type your message...');
    fireEvent.change(input, { target: { value: 'Hello' } });
    fireEvent.click(screen.getByRole('button', { name: 'Send' }));
    
    // Wait for response
    await waitFor(() => {
      expect(screen.getByText('Hello')).toBeInTheDocument();
    });
  });
});
```

## 6. Implementera E2E-tester
```typescript
// tests/e2e/chat.spec.ts
import { test, expect } from '@playwright/test';

test('complete chat flow', async ({ page }) => {
  // Navigate to chat
  await page.goto('/chat');
  
  // Send message
  await page.fill('input[placeholder="Type your message..."]', 'Hello');
  await page.click('button:has-text("Send")');
  
  // Wait for response
  await expect(page.locator('text=Hello')).toBeVisible();
  await expect(page.locator('text=Hi there!')).toBeVisible();
});
```

## 7. Konfigurera testmiljö
```bash
# Installera testverktyg
npm install --save-dev @testing-library/react @testing-library/jest-dom @playwright/test

# Uppdatera package.json
cat > package.json << 'EOF'
{
  "scripts": {
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage",
    "test:e2e": "playwright test"
  }
}
EOF
```

## 8. Kör testerna
```bash
# Kör alla frontend-tester
npm test
npm run test:e2e
``` 