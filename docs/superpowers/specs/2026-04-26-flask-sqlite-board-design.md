# Flask SQLite Board Design

## Goal
design 디렉터리의 3개 화면(`blog_list`, `post_detail`, `write_post`)을 반영해 Flask + SQLite 게시판 CRUD를 구현한다.

## Scope
- DB 테이블: `posts (id, title, content, created_at)`
- 기능: 글쓰기(C), 목록(R), 상세(R), 수정(U), 삭제(D)
- 상세 페이지에 `[수정] [삭제]` 버튼 배치
- 수정 화면은 글쓰기 폼 재사용
- 삭제 전에 `정말 삭제할까요?` 확인 창 표시

## Chosen Architecture
- 백엔드: `app.py` 단일 파일 + `sqlite3`
- 템플릿: Flask `templates` 디렉터리에 3개 파일
  - `blog_list.html`
  - `post_detail.html`
  - `write_post.html`
- 디자인 ZIP의 `code.html` 스타일/구조를 템플릿으로 변환 적용

## Data Model
- `id INTEGER PRIMARY KEY AUTOINCREMENT`
- `title TEXT NOT NULL`
- `content TEXT NOT NULL`
- `created_at TEXT NOT NULL` (ISO datetime string)

## Routes and Behavior
- `GET /` : 최신순 목록
- `GET /posts/new` : 작성 폼
- `POST /posts` : 생성 후 상세 페이지로 이동
- `GET /posts/<id>` : 상세 페이지
- `GET /posts/<id>/edit` : 수정 폼(작성 폼 재사용)
- `POST /posts/<id>/update` : 수정 저장 후 상세 페이지로 이동
- `POST /posts/<id>/delete` : 삭제 후 목록으로 이동

## UI Details
- 상세 페이지에 `[수정]` 링크, `[삭제]` 버튼 배치
- 삭제 버튼 폼 submit 전에 `confirm('정말 삭제할까요?')` 실행
- 목록/상세/작성(수정 공용) 레이아웃은 첨부 디자인을 최대한 일치하게 구성

## Error Handling
- 존재하지 않는 게시글 ID 접근 시 404 반환
- 필수 입력(title/content) 누락 시 폼 페이지에서 에러 메시지 표시

## Verification
1. 작성 후 목록/상세에 반영된다.
2. 상세에서 수정 버튼으로 진입 후 저장하면 내용이 갱신된다.
3. 상세에서 삭제 버튼 클릭 시 확인 창이 뜬다.
4. 확인 후 삭제되며 목록에서 사라진다.
5. 취소 시 삭제되지 않는다.
