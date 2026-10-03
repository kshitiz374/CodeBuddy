from __future__ import annotations

import re
from dataclasses import dataclass, field

LANGUAGE_FAMILIES = {
    "cpp": "c_family",
    "c": "c_family",
    "java": "jvm",
    "python": "python",
    "javascript": "script",
    "typescript": "script",
    "go": "go",
    "rust": "rust",
}

ERROR_LINE_PATTERNS = [
    re.compile(r"(?P<file>[^\s:]+\.(?:cpp|cc|cxx|c|h|hpp|py|java|js|ts)):(?P<line>\d+)"),
    re.compile(r"line\s+(?P<line>\d+)", re.I),
    re.compile(r"at line (?P<line>\d+)", re.I),
]


@dataclass
class StaticFinding:
    severity: str
    message: str
    line: int | None = None


@dataclass
class StaticAnalysisResult:
    language: str
    findings: list[StaticFinding] = field(default_factory=list)
    extracted_error_line: int | None = None

    @property
    def messages(self) -> list[str]:
        return [f.message for f in self.findings]


def parse_error_location(error_message: str | None) -> int | None:
    if not error_message:
        return None
    for pattern in ERROR_LINE_PATTERNS:
        match = pattern.search(error_message)
        if match:
            try:
                return int(match.group("line"))
            except (TypeError, ValueError):
                return None
    return None


def analyze_code(code: str, language: str, error_message: str | None = None) -> StaticAnalysisResult:
    lang = (language or "").lower()
    family = LANGUAGE_FAMILIES.get(lang, lang)
    findings: list[StaticFinding] = []
    line = parse_error_location(error_message)

    if family == "c_family":
        findings.extend(_c_family_heuristics(code, line))
    elif family == "python":
        findings.extend(_python_heuristics(code, error_message, line))
    elif family == "jvm":
        findings.extend(_java_heuristics(code))
    else:
        findings.extend(_generic_heuristics(code))

    if error_message and line is None:
        findings.append(
            StaticFinding(
                severity="info",
                message="An error message was provided, but no line number could be parsed from it.",
            )
        )
    if not code.strip():
        findings.append(StaticFinding(severity="error", message="Code input is empty."))

    return StaticAnalysisResult(language=lang, findings=findings, extracted_error_line=line)


def _c_family_heuristics(code: str, line: int | None) -> list[StaticFinding]:
    findings: list[StaticFinding] = []
    lines = code.splitlines()

    # Pointer declared then used with -> without new/malloc/alloca nearby.
    pointer_decl = re.compile(r"\b(?:struct\s+)?\w+\s*\*\s*(\w+)\s*;")
    uses_arrow = re.compile(r"\b(\w+)\s*->")

    allocated_vars: set[str] = set()
    for match in re.finditer(r"\b(\w+)\s*=\s*(?:new\b|malloc\s*\(|calloc\s*\(|realloc\s*\()", code):
        allocated_vars.add(match.group(1))

    declared_pointers: dict[str, int] = {}
    for idx, raw in enumerate(lines, start=1):
        for match in pointer_decl.finditer(raw):
            name = match.group(1)
            if name in {"return", "if", "while", "for"}:
                continue
            declared_pointers[name] = idx
        if any(var in allocated_vars for var in declared_pointers):
            continue

    for idx, raw in enumerate(lines, start=1):
        for match in uses_arrow.finditer(raw):
            var = match.group(1)
            if var in allocated_vars:
                continue
            if var in declared_pointers:
                decl_line = declared_pointers[var]
                # If allocation appears between decl and use, skip.
                window = "\n".join(lines[decl_line - 1 : idx])
                if re.search(rf"\b{re.escape(var)}\s*=\s*(?:new\b|malloc\s*\()", window):
                    continue
                findings.append(
                    StaticFinding(
                        severity="error",
                        message=(
                            f"Pointer '{var}' is used with '->' but appears to be used before "
                            "allocation/initialization (static heuristic)."
                        ),
                        line=idx,
                    )
                )
            else:
                # Unknown identifier used with -> — possible undeclared pointer.
                if not re.search(rf"\b{re.escape(var)}\s*\*", code):
                    findings.append(
                        StaticFinding(
                            severity="warning",
                            message=(
                                f"'{var}' is used with '->' but no pointer declaration for it was found "
                                "(static heuristic)."
                            ),
                            line=idx,
                        )
                    )

    if re.search(r"\bNode\s*\*\s*\w+\s*;", code) and re.search(r"->", code) and "new " not in code:
        findings.append(
            StaticFinding(
                severity="error",
                message="Classic beginner pattern: Node* declared, then dereferenced without new/malloc.",
            )
        )

    if "printf" not in code and "std::" not in code and "cout" not in code and "scanf" not in code:
        # not necessarily an error — only a soft note when also no main-like usage
        if "int main" not in code and "void main" not in code:
            findings.append(
                StaticFinding(
                    severity="info",
                    message="No main() or I/O detected — this may be a fragment, which is fine for snippets.",
                )
            )
    return findings


