import { useQuery } from '@tanstack/react-query'
import { Server, Activity, AlertCircle } from 'lucide-react'
import axios from 'axios'

const API_URL = import.meta.env.REACT_APP_API_URL || 'http://localhost:8000'

export default function Services() {
  const { data: servicesHealth, isLoading } = useQuery({
    queryKey: ['services-health'],
    queryFn: async () => {
      const response = await axios.get(`${API_URL}/services/health`)
      return response.data
    },
    refetchInterval: 5000,
  })

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'bg-green-500'
      case 'unhealthy':
        return 'bg-yellow-500'
      default:
        return 'bg-red-500'
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'bg-green-50 text-green-700 border-green-200'
      case 'unhealthy':
        return 'bg-yellow-50 text-yellow-700 border-yellow-200'
      default:
        return 'bg-red-50 text-red-700 border-red-200'
    }
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h2 className="text-3xl font-bold text-gray-900">Services</h2>
        <p className="mt-1 text-sm text-gray-600">
          Monitor and manage EVY nanoservices
        </p>
      </div>

      {/* Overall Status */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">System Status</h3>
            <p className="text-sm text-gray-600 mt-1">
              Overall health of EVY ecosystem
            </p>
          </div>
          <div className="flex items-center space-x-3">
            <Activity className="w-5 h-5 text-gray-400" />
            <span
              className={`px-4 py-2 rounded-full text-sm font-medium border ${
                servicesHealth?.overall_status === 'healthy'
                  ? 'bg-green-50 text-green-700 border-green-200'
                  : 'bg-yellow-50 text-yellow-700 border-yellow-200'
              }`}
            >
              {servicesHealth?.overall_status || 'Unknown'}
            </span>
          </div>
        </div>
      </div>

      {/* Services Grid */}
      {isLoading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-sm text-gray-500">Loading services...</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {servicesHealth &&
            Object.entries(servicesHealth.services).map(([name, service]: [string, any]) => (
              <div
                key={name}
                className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden"
              >
                <div className="p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start space-x-3">
                      <div className={`p-2 rounded-lg ${getStatusColor(service.status)}`}>
                        <Server className="w-5 h-5 text-white" />
                      </div>
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900">
                          {name
                            .split('-')
                            .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
                            .join(' ')}
                        </h3>
                        <p className="text-sm text-gray-500 mt-1">
                          Port: {getServicePort(name)}
                        </p>
                      </div>
                    </div>
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-medium border ${getStatusBadge(
                        service.status
                      )}`}
                    >
                      {service.status}
                    </span>
                  </div>

                  {service.details && (
                    <div className="mt-4 pt-4 border-t border-gray-200">
                      <h4 className="text-sm font-medium text-gray-700 mb-2">Details</h4>
                      <div className="space-y-1">
                        {Object.entries(service.details).map(([key, value]: [string, any]) => (
                          <div key={key} className="flex justify-between text-sm">
                            <span className="text-gray-600">
                              {key.charAt(0).toUpperCase() + key.slice(1).replace(/_/g, ' ')}:
                            </span>
                            <span className="font-medium text-gray-900">
                              {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {service.status !== 'healthy' && (
                  <div className="bg-yellow-50 border-t border-yellow-200 px-6 py-3">
                    <div className="flex items-center text-sm text-yellow-700">
                      <AlertCircle className="w-4 h-4 mr-2" />
                      <span>Service requires attention</span>
                    </div>
                  </div>
                )}
              </div>
            ))}
        </div>
      )}
    </div>
  )
}

function getServicePort(serviceName: string): string {
  const ports: Record<string, string> = {
    'api-gateway': '8000',
    'sms-gateway': '8001',
    'message-router': '8002',
    'llm-inference': '8003',
    'rag-service': '8004',
    'privacy-filter': '8005',
  }
  return ports[serviceName] || 'Unknown'
}


