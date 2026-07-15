from openai import OpenAI
import os

try:
    from config import OPENROUTER_API_KEY
except ImportError:
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Initialize OpenRouter client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

def generate_summary(conversation_text: str) -> str:
    """Summarizes user conversation context into key details."""
    prompt = (
        "Read the conversation below and summarize the user's key details, "
        "topics discussed, and context in 2-3 short sentences. "
        "Provide only the summary:\n" + conversation_text
    )
    
    response = client.chat.completions.create(
        model="google/gemma-4-31b-it:free",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

def generate_bot_response(api_messages: list) -> str:
    """Generates a professional response as a senior software engineer."""
    response = client.chat.completions.create(
        model="google/gemma-4-31b-it:free",
        messages=api_messages
    )
    return response.choices[0].message.content.strip()

def generate_vision_response(image_url: str) -> str:
    """Analyzes images for technical content or returns a refusal message."""
    vision_prompt = (
        "You are a senior software engineer. Analyze the provided image. "
        "Rule 1: If the image relates to code, technology, or hardware, analyze it professionally. "
        "Rule 2: If unrelated to technology, reply ONLY with: 'I am a software engineer. My expertise is in code and systems, so I cannot analyze this. Please provide code-related images!'"
    )
    
    response = client.chat.completions.create(
        model="meta-llama/llama-3.2-11b-vision-instruct:free", 
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": vision_prompt},
                    {"type": "image_url", "image_url": {"url": image_url}}
                ]
            }
        ]
    )
    return response.choices[0].message.content.strip()

def transcribe_audio(file_path: str) -> str:
    """Transcribes audio file to text."""
    # Placeholder for future integration
    return "This is a test message from the voice module."