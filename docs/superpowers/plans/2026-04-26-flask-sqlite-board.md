# Flask SQLite Board Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** design 디렉터리의 3개 화면을 반영한 Flask + SQLite 게시판 CRUD를 완성한다.

**Architecture:** `app.py`에서 앱 팩토리, DB 연결, CRUD 라우트를 관리하고, 화면은 `templates/`의 3개 템플릿으로 분리한다. 수정 화면은 작성 템플릿을 재사용하며, 삭제는 상세 화면의 버튼에서 확인창을 거친다. 테스트는 `pytest`로 라우트/동작/UI 핵심 문자열을 검증한다.

**Tech Stack:** Python, Flask, sqlite3, Jinja2, pytest

---

## File Structure

- Modify: `app.py` — Flask 앱 팩토리, DB 초기화, CRUD 라우트
- Create: `templates/blog_list.html` — 목록 페이지 (design/blog_list 반영)
- Create: `templates/post_detail.html` — 상세 페이지 + 수정/삭제 버튼 + confirm
- Create: `templates/write_post.html` — 작성/수정 공용 폼
- Create: `tests/conftest.py` — 테스트 앱/클라이언트 fixture
- Create: `tests/test_board.py` — CRUD/폼 재사용/삭제 확인창/404/검증 테스트

### Task 1: Bootstrap app factory, DB schema, and list page

**Files:**
- Modify: `app.py`
- Create: `templates/blog_list.html`
- Create: `tests/conftest.py`
- Test: `tests/test_board.py`

- [ ] **Step 1: Write the failing test for list page rendering**

Create `tests/test_board.py`:
```python

def test_list_page_renders(client):
    response = client.get("/")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "글쓰기" in html
```

- [ ] **Step 2: Add pytest fixtures for app/client**

Create `tests/conftest.py`:
```python
import pytest

from app import create_app


@pytest.fixture
def app(tmp_path):
    database_path = tmp_path / "test.db"
    app = create_app({"TESTING": True, "DATABASE": str(database_path)})
    return app


@pytest.fixture
def client(app):
    return app.test_client()
```

- [ ] **Step 3: Run test to verify it fails**

Run:
```bash
.venv/Scripts/python -m pytest tests/test_board.py::test_list_page_renders -v
```
Expected: FAIL with `ImportError` or `AttributeError` (`create_app` missing) or route/template missing.

- [ ] **Step 4: Implement minimal app factory, schema init, and list route**

Replace `app.py` with:
```python
import sqlite3
from datetime import datetime
from pathlib import Path

from flask import Flask, g, render_template


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(DATABASE=str(Path(app.instance_path) / "board.db"))

    if test_config:
        app.config.update(test_config)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    def get_db():
        if "db" not in g:
            g.db = sqlite3.connect(app.config["DATABASE"])
            g.db.row_factory = sqlite3.Row
        return g.db

    def close_db(error=None):
        db = g.pop("db", None)
        if db is not None:
            db.close()

    def init_db():
        db = get_db()
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        db.commit()

    @app.before_request
    def ensure_schema():
        init_db()

    app.teardown_appcontext(close_db)

    @app.get("/")
    def list_posts():
        posts = get_db().execute(
            "SELECT id, title, content, created_at FROM posts ORDER BY id DESC"
        ).fetchall()
        return render_template("blog_list.html", posts=posts)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
```

Create `templates/blog_list.html`:
```html
<!doctype html>
<html lang="ko">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
    <title>게시글 목록</title>
  </head>
  <body class="bg-[#faf9f6] text-[#1a1c1a]">
    <main class="max-w-4xl mx-auto px-6 py-10">
      <div class="flex items-center justify-between mb-8">
        <h1 class="text-3xl font-bold">게시글 목록</h1>
        <a href="/posts/new" class="rounded-md bg-[#5e604d] text-white px-4 py-2">글쓰기</a>
      </div>
      <div class="space-y-4">
        {% for post in posts %}
        <a href="/posts/{{ post.id }}" class="block rounded-lg border border-[#dbdad7] p-4 bg-white">
          <h2 class="text-xl font-semibold">{{ post.title }}</h2>
          <p class="text-sm text-[#47473f] mt-2">{{ post.created_at }}</p>
        </a>
        {% else %}
        <p class="text-[#47473f]">아직 게시글이 없습니다.</p>
        {% endfor %}
      </div>
    </main>
  </body>
</html>
```

