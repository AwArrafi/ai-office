import os

import httpx

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
# First load of a model from disk measured at ~61s on the GTX 1650, so keep this generous.
TIMEOUT = float(os.getenv("OLLAMA_TIMEOUT", "300"))
NUM_CTX = int(os.getenv("OLLAMA_NUM_CTX", "4096"))


class OllamaError(Exception):
    pass


def strip_think(text: str) -> str:
    # qwen3 can leak reasoning, sometimes without the opening <think> tag; keep only the final answer.
    if "</think>" in text:
        text = text.rsplit("</think>", 1)[1]
    return text.strip()


async def health() -> dict:
    try:
        async with httpx.AsyncClient(base_url=OLLAMA_URL, timeout=5) as client:
            version = (await client.get("/api/version")).raise_for_status().json()["version"]
            tags = (await client.get("/api/tags")).raise_for_status().json()
        return {"ok": True, "url": OLLAMA_URL, "version": version, "models": [m["name"] for m in tags.get("models", [])]}
    except httpx.HTTPError as e:
        return {"ok": False, "url": OLLAMA_URL, "error": f"Ollama tidak dapat dihubungi: {e!r}"}


async def generate(model: str, system: str, prompt: str) -> dict:
    payload = {"model": model, "system": system, "prompt": prompt, "stream": False, "options": {"num_ctx": NUM_CTX}}
    try:
        async with httpx.AsyncClient(base_url=OLLAMA_URL, timeout=TIMEOUT) as client:
            r = await client.post("/api/generate", json=payload)
    except httpx.ConnectError:
        raise OllamaError(f"Ollama tidak dapat dihubungi di {OLLAMA_URL}. Pastikan Ollama berjalan.")
    except httpx.TimeoutException:
        raise OllamaError(f"Ollama tidak merespons dalam {TIMEOUT:.0f} detik.")
    except httpx.HTTPError as e:
        raise OllamaError(f"Gagal menghubungi Ollama: {e!r}")
    if r.status_code != 200:
        try:
            detail = r.json().get("error", r.text)
        except ValueError:
            detail = r.text
        raise OllamaError(f"Ollama error {r.status_code}: {detail}")
    data = r.json()
    return {
        "text": strip_think(data.get("response", "")),
        "input_tokens": data.get("prompt_eval_count"),
        "output_tokens": data.get("eval_count"),
    }
