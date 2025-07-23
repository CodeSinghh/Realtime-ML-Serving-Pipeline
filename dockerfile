# Stage 1: Builder
FROM python:3.11-slim AS builder

LABEL maintainer="Dhiraj Singh <dhiraj.kr.singh.real@gmail.com>" \
      version="1.1.0" \
      purpose="Dynamic ML Model Lifecycle Manager containerr"

WORKDIR /app

COPY requirements.txt .

# 🧼 Clean install — only this line changed
RUN pip install --upgrade pip && \
    pip install --prefix=/install -r requirements.txt && \
    rm -rf /install/share /install/lib/python*/site-packages/__pycache__ \
           /install/lib/python*/site-packages/*.dist-info \
           /root/.cache/pip

# Stage 2: Runtime
FROM python:3.11-slim AS runtime

LABEL maintainer="Dhiraj Singh <dhiraj.kr.singh.real@gmail.com>" \
      version="1.1.0" \
      purpose="Dynamic ML Model Lifecycle Manager container"

RUN useradd -m appuser

WORKDIR /app

COPY --from=builder /install /usr/local
COPY --chown=appuser:appuser . .

USER appuser

ENV PATH=/usr/local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    ENV=production

EXPOSE 8080

CMD ["python", "main.py"]