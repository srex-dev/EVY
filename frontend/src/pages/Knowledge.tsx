import { useQuery } from '@tanstack/react-query'
import { Database, BookOpen, Search } from 'lucide-react'
import axios from 'axios'

const API_URL = import.meta.env.REACT_APP_API_URL || 'http://localhost:8000'

export default function Knowledge() {
  const { data: stats } = useQuery({
    queryKey: ['knowledge-stats'],
    queryFn: async () => {
      const response = await axios.get(`${API_URL}/knowledge/stats`)
      return response.data
    },
    refetchInterval: 10000,
  })

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h2 className="text-3xl font-bold text-gray-900">Knowledge Base</h2>
        <p className="mt-1 text-sm text-gray-600">
          Manage EVY's local knowledge and RAG database
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Documents</p>
              <p className="mt-2 text-3xl font-bold text-gray-900">
                {stats?.document_count || 0}
              </p>
            </div>
            <Database className="w-10 h-10 text-blue-500" />
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Collection</p>
              <p className="mt-2 text-lg font-semibold text-gray-900">
                {stats?.collection_name || 'N/A'}
              </p>
            </div>
            <BookOpen className="w-10 h-10 text-green-500" />
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Status</p>
              <p className="mt-2 text-lg font-semibold text-gray-900">
                {stats?.status || 'Unknown'}
              </p>
            </div>
            <Search className="w-10 h-10 text-purple-500" />
          </div>
        </div>
      </div>

      {/* Sample Knowledge */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Sample Knowledge</h3>
        </div>
        <div className="p-6">
          <div className="space-y-4">
            {[
              {
                title: 'About EVY',
                content:
                  'EVY is an SMS-based AI assistant that works offline. It helps people access information without internet.',
                category: 'about',
              },
              {
                title: 'Usage Instructions',
                content:
                  "To use EVY, simply send an SMS with your question. You'll receive a response within 15 seconds.",
                category: 'usage',
              },
              {
                title: 'Features',
                content:
                  'EVY can answer questions, provide local information, and help in emergencies. It runs on solar power.',
                category: 'features',
              },
              {
                title: 'Emergency Protocol',
                content:
                  "For emergencies, include words like 'emergency', 'help', or 'urgent' in your message for priority handling.",
                category: 'emergency',
              },
              {
                title: 'Privacy Policy',
                content:
                  'EVY respects your privacy. All messages are processed locally and not shared with third parties.',
                category: 'privacy',
              },
            ].map((item, idx) => (
              <div key={idx} className="p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-semibold text-gray-900">{item.title}</h4>
                  <span className="px-2 py-1 text-xs font-medium text-blue-700 bg-blue-50 rounded">
                    {item.category}
                  </span>
                </div>
                <p className="text-sm text-gray-700">{item.content}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button className="px-4 py-3 bg-blue-50 text-blue-600 rounded-lg font-medium hover:bg-blue-100 transition-colors">
            Add Document
          </button>
          <button className="px-4 py-3 bg-gray-50 text-gray-700 rounded-lg font-medium hover:bg-gray-100 transition-colors">
            Update Index
          </button>
          <button className="px-4 py-3 bg-gray-50 text-gray-700 rounded-lg font-medium hover:bg-gray-100 transition-colors">
            Export Data
          </button>
        </div>
      </div>
    </div>
  )
}


