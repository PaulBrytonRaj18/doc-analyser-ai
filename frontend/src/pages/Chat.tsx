import { useAppStore } from '@/store'
import ChatInput from '@/components/ChatInput'
import ChatMessages from '@/components/ChatMessages'
import { Trash2 } from 'lucide-react'

export default function Chat() {
  const { chatMessages, clearMessages } = useAppStore()

  return (
    <div className="flex h-[calc(100vh-12rem)] flex-col">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Chat</h1>
          <p className="mt-2 text-muted-foreground">
            Ask questions about your documents using RAG
          </p>
        </div>
        {chatMessages.length > 0 && (
          <button
            onClick={clearMessages}
            className="flex items-center gap-2 rounded-md border px-3 py-2 text-sm hover:bg-accent"
          >
            <Trash2 className="h-4 w-4" />
            Clear Chat
          </button>
        )}
      </div>

      <div className="mt-6 flex-1 overflow-y-auto rounded-lg border bg-card p-6">
        <ChatMessages />
      </div>

      <div className="mt-4">
        <ChatInput />
      </div>
    </div>
  )
}
