"""
ai_helper.py

AI helper for the Cybersecurity Dashboard.

This version uses the OpenRouter Chat Completions API with the free
model `openai/gpt-oss-20b:free`, which is compatible with the OpenAI
Chat API format.

- The API key is loaded from the environment variable OPENROUTER_API_KEY
  (typically defined in a .env file).
- If the API is not available, the code falls back to a local,
  rule-based "offline assistant" so the dashboard still works.
"""

from __future__ import annotations

import os
import requests
from typing import Optional

from dotenv import load_dotenv

# Load variables from .env in the project root
load_dotenv()


# -------------------------------------------------------------------
# Offline fallback assistant
# -------------------------------------------------------------------
def _offline_response(user_message: str, context_text: Optional[str] = None) -> str:
    """
    Simple rule-based assistant used when no API key is configured or
    when the HTTP request fails. It still uses the incident summary
    from the dashboard (context_text) to give meaningful feedback.
    """
    parts: list[str] = []

    parts.append(
        "Offline assistant mode (no usable AI API call succeeded).\n"
        "Below is a rule-based analysis based on your incident data."
    )

    if context_text:
        parts.append(f"\nIncident summary:\n{context_text}")

    msg = user_message.lower()

    if "priorit" in msg or "first" in msg:
        parts.append(
            "\nPrioritisation advice:\n"
            "- Resolve **High severity** incidents that are still **Open** first.\n"
            "- Next, clear Medium severity incidents that have been open for a long time.\n"
            "- Low severity incidents can be grouped and handled in batches."
        )

    if "phishing" in msg:
        parts.append(
            "\nPhishing guidance:\n"
            "- Check if a large share of incidents are phishing emails.\n"
            "- If yes, recommend short staff training and stronger email filtering rules.\n"
            "- Monitor how phishing incidents change after these actions."
        )

    if "backlog" in msg or "bottleneck" in msg:
        parts.append(
            "\nBacklog / bottleneck analysis:\n"
            "- A high count of *Open* incidents suggests insufficient capacity.\n"
            "- Many incidents stuck in *In Progress* may indicate process bottlenecks.\n"
            "- Compare incident counts per assignee to detect imbalances."
        )

    if len(parts) == 1:
        parts.append(
            "\nGeneral guidance:\n"
            "- Use the filters and charts above to inspect which incident types, "
            "severities, and assignees dominate, then adjust playbooks accordingly."
        )

    parts.append(
        "\nIn a full deployment, this panel sends the same question and context to "
        "the `openai/gpt-oss-20b:free` model via the OpenRouter API."
    )

    return "\n".join(parts)


# -------------------------------------------------------------------
# OpenRouter (OpenAI-compatible) API call
# -------------------------------------------------------------------
def _openrouter_response(
    user_message: str,
    context_text: Optional[str] = None,
) -> Optional[str]:
    """
    Calls the OpenRouter Chat Completions API using the model
    `openai/gpt-oss-20b:free`.

    Returns the model's text response, or None if the API key is missing.
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        # No key configured: let caller fall back to offline mode
        return None

    url = "https://openrouter.ai/api/v1/chat/completions"

    system_prompt = (
        "You are a helpful cybersecurity analyst assistant for a university dashboard. "
        "Explain trends, severity priorities, and risks clearly for a first-year "
        "computer science student. Be concise and practical.\n"
    )

    if context_text:
        system_prompt += f"\nHere is a summary of the current incidents:\n{context_text}\n"

    payload = {
        "model": "openai/gpt-oss-20b:free",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        "temperature": 0.2,
        "max_tokens": 400,
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        # These two are recommended by OpenRouter for identification
        "HTTP-Referer": "http://localhost:8501",
        "X-Title": "Mustafa Intelligence Platform",
    }

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        # Expected format: {"choices": [{"message": {"content": "..."}}, ...]}
        choices = data.get("choices")
        if not choices:
            return "AI API returned no choices."

        content = choices[0]["message"]["content"]
        return content.strip()

    except Exception as e:
        # In case of error we return a short message and let the caller
        # decide whether to fall back to offline mode.
        return f"Error calling OpenRouter API: {e}"


# -------------------------------------------------------------------
# Public function used by Streamlit
# -------------------------------------------------------------------
def ask_cyber_assistant(user_message: str, context_text: Optional[str] = None) -> str:
    """
    Main entry point used by the Streamlit Cyber Dashboard.

    1. Try to call the OpenRouter API with the free `gpt-oss-20b` model.
    2. If that fails or no key is defined, fall back to the offline assistant.
    """
    online_answer = _openrouter_response(user_message, context_text)

    if online_answer is None or online_answer.startswith("Error calling OpenRouter API"):
        # Either no key configured or HTTP error: use offline logic.
        return _offline_response(user_message, context_text)

    return online_answer
