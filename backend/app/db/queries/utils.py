"""Shared query utilities."""


def escape_like(term: str) -> str:
    """Escape special LIKE/ILIKE pattern characters in search terms.

    Escapes %, _, and \\ so they are treated as literal characters
    in ILIKE queries. Must be used with ESCAPE '\\' clause in SQL.
    """
    return term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