def _python_heuristics(code: str, error_message: str | None, line: int | None) -> list[StaticFinding]:
    findings: list[StaticFinding] = []
    if error_message and "IndentationError" in error_message:
        findings.append(
            StaticFinding(
                severity="error",
                message="Python reported an IndentationError — indentation is syntactic in Python.",
                line=line,
            )
        )
    if "\t" in code and "    " in code:
        findings.append(
            StaticFinding(
                severity="warning",
                message="Code mixes tabs and spaces. Python 3 rejects mixed indentation.",
            )
        )
    if re.search(r"\bprint\s+[^(]", code) and "print(" not in code:
        findings.append(
            StaticFinding(
                severity="warning",
                message="Found 'print x' style usage. Python 3 requires print(x).",
            )
        )
    if re.search(r"\bNoneType\b", error_message or ""):
        findings.append(
            StaticFinding(
                severity="error",
                message="NoneType error suggests a None value was used as an object.",
                line=line,
            )
        )
    if re.search(r"\bNameError\b", error_message or ""):
        findings.append(
            StaticFinding(
                severity="error",
                message="NameError: a variable/function name was used before definition or spelled wrong.",
                line=line,
            )
        )
    if re.search(r"\bIndexError\b", error_message or ""):
        findings.append(
            StaticFinding(
                severity="error",
                message="IndexError: index is out of range for a sequence.",
                line=line,
            )
        )
    return findings


def _java_heuristics(code: str) -> list[StaticFinding]:
    findings: list[StaticFinding] = []
    if re.search(r"System\.out\.print\s+[^(]", code):
        findings.append(
            StaticFinding(
                severity="warning",
                message="System.out.print looks malformed; Java requires parentheses: System.out.println(...).",
            )
        )
    if re.search(r"\bpublic\s+static\s+void\s+main\s*\(\s*String\s+\w+\s*\)", code) is None and "class " in code:
        # fragment is OK — soft note only
        findings.append(
            StaticFinding(
                severity="info",
                message="No standard main(String[]) entry point found. Snippet analysis continues without it.",
            )
        )
    if re.search(r"\bnull\s*;", code) and "->" in code:
        findings.append(
            StaticFinding(
                severity="warning",
                message="Possible null usage pattern detected (heuristic only).",
            )
        )
    return findings


def _generic_heuristics(code: str) -> list[StaticFinding]:
    findings: list[StaticFinding] = []
    if code.count("{") != code.count("}"):
        findings.append(
            StaticFinding(
                severity="warning",
                message="Braces are unbalanced in the submitted code.",
            )
        )
    if code.count("(") != code.count(")"):
        findings.append(
            StaticFinding(
                severity="warning",
                message="Parentheses are unbalanced in the submitted code.",
            )
        )
    return findings
