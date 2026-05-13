FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY pyproject.toml README.md ./
COPY app ./app
RUN pip install --no-cache-dir -e .[test]
COPY data ./data
COPY tests ./tests
COPY docs ./docs
CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8000"]
