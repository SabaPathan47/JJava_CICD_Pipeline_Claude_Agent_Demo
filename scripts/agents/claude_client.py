"""
claude_client.py
Shared helper used by all three CI/CD pipeline agents to call the
NVIDIA NIM API and get back a structured Markdown report section.
"""
import os
import sys
import json
import urllib.request
import urllib.error

NVIDIA_NIM_API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
MODEL = "meta/llama-3.1-70b-instruct"


def call_claude(system_prompt: str, user_prompt: str, max_tokens: int = 1500) -> str:
    api_key = os.environ.get("NVDAI_API_KEY")
    if not api_key:
        print("ERROR: NVDAI_API_KEY secret is not set.", file=sys.stderr)
        sys.exit(1)

    payload = {
        "model": MODEL,
        "max_tokens": max_tokens,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
    }

    req = urllib.request.Request(
        NVIDIA_NIM_API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_detail = e.read().decode('utf-8')
        print(f"ERROR calling NVIDIA NIM API: {e.code} {error_detail}", file=sys.stderr)
        sys.exit(1)

    # Extract content from NVIDIA's response format
    try:
        content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        print(f"ERROR: Unexpected response format from NVIDIA NIM API", file=sys.stderr)
        print(f"Response: {json.dumps(data)}", file=sys.stderr)
        sys.exit(1)
    
    return content.strip()


def write_report(path: str, content: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Report written to {path}")
