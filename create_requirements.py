#!/usr/bin/env python3

"""
requirements.txt 파일 생성 스크립트
"""

requirements = [
    "boto3>=1.37.0",
    "flask>=3.0.0",
    "requests>=2.30.0",
    "pytest>=8.0.0"
]

with open("requirements.txt", "w") as f:
    f.write("\n".join(requirements))

print("requirements.txt 파일이 생성되었습니다.")
