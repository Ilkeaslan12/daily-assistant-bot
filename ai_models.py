import os
from openai import OpenAI


# Vercel Environment Variables içindeki anahtarı doğrudan kullanır.
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    raise RuntimeError(
        "OPENROUTER_API_KEY environment variable bulunamadı."
    )


client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)


TEXT_MODEL = "google/gemma-4-31b-it:free"
VISION_MODEL = "google/gemma-4-31b-it:free"


def extract_response_text(response) -> str:
    """OpenRouter cevabını güvenli biçimde metne dönüştürür."""
    if not response.choices:
        raise RuntimeError("OpenRouter herhangi bir cevap döndürmedi.")

    content = response.choices[0].message.content

    if not content:
        raise RuntimeError("OpenRouter boş bir cevap döndürdü.")

    return content.strip()


def generate_summary(conversation_text: str) -> str:
    """Konuşmanın kısa özetini oluşturur."""
    prompt = (
        "Read the conversation below and summarize the user's key details, "
        "topics discussed, and context in 2-3 short sentences. "
        "Provide only the summary:\n\n"
        f"{conversation_text}"
    )

    response = client.chat.completions.create(
        model=TEXT_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    return extract_response_text(response)


def generate_bot_response(api_messages: list) -> str:
    """Yazılım ve teknoloji sorularına cevap oluşturur."""
    response = client.chat.completions.create(
        model=TEXT_MODEL,
        messages=api_messages,
    )

    return extract_response_text(response)


def generate_vision_response(image_url: str) -> str:
    """Teknik görselleri analiz eder."""
    vision_prompt = (
        "You are a senior software engineer. Analyze the provided image. "
        "If the image relates to code, technology, or hardware, analyze it "
        "professionally. If it is unrelated to technology, reply only with: "
        "'I am a software engineer. My expertise is in code and systems, "
        "so I cannot analyze this. Please provide code-related images!'"
    )

    response = client.chat.completions.create(
        model=VISION_MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": vision_prompt,
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url,
                        },
                    },
                ],
            }
        ],
    )

    return extract_response_text(response)


def transcribe_audio(file_path: str) -> str:
    """Geçici ses modülü."""
    return "This is a test message from the voice module."