export type ChunkKind = "text" | "heading" | "table" | "code" | "caption" | "equation";

export interface Chunk {
  id: string;
  text: string;
  kind: ChunkKind;
  level?: number;
  page: number;
  bbox: [number, number, number, number];
  sectionPath: string[];
  tokenCount: number;
  language?: string;
  confidence: number;
}

export interface TableArtifact {
  id: string;
  page: number;
  mdUrl: string;
  csvUrl: string;
  jsonUrl: string;
  quality: number;
}

export interface ImageArtifact {
  id: string;
  page: number;
  url: string;
  caption?: string;
}

export interface ParseResult {
  jobId: string;
  document: { sha256: string; pageCount: number; ocrPages: number[] };
  markdownUrl: string;
  chunksUrl: string;
  tables: TableArtifact[];
  images: ImageArtifact[];
  stats: {
    headings: number;
    tables: number;
    figures: number;
    chunks: number;
    tokens: number;
  };
}

export type ChunkStrategy =
  | "by_heading"
  | "token_budget"
  | "semantic_block"
  | "by_page"
  | "citation_aware"
  | "hybrid";

export type OcrMode = "auto" | "force" | "off";

export interface ParseRequest {
  ocr?: OcrMode;
  engine?: string;
  chunkStrategy?: ChunkStrategy;
  tokenBudget?: 256 | 512 | 1024 | 2048;
}
