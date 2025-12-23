import { useMutation } from '@tanstack/react-query'
import { useEffect, useState } from 'react'
import { sendChatMessage } from '../api/chat'
import type { ChatbotResponse, ChatHistoryItem, ChatSource } from '../types/chat'

const STORAGE_KEY = 'krediplus_chat_history'

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

function loadMessages(): ChatMessage[] {
  try {
    const stored = sessionStorage.getItem(STORAGE_KEY)
    return stored ? JSON.parse(stored) : []
  } catch {
    return []
  }
}

function saveMessages(messages: ChatMessage[]) {
  sessionStorage.setItem(STORAGE_KEY, JSON.stringify(messages))
}

function toHistory(messages: ChatMessage[]): ChatHistoryItem[] {
  return messages
    .filter((m) => !m.isError)
    .map((m) => ({ role: m.role, content: m.content }))
}

export function useChatbot() {
  const [messages, setMessages] = useState<ChatMessage[]>(loadMessages)

  useEffect(() => {
    saveMessages(messages)
  }, [messages])

  const mutation = useMutation<ChatbotResponse, Error, { query: string; history: ChatHistoryItem[] }>({
    mutationFn: ({ query, history }) => sendChatMessage(query, history),
    onSuccess: (response, { query }) => {
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
    if (!query || mutation.isPending) return false

    const history = toHistory(messages)

    setMessages((prev) => [
      ...prev,
      {
        id: createMessageId('user'),
        role: 'user',
        content: query,
        createdAt: new Date().toISOString(),
      },
    ])

    mutation.mutate({ query, history })
    return true
  }

  const clearChat = () => {
    setMessages([])
    sessionStorage.removeItem(STORAGE_KEY)
    mutation.reset()
  }

  return {
    messages,
    sendMessage,
    isSending: mutation.isPending,
    clearChat,
  }
}
