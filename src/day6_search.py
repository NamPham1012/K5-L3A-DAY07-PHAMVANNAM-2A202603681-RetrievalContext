"""Thử dense retrieval Day 6 từ dự án Day 7."""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv


# Đường dẫn đến thư mục starter của Day 6: ưu tiên biến môi trường DAY6_STARTER,
# mặc định tìm repo Day 6 nằm cạnh repo Day 7 (tránh hardcode theo máy cá nhân).
DAY6_STARTER = Path(os.getenv(
    "DAY6_STARTER",
    str(Path(__file__).resolve().parents[1].parent
        / "K5-L3A-Day06-PHAMVANNAM-2A202603681-DataIngestionEngineering" / "starter"),
))

# Cho Python tìm thấy package src của Day 6.
sys.path.insert(0, str(DAY6_STARTER))

from src.embeddings import MyEmbedder  # type: ignore
from src.store import PgVectorStore  # type: ignore


def main():
    # Đọc cấu hình database và API key từ Day 6.
    env_file = DAY6_STARTER / ".env"
    if not env_file.exists():
        raise FileNotFoundError(f"Không tìm thấy file cấu hình: {env_file}")

    load_dotenv(env_file)

    # Phải dùng model tương thích với index đã tạo ở Day 6.
    model_name = "openai/text-embedding-3-small"
    embedder = MyEmbedder(model_name=model_name)

    if embedder.dimensions != 1536:
        raise ValueError(
            f"Model trả về {embedder.dimensions} chiều; "
            "index Day 6 cần 1536 chiều."
        )

    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise ValueError("Thiếu DATABASE_URL trong cấu hình Day 6.")

    question = "An ninh mạng là gì?"

    print(f"Câu hỏi: {question}")
    print(f"Embedding model: {model_name}")
    print(f"Số chiều: {embedder.dimensions}")

    # 1. Biến câu hỏi thành vector.
    query_vector = embedder.embed_query(question)

    if len(query_vector) != 1536:
        raise ValueError(
            f"Vector câu hỏi có {len(query_vector)} chiều; cần 1536."
        )

    # 2. Tìm trong chunk B đã lưu ở Day 6.
    store = PgVectorStore(database_url, embedder.dimensions)

    try:
        results = store.search(
            strategy="B",
            query_vector=query_vector,
            top_k=3,
            filters=None,
        )
    finally:
        store.conn.close()

    # 3. Hiển thị kết quả để người đọc kiểm tra.
    print(f"\nTìm được {len(results)} đoạn:\n")

    for rank, chunk in enumerate(results, start=1):
        print(f"--- Kết quả {rank} ---")
        print(f"Chunk ID: {chunk['chunk_id']}")
        print(f"Nguồn: {chunk['source']}")
        print(f"Trang PDF: {chunk['page']}")
        print(f"Điểm cosine: {chunk['score']:.4f}")
        print(f"Nội dung: {chunk['text']}")
        print()


if __name__ == "__main__":
    main()
