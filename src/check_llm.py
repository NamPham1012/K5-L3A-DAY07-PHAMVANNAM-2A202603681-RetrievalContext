"""Kiểm tra kết nối model ngôn ngữ qua OpenRouter."""
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


DAY6_STARTER = Path(
    r"D:\AI THUC CHIEN VIN\code\LAB"
    r"\K5-L3A-Day06-PHAMVANNAM-2A202603681-DataIngestionEngineering"
    r"\starter"
)


def main():
    load_dotenv(DAY6_STARTER / ".env")
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise SystemExit("Thiếu OPENROUTER_API_KEY trong cấu hình Day 6.")

    model = os.getenv("OPENROUTER_CHAT_MODEL", "openai/gpt-4o-mini")
    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "Trả lời bằng tiếng Việt, ngắn gọn."},
            {"role": "user", "content": "Hãy giải thích RAG trong một câu."},
        ],
        max_tokens=100,
    )
    print(f"Model yêu cầu: {model}")
    print(f"Model phản hồi: {response.model}")
    print(f"Câu trả lời: {response.choices[0].message.content}")
    if response.usage:
        print(f"Token đầu vào: {response.usage.prompt_tokens}")
        print(f"Token đầu ra: {response.usage.completion_tokens}")


if __name__ == "__main__":
    main()
