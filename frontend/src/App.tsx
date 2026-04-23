import { useEffect } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Documents from './pages/Documents'
import Analyze from './pages/Analyze'
import OCRScanner from './pages/OCRScanner'
import Chat from './pages/Chat'
import Analysis from './pages/Analysis'
import BatchProcessor from './pages/BatchProcessor'
import Exporter from './pages/Exporter'
import Settings from './pages/Settings'
import { systemApi, documentApi } from './services/api'
import { useAppStore } from './store'

export default function App() {
  const { setHealth, setDocuments } = useAppStore()

  useEffect(() => {
    systemApi.health().then(setHealth).catch(console.error)
    documentApi.list().then(setDocuments).catch(console.error)
  }, [setHealth, setDocuments])

  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/documents" element={<Documents />} />
        <Route path="/upload" element={<Analyze />} />
        <Route path="/ocr" element={<OCRScanner />} />
        <Route path="/analyze" element={<Analysis />} />
        <Route path="/chat" element={<Chat />} />
        <Route path="/batch" element={<BatchProcessor />} />
        <Route path="/export" element={<Exporter />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Layout>
  )
}