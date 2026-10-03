from __future__ import annotations

import re
from typing import Any

from app.services.ai.base import (
    AIProvider,
    AnalysisContext,
    AnalysisResult,
    ConceptContext,
    ConceptResult,
)


class MockAIProvider(AIProvider):
    """Deterministic mentor-shaped responses for tests, demos, and machines without Ollama."""

    name = "mock"
    is_local = True
    model_name = "mock-mentor"

    async def analyze_code(self, request: AnalysisContext) -> AnalysisResult:
        findings = request.deterministic_findings or []
        code = request.code
        language = request.language
        error = (request.error_message or "").strip()
        profile = request.profile or {}
        level = str(profile.get("level", "beginner")).lower()

        pointer_bug = bool(
            re.search(r"\b(Node|node)\s*\*\s*\w+\s*;", code)
            and re.search(r"\w+\s*->\s*\w+", code)
            and "new " not in code
            and "malloc" not in code
        )
        uninitialized = bool(
            pointer_bug
            or re.search(r"\bint\s+\w+\s*;", code)
            and "->" in code
        )
        python_indent = "IndentationError" in error or "unexpected indent" in error.lower()
        nullish = "NullReference" in error or "null pointer" in error.lower() or "NoneType" in error

        if pointer_bug or (language in {"cpp", "c"} and "->" in code and "new " not in code):
            problem = "A pointer is used before it points to a valid object."
            location = "pointer dereference (->)"
            explanation = (
                "In this code a pointer variable is declared, then used with -> without "
                "allocating/creating the object it should point to. That is undefined behavior "
                "in C/C++ and a classic beginner crash."
            )
            hint = (
                "Before head->data (or similar), ask: "
                "'What object does this pointer actually point to right now?'"
            )
            concept = "Pointers and dynamic memory allocation in C/C++"
            fix = (
                "Create the node before dereferencing:\n"
                "Node* head = new Node();\n"
                "head->data = 10;\n"
                "Also ensure Node has a data member and free/delete later when learning RAII/ownership."
            )
            lesson = (
                "A pointer stores an address. It does not automatically create the object. "
                "Allocate or initialize the pointer before you read or write through it."
            )
            severity = "error"
        elif python_indent:
            problem = "Python indentation is inconsistent around a statement block."
            location = "Python block indentation"
            explanation = (
                "Python uses indentation as syntax. If a block jumps between spaces and tabs, "
                "or a nested line is indented incorrectly, the interpreter raises IndentationError."
            )
            hint = "Look at the line right before this one and match the indentation level exactly."
            concept = "Python blocks and indentation rules"
            fix = "Use the same number of spaces (usually 4) for every block level. Avoid mixing tabs and spaces."
            lesson = "In Python, indentation is not style — it is part of the language grammar."
            severity = "error"
        elif nullish:
            problem = "Code tried to use a value that is null/None at runtime."
            location = "null/None usage"
            explanation = (
                "Something that can be null/None was dereferenced or called without a check. "
                "The program needs a guard, or the value needs to be created before use."
            )
            hint = "Add a debug print of the value right before the failing line and confirm what it is."
            concept = "Null/None safety and defensive checks"
            fix = "Guard the access (if value is None) or ensure the object is constructed first."
            lesson = "Treat nullable references as real inputs: validate before use."
            severity = "error"
        elif "NameError" in error or "undefined" in error.lower():
            problem = "Code references a name that does not exist in the current scope."
            location = "identifier / scope"
            explanation = (
                "A variable, function, or class name was used but not defined (or spelled differently "
                "than its definition)."
            )
            hint = "Compare the name at the error with the exact spelling where it was defined."
            concept = "Scope and naming in programming"
            fix = "Define the name before use, or fix the spelling/import."
            lesson = "Read errors top-down: the first NameError/undefined symbol is usually the real problem."
            severity = "error"
        elif findings:
            problem = findings[0]
            location = "see static analysis"
            explanation = "Static analysis found a likely issue in the submitted code."
            hint = "Start with the first static-analysis finding and check that code path carefully."
            concept = "Reading compiler/static-analysis feedback"
            fix = "Address the highest-confidence finding first, then re-check the rest."
            lesson = "Deterministic feedback is data, not a full explanation — combine it with careful reading."
            severity = "warning"
        else:
            problem = "The code path needs closer inspection; the provided details are not enough to pinpoint one root cause."
            location = "unspecified"
            explanation = (
                "Without a clear error message, expected vs actual behavior, or a suspicious pattern, "
                "CodeBuddy cannot honestly claim a single root cause."
            )
            hint = "Paste the exact error text and the smallest failing example you can build."
            concept = "Debugging with minimal reproducible examples"
            fix = "Shrink the code until it still fails, then read the first error line carefully."
            lesson = "Good debugging starts with precise symptoms, not guessing at solutions."
            severity = "concept"

        prior_note = ""
        if request.prior_mistakes:
            prior_note = (
                " You encountered a similar issue earlier in Mistake Memory; review that lesson "
                "after you try this hint yourself."
            )
        explanation = explanation + prior_note

        if level in {"advanced"}:
            hint = hint + " If you are stuck after one attempt, add a comment that states the invariant you think should hold."

        return AnalysisResult(
            problem=problem,
            severity=severity,
            location=location,
            explanation=explanation,
            hint=hint,
            concept=concept,
            fix=fix,
            lesson=lesson,
            raw={"provider": self.name, "findings": findings},
        )

    async def explain_concept(self, request: ConceptContext) -> ConceptResult:
        query = request.query.strip()
        low = query.lower()
        language = request.language or ""
        profile = request.profile or {}

        if "recursion" in low:
            concept = "Recursion"
            simple = (
                "A function that solves a problem by calling itself on a smaller version of the same problem, "
                "until it reaches a base case."
            )
            analogy = (
                "Imagine you are standing between two mirrors. Each reflection is a smaller 'you' until "
                "the scene gets too small to continue — that stopping point is the base case."
            )
            example = (
                "def factorial(n):\n"
                "    if n <= 1:\n"
                "        return 1          # base case\n"
                "    return n * factorial(n - 1)  # recursive case\n\n"
                "print(factorial(3))"
            )
            steps = (
                "factorial(3)\n"
                "  → 3 * factorial(2)\n"
                "    → 2 * factorial(1)\n"
                "      → returns 1\n"
                "    → returns 2\n"
                "  → returns 6"
            )
            mistake = "Forgetting the base case, or making the recursive step not get smaller → infinite recursion / stack overflow."
            mini = "What happens when n = 0 or n = 1? Run the function in your head before the compiler does."
        elif "pointer" in low or "linked list" in low or "linked-list" in low:
            concept = "Pointers and linked lists" if "linked" in low else "Pointers"
            simple = (
                "A pointer stores the address of another value. In a linked list, each node stores data "
                "and a pointer to the next node."
            )
            analogy = (
                "A node is a box with two compartments: a treasure (data) and a note saying which box to open next."
            )
            example = (
                "struct Node {\n"
                "    int data;\n"
                "    Node* next;\n"
                "};\n\n"
                "Node* head = new Node();\n"
                "head->data = 10;\n"
                "head->next = nullptr;"
            )
            steps = (
                "1. Allocate memory for the node.\n"
                "2. Write data into it.\n"
                "3. Set next to nullptr (or another node address)."
            )
            mistake = "Using head->data before head points to an allocated Node."
            mini = "If you only write Node* head; what address does head contain? Is it safe to use?"
        else:
            concept = query[:80]
            simple = (
                f"'{query}' is best learned by connecting a small definition, a concrete example, "
                "and one mistake you can avoid."
            )
            analogy = (
                "Think of the concept like a tool in a toolbox: you need to know what job it does, "
                "when to pick it up, and what happens if you use it the wrong way."
            )
            example = (
                f"# Minimal example for: {query}\n"
                "def demo():\n"
                "    return 'change one thing at a time'\n\n"
                "print(demo())"
            )
            steps = (
                "1. State the idea in one sentence.\n"
                "2. Show the smallest working example.\n"
                "3. Change one input and predict the output before running it."
            )
            mistake = "Copying an example without changing one variable and predicting the result."
            mini = "What single change would make this example break? Try to predict it first."
            if language:
                simple += f" Prefer examples in {language} while you learn."

        style = str(profile.get("preferred_explanation", "simple")).lower()
        if style == "detailed":
            simple = simple + " Focus on definitions first, then mechanics."
        elif style == "analogy-first":
            simple = analogy + " " + simple

        return ConceptResult(
            concept=concept,
            simple_explanation=simple,
            analogy=analogy,
            example_code=example,
            step_by_step=steps,
            common_mistake=mistake,
            mini_question=mini,
            raw={"provider": self.name},
        )

    async def status(self) -> dict[str, Any]:
        return {
            "provider": self.name,
            "model_name": self.model_name,
            "is_local": True,
            "available": True,
            "detail": "Mock provider (no external model required). Set AI_PROVIDER=ollama for local open-weight models.",
        }
