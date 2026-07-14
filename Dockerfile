FROM python:3.11-slim

# Unbuffered stdout so print() lines appear in docker logs immediately
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 7860

CMD ["python", "app/gradio_ui.py"]
