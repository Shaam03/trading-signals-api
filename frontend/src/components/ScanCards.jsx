import { useState, useRef } from 'react';
import { startScan, getScanStatus } from '../api';
import './ScanCards.css';

const SCANS = [
  {
    type: 'ema_daily',
    icon: '📊',
    title: 'EMA Daily',
    desc: 'EMA 10 / 20 / 40 on Daily chart',
    condition: 'Fresh crossover above EMA10 · EMAs stacked 10 > 20 > 40',
    color: 'green',
  },
  {
    type: 'ema_weekly',
    icon: '📈',
    title: 'EMA Weekly',
    desc: 'EMA 10 / 20 / 40 on Weekly chart',
    condition: 'Fresh crossover above EMA10 · EMAs stacked 10 > 20 > 40',
    color: 'blue',
  },
  {
    type: 'sma50',
    icon: '🎯',
    title: 'SMA50 Multi-TF',
    desc: 'SMA 50 on Daily + 1HR + 15min',
    condition: 'Above SMA50 on all 3 timeframes',
    color: 'purple',
  },
];

function ScanCards({ onResults }) {
  const [scanState, setScanState] = useState({});
  const pollRefs = useRef({});

  const handleStartScan = async (scanType) => {
    if (scanState[scanType]?.status === 'running') return;

    setScanState((prev) => ({
      ...prev,
      [scanType]: { status: 'starting', percent: 0, found: 0, total: 0 },
    }));

    try {
      const res = await startScan(scanType);
      const jobId = res.data.job_id;

      setScanState((prev) => ({
        ...prev,
        [scanType]: { status: 'running', percent: 0, found: 0, total: 0, jobId },
      }));

      // Start polling
      pollRefs.current[scanType] = setInterval(async () => {
        try {
          const statusRes = await getScanStatus(jobId);
          const d = statusRes.data;

          setScanState((prev) => ({
            ...prev,
            [scanType]: {
              status: d.status,
              percent: d.percent,
              found: d.results_count || d.results_so_far || 0,
              total: d.total,
              jobId,
            },
          }));

          if (d.status === 'completed') {
            clearInterval(pollRefs.current[scanType]);
            const scan = SCANS.find((s) => s.type === scanType);
            onResults(d.results || [], scan.title + ' Results', scanType);
          }
        } catch {
          // ignore poll errors
        }
      }, 5000);
    } catch {
      setScanState((prev) => ({
        ...prev,
        [scanType]: { status: 'error', percent: 0, found: 0, total: 0 },
      }));
    }
  };

  return (
    <section className="scan-grid">
      {SCANS.map((scan) => {
        const state = scanState[scan.type] || {};
        const isRunning = state.status === 'running' || state.status === 'starting';
        const isDone = state.status === 'completed';

        return (
          <div className={`card scan-card scan-${scan.color}`} key={scan.type}>
            <div className="scan-card-top">
              <span className="scan-icon">{scan.icon}</span>
              <div>
                <h3>{scan.title}</h3>
                <p className="scan-desc">{scan.desc}</p>
              </div>
            </div>
            <div className="scan-condition">{scan.condition}</div>

            {/* Progress */}
            {isRunning && (
              <div className="progress-area">
                <div className="progress-bar">
                  <div
                    className={`progress-fill fill-${scan.color}`}
                    style={{ width: `${state.percent || 0}%` }}
                  />
                </div>
                <div className="progress-info">
                  <span>{state.percent || 0}%</span>
                  <span>{state.found} found</span>
                  <span>{state.total ? `${state.total - (state.total * (state.percent / 100) | 0)} left` : ''}</span>
                </div>
              </div>
            )}

            {isDone && (
              <div className="scan-done">
                ✅ Complete — {state.found} stocks found
              </div>
            )}

            {state.status === 'error' && (
              <div className="scan-error">❌ Scan failed. Try again.</div>
            )}

            <button
              className={`btn-scan btn-${scan.color}`}
              onClick={() => handleStartScan(scan.type)}
              disabled={isRunning}
            >
              {isRunning ? (
                <>
                  <span className="spinner-sm"></span>
                  Scanning...
                </>
              ) : isDone ? (
                'Re-scan'
              ) : (
                'Start Scan'
              )}
            </button>
          </div>
        );
      })}
    </section>
  );
}

export default ScanCards;
