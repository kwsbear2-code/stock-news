import os
import requests
from bs4 import BeautifulSoup
from openai import OpenAI


# ==========================================
# 1. OpenAI API 키 확인
# ==========================================

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("❌ OPENAI_API_KEY가 설정되어 있지 않습니다.")
    print("API 키를 환경변수에 설정한 후 다시 실행하세요.")
    raise SystemExit


# OpenAI 클라이언트 생성
client = OpenAI(api_key=api_key)


# ==========================================
# 2. 네이버 금융 뉴스 가져오기
# ==========================================

url = "https://finance.naver.com/news/mainnews.naver"

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    )
}


try:
    res = requests.get(
        url,
        headers=headers,
        timeout=10
    )

    res.raise_for_status()

    # 네이버 금융 페이지 한글 인코딩
    res.encoding = "euc-kr"

except requests.RequestException as e:
    print("❌ 네이버 금융 페이지 접속에 실패했습니다.")
    print("오류:", e)
    raise SystemExit


# ==========================================
# 3. HTML 분석
# ==========================================

soup = BeautifulSoup(
    res.text,
    "html.parser"
)


# ==========================================
# 4. 뉴스 제목 5개 가져오기
# ==========================================

titles = []

for a in soup.select(".block1 .articleSubject a")[:5]:

    title = a.get_text(strip=True)

    if title:
        titles.append(title)


# 뉴스 수집 확인
if not titles:

    print("❌ 네이버 금융에서 뉴스 제목을 가져오지 못했습니다.")
    print()
    print("네이버 금융 페이지의 HTML 구조가 변경되었을 가능성이 있습니다.")

    raise SystemExit


# ==========================================
# 5. 뉴스 출력
# ==========================================

print()
print("=" * 50)
print("오늘의 주요 증시 뉴스")
print("=" * 50)

for i, title in enumerate(titles, 1):
    print(f"{i}. {title}")


# GPT에게 전달할 뉴스
kr_news = "\n".join(
    f"- {title}"
    for title in titles
)


# ==========================================
# 6. GPT에게 뉴스 요약 요청
# ==========================================

prompt = f"""
당신은 한국 증시 뉴스를 쉽게 설명하는 분석가입니다.

아래의 한국 증시 주요 뉴스 5개를 읽고
바쁜 직장인이 쉽게 이해할 수 있도록 정리해주세요.

다음 형식으로 작성해주세요.

[오늘의 증시 핵심]
1. 가장 중요한 시장 이슈
2. 주요 업종에 미칠 수 있는 영향
3. 투자자가 주목할 부분

투자 권유나 매수·매도 추천은 하지 말고
뉴스에 나타난 내용을 중심으로 객관적으로 설명해주세요.

[오늘의 주요 뉴스]

{kr_news}
"""


# ==========================================
# 7. OpenAI API 호출
# ==========================================

try:

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


except Exception as e:

    error_text = str(e)

    print()
    print("=" * 50)
    print("❌ OpenAI API 호출에 실패했습니다.")
    print("=" * 50)

    # 크레딧 부족
    if (
        "insufficient_quota" in error_text
        or "credit_balance_exhausted" in error_text
        or "no credits remaining" in error_text
    ):

        print()
        print("원인: OpenAI API 크레딧이 부족합니다.")
        print()
        print("중요:")
        print("현재 프로그램의 문법 오류가 아닙니다.")
        print("OpenAI API 계정의 사용 가능한 크레딧이 없어서")
        print("AI 요약 요청 단계에서 중단된 것입니다.")

    else:

        print()
        print("API 오류 내용:")
        print(error_text)

    raise SystemExit


# ==========================================
# 8. GPT 결과 출력
# ==========================================

print()
print("=" * 50)
print("오늘의 증시 AI 요약")
print("=" * 50)

print(
    response.choices[0].message.content
)
