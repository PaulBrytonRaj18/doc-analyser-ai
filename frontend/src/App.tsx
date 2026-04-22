import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Documents from './pages/Documents'
import Chat from './pages/Chat'
import Analysis from './pages/Analysis'
import Analyze from './pages/Analyze'
function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Dashboard />} />
        <Route path="documents" element={<Documents />} />
        <Route path="chat" element={<Chat />} />
        <Route path="analysis" element={<Analysis />} />
        <Route path="analyze" element={<Analyze />} />
      </Route>
    </Routes>
  )
}

export default App
