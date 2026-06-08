import sys
sys.path.insert(0, ".")
from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL
from openai import OpenAI

client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL, timeout=30)

# Test different models
for model in ["deepseek-chat", "deepseek-v4-flash"]:
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "你好，请回复：收到"}],
            max_tokens=20
        )
        print(f"{model}: {resp.choices[0].message.content}")
    except Exception as e:
        print(f"{model}: ERROR - {e}")
