from __future__ import annotations

REFERENCES_APA = [
    "Braun, V., & Clarke, V. (2006). Using thematic analysis in psychology. Qualitative Research in Psychology, 3, 77–101.",
    "Nowell, L. S., Norris, J. M., White, D. E., & Moules, N. J. (2017). Thematic Analysis: Striving to Meet the Trustworthiness Criteria. International Journal of Qualitative Methods, 16, 1–13.",
    "Boyatzis, R. E. (1998). Transforming Qualitative Information: Thematic Analysis and Code Development. Sage.",
]


def markdown_table(rows: list[dict[str, object]]) -> str:
    if not rows:
        return "_No records._\n"
    columns = list(rows[0].keys())
    header = "| " + " | ".join(columns) + " |"
    divider = "| " + " | ".join("---" for _ in columns) + " |"
    body = []
    for row in rows:
        body.append("| " + " | ".join(str(row.get(column, "")).replace("\n", " ") for column in columns) + " |")
    return "\n".join([header, divider, *body]) + "\n"
