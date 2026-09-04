# HIVE – Copilot Instructions

You are assisting with HIVE (Holistic Injury Visualization Environment), a Python + web frontend for LS‑DYNA post‑processing of FE simulations in the field of crashworhtiness of vehicle structures and biomechanics.

## Tech stack

- Backend: Python 3.8+, pandas, numpy, matplotlib, seaborn, typing, dataclasses, pathlib, visualizer (by jkneifl on github), ls-reader
- LS‑DYNA I/O: Dynasaur (binary binout reader), lsreader and visualizer (d3plot file extraction and visualization).
- Frontend: HTML/CSS/JS (or your chosen stack, e.g. Streamlit/Plotly/Dash/FastAPI + simple frontend).
- Tooling: VSCode, Git, pytest, black, ruff/flake8, mypy (optional).

## Architecture principles

- Modular case modules (e.g. whiplash, airbag, energy_balance) built on a generic `core`.
- Each case module defines:
  - metadata,
  - available plots,
  - injury criteria,
  - visualization logic.
- Backend produces publication‑quality plots (Matplotlib/Seaborn) with SVG export.
- Frontend is an interactive dashboard for multi‑case comparison and exploration, as well as animation of simulation.

## Coding style

- Prefer clear, typed Python with dataclasses for data containers.
- Use `pathlib.Path` for paths.
- Keep functions small and testable; avoid side effects in core utilities.
- Use docstrings (Google or NumPy style) for public functions/classes.
- Follow PEP 8; format with `black`; lint with `ruff`/`flake8`.
- Use type hints consistently; aim for mypy‑clean core.

## When suggesting code

- Respect the existing HIVE structure (core/, whiplash/, airbag/, frontend/, etc.).
- When adding a new case module, follow the pattern in existing modules.
- Prefer Matplotlib/Seaborn for plots intended for papers; keep styling consistent.
- When touching LS‑DYNA I/O, assume data comes via Dynasaur; do not reinvent binout parsing.
- Suggest tests (pytest) for new computations and plot generators.
- Keep suggestions concise and directly usable; avoid over‑engineering.

## Typical tasks

- Implement new injury criteria in a case module.
- Add new plot types and metadata fields.
- Refactor core classes (SimulationData, PlotStyle, etc.) for clarity and extensibility.
- Write CSS/layout for the frontend dashboard.
- Write/export SVG figures suitable for papers.