import { useState } from 'react';
import { analyzeSymbol } from '../api';
import './SymbolSearch.css';

function SymbolSearch() {
  const [symbol, setSymbol] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const handleAnalyze = async () => {
    if (!symbol.trim()) return;
    setLoading(true);
    setError('');
    setResult(null);

    try {
      const res = await analyzeSymbol(symbol.trim());
      setResult(res.data);
    } catch (err) {
      setError('Failed to analyze symbol. Please check and try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') handleAnalyze();
  };

  const renderSignalCard = (title, icon, data, type) => {
    if (!data) {
      return (
        <div className="signal-card signal-null">
          <div className="signal-card-header">
            <span className="signal-icon">{icon}</span>
            <span className="signal-title">{title}</span>
          </div>
          <div className="signal-body">
            <span className="signal-badge neutral">No Signal</span>
            <p className="signal-note">No fresh EMA crossover signal</p>
          </div>
        </div>
      );
    }

    const isSma = type === 'sma50';

    return (
      <div className="signal-card signal-bullish">
        <div className="signal-card-header">
          <span className="signal-icon">{icon}</span>
          <span className="signal-title">{title}</span>
        </div>
        <div className="signal-body">
          <span className="signal-badge bullish">🟢 BULLISH</span>
          {isSma ? (
            <div className="signal-values">
              <div className="val-row"><span className="val-label">Daily</span><span className="val-num">${data.daily_price}</span><span className="val-sub">SMA50: ${data.daily_sma50}</span></div>
              <div className="val-row"><span className="val-label">1HR</span><span className="val-num">${data.hourly_price}</span><span className="val-sub">SMA50: ${data.hourly_sma50}</span></div>
              <div className="val-row"><span className="val-label">15min</span><span className="val-num">${data.min15_price}</span><span className="val-sub">SMA50: ${data.min15_sma50}</span></div>
            </div>
          ) : (
            <div className="signal-values">
              <div className="val-row"><span className="val-label">Price</span><span className="val-num val-highlight">${data.price}</span></div>
              <div className="val-row"><span className="val-label">EMA 10</span><span className="val-num">${data.ema10}</span></div>
              <div className="val-row"><span className="val-label">EMA 20</span><span className="val-num">${data.ema20}</span></div>
              <div className="val-row"><span className="val-label">EMA 40</span><span className="val-num">${data.ema40}</span></div>
              <p className="signal-note" style={{marginTop: '8px', fontSize: '0.75rem'}}>↑ Fresh crossover · Prev close was below EMA10</p>
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <section className="card search-section">
      <div className="search-header">
        <h2>🔍 Quick Symbol Lookup</h2>
        <p>Instantly analyze any stock across all 3 scanners</p>
      </div>
      <div className="search-bar">
        <input
          type="text"
          value={symbol}
          onChange={(e) => setSymbol(e.target.value.toUpperCase())}
          onKeyDown={handleKeyDown}
          placeholder="Enter symbol (e.g. NVDA, AAPL, TSLA)"
          maxLength={10}
        />
        <button className="btn-analyze" onClick={handleAnalyze} disabled={loading}>
          {loading ? (
            <span className="spinner"></span>
          ) : (
            'Analyze'
          )}
        </button>
      </div>

      {error && <div className="search-error">{error}</div>}

      {result && (
        <div className="signal-grid">
          {renderSignalCard('EMA Daily', '📊', result.ema_daily, 'ema')}
          {renderSignalCard('EMA Weekly', '📈', result.ema_weekly, 'ema')}
          {renderSignalCard('SMA50 Multi-TF', '🎯', result.sma50, 'sma50')}
        </div>
      )}
    </section>
  );
}

export default SymbolSearch;
