#!/bin/bash
set -e  # 오류 발생 시 스크립트 중단

# 1. DB 마이그레이션
echo "🛠️ Alembic 마이그레이션 실행 중..."
alembic upgrade head

# 2. 관리자 계정 생성
echo "👤 관리자 계정 생성 스크립트 실행 중..."
python tools/create_admin.py

# 3. FastAPI 서버 실행
echo "🚀 FastAPI 서버 시작 중..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
