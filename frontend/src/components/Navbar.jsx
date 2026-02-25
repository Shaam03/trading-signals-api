import './Navbar.css';

function Navbar({ apiOnline }) {
  return (
    <nav className="navbar">
      <div className="nav-brand">
        <span className="nav-logo">📈</span>
        <span className="nav-title">TradingSignals</span>
      </div>
      <div className="nav-status">
        <span className={`status-dot ${apiOnline ? 'online' : 'offline'}`}></span>
        <span className="status-text">
          {apiOnline ? 'API Connected' : 'API Offline'}
        </span>
      </div>
    </nav>
  );
}

export default Navbar;
