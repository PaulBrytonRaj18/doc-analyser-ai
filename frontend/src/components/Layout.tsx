import { Outlet, Link, useLocation } from 'react-router-dom'
import { cn } from '@/lib/utils'
import { LayoutDashboard, FileText, MessageSquare, BarChart3, Settings, Sparkles, Scan } from 'lucide-react'

const navItems = [
  { path: '/', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/documents', label: 'Documents', icon: FileText },
  { path: '/chat', label: 'Chat', icon: MessageSquare },
  { path: '/analyze', label: 'Analyze', icon: Scan },
  { path: '/analysis', label: 'Analysis', icon: BarChart3 },
  { path: '/settings', label: 'Settings', icon: Settings },
]

export default function Layout() {
  const location = useLocation()

  return (
    <div className="min-h-screen bg-background">
      {/* RCB Themed Navigation */}
      <nav className="border-b border-border/50 bg-card/80 backdrop-blur-md sticky top-0 z-50">
        <div className="container mx-auto px-4">
          <div className="flex h-16 items-center justify-between">
            {/* Logo */}
            <Link to="/" className="flex items-center gap-3">
              <div className="relative">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary animate-pulse-red">
                  <Sparkles className="h-6 w-6 text-white" />
                </div>
              </div>
              <div>
                <span className="text-xl font-bold gradient-text">DocuLens AI</span>
                <span className="ml-2 text-xs text-muted-foreground">Powered by Gemini</span>
              </div>
            </Link>

            {/* Navigation */}
            <div className="flex gap-1">
              {navItems.map((item) => (
                <Link
                  key={item.path}
                  to={item.path}
                  className={cn(
                    'flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition-all duration-200',
                    location.pathname === item.path
                      ? 'bg-primary text-primary-foreground shadow-lg shadow-primary/20'
                      : 'text-muted-foreground hover:bg-accent/50 hover:text-foreground'
                  )}
                >
                  <item.icon className="h-4 w-4" />
                  {item.label}
                </Link>
              ))}
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <Outlet />
      </main>

      {/* Footer */}
      <footer className="border-t border-border/50 py-6 mt-12">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between text-sm text-muted-foreground">
            <div className="flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-primary animate-pulse"></span>
              <span>DocuLens AI v3.0</span>
            </div>
            <div>
              Built with ❤️ using FastAPI, React & Gemini
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}
