# Flask Hello World Design (Windows)

## Goal
Windows 환경에서 Flask 프로젝트를 최소 구성으로 시작해, `app.py`에서 Hello World를 출력한다.

## Scope
- 가상환경 생성: `.venv`
- 가상환경 활성화(Windows)
- Flask 설치
- `app.py` 생성 및 실행 확인

## Chosen Approach
수동 설치(최소 단계)로 진행한다.

### Steps
1. `python -m venv .venv`
2. `.venv\Scripts\activate`
3. `python -m pip install flask`
4. 루트에 `app.py` 생성
5. `python app.py` 실행 후 `http://127.0.0.1:5000` 확인

## app.py Behavior
- Flask 앱 인스턴스를 생성한다.
- `/` 경로에서 문자열 `Hello, World!`를 반환한다.
- 직접 실행 시 개발 서버를 `debug=True`로 구동한다.

## Error Handling
- 별도 예외 처리 추가 없음(초기 학습용 최소 범위)

## Verification
- 서버 실행 로그에 `Running on http://127.0.0.1:5000` 확인
- 브라우저에서 `Hello, World!` 렌더링 확인

## Testing
- 자동 테스트는 범위 밖
- 수동 골든패스 검증만 수행
