# -API

이 프로젝트는 한국환경공단 에어코리아 API를 사용하여 미세먼지 경보 발령 현황을 표시하는 웹 애플리케이션입니다.

## 설치 및 실행

1. 의존성 설치:
   ```
   pip install -r requirements.txt
   ```

2. 앱 실행:
   ```
   python app.py
   ```

3. 브라우저에서 http://127.0.0.1:5000으로 접속하여 현황을 확인하세요.

## API 정보

- API 키: 제공된 키를 사용합니다.
- 엔드포인트: http://apis.data.go.kr/B552584/UlfptcaAlarmInqireSvc/getUlfptcaAlarmInfo
- 데이터: 현재 월의 미세먼지 경보 발령 기록을 표시합니다.
