import { useEffect, useRef, useState } from 'react'
import type { FormEvent } from 'react'
import { RotateCcw, Send, X } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useChatbot } from '../hooks/use-chatbot'

type ChatbotWidgetProps = {
  onClose: () => void
}

export function ChatbotWidget({ onClose }: ChatbotWidgetProps) {
  const { messages, sendMessage, isSending, clearChat } = useChatbot()
  const [inputValue, setInputValue] = useState('')
  const scrollRef = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    if (!scrollRef.current) return
    scrollRef.current.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' })
  }, [messages, isSending])

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (sendMessage(inputValue)) {
      setInputValue('')
    }
  }

  const canReset = messages.length > 0 && !isSending

  return (
    <div className="fixed bottom-20 right-6 z-50 w-[380px] max-w-[calc(100%-2rem)] rounded-3xl bg-white shadow-2xl ring-1 ring-slate-200">
      <div className="flex items-center justify-between border-b px-4 py-3">
        <div>
          <p className="text-sm font-semibold text-[#0d2f62]">Asistente virtual</p>
          <p className="text-xs text-slate-500">Consulta documentos reales de KrediPlus.</p>
        </div>
        <div className="flex items-center gap-1">
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8 text-slate-500 hover:text-[#f26522]"
            onClick={clearChat}
            disabled={!canReset}
            aria-label="Reiniciar conversación"
          >
            <RotateCcw className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8 text-slate-500 hover:text-[#f26522]"
            onClick={onClose}
            aria-label="Cerrar chatbot"
          >
            <X className="h-4 w-4" />
          </Button>
        </div>
      </div>

      <div ref={scrollRef} className="h-72 overflow-y-auto bg-slate-50/60 px-4 py-4 text-sm">
        {messages.length === 0 && !isSending ? (
          <div className="rounded-2xl border border-dashed border-slate-200 bg-white/80 p-4 text-center text-slate-500">
            <p className="font-semibold text-[#0d2f62]">¿Sobre qué necesitas información?</p>
            <p className="mt-2 text-xs text-slate-500">
              Pregunta por políticas, misión, visión o procesos y te responderé usando los documentos cargados.
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[90%] rounded-2xl px-4 py-3 text-sm shadow-sm ${
                    message.role === 'user'
                      ? 'bg-gradient-to-r from-[#f26522] to-[#ff8a4c] text-white'
                      : message.isError
                        ? 'border border-rose-100 bg-rose-50 text-rose-700'
                        : 'border border-slate-100 bg-white text-slate-700'
                  }`}
                >
                  <p className="whitespace-pre-line text-sm leading-relaxed">{message.content}</p>
                </div>
              </div>
            ))}
          </div>
        )}

        {isSending && (
          <div className="mt-4 flex items-start gap-2 text-xs text-slate-500">
            <span className="mt-1 inline-flex h-2 w-2 animate-pulse rounded-full bg-[#f26522]" aria-hidden />
            <p>Consultando documentos y generando respuesta...</p>
          </div>
        )}
      </div>

      <form className="border-t bg-white px-4 py-3" onSubmit={handleSubmit}>
        <label className="sr-only" htmlFor="chatbot-message-input">
          Escribe tu mensaje para el chatbot
        </label>
        <div className="flex items-center gap-2">
          <input
            id="chatbot-message-input"
            type="text"
            placeholder="Pregunta algo sobre KrediPlus..."
            value={inputValue}
            onChange={(event) => setInputValue(event.target.value)}
            disabled={isSending}
            className="flex-1 rounded-2xl border border-slate-200 px-3 py-2 text-sm text-slate-700 outline-none transition focus:border-[#f26522] focus:ring-2 focus:ring-[#f26522]/20 disabled:bg-slate-100"
          />
          <Button
            type="submit"
            size="icon"
            className="h-10 w-10 bg-[#f26522] text-white hover:bg-[#d85314] disabled:opacity-60"
            aria-label="Enviar mensaje al chatbot"
            disabled={isSending || inputValue.trim().length === 0}
          >
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </form>
    </div>
  )
}
