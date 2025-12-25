import React from 'react'

interface KPICardProps {
  title: string
  value: number
  unit: string
  severity: 'good' | 'moderate' | 'poor' | 'unhealthy'
}

export const KPICard: React.FC<KPICardProps> = ({ title, value, unit, severity }) => {
  const colors = {
    good: 'bg-green-100 border-green-500',
    moderate: 'bg-yellow-100 border-yellow-500',
    poor: 'bg-orange-100 border-orange-500',
    unhealthy: 'bg-red-100 border-red-500'
  }

  return (
    <div className={`rounded-lg border-l-4 p-6 ${colors[severity]}`}>
      <h3 className="text-sm font-medium text-gray-600">{title}</h3>
      <div className="mt-2 flex items-baseline">
        <p className="text-3xl font-semibold text-gray-900">{value.toFixed(1)}</p>
        <span className="ml-2 text-sm text-gray-500">{unit}</span>
      </div>
    </div>
  )
}
