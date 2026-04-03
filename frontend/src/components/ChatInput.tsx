import { useState } from 'react'
import { Send, Loader2 } from 'lucide-react'
import { cn } from '@/lib/utils'
import { ragApi } from '@/services/api'
import { useAppStore } from '@/store'
import { generateId } from '@/lib/utils'

export default function ChatInput() {
  const [query, setQuery] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const { addMessage, updateMessage } = useAppStore()

  const sendQuery = async () => {
    if (!query.trim() || isLoading) return

    const userMessageId = generateId()
    addMessage({
      id: userMessageId,
      role: 'user',
      content: query,
      timestamp: new Date(),
    })

    const assistantMessageId = generateId()
    addMessage({
      id: assistantMessageId,
      role: 'assistant',
      content: '',
      timestamp: new Date(),
      isLoading: true,
    })

    setQuery('')
    setIsLoading(true)

    try {
      const response = await ragApi.query({ query })
      updateMessage(assistantMessageId, {
        content: response.answer,
        sources: response.sources,
        isLoading: false,
      })
    } catch (error) {
      updateMessage(assistantMessageId, {
        content: 'Sorry, I encountered an error processing your query.',
        isLoading: false,
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendQuery()
    }
  }

  return (
    <div className="relative">
      <textarea
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Ask questions about your documents..."
        className={cn(
          'w-full rounded-lg border bg-background px-4 py-3 pr-12 text-sm',
          'focus:outline-none focus:ring-2 focus:ring-primary',
          'min-h-[80px] max-h-[200px] resize-none'
        )}
        rows={1}
      />
      <button
        onClick={sendQuery}
        disabled={!query.trim() || isLoading}
        className={cn(
          'absolute right-2 bottom-2 rounded-md p-2 transition-colors',
          'hover:bg-accent disabled:opacity-50'
        )}
      >
        {isLoading ? (
          <Loader2 className="h-5 w-5 animate-spin" />
        ) : (
          <Send className="h-5 w-5" />
        )}
      </button>
    </div>
  )
}
