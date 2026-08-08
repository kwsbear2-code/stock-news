name: Stock News Report

on:
  workflow_dispatch:

jobs:
  stock-news:
    runs-on: ubuntu-latest

    steps:

      # 1. 저장소 가져오기
      - name: Checkout repository
        uses: actions/checkout@v7

      # 2. Python 설치
      - name: Set up Python
        uses: actions/setup-python@v6
        with:
          python-version: "3.12"

      # 3. 필요한 라이브러리 설치
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install openai requests beautifulsoup4

      # 4. 뉴스 프로그램 실행
      - name: Run stock news program
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          python main.py

      # 5. 생성된 리포트 확인
      - name: Check report file
        if: always()
        run: |
          echo "===== 생성된 파일 ====="
          ls -la
          echo ""
          if [ -f report.txt ]; then
            echo "===== report.txt ====="
            cat report.txt
          else
            echo "⚠️ report.txt 파일이 생성되지 않았습니다."
          fi

      # 6. 리포트를 GitHub Actions 결과에 보관
      - name: Upload stock report
        if: always()
        uses: actions/upload-artifact@v7
        with:
          name: stock-news-report
          path: report.txt
          if-no-files-found: warn
