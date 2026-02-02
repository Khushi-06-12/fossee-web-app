import React from 'react';

function History({ history, onSelectDataset, currentDatasetId }) {
  if (history.length === 0) {
    return null;
  }

  return (
    <div className="card">
      <h2>Upload History (Last 5)</h2>
      <div className="history-list">
        {history.map((item) => (
          <div
            key={item.id}
            className={`history-item ${item.id === currentDatasetId ? 'active' : ''}`}
            onClick={() => onSelectDataset(item.id)}
          >
            <div className="history-item-name">{item.name}</div>
            <div className="history-item-meta">
              <span>{item.equipment_count} equipment</span>
              <span>{new Date(item.uploaded_at).toLocaleString()}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default History;
