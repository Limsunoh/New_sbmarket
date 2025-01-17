# 1. Python 3.10-slim 이미지 사용 (Debian 기반)
FROM python:3.10-slim

# 2. Python 버퍼링 비활성화 (로깅 출력 즉시 확인 가능)
ENV PYTHONUNBUFFERED=1

# 3. 시스템 패키지 설치 (PostgreSQL 및 빌드 도구)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    python3-dev \
    build-essential \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# 4. 작업 디렉토리 설정
WORKDIR /app

# 5. Python 의존성 설치
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 6. 프로젝트 파일 복사
COPY . /app

# 7. Django 서버 실행
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