- [ ] **Step 5: Run test to verify it passes**

Run:
```bash
.venv/Scripts/python -m pytest tests/test_board.py::test_list_page_renders -v
```
Expected: PASS

- [ ] **Step 6: Commit**

Run:
```bash
git add app.py templates/blog_list.html tests/conftest.py tests/test_board.py
git commit -m "feat: bootstrap flask board list page and schema"
```
Expected: git 저장소인 경우 커밋 성공. (현재 디렉터리가 git repo가 아니면 이 단계는 생략)

### Task 2: Implement create and detail views with required buttons

**Files:**
- Modify: `app.py`
- Create: `templates/write_post.html`
- Create: `templates/post_detail.html`
- Test: `tests/test_board.py`

- [ ] **Step 1: Write failing tests for create and detail**

Append to `tests/test_board.py`:
```python

def test_create_post_and_view_detail(client):
    response = client.post(
        "/posts",
        data={"title": "첫 글", "content": "내용입니다."},
        follow_redirects=True,
    )

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "첫 글" in html
    assert "내용입니다." in html
    assert "수정" in html
    assert "삭제" in html


def test_new_post_form_page(client):
    response = client.get("/posts/new")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "name=\"title\"" in html
    assert "name=\"content\"" in html
    assert "action=\"/posts\"" in html
```

- [ ] **Step 2: Run tests to verify they fail**

Run:
```bash
.venv/Scripts/python -m pytest tests/test_board.py::test_create_post_and_view_detail tests/test_board.py::test_new_post_form_page -v
```
Expected: FAIL with 404 for `/posts` or `/posts/new`.

- [ ] **Step 3: Implement create/detail routes and templates**

Update `app.py` imports and routes:
```python
from flask import Flask, abort, g, redirect, render_template, request
```

Add routes inside `create_app` before `return app`:
```python
    @app.get("/posts/new")
    def new_post_form():
        return render_template(
            "write_post.html",
            form_title="글쓰기",
            submit_label="등록",
            form_action="/posts",
            post={"title": "", "content": ""},
            error_message=None,
        )

    @app.post("/posts")
    def create_post():
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()

        if not title or not content:
            return (
                render_template(
                    "write_post.html",
                    form_title="글쓰기",
                    submit_label="등록",
                    form_action="/posts",
                    post={"title": title, "content": content},
                    error_message="제목과 내용을 모두 입력해주세요.",
                ),
                400,
            )

        db = get_db()
        created_at = datetime.now().isoformat(timespec="seconds")
        cursor = db.execute(
            "INSERT INTO posts (title, content, created_at) VALUES (?, ?, ?)",
            (title, content, created_at),
        )
        db.commit()
        return redirect(f"/posts/{cursor.lastrowid}")

    @app.get("/posts/<int:post_id>")
    def post_detail(post_id):
        post = get_db().execute(
            "SELECT id, title, content, created_at FROM posts WHERE id = ?",
            (post_id,),
        ).fetchone()
        if post is None:
            abort(404)
        return render_template("post_detail.html", post=post)
```

Create `templates/write_post.html`:
```html
<!doctype html>
<html lang="ko">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
    <title>{{ form_title }}</title>
  </head>
  <body class="bg-[#faf9f6] text-[#1a1c1a]">
    <main class="max-w-3xl mx-auto px-6 py-10">
      <h1 class="text-3xl font-bold mb-6">{{ form_title }}</h1>
      {% if error_message %}
      <div class="mb-4 rounded-md bg-red-100 px-4 py-3 text-red-800">{{ error_message }}</div>
      {% endif %}
      <form method="post" action="{{ form_action }}" class="space-y-4">
        <label class="block">
          <span class="block font-medium mb-1">제목</span>
          <input name="title" value="{{ post.title }}" class="w-full rounded-md border-[#dbdad7]" />
        </label>
        <label class="block">
          <span class="block font-medium mb-1">내용</span>
          <textarea name="content" rows="10" class="w-full rounded-md border-[#dbdad7]">{{ post.content }}</textarea>
        </label>
        <div class="flex gap-3">
          <button type="submit" class="rounded-md bg-[#5e604d] text-white px-4 py-2">{{ submit_label }}</button>
          <a href="/" class="rounded-md border border-[#dbdad7] px-4 py-2">취소</a>
        </div>
      </form>
    </main>
  </body>
</html>
```

