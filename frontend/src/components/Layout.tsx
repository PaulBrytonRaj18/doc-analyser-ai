import { useState, ReactNode } from 'react'
import { Outlet, Link, useLocation } from 'react-router-dom'
import { cn } from '@/lib/utils'
import {
  LayoutDashboard,
  FileText,
  Upload,
  Scan,
  BarChart3,
  MessageSquare,
  Layers,
  Download,
  Webhook,
  Settings,
  ChevronLeft,
  ChevronRight,
  Sparkles,
  X,
} from 'lucide-react'

interface LayoutProps {
  children?: ReactNode
}

const navItems = [
  { path: '/', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/documents', label: 'Documents', icon: FileText },
  { path: '/upload', label: 'Upload', icon: Upload },
  { path: '/ocr', label: 'OCR', icon: Scan },
  { path: '/analyze', label: 'Analyze', icon: BarChart3 },
  { path: '/chat', label: 'Chat', icon: MessageSquare },
  { path: '/batch', label: 'Batch', icon: Layers },
  { path: '/export', label: 'Export', icon: Download },
  { path: '/webhooks', label: 'Webhooks', icon: Webhook },
  { path: '/settings', label: 'Settings', icon: Settings },
]

export default function Layout({ children }: LayoutProps) {
  const location = useLocation()
  const [collapsed, setCollapsed] = useState(false)
  const [mobileOpen, setMobileOpen] = useState(false)

  return (
    <div className="min-h-screen bg-[#0B1120]">
      {/* Mobile Overlay */}
      {mobileOpen && (
        <div
          className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 lg:hidden"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          'fixed top-0 left-0 h-full bg-[#111827] border-r border-white/5 z-50 transition-all duration-300',
          'flex flex-col',
          collapsed ? 'w-20' : 'w-64',
          mobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        )}
      >
        {/* Logo Section */}
        <div className="h-16 flex items-center justify-between px-4 border-b border-white/5">
          {!collapsed && (
            <Link to="/" className="flex items-center gap-3">
              <div className="relative">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-[#7C3AED] to-[#06B6D4]">
                  <Sparkles className="h-5 w-5 text-white" />
                </div>
                <div className="absolute -inset-1 rounded-lg bg-gradient-to-br from-[#7C3AED]/20 to-[#06B6D4]/20 blur-md -z-10" />
              </div>
              <div>
                <span className="text-lg font-bold text-white">DocuLens AI</span>
              </div>
            </Link>
          )}
          {collapsed && (
            <Link to="/" className="mx-auto">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-[#7C3AED] to-[#06B6D4]">
                <Sparkles className="h-5 w-5 text-white" />
              </div>
            </Link>
          )}
          <button
            onClick={() => setMobileOpen(false)}
            className="lg:hidden p-2 text-gray-400 hover:text-white transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 py-4 px-3 space-y-1 overflow-y-auto">
          {navItems.map((item) => {
            const isActive = location.pathname === item.path
            return (
              <Link
                key={item.path}
                to={item.path}
                onClick={() => setMobileOpen(false)}
                className={cn(
                  'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200',
                  isActive
                    ? 'bg-[#7C3AED]/10 text-[#7C3AED] border border-[#7C3AED]/20'
                    : 'text-gray-400 hover:bg-white/5 hover:text-white',
                  collapsed && 'justify-center'
                )}
              >
                <item.icon className={cn('h-5 w-5 flex-shrink-0', isActive && 'text-[#7C3AED]')} />
                {!collapsed && <span>{item.label}</span>}
                {isActive && !collapsed && (
                  <div className="ml-auto w-1.5 h-1.5 rounded-full bg-[#06B6D4]" />
                )}
              </Link>
            )
          })}
        </nav>

        {/* Collapse Toggle */}
        <div className="p-3 border-t border-white/5">
          <button
            onClick={() => setCollapsed(!collapsed)}
            className={cn(
              'flex items-center gap-3 w-full px-3 py-2.5 rounded-lg text-sm font-medium text-gray-400 hover:text-white hover:bg-white/5 transition-all duration-200',
              collapsed && 'justify-center'
            )}
          >
            {collapsed ? (
              <ChevronRight className="h-5 w-5" />
            ) : (
              <>
                <ChevronLeft className="h-5 w-5" />
                <span>Collapse</span>
              </>
            )}
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <div
        className={cn(
          'transition-all duration-300',
          collapsed ? 'lg:pl-20' : 'lg:pl-64'
        )}
      >
        {/* Top Bar */}
        <header className="h-16 bg-[#111827]/80 backdrop-blur-md border-b border-white/5 sticky top-0 z-30">
          <div className="h-full px-6 flex items-center justify-between">
            {/* Mobile Menu Toggle */}
            <button
              onClick={() => setMobileOpen(true)}
              className="lg:hidden p-2 -ml-2 text-gray-400 hover:text-white transition-colors"
            >
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>

            {/* Breadcrumb / Page Title */}
            <div className="flex items-center gap-2 text-sm">
              <span className="text-gray-500">Pages</span>
              <span className="text-gray-600">/</span>
              <span className="text-white font-medium">
                {navItems.find((item) => item.path === location.pathname)?.label || 'Dashboard'}
              </span>
            </div>

            {/* Right Actions */}
            <div className="flex items-center gap-4">
              <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full bg-[#06B6D4]/10 border border-[#06B6D4]/20">
                <div className="w-2 h-2 rounded-full bg-[#06B6D4] animate-pulse" />
                <span className="text-xs font-medium text-[#06B6D4]">Gemini Active</span>
              </div>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="p-6">
          {children || <Outlet />}
        </main>

        {/* Footer */}
        <footer className="border-t border-white/5 py-6 px-6">
          <div className="flex items-center justify-between text-sm text-gray-500">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-[#7C3AED] animate-pulse" />
              <span>DocuLens AI v3.0</span>
            </div>
            <div>
              Built with FastAPI, React & Gemini
            </div>
          </div>
        </footer>
      </div>
    </div>
  )
}