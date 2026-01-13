function LoadingSpinner() {
  return (
    <div className="loading-spinner">
      <div className="spinner"></div>
      <p style={{ color: '#4b5563', fontWeight: '500' }}>Makaleler analiz ediliyor, lütfen bekleyin...</p>
    </div>
  );
}

export default LoadingSpinner;
