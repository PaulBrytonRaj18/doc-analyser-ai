import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { Document, ChatMessage, AnalysisResult, BatchJobStatus, HealthStatus } from '@/types'

interface AppState {
  documents: Document[]
  setDocuments: (docs: Document[]) => void
  addDocument: (doc: Document) => void
  removeDocument: (id: string) => void
  updateDocument: (id: string, updates: Partial<Document>) => void

  chatMessages: ChatMessage[]
  addMessage: (msg: ChatMessage) => void
  updateMessage: (id: string, updates: Partial<ChatMessage>) => void
  clearMessages: () => void

  currentAnalysis: AnalysisResult | null
  setCurrentAnalysis: (analysis: AnalysisResult | null) => void

  batchJobs: BatchJobStatus[]
  addBatchJob: (job: BatchJobStatus) => void
  updateBatchJob: (batchId: string, updates: Partial<BatchJobStatus>) => void

  health: HealthStatus | null
  setHealth: (health: HealthStatus | null) => void

  isLoading: boolean
  setIsLoading: (loading: boolean) => void

  uploadProgress: number
  setUploadProgress: (progress: number) => void

  selectedDocumentIds: string[]
  setSelectedDocumentIds: (ids: string[]) => void
  toggleDocumentSelection: (id: string) => void

  sidebarCollapsed: boolean
  setSidebarCollapsed: (collapsed: boolean) => void
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      documents: [],
      setDocuments: (docs) => set({ documents: docs }),
      addDocument: (doc) => set((state) => ({ documents: [doc, ...state.documents] })),
      removeDocument: (id) => set((state) => ({
        documents: state.documents.filter((d) => d.document_id !== id)
      })),
      updateDocument: (id, updates) => set((state) => ({
        documents: state.documents.map((d) =>
          d.document_id === id ? { ...d, ...updates } : d
        )
      })),

      chatMessages: [],
      addMessage: (msg) => set((state) => ({ chatMessages: [...state.chatMessages, msg] })),
      updateMessage: (id, updates) => set((state) => ({
        chatMessages: state.chatMessages.map((m) =>
          m.id === id ? { ...m, ...updates } : m
        )
      })),
      clearMessages: () => set({ chatMessages: [] }),

      currentAnalysis: null,
      setCurrentAnalysis: (analysis) => set({ currentAnalysis: analysis }),

      batchJobs: [],
      addBatchJob: (job) => set((state) => ({ batchJobs: [...state.batchJobs, job] })),
      updateBatchJob: (batchId, updates) => set((state) => ({
        batchJobs: state.batchJobs.map((b) =>
          b.batch_id === batchId ? { ...b, ...updates } : b
        )
      })),

      health: null,
      setHealth: (health) => set({ health }),

      isLoading: false,
      setIsLoading: (loading) => set({ isLoading: loading }),

      uploadProgress: 0,
      setUploadProgress: (progress) => set({ uploadProgress: progress }),

      selectedDocumentIds: [],
      setSelectedDocumentIds: (ids) => set({ selectedDocumentIds: ids }),
      toggleDocumentSelection: (id) => set((state) => ({
        selectedDocumentIds: state.selectedDocumentIds.includes(id)
          ? state.selectedDocumentIds.filter((docId) => docId !== id)
          : [...state.selectedDocumentIds, id],
      })),

      sidebarCollapsed: false,
      setSidebarCollapsed: (collapsed) => set({ sidebarCollapsed: collapsed }),
    }),
    {
      name: 'doculens-storage',
      partialize: (state) => ({
        documents: state.documents,
        selectedDocumentIds: state.selectedDocumentIds,
        sidebarCollapsed: state.sidebarCollapsed,
      }),
    }
  )
)