import sqlite3
from pathlib import Path

from flask import Flask, abort, redirect, render_template, request, url_for

app = Flask(__name__)
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "posts.db"


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
            )
            """
        )


def get_post_or_404(post_id: int) -> sqlite3.Row:
    with get_db() as conn:
        post = conn.execute(
            "SELECT id, title, content, created_at FROM posts WHERE id = ?", (post_id,)
        ).fetchone()
    if post is None:
        abort(404)
    return post


@app.get("/")
def list_posts():
    per_page = 10
    page = request.args.get("page", default=1, type=int) or 1
    if page < 1:
        page = 1

    search = request.args.get("q", default="", type=str).strip()
    sort = request.args.get("sort", default="latest", type=str)

    sort_map = {
        "latest": "id DESC",
        "oldest": "id ASC",
        "title": "title COLLATE NOCASE ASC",
    }
    if sort not in sort_map:
        sort = "latest"

    where_sql = ""
    params: list[object] = []
    if search:
        where_sql = "WHERE title LIKE ? OR content LIKE ?"
        keyword = f"%{search}%"
        params.extend([keyword, keyword])

    with get_db() as conn:
        total_posts = conn.execute(
            f"SELECT COUNT(*) FROM posts {where_sql}",
            params,
        ).fetchone()[0]

        total_pages = (total_posts + per_page - 1) // per_page
        if total_pages == 0:
            total_pages = 1

        if page > total_pages:
            page = total_pages

        offset = (page - 1) * per_page
        page_params = [*params, per_page, offset]
        posts = conn.execute(
            f"SELECT id, title, content, created_at FROM posts {where_sql} ORDER BY {sort_map[sort]} LIMIT ? OFFSET ?",
            page_params,
        ).fetchall()

    return render_template(
        "post_list.html",
        posts=posts,
        page=page,
        total_pages=total_pages,
        has_prev=page > 1,
        has_next=page < total_pages,
        prev_page=page - 1,
        next_page=page + 1,
        sort=sort,
        q=search,
    )


@app.get("/posts")
def list_posts_alias():
    return redirect(url_for("list_posts"))


@app.get("/posts/<int:post_id>")
def post_detail(post_id: int):
    post = get_post_or_404(post_id)
    return render_template("post_detail.html", post=post)


@app.get("/posts/new")
def new_post_form():
    return render_template(
        "post_form.html",
        post=None,
        form_title="글쓰기",
        submit_label="등록",
        form_action=url_for("create_post"),
    )


@app.post("/posts")
def create_post():
    title = request.form.get("title", "").strip()
    content = request.form.get("content", "").strip()
    if not title or not content:
        return render_template(
            "post_form.html",
            post={"title": title, "content": content},
            form_title="글쓰기",
            submit_label="등록",
            form_action=url_for("create_post"),
            error="제목과 내용을 모두 입력해 주세요.",
        ), 400

    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO posts (title, content) VALUES (?, ?)",
            (title, content),
        )
        new_id = cursor.lastrowid
    return redirect(url_for("post_detail", post_id=new_id))


@app.route("/posts/<int:post_id>/edit", methods=["GET", "POST"])
def edit_post(post_id: int):
    post = get_post_or_404(post_id)

    if request.method == "GET":
        return render_template(
            "post_form.html",
            post=post,
            form_title="글 수정",
            submit_label="수정",
            form_action=url_for("edit_post", post_id=post_id),
        )

    title = request.form.get("title", "").strip()
    content = request.form.get("content", "").strip()
    if not title or not content:
        draft = {"id": post_id, "title": title, "content": content}
        return render_template(
            "post_form.html",
            post=draft,
            form_title="글 수정",
            submit_label="수정",
            form_action=url_for("edit_post", post_id=post_id),
            error="제목과 내용을 모두 입력해 주세요.",
        ), 400

    with get_db() as conn:
        conn.execute(
            "UPDATE posts SET title = ?, content = ? WHERE id = ?",
            (title, content, post_id),
        )
    return redirect(url_for("post_detail", post_id=post_id))


@app.post("/posts/<int:post_id>/delete")
def delete_post(post_id: int):
    get_post_or_404(post_id)
    with get_db() as conn:
        conn.execute("DELETE FROM posts WHERE id = ?", (post_id,))
    return redirect(url_for("list_posts"))


init_db()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
