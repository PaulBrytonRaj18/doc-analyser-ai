import { create } from 'zustand'
import type { Document, ChatMessage, InsightExtractionResponse, HealthStatus } from '@/types'

interface AppState {
  documents: Document[]
  setDocuments: (docs: Document[]) => void
  addDocument: (doc: Document) => void
  removeDocument: (id: string) => void

  chatMessages: ChatMessage[]
  addMessage: (msg: ChatMessage) => void
  updateMessage: (id: string, updates: Partial<ChatMessage>) => void
  clearMessages: () => void

  insights: InsightExtractionResponse | null
  setInsights: (insights: InsightExtractionResponse | null) => void

  health: HealthStatus | null
  setHealth: (health: HealthStatus | null) => void

  isLoading: boolean
  setIsLoading: (loading: boolean) => void

  selectedDocumentIds: string[]
  setSelectedDocumentIds: (ids: string[]) => void
  toggleDocumentSelection: (id: string) => void
}

export const useAppStore = create<AppState>((set) => ({
  documents: [],
  setDocuments: (docs) => set({ documents: docs }),
  addDocument: (doc) => set((state) => ({ documents: [doc, ...state.documents] })),
  removeDocument: (id) => set((state) => ({
    documents: state.documents.filter((d) => d.document_id !== id)
  })),

  chatMessages: [],
  addMessage: (msg) => set((state) => ({ chatMessages: [...state.chatMessages, msg] })),
  updateMessage: (id, updates) => set((state) => ({
    chatMessages: state.chatMessages.map((m) =>
      m.id === id ? { ...m, ...updates } : m
    ),
  })),
  clearMessages: () => set({ chatMessages: [] }),

  insights: null,
  setInsights: (insights) => set({ insights }),

  health: null,
  setHealth: (health) => set({ health }),

  isLoading: false,
  setIsLoading: (loading) => set({ isLoading: loading }),

  selectedDocumentIds: [],
  setSelectedDocumentIds: (ids) => set({ selectedDocumentIds: ids }),
  toggleDocumentSelection: (id) => set((state) => ({
    selectedDocumentIds: state.selectedDocumentIds.includes(id)
      ? state.selectedDocumentIds.filter((docId) => docId !== id)
      : [...state.selectedDocumentIds, id],
  })),
}))
