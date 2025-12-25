import React from 'react'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js'
import { Line } from 'react-chartjs-2'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
)

interface CorrelationChartProps {
  timestamps: string[]
  pollutionData: number[]
  pollutionLabel: string
  weatherData: number[]
  weatherLabel: string
  weatherUnit: string
}

export const CorrelationChart: React.FC<CorrelationChartProps> = ({
  timestamps,
  pollutionData,
  pollutionLabel,
  weatherData,
  weatherLabel,
  weatherUnit
}) => {
  // Format timestamps for display (show only date and hour)
  const labels = timestamps.map(ts => {
    const date = new Date(ts)
    return `${date.getDate()}/${date.getMonth() + 1} ${date.getHours()}h`
  })

  const data = {
    labels,
    datasets: [
      {
        label: pollutionLabel,
        data: pollutionData,
        borderColor: 'rgb(239, 68, 68)', // red-500
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        yAxisID: 'y1',
        tension: 0.3,
        pointRadius: 0,
        borderWidth: 2
      },
      {
        label: weatherLabel,
        data: weatherData,
        borderColor: 'rgb(59, 130, 246)', // blue-500
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        yAxisID: 'y2',
        tension: 0.3,
        pointRadius: 0,
        borderWidth: 2
      }
    ]
  }

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: 'index' as const,
      intersect: false
    },
    plugins: {
      legend: {
        position: 'top' as const,
        labels: {
          usePointStyle: true,
          padding: 15
        }
      },
      title: {
        display: false
      },
      tooltip: {
        callbacks: {
          label: function(context: any) {
            let label = context.dataset.label || ''
            if (label) {
              label += ': '
            }
            if (context.parsed.y !== null) {
              label += context.parsed.y.toFixed(1)
              if (context.datasetIndex === 0) {
                label += ' μg/m³'
              } else {
                label += ` ${weatherUnit}`
              }
            }
            return label
          }
        }
      }
    },
    scales: {
      y1: {
        type: 'linear' as const,
        display: true,
        position: 'left' as const,
        title: {
          display: true,
          text: `${pollutionLabel} (μg/m³)`,
          color: 'rgb(239, 68, 68)'
        },
        ticks: {
          color: 'rgb(239, 68, 68)'
        },
        grid: {
          drawOnChartArea: false
        }
      },
      y2: {
        type: 'linear' as const,
        display: true,
        position: 'right' as const,
        title: {
          display: true,
          text: `${weatherLabel} (${weatherUnit})`,
          color: 'rgb(59, 130, 246)'
        },
        ticks: {
          color: 'rgb(59, 130, 246)'
        },
        grid: {
          drawOnChartArea: false
        }
      },
      x: {
        ticks: {
          maxRotation: 45,
          minRotation: 45,
          autoSkip: true,
          maxTicksLimit: 12
        }
      }
    }
  }

  return (
    <div style={{ height: '400px' }}>
      <Line data={data} options={options} />
    </div>
  )
}
