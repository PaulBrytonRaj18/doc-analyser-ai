import { useEffect, useState } from 'react'
import { FileText, MessageSquare, Brain, TrendingUp, Database, Zap, Sparkles, ChevronRight } from 'lucide-react'
import { Link } from 'react-router-dom'
import { systemApi, ragApi } from '@/services/api'
import { useAppStore } from '@/store'

export default function Dashboard() {
  const { health, setHealth } = useAppStore()
  const [stats, setStats] = useState<{ total_vectors: number; dimension: number } | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [healthData, statsDataRaw] = await Promise.all([
          systemApi.health(),
          ragApi.getStats().catch(() => ({ total_vectors: 0, dimension: 0 })),
        ])
        setHealth(healthData)
        const stats = statsDataRaw as { total_vectors: number; dimension: number }
        setStats(stats)
      } catch (error) {
        console.error('Failed to fetch data:', error)
      } finally {
        setIsLoading(false)
      }
    }
    fetchData()
  }, [setHealth])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-24">
        <div className="flex flex-col items-center gap-4">
          <div className="relative">
            <div className="h-16 w-16 animate-spin rounded-full border-4 border-primary/20 border-t-primary" />
            <Sparkles className="absolute inset-0 m-auto h-8 w-8 text-primary animate-pulse" />
          </div>
          <p className="text-muted-foreground">Loading DocuLens AI...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="relative overflow-hidden rounded-2xl border border-primary/20 bg-gradient-to-br from-card to-card/50 p-8">
        <div className="absolute -right-10 -top-10 h-40 w-40 rounded-full bg-primary/10 blur-3xl" />
        <div className="absolute -bottom-10 -left-10 h-32 w-32 rounded-full bg-primary/5 blur-2xl" />
        
        <div className="relative">
          <div className="flex items-center gap-2 text-primary">
            <Sparkles className="h-5 w-5" />
            <span className="text-sm font-medium">AI-Powered Document Intelligence</span>
          </div>
          <h1 className="mt-4 text-4xl font-bold tracking-tight">
            Welcome to <span className="gradient-text">DocuLens AI</span>
          </h1>
          <p className="mt-4 max-w-2xl text-lg text-muted-foreground">
            Transform how you interact with documents. Upload, analyze, and extract insights 
            using cutting-edge AI powered by Google's Gemini.
          </p>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Documents"
          value={useAppStore.getState().documents.length}
          icon={FileText}
          gradient="from-red-500/20 to-transparent"
        />
        <StatCard
          title="Vector Chunks"
          value={stats?.total_vectors || 0}
          icon={Database}
          gradient="from-orange-500/20 to-transparent"
        />
        <StatCard
          title="AI Features"
          value={4}
          icon={Brain}
          gradient="from-purple-500/20 to-transparent"
        />
        <StatCard
          title="Status"
          value={health?.features.rag ? 'Online' : 'Offline'}
          icon={Zap}
          gradient="from-green-500/20 to-transparent"
          isStatus
        />
      </div>

      {/* Feature Cards */}
      <div className="grid gap-6 lg:grid-cols-3">
        <FeatureCard
          title="Upload & Index"
          description="Upload PDF, DOCX, TXT files. They are automatically chunked and embedded for semantic search."
          icon={FileText}
          href="/documents"
          color="red"
        />
        <FeatureCard
          title="RAG Chat"
          description="Ask questions in natural language. Get answers with source citations from your documents."
          icon={MessageSquare}
          href="/chat"
          color="orange"
        />
        <FeatureCard
          title="Advanced Analysis"
          description="Synthesize multiple documents, compare versions, extract action items and insights."
          icon={TrendingUp}
          href="/analysis"
          color="purple"
        />
      </div>

      {/* Getting Started */}
      <div className="rounded-xl border border-border/50 bg-card/50 p-6">
        <h2 className="text-xl font-semibold">Quick Start</h2>
        <div className="mt-4 grid gap-4 md:grid-cols-2">
          <QuickStart
            step={1}
            title="Upload Documents"
            description="Add files to start analyzing"
            href="/documents"
          />
          <QuickStart
            step={2}
            title="Ask Questions"
            description="Get AI-powered answers"
            href="/chat"
          />
        </div>
      </div>
    </div>
  )
}

function StatCard({
  title,
  value,
  icon: Icon,
  gradient,
  isStatus = false,
}: {
  title: string
  value: number | string
  icon: React.ElementType
  gradient: string
  isStatus?: boolean
}) {
  const isOnline = value === 'Online' || (typeof value === 'number' && value > 0)
  
  return (
    <div className={`relative overflow-hidden rounded-xl border bg-gradient-to-br ${gradient} p-6 transition-all hover:scale-[1.02]`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-muted-foreground">{title}</p>
          <p className={`mt-1 text-3xl font-bold ${isStatus ? (isOnline ? 'text-green-500' : 'text-yellow-500') : ''}`}>
            {value}
          </p>
        </div>
        <div className={`rounded-full p-3 ${isStatus ? (isOnline ? 'bg-green-500/20' : 'bg-yellow-500/20') : 'bg-primary/20'}`}>
          <Icon className={`h-6 w-6 ${isStatus ? (isOnline ? 'text-green-500' : 'text-yellow-500') : 'text-primary'}`} />
        </div>
      </div>
    </div>
  )
}

function FeatureCard({
  title,
  description,
  icon: Icon,
  href,
  color,
}: {
  title: string
  description: string
  icon: React.ElementType
  href: string
  color: 'red' | 'orange' | 'purple'
}) {
  const colorClasses = {
    red: 'border-red-500/30 hover:border-red-500/50 hover:bg-red-500/5',
    orange: 'border-orange-500/30 hover:border-orange-500/50 hover:bg-orange-500/5',
    purple: 'border-purple-500/30 hover:border-purple-500/50 hover:bg-purple-500/5',
  }
  
  return (
    <Link
      to={href}
      className={`group rounded-xl border bg-card p-6 transition-all ${colorClasses[color]} rcb-glow`}
    >
      <div className="flex items-center gap-4">
        <div className={`rounded-lg p-3 bg-${color === 'red' ? 'primary' : color === 'orange' ? 'orange-500' : 'purple-500'}/20`}>
          <Icon className={`h-6 w-6 text-${color === 'red' ? 'primary' : color === 'orange' ? 'orange-500' : 'purple-500'}`} />
        </div>
        <ChevronRight className="h-5 w-5 text-muted-foreground transition-transform group-hover:translate-x-1" />
      </div>
      <h3 className="mt-4 text-lg font-semibold">{title}</h3>
      <p className="mt-2 text-sm text-muted-foreground">{description}</p>
    </Link>
  )
}

function QuickStart({
  step,
  title,
  description,
  href,
}: {
  step: number
  title: string
  description: string
  href: string
}) {
  return (
    <Link
      to={href}
      className="flex items-start gap-4 rounded-lg border border-border/50 p-4 transition-colors hover:bg-accent"
    >
      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary text-sm font-bold text-primary-foreground">
        {step}
      </div>
      <div>
        <p className="font-medium">{title}</p>
        <p className="text-sm text-muted-foreground">{description}</p>
      </div>
    </Link>
  )
}
