# LLM Intent Assistant

This project is a modular, testable and scalable assistant for detecting user intents and entities using large language models (LLMs). It's structured using a Maven-style layout adapted for Python.

## Structure

- `src/app/`: Core application logic
- `src/tests/`: Unit tests and test data
- `requirements.txt`: Python dependencies
- `pyproject.toml`: Optional build configuration

## How to Run

```bash
cd src/app
python main.py
```

## How to Test

```bash
cd src
python -m unittest discover -s tests -v
```
