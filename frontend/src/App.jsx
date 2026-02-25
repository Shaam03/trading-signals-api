import { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import SymbolSearch from './components/SymbolSearch';
import ScanCards from './components/ScanCards';
import ResultsTable from './components/ResultsTable';
import { checkHealth } from './api';
import './App.css';

function App() {
  const [apiOnline, setApiOnline] = useState(false);
  const [results, setResults] = useState([]);
  const [resultsMeta, setResultsMeta] = useState({ title: '', scanType: '' });

  useEffect(() => {
    const ping = async () => {
      try {
        await checkHealth();
        setApiOnline(true);
      } catch {
        setApiOnline(false);
      }
    };
    ping();
    const interval = setInterval(ping, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleResults = (data, title, scanType) => {
    setResults(data);
    setResultsMeta({ title, scanType });
  };

  return (
    <div className="app">
      <Navbar apiOnline={apiOnline} />
      <main className="main-content">
        <section className="hero">
          <h1>Stock Scanner Dashboard</h1>
          <p>Scan 500+ stocks across EMA & SMA indicators. Find strong uptrend signals in real-time.</p>
        </section>
        <SymbolSearch />
        <ScanCards onResults={handleResults} />
        {results.length > 0 && (
          <ResultsTable
            results={results}
            title={resultsMeta.title}
            scanType={resultsMeta.scanType}
          />
        )}
      </main>
      <footer className="footer">
        <p>Trading Signals Dashboard · EMA & SMA Scanner · Data via Yahoo Finance</p>
      </footer>
    </div>
  );
}

export default App;
