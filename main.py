import os
import requests
from bs4 import BeautifulSoup
from openai import OpenAI


# ==========================================
# 1. OpenAI API 키 확인
# ==========================================

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("OPENAI_API_KEY가 설정되지 않았습니다.")

    with open("report.txt", "w", encoding="utf-8") as f:
        f.write(
            "증시 뉴스 리포트\n\n"
            "OPENAI_API_KEY가 설정되지 않았습니다.\n"
        )

    raise SystemExit(1)


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
    response = requests.get(
        url,
        headers=headers,
        timeout=15
    )

    response.raise_for_status()
    response.encoding = "euc-kr"

except Exception as e:

    error_message = (
        "증시 뉴스 리포트\n\n"
        "네이버 금융 접속 실패\n\n"
        f"오류 내용: {e}\n"
    )

    print(error_message)

    with open("report.txt", "w", encoding="utf-8") as f:
        f.write(error_message)

    raise SystemExit(1)


# ==========================================
# 3. HTML 분석
# ==========================================

soup = BeautifulSoup(
    response.text,
    "html.parser"
)


# ==========================================
# 4. 뉴스 제목 5개 수집
# ==========================================

titles = []

for a in soup.select(".block1 .articleSubject a")[:5]:

    title = a.get_text(strip=True)

    if title:
        titles.append(title)


# ==========================================
# 5. 뉴스 수집 실패 확인
# ==========================================

if not titles:

    error_message = (
        "증시 뉴스 리포트\n\n"
        "네이버 금융에서 뉴스 제목을 가져오지 못했습니다.\n"
        "페이지 구조가 변경되었을 가능성이 있습니다.\n"
    )

    print(error_message)

    with open("report.txt", "w", encoding="utf-8") as f:
        f.write(error_message)

    raise SystemExit(1)


# ==========================================
# 6. 뉴스 목록 작성
# ==========================================

news_text = "\n".join(
    f"{i}. {title}"
    for i, title in enumerate(titles, 1)
)


print()
print("=" * 50)
print("오늘의 주요 증시 뉴스")
print("=" * 50)
print(news_text)


# ==========================================
# 7. GPT에게 전달할 내용
# ==========================================

prompt = f"""
당신은 한국 증시 뉴스를 쉽게 설명하는 분석가입니다.

아래의 주요 뉴스 5개를 바탕으로
오늘의 증시 흐름을 이해하기 쉽게 요약해주세요.

다음 형식으로 작성해주세요.

[오늘의 증시 핵심]

1. 오늘의 가장 중요한 이슈
2. 주요 업종에 미칠 수 있는 영향
3. 투자자가 주목할 부분

각 항목은 1~2문장으로 작성하세요.

특정 주식의 매수나 매도를 권유하지 말고
뉴스에 근거하여 객관적으로 설명해주세요.

[주요 뉴스]

{news_text}
"""


# ==========================================
# 8. OpenAI API 호출
# ==========================================

try:

    ai_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3
    )

    ai_summary = ai_response.choices[0].message.content


except Exception as e:

    error_text = str(e)

    if (
        "insufficient_quota" in error_text
        or "credit_balance_exhausted" in error_text
        or "no credits remaining" in error_text
    ):

        ai_summary = (
            "OpenAI API 크레딧이 부족합니다.\n\n"
            "네이버 금융 뉴스 수집은 정상적으로 완료되었지만 "
            "AI 요약 단계에서 중단되었습니다."
        )

    else:

        ai_summary = (
            "OpenAI API 오류가 발생했습니다.\n\n"
            f"오류 내용: {error_text}"
        )


# ==========================================
# 9. 최종 리포트 작성
# ==========================================

report = f"""
========================================
오늘의 증시 뉴스 리포트
========================================

[주요 뉴스]

{news_text}


========================================
AI 증시 요약
========================================

{ai_summary}


========================================
리포트 작성 완료
========================================
"""


# ==========================================
# 10. 화면에 출력
# ==========================================

print()
print(report)


# ==========================================
# 11. report.txt 저장
# ==========================================

with open(
    "report.txt",
    "w",
    encoding="utf-8"
) as f:

    f.write(report)


print()
print("report.txt 파일이 생성되었습니다.")
