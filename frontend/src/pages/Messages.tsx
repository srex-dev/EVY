import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { Send, Inbox, MessageSquare } from 'lucide-react'
import axios from 'axios'

const API_URL = import.meta.env.REACT_APP_API_URL || 'http://localhost:8000'

interface SMSMessage {
  id?: string
  sender: string
  receiver: string
  content: string
  timestamp?: string
  priority?: string
}

export default function Messages() {
  const [phoneNumber, setPhoneNumber] = useState('+1234567890')
  const [message, setMessage] = useState('')

  const { data: history, refetch } = useQuery({
    queryKey: ['sms-history'],
    queryFn: async () => {
      const response = await axios.get(`${API_URL}/sms/history`)
      return response.data
    },
    refetchInterval: 3000,
  })

  const sendMutation = useMutation({
    mutationFn: async (smsData: SMSMessage) => {
      const response = await axios.post(`${API_URL}/sms/receive`, smsData)
      return response.data
    },
    onSuccess: () => {
      setMessage('')
      refetch()
    },
  })

  const handleSend = () => {
    if (!message.trim()) return

    sendMutation.mutate({
      sender: phoneNumber,
      receiver: '+1000000000', // EVY system number
      content: message,
    })
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h2 className="text-3xl font-bold text-gray-900">Messages</h2>
        <p className="mt-1 text-sm text-gray-600">
          Send and receive SMS messages through EVY
        </p>
      </div>

      {/* Send Message Form */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <Send className="w-5 h-5 mr-2 text-blue-500" />
          Send Test Message
        </h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Your Phone Number
            </label>
            <input
              type="text"
              value={phoneNumber}
              onChange={(e) => setPhoneNumber(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="+1234567890"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Message (max 160 characters)
            </label>
            <textarea
              value={message}
              onChange={(e) => setMessage(e.target.value.slice(0, 160))}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              rows={3}
              placeholder="What is EVY?"
            />
            <p className="mt-1 text-sm text-gray-500 text-right">
              {message.length}/160 characters
            </p>
          </div>
          <button
            onClick={handleSend}
            disabled={sendMutation.isPending || !message.trim()}
            className="w-full bg-blue-500 text-white px-4 py-2 rounded-lg font-medium hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
          >
            {sendMutation.isPending ? 'Sending...' : 'Send Message'}
          </button>
        </div>
      </div>

      {/* Message History */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Received Messages */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center">
              <Inbox className="w-5 h-5 mr-2 text-green-500" />
              Received Messages
            </h3>
          </div>
          <div className="p-4 space-y-3 max-h-96 overflow-y-auto">
            {history?.received?.length > 0 ? (
              history.received.map((msg: SMSMessage, idx: number) => (
                <div key={idx} className="p-3 bg-gray-50 rounded-lg">
                  <div className="flex justify-between mb-1">
                    <span className="text-sm font-medium text-gray-900">
                      {msg.sender}
                    </span>
                    <span className="text-xs text-gray-500">
                      {msg.timestamp ? new Date(msg.timestamp).toLocaleTimeString() : 'Just now'}
                    </span>
                  </div>
                  <p className="text-sm text-gray-700">{msg.content}</p>
                </div>
              ))
            ) : (
              <p className="text-center text-gray-500 py-8">No received messages yet</p>
            )}
          </div>
        </div>

        {/* Sent Messages */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center">
              <MessageSquare className="w-5 h-5 mr-2 text-blue-500" />
              Sent Messages
            </h3>
          </div>
          <div className="p-4 space-y-3 max-h-96 overflow-y-auto">
            {history?.sent?.length > 0 ? (
              history.sent.map((msg: SMSMessage, idx: number) => (
                <div key={idx} className="p-3 bg-blue-50 rounded-lg">
                  <div className="flex justify-between mb-1">
                    <span className="text-sm font-medium text-gray-900">
                      To: {msg.receiver}
                    </span>
                    <span className="text-xs text-gray-500">
                      {msg.timestamp ? new Date(msg.timestamp).toLocaleTimeString() : 'Just now'}
                    </span>
                  </div>
                  <p className="text-sm text-gray-700">{msg.content}</p>
                </div>
              ))
            ) : (
              <p className="text-center text-gray-500 py-8">No sent messages yet</p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}


