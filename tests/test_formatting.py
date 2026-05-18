from carl_weread.formatting import format_date, seconds_to_readable, weread_link


def test_seconds_to_readable_formats_hours_and_minutes():
    assert seconds_to_readable(7380) == "2 小时 3 分钟"
    assert seconds_to_readable(1800) == "30 分钟"


def test_format_date_converts_unix_timestamp_to_date():
    assert format_date(1779105600, tz="Asia/Shanghai") == "2026-05-18"


def test_weread_link_builds_book_and_chapter_deep_link():
    assert weread_link("abc123") == "weread://reading?bId=abc123"
    assert weread_link("abc123", chapter_uid="42") == "weread://reading?bId=abc123&chapterUid=42"