Create `templates/post_detail.html`:
```html
<!doctype html>
<html lang="ko">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
    <title>{{ post.title }}</title>
  </head>
  <body class="bg-[#faf9f6] text-[#1a1c1a]">
    <main class="max-w-3xl mx-auto px-6 py-10">
      <a href="/" class="inline-block mb-6 text-sm text-[#47473f]">← 목록</a>
      <h1 class="text-3xl font-bold mb-3">{{ post.title }}</h1>
      <p class="text-sm text-[#47473f] mb-8">{{ post.created_at }}</p>
      <article class="whitespace-pre-wrap leading-7 mb-10">{{ post.content }}</article>
      <div class="flex gap-3">
        <a href="/posts/{{ post.id }}/edit" class="rounded-md border border-[#dbdad7] px-4 py-2">수정</a>
        <form method="post" action="/posts/{{ post.id }}/delete" onsubmit="return confirm('정말 삭제할까요?');">
          <button type="submit" class="rounded-md bg-red-600 text-white px-4 py-2">삭제</button>
        </form>
      </div>
    </main>
  </body>
</html>
```

- [ ] **Step 4: Run tests to verify they pass**

Run:
```bash
.venv/Scripts/python -m pytest tests/test_board.py::test_create_post_and_view_detail tests/test_board.py::test_new_post_form_page -v
```
Expected: PASS

- [ ] **Step 5: Commit**

Run:
```bash
git add app.py templates/write_post.html templates/post_detail.html tests/test_board.py
git commit -m "feat: add post create and detail pages"
```
Expected: git 저장소인 경우 커밋 성공. (git repo가 아니면 생략)

### Task 3: Implement update/delete, form reuse verification, and edge cases

**Files:**
- Modify: `app.py`
- Modify: `templates/write_post.html`
- Modify: `templates/post_detail.html`
- Test: `tests/test_board.py`

- [ ] **Step 1: Write failing tests for edit/update/delete and validation**

Append to `tests/test_board.py`:
```python

def create_seed_post(client, title="원본 제목", content="원본 내용"):
    response = client.post("/posts", data={"title": title, "content": content})
    location = response.headers["Location"]
    post_id = int(location.rsplit("/", 1)[-1])
    return post_id


def test_edit_uses_same_form_template(client):
    post_id = create_seed_post(client)

    new_form = client.get("/posts/new").get_data(as_text=True)
    edit_form = client.get(f"/posts/{post_id}/edit").get_data(as_text=True)

    assert "name=\"title\"" in new_form
    assert "name=\"title\"" in edit_form
    assert "name=\"content\"" in new_form
    assert "name=\"content\"" in edit_form
    assert "action=\"/posts\"" in new_form
    assert f"action=\"/posts/{post_id}/update\"" in edit_form


def test_update_post(client):
    post_id = create_seed_post(client)

    response = client.post(
        f"/posts/{post_id}/update",
        data={"title": "수정 제목", "content": "수정 내용"},
        follow_redirects=True,
    )

    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "수정 제목" in html
    assert "수정 내용" in html


def test_delete_requires_confirm_text_and_deletes(client):
    post_id = create_seed_post(client)

    detail_html = client.get(f"/posts/{post_id}").get_data(as_text=True)
    assert "정말 삭제할까요?" in detail_html

    delete_response = client.post(f"/posts/{post_id}/delete", follow_redirects=True)
    assert delete_response.status_code == 200

    missing_response = client.get(f"/posts/{post_id}")
    assert missing_response.status_code == 404


def test_missing_post_returns_404(client):
    response = client.get("/posts/9999")
    assert response.status_code == 404


def test_create_validation_error(client):
    response = client.post("/posts", data={"title": "", "content": ""})

    assert response.status_code == 400
    assert "제목과 내용을 모두 입력해주세요." in response.get_data(as_text=True)
```

- [ ] **Step 2: Run tests to verify they fail**

