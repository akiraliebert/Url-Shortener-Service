FROM python:3.12-slim

# Чтобы Python не писал .pyc и не буферизовал вывод
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Рабочая директория внутри контейнера
WORKDIR /app

# Устанавливаем зависимости для сборки Python-пакетов
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
  && rm -rf /var/lib/apt/lists/*

# Скопируем файл зависимостей и установим их
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Копируем код проекта
COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]