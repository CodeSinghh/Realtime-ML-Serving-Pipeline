# -------------------------------
# Stage 1: Builder (optional if you build assets)
# -------------------------------
FROM python:3.11-slim AS builder

# Metadata for traceability
LABEL maintainer="Dhiraj Singh <your.email@example.com>" \
      version="1.0.0" \
      purpose="Dynamic ML Model Lifecycle Manager container"

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --user -r requirements.txt

# -------------------------------
# Stage 2: Runtime
# -------------------------------
FROM python:3.11-slim AS runtime

# Create non-root user for security
RUN useradd -m appuser

WORKDIR /app

# Copy only required files (keep .dockerignore strict)
COPY --from=builder /root/.local /root/.local
COPY --chown=appuser:appuser . .

# Use non-root user
USER appuser

# Set environment variables (runtime contracts)
ENV PATH=/root/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    ENV=production

# Expose port if needed (e.g., for Flask)
EXPOSE 8080

# Set entrypoint
CMD ["python", "main.py"]