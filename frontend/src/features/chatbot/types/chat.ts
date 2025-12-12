export type ChatRequestPayload = {
  query: string
}

export type ChatSourceMetadata = {
  sourceFile: string
  fileType: string
  page?: number | null
  totalPages?: number | null
  chunkIndex?: number | null
  totalChunks?: number | null
  charStart?: number | null
  charEnd?: number | null
}

export type ChatSource = {
  chunkId: number
  documentId: number
  contentPreview: string
  similarity: number
  metadata: ChatSourceMetadata
}

export type ChatbotResponse = {
  response: string
  sources: ChatSource[]
  processingTime?: number
  query: string
}
