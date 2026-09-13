# Python: Zero to AI Engineering

A hands-on course in executable Python files. Every file is a lesson you read,
run, break, and do exercises in. Nothing is theoretical — it all runs.

Built for someone starting from `print("hello")` and heading toward building
web backends, analysing data, automating work, and engineering AI systems.

---

## How to use this

**One file per session.** Each takes 45–95 minutes. At ~12 hours a week that's
about 8 weeks for the whole course.

For every file:

1. **Read** it top to bottom, like a textbook chapter. The long comment blocks
   are the teaching, not filler.
2. **Run** it — `python3 01_variables_and_data_types.py`, or the ▷ button in
   VS Code. Match each piece of output to the code that produced it.
3. **Break** it. Change a number, delete a quote, misspell a name. Read the
   error. This is the step people skip and it's the most valuable one.
4. **Do the exercises** at the bottom. Write the code yourself.
5. **Then** check the SOLUTIONS section at the very end of each file.

Don't comment out code after you finish a file. Leave it runnable so you can
come back and tinker.

---

## The files, in order

### Foundations — the language itself

| # | File | You'll learn |
|---|------|--------------|
| 00 | `00_START_HERE.py` | What a program is, how to run one, how to read an error message without panicking |
| 01 | `01_variables_and_data_types.py` | Variables, `int`/`float`/`str`/`bool`/`None`, type conversion, f-strings |
| 02 | `02_strings_and_text.py` | Slicing, string methods, `split`/`join`, formatting numbers into tables |
| 03 | `03_numbers_and_math.py` | Operators, `//` and `%` in real use, precedence, `math`, `random`, float precision |
| 04 | `04_input_and_conversion.py` | `input()`, validation loops, `sys.argv` — and why all input is untrusted text |
| 05 | `05_conditionals_and_logic.py` | `if`/`elif`/`else`, boolean logic, truthiness, guard clauses, `match` |

### Data structures — how to hold information

| # | File | You'll learn |
|---|------|--------------|
| 06 | `06_lists.py` | Lists, indexing, sorting, the copy trap, list-of-lists as a table |
| 07 | `07_loops.py` | `for`/`while`, `range`, `enumerate`, `zip`, accumulator patterns, `break`/`continue` |
| 08 | `08_tuples_and_sets.py` | Tuples as records, sets for uniqueness and fast lookup, set maths |
| 09 | `09_dictionaries.py` | **The most important lesson.** Key-value data, counting, grouping, nested JSON-shaped data |

### Writing real code

| # | File | You'll learn |
|---|------|--------------|
| 10 | `10_functions.py` | `def`, arguments, `return` vs `print`, scope, the mutable-default trap, `lambda` |
| 11 | `11_comprehensions.py` | List/dict/set comprehensions, generators — and when *not* to use them |
| 12 | `12_error_handling.py` | `try`/`except`, raising your own, custom exception types, anti-patterns |

### Files and data — the automation toolkit

| # | File | You'll learn |
|---|------|--------------|
| 13 | `13_files_and_folders.py` | `pathlib`, reading/writing, globbing, bulk renaming, a real log analyser |
| 14 | `14_json_and_csv.py` | The two formats that run the world; type conversion at the boundary |
| 15 | `15_modules_and_packages.py` | `import`, writing your own modules, `__main__`, venvs, project layout |

### Objects and the standard library

| # | File | You'll learn |
|---|------|--------------|
| 16 | `16_classes_and_objects.py` | Classes, `self`, properties, dunder methods — and when a dict is better |
| 17 | `17_inheritance.py` | Inheritance, polymorphism, abstract base classes, composition over inheritance |
| 18 | `18_standard_library.py` | `datetime`, `collections`, `re`, `itertools`, `statistics`, `decimal`, `secrets`, `argparse` |

### Applied work

| # | File | You'll learn |
|---|------|--------------|
| 19 | `19_data_analysis.py` | Load → clean → explore → aggregate → present, plus text charts. Maps directly onto pandas |
| 20 | `20_automation_project.py` | **Project:** a real CLI tool — dry runs, logging, config, exit codes, duplicate detection |

### AI engineering

| # | File | You'll learn |
|---|------|--------------|
| 21 | `21_http_and_apis.py` | HTTP, status codes, retries with backoff, rate limits, API keys from the environment |
| 22 | `22_claude_api.py` | The Messages API, models and pricing, streaming, token counting, prompt caching, errors |
| 23 | `23_ai_engineering_patterns.py` | Structured outputs, tool use, RAG, **evals**, prompt injection, cost discipline |
| 24 | `24_ai_backend_and_capstone.py` | Serving an AI feature over HTTP, FastAPI, capstone projects, roadmap |

### Supporting files

- `toolkit/` — an example package used by lesson 15 (`text_tools.py`, `money.py`)
- `data/` — sample data: `sales.csv`, `server.log`, `config.json`
- `workspace/` — scratch folder that lessons write into. Safe to delete.

---

## Setup

Lessons 00–20 need **nothing but Python 3**. Check you have it:

```bash
python3 --version        # 3.10 or newer
```

Lessons 22–24 optionally use the Anthropic SDK. **They run fine without it** —
they print every example and explain it, and only make live calls if both the
SDK and a key are present.

To go live:

```bash
cd python_course
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install anthropic
export ANTHROPIC_API_KEY="sk-ant-..."
```

Never put an API key in your source code. Lesson 21 part 5 explains why.

---

## The four goals, and where they're covered

**Understand coding fundamentals** — lessons 00–12. The whole foundation.

**Automate repetitive tasks** — lessons 13, 14, 18, and the project in 20.
After lesson 13 you can rename 3,000 files while you drink coffee.

**Analyse and visualise data** — lessons 06, 09, 14, 19. Lesson 19 does it the
long way on purpose, then shows the pandas translation so you understand what
the shortcuts are shortcutting.

**Build web apps and backends** — lessons 16, 17, 21, 24. Plus lesson 09, since
JSON is just nested dictionaries.

**AI engineering** — lessons 21–24, resting on everything before them. An LLM
call is an HTTP POST with JSON (21), the model is one component in a system you
have to make reliable (23), and it's only a product once it's served (24).

---

## If you get stuck

- **Read the error from the bottom up.** The last line says *what*, the `line N`
  says *where*. Lesson 00 part 4 covers this properly.
- **Print things.** When confused about what your code is holding, print it and
  its `type()`. This solves most problems.
- **Make it smaller.** Cut the code down to the smallest version that still
  shows the problem. Usually you find the bug while doing this.
- **Check the COMMON MISTAKES section** near the end of each lesson — it lists
  the specific things that go wrong with that topic.

Everyone gets stuck constantly. It's the job, not a sign you're bad at it.
