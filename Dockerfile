FROM python:3.11-slim

# 시스템 의존성 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 의존성 파일 복사
COPY ./requirements.txt /app/requirements.txt

# 의존성 설치
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# entrypoint.sh 복사 및 실행 권한 부여
COPY ./entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# 애플리케이션 실행
ENTRYPOINT ["/app/entrypoint.sh"]