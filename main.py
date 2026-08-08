import os
import requests
from bs4 import BeautifulSoup
from openai import OpenAI

# 1. 최신 OpenAI 클라이언트 생성
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 2. 네이버 금융 헤드라인 수집
url = "https://finance.naver.com/news/mainnews.naver"
res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
soup = BeautifulSoup(res.text, "html.parser")

titles = [a.get_text(strip=True) for a in soup.select(".block1 .articleSubject a")[:5]]
kr_news = "\n".join([f"- {t}" for t in titles])

# 3. AI 요약 요청 (최신 문법 적용)
prompt = f"""
당신은 증시 전문가입니다. 아래 한국 증시 주요 뉴스 5개를 바탕으로 바쁜 직장인을 위한 3줄 요약을 작성해주세요.

[오늘의 주요 뉴스]
{kr_news}
"""

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": prompt}]
)

print("=== 오늘의 증시 요약 ===")
print(response.choices[0].message.content)
