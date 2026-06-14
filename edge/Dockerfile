FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Using -u to prevent Python from buffering stdout
CMD ["python", "-u", "main.py", "--machine-id", "M-101"]
