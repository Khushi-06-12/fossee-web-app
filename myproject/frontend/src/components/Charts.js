import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar, Pie, Line } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

function Charts({ summary, equipmentData }) {
  if (!summary || !equipmentData) return null;

  // Type Distribution Pie Chart
  const typeDistributionData = {
    labels: Object.keys(summary.summary.type_distribution),
    datasets: [
      {
        label: 'Equipment Count',
        data: Object.values(summary.summary.type_distribution),
        backgroundColor: [
          'rgba(255, 99, 132, 0.6)',
          'rgba(54, 162, 235, 0.6)',
          'rgba(255, 206, 86, 0.6)',
          'rgba(75, 192, 192, 0.6)',
          'rgba(153, 102, 255, 0.6)',
          'rgba(255, 159, 64, 0.6)',
        ],
        borderColor: [
          'rgba(255, 99, 132, 1)',
          'rgba(54, 162, 235, 1)',
          'rgba(255, 206, 86, 1)',
          'rgba(75, 192, 192, 1)',
          'rgba(153, 102, 255, 1)',
          'rgba(255, 159, 64, 1)',
        ],
        borderWidth: 1,
      },
    ],
  };

  // Averages Bar Chart
  const averagesData = {
    labels: ['Flowrate', 'Pressure', 'Temperature'],
    datasets: [
      {
        label: 'Average Values',
        data: [
          summary.summary.averages.flowrate,
          summary.summary.averages.pressure,
          summary.summary.averages.temperature,
        ],
        backgroundColor: 'rgba(54, 162, 235, 0.6)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 1,
      },
    ],
  };

  // Flowrate vs Pressure Line Chart
  const flowratePressureData = {
    labels: equipmentData.slice(0, 20).map((item, index) => `Equipment ${index + 1}`),
    datasets: [
      {
        label: 'Flowrate',
        data: equipmentData.slice(0, 20).map(item => item.flowrate),
        borderColor: 'rgba(75, 192, 192, 1)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        yAxisID: 'y',
      },
      {
        label: 'Pressure',
        data: equipmentData.slice(0, 20).map(item => item.pressure),
        borderColor: 'rgba(255, 99, 132, 1)',
        backgroundColor: 'rgba(255, 99, 132, 0.2)',
        yAxisID: 'y1',
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Equipment Type Distribution',
      },
    },
  };

  const barOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Average Values',
      },
    },
    scales: {
      y: {
        beginAtZero: true,
      },
    },
  };

  const lineOptions = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: 'index',
      intersect: false,
    },
    plugins: {
      title: {
        display: true,
        text: 'Flowrate vs Pressure (First 20 Equipment)',
      },
    },
    scales: {
      y: {
        type: 'linear',
        display: true,
        position: 'left',
        title: {
          display: true,
          text: 'Flowrate',
        },
      },
      y1: {
        type: 'linear',
        display: true,
        position: 'right',
        title: {
          display: true,
          text: 'Pressure',
        },
        grid: {
          drawOnChartArea: false,
        },
      },
    },
  };

  return (
    <div className="charts-container">
      <div className="card">
        <h2>Visualizations</h2>
        <div className="charts-grid">
          <div className="chart-container">
            <Pie data={typeDistributionData} options={chartOptions} />
          </div>
          <div className="chart-container">
            <Bar data={averagesData} options={barOptions} />
          </div>
        </div>
        <div className="chart-container" style={{ marginTop: '20px' }}>
          <Line data={flowratePressureData} options={lineOptions} />
        </div>
      </div>
    </div>
  );
}

export default Charts;
