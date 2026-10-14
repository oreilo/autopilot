FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir . && python -m playwright install --with-deps chromium
RUN useradd --create-home runner && chown -R runner:runner /app
USER runner
EXPOSE 8000
CMD ["uvicorn", "oreilo_autopilot.api:app", "--host", "0.0.0.0", "--port", "8000"]
