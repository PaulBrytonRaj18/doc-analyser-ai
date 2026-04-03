import { useAppStore } from '@/store'
import { cn } from '@/lib/utils'
import { Bot, User, FileText, ExternalLink } from 'lucide-react'
import ReactMarkdown from 'react-markdown'

export default function ChatMessages() {
  const { chatMessages } = useAppStore()

  if (chatMessages.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center">
        <Bot className="h-16 w-16 text-muted-foreground/50" />
        <h3 className="mt-4 text-lg font-medium">Start a conversation</h3>
        <p className="mt-2 text-sm text-muted-foreground">
          Upload documents and ask questions about them
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {chatMessages.map((message) => (
        <div
          key={message.id}
          className={cn(
            'flex gap-3',
            message.role === 'user' && 'flex-row-reverse'
          )}
        >
          <div
            className={cn(
              'flex h-8 w-8 shrink-0 items-center justify-center rounded-full',
              message.role === 'user' ? 'bg-primary' : 'bg-muted'
            )}
          >
            {message.role === 'user' ? (
              <User className="h-4 w-4 text-primary-foreground" />
            ) : (
              <Bot className="h-4 w-4" />
            )}
          </div>

          <div
            className={cn(
              'max-w-[80%] rounded-lg px-4 py-3',
              message.role === 'user'
                ? 'bg-primary text-primary-foreground'
                : 'bg-muted'
            )}
          >
            {message.isLoading ? (
              <div className="flex items-center gap-2">
                <div className="h-2 w-2 animate-bounce rounded-full bg-current [animation-delay:-0.3s]" />
                <div className="h-2 w-2 animate-bounce rounded-full bg-current [animation-delay:-0.15s]" />
                <div className="h-2 w-2 animate-bounce rounded-full bg-current" />
              </div>
            ) : (
              <>
                <div className="prose prose-sm max-w-none dark:prose-invert">
                  <ReactMarkdown>{message.content}</ReactMarkdown>
                </div>

                {message.sources && message.sources.length > 0 && (
                  <div className="mt-4 border-t pt-4">
                    <p className="text-xs font-medium opacity-70 mb-2">Sources:</p>
                    <div className="space-y-2">
                      {message.sources.map((source, idx) => (
                        <div
                          key={idx}
                          className="flex items-start gap-2 rounded bg-background/50 p-2 text-xs"
                        >
                          <FileText className="h-4 w-4 mt-0.5 shrink-0 opacity-70" />
                          <div className="min-w-0 flex-1">
                            <p className="font-medium truncate">{source.filename}</p>
                            <p className="opacity-70 line-clamp-2">{source.preview}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      ))}
    </div>
  )
}
