import json
import subprocess
import sys
from pathlib import Path

from carl_weread.candidates import (
    BookRef,
    build_candidate_chapters,
    chapters_from_chapterinfo,
    extract_book_refs,
)


ROOT = Path(__file__).resolve().parents[1]


def test_extract_book_refs_handles_wrapped_shelf_and_notebooks_shapes():
    payload = {
        "data": {
            "books": [
                {"bookId": "b1", "title": "AI Harness Engineering"},
                {"book": {"bookId": "b2", "title": "写作是门手艺"}},
                {"bookId": "", "title": "缺失 ID 的书"},
            ]
        }
    }

    refs = extract_book_refs(payload)

    assert refs == [
        BookRef(book_id="b1", title="AI Harness Engineering"),
        BookRef(book_id="b2", title="写作是门手艺"),
    ]


def test_chapters_from_chapterinfo_normalizes_common_chapter_fields():
    payload = {
        "data": {
            "chapters": [
                {"chapterUid": "c1", "title": "开场：为什么要从问题开始读"},
                {"uid": "c2", "chapterName": "Agent Skill 交付验证"},
                {"chapterUid": "", "title": "缺失 uid 的章节"},
            ]
        }
    }

    chapters = chapters_from_chapterinfo("b1", "AI Harness Engineering", payload)

    assert [chapter.chapter_uid for chapter in chapters] == ["c1", "c2"]
    assert chapters[1].book_id == "b1"
    assert chapters[1].book_title == "AI Harness Engineering"
    assert chapters[1].title == "Agent Skill 交付验证"


def test_build_candidate_chapters_merges_books_and_deduplicates_by_book_order():
    shelf = {"data": {"books": [{"bookId": "b1", "title": "AI Harness Engineering"}]}}
    notebooks = {
        "data": {
            "books": [
                {"bookId": "b1", "title": "AI Harness Engineering"},
                {"bookId": "b2", "title": "写作是门手艺"},
            ]
        }
    }
    chapterinfo_by_book_id = {
        "b1": {"data": {"chapters": [{"chapterUid": "c1", "title": "Agent Skill 交付验证"}]}},
        "b2": {"data": {"chapters": [{"chapterUid": "c2", "title": "从真实问题开始写"}]}},
    }

    chapters = build_candidate_chapters(shelf, notebooks, chapterinfo_by_book_id)

    assert [(chapter.book_id, chapter.chapter_uid) for chapter in chapters] == [("b1", "c1"), ("b2", "c2")]


def test_build_candidates_script_writes_today_compatible_json(tmp_path):
    shelf_path = tmp_path / "shelf.json"
    notebooks_path = tmp_path / "notebooks.json"
    chapter_dir = tmp_path / "chapters"
    output_path = tmp_path / "candidates.json"
    chapter_dir.mkdir()

    shelf_path.write_text(json.dumps({"data": {"books": [{"bookId": "b1", "title": "AI Harness Engineering"}]}}), encoding="utf-8")
    notebooks_path.write_text(json.dumps({"data": {"books": []}}), encoding="utf-8")
    (chapter_dir / "b1.json").write_text(
        json.dumps({"data": {"chapters": [{"chapterUid": "c1", "title": "Agent Skill 交付验证"}]}}),
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "build_candidates.py"),
            "--shelf",
            str(shelf_path),
            "--notebooks",
            str(notebooks_path),
            "--chapter-dir",
            str(chapter_dir),
            "--output",
            str(output_path),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0
    assert "已写入候选章节" in result.stdout
    data = json.loads(output_path.read_text(encoding="utf-8"))
    assert data == [
        {
            "book_id": "b1",
            "book_title": "AI Harness Engineering",
            "chapter_uid": "c1",
            "title": "Agent Skill 交付验证",
        }
    ]
