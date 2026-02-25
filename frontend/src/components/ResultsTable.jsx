import { useState, useMemo } from 'react';
import './ResultsTable.css';

function ResultsTable({ results, title, scanType }) {
  const [filter, setFilter] = useState('');
  const [sortKey, setSortKey] = useState('symbol_asc');

  const isSma = scanType === 'sma50';

  const columns = isSma
    ? [
        { key: 'symbol', label: 'Symbol' },
        { key: 'daily_price', label: 'Daily Price' },
        { key: 'daily_sma50', label: 'Daily SMA50' },
        { key: 'hourly_price', label: '1HR Price' },
        { key: 'hourly_sma50', label: '1HR SMA50' },
        { key: 'min15_price', label: '15m Price' },
        { key: 'min15_sma50', label: '15m SMA50' },
      ]
    : [
        { key: 'symbol', label: 'Symbol' },
        { key: 'price', label: 'Price' },
        { key: 'ema10', label: 'EMA 10' },
        { key: 'ema20', label: 'EMA 20' },
        { key: 'ema40', label: 'EMA 40' },
        { key: 'timeframe', label: 'Timeframe' },
      ];

  const priceKey = isSma ? 'daily_price' : 'price';

  const processedData = useMemo(() => {
    let data = [...results];

    // Filter
    if (filter) {
      data = data.filter((r) =>
        r.symbol.toLowerCase().includes(filter.toLowerCase())
      );
    }

    // Sort
    const [key, dir] = sortKey.split('_');
    data.sort((a, b) => {
      if (key === 'symbol') {
        return dir === 'asc'
          ? a.symbol.localeCompare(b.symbol)
          : b.symbol.localeCompare(a.symbol);
      }
      const aVal = a[priceKey] || 0;
      const bVal = b[priceKey] || 0;
      return dir === 'asc' ? aVal - bVal : bVal - aVal;
    });

    return data;
  }, [results, filter, sortKey, priceKey]);

  const exportCSV = () => {
    if (!processedData.length) return;
    const headers = columns.map((c) => c.label).join(',');
    const rows = processedData.map((r) =>
      columns.map((c) => r[c.key] ?? '').join(',')
    );
    const csv = [headers, ...rows].join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${scanType}_results_${new Date().toISOString().slice(0, 10)}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <section className="card results-section">
      <div className="results-top">
        <div className="results-title-row">
          <h2>🟢 {title}</h2>
          <span className="results-count">{processedData.length} stocks</span>
        </div>
        {!isSma && (
          <div className="logic-banner">
            <span className="logic-tag">Signal Logic</span>
            <span>Close &gt; EMA10, 20, 40 &nbsp;·&nbsp; Prev Close &lt; Prev EMA10 (fresh crossover) &nbsp;·&nbsp; EMA10 &gt; EMA20 &gt; EMA40</span>
          </div>
        )}
        <div className="results-controls">
          <input
            type="text"
            className="filter-input"
            placeholder="Filter by symbol..."
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
          />
          <select
            className="sort-select"
            value={sortKey}
            onChange={(e) => setSortKey(e.target.value)}
          >
            <option value="symbol_asc">Symbol A→Z</option>
            <option value="symbol_desc">Symbol Z→A</option>
            <option value="price_desc">Price High→Low</option>
            <option value="price_asc">Price Low→High</option>
          </select>
          <button className="btn-export" onClick={exportCSV}>
            ⬇ Export CSV
          </button>
        </div>
      </div>

      <div className="table-wrapper">
        <table className="results-table">
          <thead>
            <tr>
              <th className="th-num">#</th>
              {columns.map((col) => (
                <th key={col.key}>{col.label}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {processedData.map((row, i) => (
              <tr key={row.symbol}>
                <td className="td-num">{i + 1}</td>
                {columns.map((col) => (
                  <td
                    key={col.key}
                    className={
                      col.key === 'symbol'
                        ? 'td-symbol'
                        : col.key === 'timeframe'
                        ? 'td-tf'
                        : 'td-price'
                    }
                  >
                    {col.key === 'symbol' ? (
                      <span className="symbol-chip">{row.symbol}</span>
                    ) : col.key === 'timeframe' ? (
                      <span className="tf-badge">{row.timeframe}</span>
                    ) : typeof row[col.key] === 'number' ? (
                      `$${row[col.key].toLocaleString()}`
                    ) : (
                      row[col.key] ?? '-'
                    )}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
        {processedData.length === 0 && (
          <div className="table-empty">No results match your filter.</div>
        )}
      </div>
    </section>
  );
}

export default ResultsTable;
