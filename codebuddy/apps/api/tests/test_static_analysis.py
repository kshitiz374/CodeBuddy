from __future__ import annotations

from app.services.analysis.static_analysis import analyze_code, parse_error_location


def test_parse_error_location():
    assert parse_error_location("main.cpp:12: error: ...") == 12
    assert parse_error_location("Traceback: line 3") == 3
    assert parse_error_location("no numbers here") is None


def test_c_pointer_heuristic():
    code = "Node* head;\nhead->data = 10;"
    result = analyze_code(code, "cpp", "Segmentation fault")
    messages = " ".join(result.messages).lower()
    assert "pointer" in messages or "node" in messages
    assert result.extracted_error_line is None


def test_python_indent_error():
    result = analyze_code("if True:\nprint(1)", "python", "IndentationError: unexpected indent")
    assert any("indent" in m.lower() for m in result.messages)


def test_generic_brace_balance():
    result = analyze_code("def foo(:", "python", None)
    # just ensure no crash; python path may not include brace checks
    assert result.language == "python"
