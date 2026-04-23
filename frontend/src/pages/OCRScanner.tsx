import { useState } from 'react'
import FileUploader from '@/components/FileUploader'
import type { OCRResult } from '@/types'

export default function OCRScanner() {
  const [ocrResult, setOcrResult] = useState<OCRResult | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleOCR = async (file: File) => {
    setIsLoading(true)
    setError(null)
    setOcrResult(null)

    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await fetch(`${import.meta.env.VITE_API_URL}/v1/ocr/scan`, {
        method: 'POST',
        headers: {
          'X-API-Key': localStorage.getItem('api_key') || '',
        },
        body: formData,
      })

      if (!response.ok) {
        throw new Error('OCR scan failed')
      }

      const data = await response.json()
      setOcrResult(data.ocr_result)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setIsLoading(false)
    }
  }

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.9) return 'text-emerald-500'
    if (confidence >= 0.7) return 'text-amber-500'
    return 'text-rose-500'
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-3xl font-bold text-slate-100 mb-6">
        OCR Scanner
      </h1>

      <div className="bg-slate-800 rounded-lg p-6 mb-6">
        <FileUploader
          onFileSelect={handleOCR}
          isLoading={isLoading}
          accept="image/*"
          maxSize={100 * 1024 * 1024}
        />
      </div>

      {error && (
        <div className="bg-rose-500/20 text-rose-400 p-4 rounded-lg mb-6">
          {error}
        </div>
      )}

      {ocrResult && (
        <div className="space-y-6">
          <div className="bg-slate-800 rounded-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-slate-100">
                OCR Result
              </h2>
              <div className="flex items-center gap-4">
                <span className="text-slate-400">
                  Language: {ocrResult.language_detected}
                </span>
                <span className={getConfidenceColor(ocrResult.overall_confidence)}>
                  {Math.round(ocrResult.overall_confidence * 100)}% confidence
                </span>
              </div>
            </div>

            {ocrResult.preprocessing_applied.length > 0 && (
              <div className="flex gap-2 mb-4">
                {ocrResult.preprocessing_applied.map((step) => (
                  <span
                    key={step}
                    className="px-2 py-1 bg-cyan-500/20 text-cyan-400 text-sm rounded"
                  >
                    {step}
                  </span>
                ))}
              </div>
            )}

            <pre className="bg-slate-900 p-4 rounded-lg text-slate-300 whitespace-pre-wrap max-h-96 overflow-y-auto">
              {ocrResult.full_text}
            </pre>
          </div>

          {ocrResult.regions.length > 0 && (
            <div className="bg-slate-800 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-slate-100 mb-4">
                Text Regions ({ocrResult.regions.length})
              </h3>
              <div className="space-y-3">
                {ocrResult.regions.map((region) => (
                  <div
                    key={region.region_id}
                    className="flex items-start gap-4 p-3 bg-slate-900 rounded"
                  >
                    <span className="text-slate-500 w-8">
                      #{region.region_id}
                    </span>
                    <div className="flex-1">
                      <p className="text-slate-300">{region.text}</p>
                    </div>
                    <span className={getConfidenceColor(region.confidence)}>
                      {Math.round(region.confidence * 100)}%
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {ocrResult.low_confidence_regions.length > 0 && (
            <div className="bg-amber-500/20 text-amber-400 p-4 rounded-lg">
              Low confidence regions: {ocrResult.low_confidence_regions.join(', ')}
            </div>
          )}
        </div>
      )}
    </div>
  )
}