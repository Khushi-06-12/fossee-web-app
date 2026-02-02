import React from 'react';

function DataTable({ equipmentData }) {
  if (!equipmentData || equipmentData.length === 0) {
    return null;
  }

  return (
    <div className="card">
      <h2>Equipment Data Table</h2>
      <div style={{ overflowX: 'auto' }}>
        <table className="table">
          <thead>
            <tr>
              <th>Equipment Name</th>
              <th>Type</th>
              <th>Flowrate</th>
              <th>Pressure</th>
              <th>Temperature</th>
            </tr>
          </thead>
          <tbody>
            {equipmentData.map((item) => (
              <tr key={item.id}>
                <td>{item.equipment_name}</td>
                <td>{item.equipment_type}</td>
                <td>{item.flowrate.toFixed(2)}</td>
                <td>{item.pressure.toFixed(2)}</td>
                <td>{item.temperature.toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default DataTable;
