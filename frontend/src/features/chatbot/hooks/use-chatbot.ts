import { useMutation } from '@tanstack/react-query'
import { useState } from 'react'
import { sendChatMessage } from '../api/chat'
import type { ChatbotResponse, ChatSource } from '../types/chat'

export type ChatMessage = {
  id: string
  role: 'user' | 'assistant'
  content: string
  createdAt: string
  sources?: ChatSource[]
  processingTime?: number
  queryUsed?: string
  isError?: boolean
}

function createMessageId(prefix: string) {
  return `${prefix}-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`
}

export function useChatbot() {
  const [messages, setMessages] = useState<ChatMessage[]>([])

  const mutation = useMutation<ChatbotResponse, Error, string>({
    mutationFn: (query) => sendChatMessage(query),
    onSuccess: (response, query) => {
      setMessages((prev) => [
        ...prev,
        {
          id: createMessageId('assistant'),
          role: 'assistant',
          content: response.response,
          createdAt: new Date().toISOString(),
          sources: response.sources,
          processingTime: response.processingTime,
          queryUsed: response.query || query,
        },
      ])
    },
    onError: (error: Error) => {
      setMessages((prev) => [
        ...prev,
        {
          id: createMessageId('assistant'),
          role: 'assistant',
          content: error.message || 'No fue posible obtener una respuesta.',
          createdAt: new Date().toISOString(),
          isError: true,
        },
      ])
    },
  })

  const sendMessage = (rawQuery: string) => {
    const query = rawQuery.trim()
    if (!query || mutation.isPending) {
      return false
    }

    setMessages((prev) => [
      ...prev,
      {
        id: createMessageId('user'),
        role: 'user',
        content: query,
        createdAt: new Date().toISOString(),
      },
    ])

    mutation.mutate(query)
    return true
  }

  const resetConversation = () => {
    setMessages([])
    mutation.reset()
  }

  return {
    messages,
    sendMessage,
    isSending: mutation.isPending,
    resetConversation,
  }
}
