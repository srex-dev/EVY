import { useQuery } from '@tanstack/react-query'
import { Activity, MessageSquare, Server, TrendingUp } from 'lucide-react'
import axios from 'axios'

const API_URL = import.meta.env.REACT_APP_API_URL || 'http://localhost:8000'

interface ServiceHealth {
  status: string
  details?: Record<string, any>
}

interface ServicesHealth {
  overall_status: string
  services: Record<string, ServiceHealth>
}

export default function Dashboard() {
  const { data: servicesHealth, isLoading } = useQuery<ServicesHealth>({
    queryKey: ['services-health'],
    queryFn: async () => {
      const response = await axios.get(`${API_URL}/services/health`)
      return response.data
    },
    refetchInterval: 5000,
  })

  const stats = [
    {
      name: 'Total Messages',
      value: '0',
      change: '+0%',
      icon: MessageSquare,
      color: 'bg-blue-500',
    },
    {
      name: 'Active Services',
      value: servicesHealth ? Object.keys(servicesHealth.services).length : '0',
      change: servicesHealth?.overall_status === 'healthy' ? 'All Healthy' : 'Degraded',
      icon: Server,
      color: 'bg-green-500',
    },
    {
      name: 'Response Time',
      value: '<1s',
      change: 'Optimal',
      icon: Activity,
      color: 'bg-purple-500',
    },
    {
      name: 'Uptime',
      value: '99.9%',
      change: '+0.1%',
      icon: TrendingUp,
      color: 'bg-orange-500',
    },
  ]

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h2 className="text-3xl font-bold text-gray-900">Dashboard</h2>
        <p className="mt-1 text-sm text-gray-600">
          Real-time overview of EVY system status and metrics
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => (
          <div
            key={stat.name}
            className="bg-white rounded-xl shadow-sm border border-gray-200 p-6"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">{stat.name}</p>
                <p className="mt-2 text-3xl font-bold text-gray-900">{stat.value}</p>
                <p className="mt-1 text-sm text-gray-500">{stat.change}</p>
              </div>
              <div className={`${stat.color} p-3 rounded-lg`}>
                <stat.icon className="w-6 h-6 text-white" />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Services Status */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Services Status</h3>
        </div>
        <div className="p-6">
          {isLoading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
              <p className="mt-2 text-sm text-gray-500">Loading services...</p>
            </div>
          ) : (
            <div className="space-y-3">
              {servicesHealth &&
                Object.entries(servicesHealth.services).map(([name, service]) => (
                  <div
                    key={name}
                    className="flex items-center justify-between p-4 rounded-lg bg-gray-50"
                  >
                    <div className="flex items-center space-x-3">
                      <div
                        className={`w-3 h-3 rounded-full ${
                          service.status === 'healthy'
                            ? 'bg-green-500'
                            : service.status === 'unhealthy'
                            ? 'bg-yellow-500'
                            : 'bg-red-500'
                        }`}
                      ></div>
                      <div>
                        <p className="font-medium text-gray-900">
                          {name.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}
                        </p>
                        <p className="text-sm text-gray-500">{service.status}</p>
                      </div>
                    </div>
                    {service.details && (
                      <div className="text-right">
                        <p className="text-sm text-gray-600">
                          {JSON.stringify(service.details)}
                        </p>
                      </div>
                    )}
                  </div>
                ))}
            </div>
          )}
        </div>
      </div>

      {/* System Info */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Architecture</h3>
          <div className="space-y-3 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">Deployment Model:</span>
              <span className="font-medium text-gray-900">Development</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Node Type:</span>
              <span className="font-medium text-gray-900">lilEVY (Prototype)</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">LLM Provider:</span>
              <span className="font-medium text-gray-900">OpenAI GPT-4</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Vector Database:</span>
              <span className="font-medium text-gray-900">ChromaDB</span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
          <div className="space-y-2">
            <button className="w-full text-left px-4 py-3 rounded-lg bg-blue-50 text-blue-600 font-medium hover:bg-blue-100 transition-colors">
              Send Test SMS
            </button>
            <button className="w-full text-left px-4 py-3 rounded-lg bg-gray-50 text-gray-700 font-medium hover:bg-gray-100 transition-colors">
              View Logs
            </button>
            <button className="w-full text-left px-4 py-3 rounded-lg bg-gray-50 text-gray-700 font-medium hover:bg-gray-100 transition-colors">
              Update Knowledge Base
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}


