-- Enable pgvector for semantic retrieval (open source).
CREATE EXTENSION IF NOT EXISTS vector;
-- The app stores embeddings as JSON for portability and computes cosine in
-- Python by default. To scale, migrate Embedding.vector to a native
-- `vector(768)` column and add an ivfflat/hnsw index, e.g.:
--   ALTER TABLE embeddings ADD COLUMN vec vector(768);
--   CREATE INDEX ON embeddings USING hnsw (vec vector_cosine_ops);
