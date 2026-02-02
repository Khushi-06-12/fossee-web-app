import React, { useState } from 'react';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/equipment';

function CSVUpload({ token, onUploadSuccess, loading }) {
  const [file, setFile] = useState(null);
  const [error, setError] = useState('');
  const [uploading, setUploading] = useState(false);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!file) {
      setError('Please select a file');
      return;
    }

    setUploading(true);
    setError('');

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await axios.post(
        `${API_BASE_URL}/upload/`,
        formData,
        {
          headers: {
            'Authorization': `Token ${token}`,
            'Content-Type': 'multipart/form-data'
          }
        }
      );

      if (response.data.dataset_id) {
        onUploadSuccess(response.data);
        setFile(null);
        e.target.reset();
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Error uploading file');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="card">
      <h2>Upload CSV File</h2>
      <form onSubmit={handleSubmit}>
        <div className="file-input">
          <input
            type="file"
            accept=".csv"
            onChange={handleFileChange}
            className="input"
            disabled={uploading || loading}
          />
        </div>
        {error && <div className="error">{error}</div>}
        <button
          type="submit"
          className="button"
          disabled={uploading || loading || !file}
        >
          {uploading ? 'Uploading...' : 'Upload CSV'}
        </button>
      </form>
      <p style={{ marginTop: '10px', fontSize: '14px', color: '#666' }}>
        Required columns: Equipment Name, Type, Flowrate, Pressure, Temperature
      </p>
    </div>
  );
}

export default CSVUpload;
