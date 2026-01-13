import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

console.log('React app başlatılıyor...');

const rootElement = document.getElementById('root');
if (!rootElement) {
  console.error('Root element bulunamadı!');
} else {
  console.log('Root element bulundu:', rootElement);
  try {
    createRoot(rootElement).render(
      <StrictMode>
        <App />
      </StrictMode>,
    );
    console.log('React app render edildi');
  } catch (error) {
    console.error('Render hatası:', error);
  }
}
