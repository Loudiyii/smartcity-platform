import React from 'react'
import { Line } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend)

interface AirQualityChartProps {
  data: any[]
}

export const AirQualityChart: React.FC<AirQualityChartProps> = ({ data }) => {
  const chartData = {
    labels: data.map(d => new Date(d.timestamp).toLocaleTimeString()),
    datasets: [
      {
        label: 'PM2.5',
        data: data.map(d => d.pm25),
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
      },
      {
        label: 'PM10',
        data: data.map(d => d.pm10),
        borderColor: 'rgb(239, 68, 68)',
        backgroundColor: 'rgba(239, 68, 68, 0.2)',
      },
    ]
  }

  const options = {
    responsive: true,
    plugins: {
      title: { display: true, text: 'Évolution Qualité Air (24h)' }
    }
  }

  return <Line data={chartData} options={options} />
}