Run:
```bash
.venv/Scripts/python -m pytest tests/test_board.py::test_edit_uses_same_form_template tests/test_board.py::test_update_post tests/test_board.py::test_delete_requires_confirm_text_and_deletes tests/test_board.py::test_missing_post_returns_404 tests/test_board.py::test_create_validation_error -v
```
Expected: FAIL with missing `/edit`, `/update`, `/delete` routes.

- [ ] **Step 3: Implement update/delete routes and form reuse wiring**

Add routes inside `create_app` in `app.py`:
```python
    @app.get("/posts/<int:post_id>/edit")
    def edit_post_form(post_id):
        post = get_db().execute(
            "SELECT id, title, content, created_at FROM posts WHERE id = ?",
            (post_id,),
        ).fetchone()
        if post is None:
            abort(404)
        return render_template(
            "write_post.html",
            form_title="글 수정",
            submit_label="수정 저장",
            form_action=f"/posts/{post_id}/update",
            post=post,
            error_message=None,
        )

    @app.post("/posts/<int:post_id>/update")
    def update_post(post_id):
        existing = get_db().execute("SELECT id FROM posts WHERE id = ?", (post_id,)).fetchone()
        if existing is None:
            abort(404)

        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()

        if not title or not content:
            post_data = {"id": post_id, "title": title, "content": content}
            return (
                render_template(
                    "write_post.html",
                    form_title="글 수정",
                    submit_label="수정 저장",
                    form_action=f"/posts/{post_id}/update",
                    post=post_data,
                    error_message="제목과 내용을 모두 입력해주세요.",
                ),
                400,
            )

        db = get_db()
        db.execute(
            "UPDATE posts SET title = ?, content = ? WHERE id = ?",
            (title, content, post_id),
        )
        db.commit()
        return redirect(f"/posts/{post_id}")

    @app.post("/posts/<int:post_id>/delete")
    def delete_post(post_id):
        db = get_db()
        deleted = db.execute("DELETE FROM posts WHERE id = ?", (post_id,))
        db.commit()
        if deleted.rowcount == 0:
            abort(404)
        return redirect("/")
```

- [ ] **Step 4: Run tests to verify they pass**

Run:
```bash
.venv/Scripts/python -m pytest tests/test_board.py -v
```
Expected: PASS (all board tests green)

- [ ] **Step 5: Commit**

Run:
```bash
git add app.py tests/test_board.py templates/write_post.html templates/post_detail.html
git commit -m "feat: add update delete and form reuse for posts"
```
Expected: git 저장소인 경우 커밋 성공. (git repo가 아니면 생략)

### Task 4: Align templates more closely to provided design HTML and verify manually

**Files:**
- Modify: `templates/blog_list.html`
- Modify: `templates/post_detail.html`
- Modify: `templates/write_post.html`

- [ ] **Step 1: Copy visual tokens from zip design into templates**

Use these sources:
- `design/stitch_simple_beige_blog_ui.zip` → `blog_list/code.html`
- `design/stitch_simple_beige_blog_ui.zip` → `post_detail/code.html`
- `design/stitch_simple_beige_blog_ui.zip` → `write_post/code.html`

Apply:
- Tailwind CDN and same font imports
- background/surface color palette
- card/container spacing and button styles

Expected: 페이지 톤/레이아웃이 첨부 디자인과 유사해진다.

- [ ] **Step 2: Run full test suite after markup refinement**

Run:
```bash
.venv/Scripts/python -m pytest tests/test_board.py -v
```
Expected: PASS

- [ ] **Step 3: Run app and execute manual verification flow**

Run:
```bash
.venv/Scripts/python app.py
```
Manual checks:
1. `/` 목록에서 글쓰기 이동
2. 글 작성 후 상세 이동
3. 상세의 `[수정] [삭제]` 버튼 확인
4. 수정 진입 시 작성 폼과 같은 필드 구조 확인
5. 삭제 클릭 시 `정말 삭제할까요?` 확인창 확인
6. 확인 시 삭제, 취소 시 유지

Expected: 모든 동작이 요구사항과 일치.

- [ ] **Step 4: Commit**

Run:
```bash
git add templates/blog_list.html templates/post_detail.html templates/write_post.html
git commit -m "style: match board pages to provided design"
```
Expected: git 저장소인 경우 커밋 성공. (git repo가 아니면 생략)
