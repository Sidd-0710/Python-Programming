"""
course_tools.py - small helpers shared by FastAPI lessons 03 onwards.

You do NOT need to understand this file to follow the course. Read it after
lesson 07 if you're curious - by then every line will make sense.

It gives every lesson three ways to run:

    python 03_first_api.py            the TOUR: sends requests to the lesson's
                                      API and prints each request and response,
                                      so you can see what the code does

    python 03_first_api.py --serve    starts a REAL server. Open
                                      http://127.0.0.1:8000/docs in a browser
                                      and click "Try it out" on any endpoint

    python 03_first_api.py --check    grades your EXERCISE answers, printing
                                      PASS or FAIL for each one
"""

import json
import sys
from http import HTTPStatus
from pathlib import Path

HERE = Path(__file__).resolve().parent

try:
    from fastapi.testclient import TestClient
except ModuleNotFoundError:
    print(f"""
  FastAPI isn't installed in the Python you're using right now:
      {sys.executable}

  Fix it by running these commands in the terminal:
      cd {HERE}
      source .venv/bin/activate
      pip install -r requirements.txt

  Then run the lesson again with:  python <lesson file name>
  (lesson 00 walks through this step by step)
""")
    sys.exit(1)


LINE = "-" * 70
MAX_BODY_LINES = 22
_check_results = []


def section(title):
    """Print a heading so the tour output is easy to follow."""
    print()
    print(LINE)
    print(f"  {title}")
    print(LINE)


def _print_json(label, content):
    text = json.dumps(content, indent=2, ensure_ascii=False, default=str)
    lines = text.splitlines()
    indent = " " * 6
    print(f"{indent}{label}{lines[0]}")
    padding = indent + " " * len(label)
    for line in lines[1:MAX_BODY_LINES]:
        print(f"{padding}{line}")
    if len(lines) > MAX_BODY_LINES:
        print(f"{padding}... ({len(lines) - MAX_BODY_LINES} more lines)")


def show(client, method, url, note=None, **kwargs):
    """Send ONE request to the app, print both sides, and return the response.

    Extra keyword arguments go straight to the test client, for example:
        show(client, "POST", "/users", json={"name": "Sidd"})
        show(client, "GET", "/me", headers={"Authorization": "Bearer ..."})
    """
    print()
    if note:
        print(f"  # {note}")
    print(f"  --> {method.upper()} {url}")

    for name, value in (kwargs.get("headers") or {}).items():
        if name.lower() == "authorization" and len(value) > 40:
            value = value[:36] + "..."
        print(f"      {name}: {value}")
    if "json" in kwargs:
        _print_json("body: ", kwargs["json"])
    if "data" in kwargs:
        _print_json("form: ", kwargs["data"])

    response = client.request(method.upper(), url, **kwargs)

    try:
        phrase = HTTPStatus(response.status_code).phrase
    except ValueError:
        phrase = ""
    print(f"  <-- {response.status_code} {phrase}")

    for name in ("location", "x-process-time", "x-request-id", "www-authenticate"):
        if name in response.headers:
            print(f"      {name}: {response.headers[name]}")

    if response.content:
        try:
            _print_json("", response.json())
        except ValueError:
            print(f"      {response.text[:300]}")
    return response


def check(description, condition):
    """Record one PASS/FAIL line. Used by each lesson's exercise checks."""
    passed = bool(condition)
    _check_results.append(passed)
    print(f"  [{'PASS' if passed else 'FAIL'}] {description}")
    return passed


def start(app, tour, checks=None, port=8000, raise_server_exceptions=True):
    """Run the tour, start a real server (--serve), or grade exercises (--check)."""
    script = Path(sys.argv[0]).name

    if "--serve" in sys.argv:
        import uvicorn
        print(LINE)
        print("  SERVER RUNNING. Open one of these in your browser:")
        print(f"      http://127.0.0.1:{port}/docs    interactive docs - click 'Try it out'")
        print(f"      http://127.0.0.1:{port}/redoc   a read-only docs view")
        print("  Every request you make appears as a line below.")
        print("  Press Ctrl+C in this terminal to stop the server.")
        print(LINE)
        uvicorn.run(app, host="127.0.0.1", port=port)
        return

    if "--check" in sys.argv:
        section("EXERCISE CHECKS")
        if checks is None:
            print("  This lesson has no automatic checks.")
            return
        with TestClient(app, raise_server_exceptions=False) as client:
            try:
                checks(client)
            except Exception as error:
                _check_results.append(False)
                print(f"  [FAIL] a check crashed: {type(error).__name__}: {error}")
                print("         Usually an exercise endpoint is missing, or returns")
                print("         a different shape from what the exercise asks for.")
        passed, total = sum(_check_results), len(_check_results)
        print()
        if total and passed == total:
            print(f"  ALL {total} CHECKS PASSED. Compare your code with the SOLUTIONS")
            print("  section at the bottom of the lesson - there's often more than")
            print("  one good answer.")
        else:
            print(f"  {passed}/{total} passed. Fix the next FAIL, save, and run:")
            print(f"      python {script} --check")
        return

    with TestClient(app, raise_server_exceptions=raise_server_exceptions) as client:
        tour(client)

    print()
    print("=" * 70)
    print("  Tour finished. Next steps:")
    print(f"    python {script} --serve    explore it yourself at /docs")
    print(f"    python {script} --check    grade your exercise answers")
    print("=" * 70)
