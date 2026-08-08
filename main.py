import os
import requests
from bs4 import BeautifulSoup
from openai import OpenAI

# 1. OpenAI API 클라이언트 생성
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("OPENAI_API_KEY 환경변수가 설정되어 있지 않습니다.")

client = OpenAI(api_key=api_key)


# 2. 네이버 금융 주요 뉴스 수집
url = "https://finance.naver.com/news/mainnews.naver"

headers = {
    "User-Agent": "Mozilla/5.0"
}

res = requests.get(url, headers=headers, timeout=10)
res.raise_for_status()

# 네이버 페이지 한글 인코딩 설정
res.encoding = "euc-kr"

soup = BeautifulSoup(res.text, "html.parser")


# 주요 뉴스 제목 5개 가져오기
titles = [
    a.get_text(strip=True)
    for a in soup.select(".block1 .articleSubject a")[:5]
]

# 뉴스가 정상적으로 수집되었는지 확인
if not titles:
    raise ValueError("네이버 금융에서 뉴스 제목을 가져오지 못했습니다.")

kr_news = "\n".join(
    [f"- {title}" for title in titles]
)


# 3. GPT에게 뉴스 요약 요청
prompt = f"""
당신은 한국 증시 전문 애널리스트입니다.

아래 한국 증시 주요 뉴스 5개를 바탕으로
바쁜 직장인이 빠르게 이해할 수 있도록 핵심 내용을 3줄로 요약해주세요.

각 줄은 다음 내용을 포함해주세요.

1. 오늘 증시에 가장 중요한 이슈
2. 관련 업종이나 종목에 미칠 영향
3. 투자자가 주의해서 볼 포인트

특정 종목의 매수나 매도를 직접적으로 권유하지 말고,
뉴스에 근거하여 객관적으로 설명해주세요.

[오늘의 주요 뉴스]
{kr_news}
"""


# 4. OpenAI API 호출
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ],
    temperature=0.3
)


# 5. 결과 출력
print("\n=== 오늘의 증시 요약 ===")
print(response.choices[0].message.content)
