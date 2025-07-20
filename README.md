## AI Interview API

A FastAPI-based backend service that leverages Google Gemini to generate interview questions, evaluate candidate answers, and suggest follow-up questions.

### Features

* **Question Generation**: Generate a series of interview questions based on a user-provided topic or role.
* **Answer Evaluation**: Evaluate candidate responses and provide feedback.
* **Follow-Up Questions**: Suggest the next best question based on previous answers.
* **Health Check**: Simple `/healthz` endpoint for service monitoring.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Running the API](#running-the-api)
5. [Running Tests](#running-tests)
6. [Docker Setup](#docker-setup)
7. [Folder Structure](#folder-structure)
8. [Environment Variables](#environment-variables)
9. [Contributing](#contributing)
10. [License](#license)

---

## Getting Started

These instructions will help you set up and run the AI Interview API locally.

## Prerequisites

* Python 3.11+
* pip
* Docker (for containerized setup)
* [Google Gemini API key](https://developers.google.com/)

## Installation

1. Clone the repository:

   ```bash
   git clone <https://github.com/Saubhik998/ml-interview-analyzer>
   ```
2. Create & activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # macOS/Linux
   venv\\Scripts\\activate  # Windows
   ```
3. Install dependencies:

   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

## Running the API

1. Copy the example `.env` and set your Gemini API key:

   ```bash
   cp .env.example .env
   # then edit .env
   ```
2. Start the FastAPI server:

   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
3. Access the documentation at `http://localhost:8000/docs`.

## Running Tests

Execute the test suite with pytest:

```bash
pytest
```

## Docker Setup

1. Build the Docker image:

   ```bash
   docker build -t ai-interview-api .
   ```
2. Run with Docker Compose:

   ```bash
   docker-compose up --build
   ```

   * The API will be available at `http://localhost:9000`.

## Folder Structure

```text
ai_interview_api/
├── app/
│   ├── **main.py**           # Entry point with FastAPI initialization
│   ├── **config.py**         # Environment and configuration loader
│   ├── routers/              # API route definitions
│   │   ├── generate.py       # /api/generate-question endpoint
│   │   ├── evaluate.py       # /api/evaluate-answer endpoint
│   │   └── next_question.py  # /api/next-question endpoint
│   ├── services/             # Business logic implementations
│   │   ├── question_generator.py
│   │   ├── evaluation_service.py
│   │   └── next_question_service.py
│   └── schemas/              # Request/response Pydantic models
├── tests/                    # Test suite (pytest)
│   ├── test_question_generator.py
│   ├── test_evaluation_service.py
│   └── test_next_question_service.py
├── Dockerfile                # Container image definition
├── docker-compose.yml        # Multi-service Docker config
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables
├── .dockerignore             # Files ignored by Docker
├── .github/                  # CI/CD workflows
├── .git/                     # Git repository data
└── venv/                     # Virtual environment (optional)
```

## Environment Variables

| Variable         | Description                |
| ---------------- | -------------------------- |
| `GEMINI_API_KEY` | Your Google Gemini API key |

## Contributing

Contributions are welcome! Please open issues and submit pull requests.


