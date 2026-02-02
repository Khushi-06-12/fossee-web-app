import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './Dashboard.css';
import CSVUpload from './CSVUpload';
import DataTable from './DataTable';
import Charts from './Charts';
import History from './History';

const API_BASE_URL = 'http://localhost:8000/api/equipment';

function Dashboard({ token, username, onLogout }) {
  const [currentDataset, setCurrentDataset] = useState(null);
  const [equipmentData, setEquipmentData] = useState([]);
  const [summary, setSummary] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);

  const axiosConfig = {
    headers: {
      'Authorization': `Token ${token}`,
      'Content-Type': 'multipart/form-data'
    }
  };

  const fetchHistory = async () => {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/history/`,
        { headers: { 'Authorization': `Token ${token}` } }
      );
      setHistory(response.data.history);
    } catch (error) {
      console.error('Error fetching history:', error);
    }
  };

  const loadDataset = async (datasetId) => {
    setLoading(true);
    try {
      // Fetch summary
      const summaryResponse = await axios.get(
        `${API_BASE_URL}/summary/${datasetId}/`,
        { headers: { 'Authorization': `Token ${token}` } }
      );
      setSummary(summaryResponse.data);

      // Fetch equipment data
      const dataResponse = await axios.get(
        `${API_BASE_URL}/data/${datasetId}/`,
        { headers: { 'Authorization': `Token ${token}` } }
      );
      setEquipmentData(dataResponse.data.data);
      setCurrentDataset(summaryResponse.data);
    } catch (error) {
      console.error('Error loading dataset:', error);
      alert('Error loading dataset');
    } finally {
      setLoading(false);
    }
  };

  const handleUploadSuccess = (dataset) => {
    setCurrentDataset(dataset);
    fetchHistory();
    loadDataset(dataset.dataset_id);
  };

  const handleDownloadPDF = async (datasetId) => {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/pdf/${datasetId}/`,
        {
          headers: { 'Authorization': `Token ${token}` },
          responseType: 'blob'
        }
      );
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `equipment_report_${datasetId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Error downloading PDF:', error);
      alert('Error downloading PDF');
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>Chemical Equipment Parameter Visualizer</h1>
        <div className="header-actions">
          <span className="username">Welcome, {username}</span>
          <button onClick={onLogout} className="button logout-button">
            Logout
          </button>
        </div>
      </header>

      <div className="container">
        <CSVUpload
          token={token}
          onUploadSuccess={handleUploadSuccess}
          loading={loading}
        />

        <History
          history={history}
          onSelectDataset={loadDataset}
          currentDatasetId={currentDataset?.dataset_id}
        />

        {currentDataset && summary && (
          <>
            <div className="card">
              <div className="card-header">
                <h2>Summary Statistics</h2>
                <button
                  onClick={() => handleDownloadPDF(currentDataset.dataset_id)}
                  className="button"
                >
                  Download PDF Report
                </button>
              </div>
              <div className="summary-grid">
                <div className="summary-item">
                  <span className="summary-label">Total Equipment:</span>
                  <span className="summary-value">{summary.summary.total_count}</span>
                </div>
                <div className="summary-item">
                  <span className="summary-label">Avg Flowrate:</span>
                  <span className="summary-value">{summary.summary.averages.flowrate}</span>
                </div>
                <div className="summary-item">
                  <span className="summary-label">Avg Pressure:</span>
                  <span className="summary-value">{summary.summary.averages.pressure}</span>
                </div>
                <div className="summary-item">
                  <span className="summary-label">Avg Temperature:</span>
                  <span className="summary-value">{summary.summary.averages.temperature}</span>
                </div>
              </div>
            </div>

            <Charts summary={summary} equipmentData={equipmentData} />

            <DataTable equipmentData={equipmentData} />
          </>
        )}
      </div>
    </div>
  );
}

export default Dashboard;
