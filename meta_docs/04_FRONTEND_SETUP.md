# Frontend Setup

## Projektstruktur

```
src/frontend/
├── public/             # Statiska filer
├── src/               # Källkod
│   ├── components/    # React-komponenter
│   ├── pages/        # Sidkomponenter
│   ├── services/     # API-tjänster
│   ├── store/        # Redux store
│   ├── styles/       # CSS/SCSS
│   └── utils/        # Hjälpfunktioner
├── package.json       # Beroenden
└── tsconfig.json     # TypeScript-konfiguration
```

## Installation

1. Installera beroenden:
```bash
cd src/frontend
npm install
```

2. Konfigurera miljövariabler:
```bash
cp .env.example .env
```

## Utveckling

1. Starta utvecklingsservern:
```bash
npm start
```

2. Bygg för produktion:
```bash
npm run build
```

## Testning

1. Kör enhetstester:
```bash
npm test
```

2. Kör end-to-end-tester:
```bash
npm run e2e
```

## Komponenter

### Huvudkomponenter
- App.tsx
- Layout.tsx
- Router.tsx

### Sidor
- Home.tsx
- Dashboard.tsx
- Settings.tsx

### Delade Komponenter
- Button.tsx
- Input.tsx
- Modal.tsx
- Table.tsx

## Styling

1. Använd SCSS-moduler:
```scss
// Button.module.scss
.button {
  // Stilar
}
```

2. Använd Tailwind CSS:
```jsx
<button className="bg-blue-500 hover:bg-blue-700">
  Click me
</button>
```

## State Management

1. Redux Store:
```typescript
// store/index.ts
import { configureStore } from '@reduxjs/toolkit';

export const store = configureStore({
  reducer: {
    // Reducers
  }
});
```

2. Användning:
```typescript
import { useSelector, useDispatch } from 'react-redux';
```

## API Integration

1. Skapa API-tjänster:
```typescript
// services/api.ts
import axios from 'axios';

export const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL
});
```

2. Använd i komponenter:
```typescript
import { api } from '../services/api';
```

## Deployment

1. Bygg för produktion:
```bash
npm run build
```

2. Deploya till server:
```bash
scp -r build/* user@server:/var/www/html/
```
