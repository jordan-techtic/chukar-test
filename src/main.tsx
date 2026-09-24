import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { setupInterceptors } from '@/lib/api/interceptors';
import App from './App';
import './index.css';

setupInterceptors();

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
