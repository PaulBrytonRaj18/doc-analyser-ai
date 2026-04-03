import FileUploader from '@/components/FileUploader'
import DocumentList from '@/components/DocumentList'

export default function Documents() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold">Documents</h1>
        <p className="mt-2 text-muted-foreground">
          Upload and manage your documents for analysis
        </p>
      </div>

      <div className="grid gap-8 lg:grid-cols-2">
        <div className="space-y-4">
          <h2 className="text-xl font-semibold">Upload Files</h2>
          <FileUploader />
        </div>

        <div className="space-y-4">
          <h2 className="text-xl font-semibold">Your Documents</h2>
          <DocumentList />
        </div>
      </div>
    </div>
  )
}
