#!/bin/bash

# AWS Pricing API 서버 실행 스크립트

# 환경 변수 설정 (필요한 경우)
# export AWS_ACCESS_KEY_ID=your_access_key
# export AWS_SECRET_ACCESS_KEY=your_secret_key
# export AWS_REGION=us-east-1

# 서버 실행
echo "AWS Pricing API 서버를 실행합니다..."
python3 app_swagger.py
