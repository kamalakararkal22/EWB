"""
app/ai.py - Optional AI Helper Module (Local Ollama Integration)

Provides optional AI-powered features (e.g., student profile summarization or
academic recommendation) using a local Ollama instance (e.g., llama3, mistral).
Designed with a graceful fallback if Ollama is not running.
"""

import httpx
from typing import Optional

OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "llama3"


async def generate_student_summary(
    student_name: str,
    course: str,
    model: str = DEFAULT_MODEL,
) -> dict:
    """
    Generate an AI academic summary or career recommendation for a student
    using a locally running Ollama LLM.

    If Ollama is offline or unreachable, returns a helpful fallback response
    without raising an unhandled 500 error.
    """
    prompt = (
        f"Generate a brief 2-sentence encouraging academic and career recommendation "
        f"for a student named '{student_name}' majoring in '{course}'."
    )

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                },
            )

            if response.status_code == 200:
                result = response.json()
                return {
                    "status": "success",
                    "student_name": student_name,
                    "course": course,
                    "model_used": model,
                    "recommendation": result.get("response", "").strip(),
                }
            else:
                return {
                    "status": "unavailable",
                    "message": f"Ollama returned status code {response.status_code}.",
                    "fallback_note": f"{student_name} is enrolled in {course}. Work hard and excel in your coursework!",
                }

    except httpx.ConnectError:
        return {
            "status": "offline",
            "message": "Local Ollama service is not running on http://localhost:11434.",
            "fallback_note": f"{student_name} is enrolled in {course}. Start Ollama ('ollama serve') to enable AI recommendations.",
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "fallback_note": f"Standard academic path for {course}.",
        }
