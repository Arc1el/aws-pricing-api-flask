# AWS Pricing API 서버 배포 및 사용 가이드
## 목차
1. [시스템 요구사항](#시스템-요구사항)
2. [설치 방법](#설치-방법)
3. [실행 방법](#실행-방법)
4. [API 엔드포인트](#api-엔드포인트)
5. [사용 예제](#사용-예제)
6. [AWS 자격 증명 설정](#aws-자격-증명-설정)
7. [문제 해결](#문제-해결)
8. [기여하기](#기여하기)

## 시스템 요구사항
- Python 3.11 이상
- pip (Python 패키지 관리자)
- AWS 계정 및 자격 증명
- 인터넷 연결

## 설치 방법

### 1. 소스 코드 다운로드
GitHub 저장소에서 소스 코드를 다운로드하거나 클론합니다.
```bash
git clone https://github.com/Arc1el/aws-pricing-api-flask.git
cd aws-pricing-api-flask
```

### 2. 필요한 패키지 설치
필요한 Python 패키지를 설치합니다.
```bash
pip install -r requirements.txt
```

## 실행 방법

### 1. AWS 자격 증명 설정
AWS Pricing API를 사용하기 위해서는 AWS 자격 증명이 필요합니다. [AWS 자격 증명 설정](#aws-자격-증명-설정) 섹션을 참고하여 자격 증명을 설정하세요.

### 2. API 서버 실행
다음 명령어로 API 서버를 실행합니다.
```bash
python app.py
```

기본적으로 서버는 `http://0.0.0.0:5000`에서 실행됩니다. 포트를 변경하려면 환경 변수 `PORT`를 설정하세요.
```bash
PORT=8080 python app.py
```

### 3. Docker를 사용한 실행 (선택사항)
Docker를 사용하여 API 서버를 실행할 수도 있습니다.

Dockerfile 생성:
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=5000
EXPOSE 5000

CMD ["python", "app.py"]
```

Docker 이미지 빌드 및 실행:
```bash
docker build -t aws-pricing-api-flask .
docker run -p 5000:5000 -e AWS_ACCESS_KEY_ID=your_access_key -e AWS_SECRET_ACCESS_KEY=your_secret_key aws-pricing-api-flask
```

## API 엔드포인트

### Swagger UI
- **URL**: `/swagger`
- **설명**: API 문서를 대화형으로 탐색하고 테스트할 수 있는 Swagger UI 인터페이스를 제공합니다.
- **기능**:
  - 모든 API 엔드포인트의 상세 문서 확인
  - API 요청/응답 스키마 확인
  - API 직접 테스트 실행
  - 요청/응답 예제 확인
- **사용 방법**:
  1. 웹 브라우저에서 `http://localhost:5000/swagger` 접속
  2. 원하는 API 엔드포인트 선택
  3. "Try it out" 버튼 클릭
  4. 필요한 파라미터 입력
  5. "Execute" 버튼을 클릭하여 API 테스트

### 1. 서비스 목록 조회
- **엔드포인트**: `/api/services`
- **메서드**: GET
- **설명**: AWS에서 제공하는 모든 서비스 목록을 반환합니다.
- **응답 예시**:
```json
{
  "services": [
    {
      "serviceCode": "AmazonEC2",
      "serviceName": "Amazon Elastic Compute Cloud"
    },
    {
      "serviceCode": "AmazonS3",
      "serviceName": "Amazon Simple Storage Service"
    }
  ]
}
```

### 2. 서비스 속성 조회
- **엔드포인트**: `/api/services/{serviceCode}/attributes`
- **메서드**: GET
- **설명**: 특정 서비스의 속성 목록을 반환합니다.
- **응답 예시**:
```json
{
  "serviceCode": "AmazonEC2",
  "attributes": [
    "instanceType",
    "location",
    "operatingSystem",
    "tenancy"
  ]
}
```

### 3. 속성 값 조회
- **엔드포인트**: `/api/services/{serviceCode}/attributes/{attributeName}/values`
- **메서드**: GET
- **설명**: 특정 서비스의 특정 속성에 대한 가능한 값 목록을 반환합니다.
- **응답 예시**:
```json
{
  "serviceCode": "AmazonEC2",
  "attributeName": "instanceType",
  "values": [
    "t2.micro",
    "t2.small",
    "t2.medium"
  ]
}
```

### 4. 가격 조회
- **엔드포인트**: `/api/pricing`
- **메서드**: POST
- **설명**: 입력받은 AWS 리소스 정보를 기반으로 가격을 계산하여 반환합니다.
- **요청 예시**:
```json
{
  "serviceCode": "AmazonEC2",
  "filters": [
    {
      "type": "TERM_MATCH",
      "field": "instanceType",
      "value": "t2.micro"
    },
    {
      "type": "TERM_MATCH",
      "field": "location",
      "value": "US East (N. Virginia)"
    },
    {
      "type": "TERM_MATCH",
      "field": "operatingSystem",
      "value": "Linux"
    }
  ]
}
```
- **응답 예시**:
```json
{
  "serviceCode": "AmazonEC2",
  "resourceDetails": {
    "instanceType": "t2.micro",
    "location": "US East (N. Virginia)",
    "operatingSystem": "Linux"
  },
  "pricing": {
    "currency": "USD",
    "pricePerUnit": 0.0116,
    "unit": "Hrs"
  },
  "estimatedMonthlyCost": 8.47
}
```

### 5. 비용 계산
- **엔드포인트**: `/api/calculate`
- **메서드**: POST
- **설명**: 여러 AWS 리소스의 조합에 대한 총 비용을 계산하여 반환합니다.
- **요청 예시**:
```json
{
  "resources": [
    {
      "serviceCode": "AmazonEC2",
      "filters": [
        {
          "type": "TERM_MATCH",
          "field": "instanceType",
          "value": "t2.micro"
        },
        {
          "type": "TERM_MATCH",
          "field": "location",
          "value": "US East (N. Virginia)"
        }
      ],
      "quantity": 5,
      "usageType": "Hours",
      "usageValue": 730
    },
    {
      "serviceCode": "AmazonS3",
      "filters": [
        {
          "type": "TERM_MATCH",
          "field": "volumeType",
          "value": "Standard"
        },
        {
          "type": "TERM_MATCH",
          "field": "location",
          "value": "US East (N. Virginia)"
        }
      ],
      "quantity": 1,
      "usageType": "GB-Month",
      "usageValue": 1000
    }
  ]
}
```
- **응답 예시**:
```json
{
  "totalCost": {
    "currency": "USD",
    "amount": 65.35,
    "timeUnit": "monthly"
  },
  "resourceCosts": [
    {
      "serviceCode": "AmazonEC2",
      "resourceDetails": {
        "instanceType": "t2.micro",
        "location": "US East (N. Virginia)"
      },
      "quantity": 5,
      "usageDetails": {
        "type": "Hours",
        "value": 730
      },
      "cost": 42.35
    },
    {
      "serviceCode": "AmazonS3",
      "resourceDetails": {
        "volumeType": "Standard",
        "location": "US East (N. Virginia)"
      },
      "quantity": 1,
      "usageDetails": {
        "type": "GB-Month",
        "value": 1000
      },
      "cost": 23.00
    }
  ]
}
```

## 사용 예제

### curl을 사용한 API 호출 예제

#### 서비스 목록 조회
```bash
curl -X GET http://localhost:5000/api/services
```

#### EC2 서비스 속성 조회
```bash
curl -X GET http://localhost:5000/api/services/AmazonEC2/attributes
```

#### EC2 인스턴스 타입 조회
```bash
curl -X GET http://localhost:5000/api/services/AmazonEC2/attributes/instanceType/values
```

#### EC2 t2.micro 가격 조회
```bash
curl -X POST http://localhost:5000/api/pricing \
  -H "Content-Type: application/json" \
  -d '{
    "serviceCode": "AmazonEC2",
    "filters": [
      {
        "type": "TERM_MATCH",
        "field": "instanceType",
        "value": "t2.micro"
      },
      {
        "type": "TERM_MATCH",
        "field": "location",
        "value": "US East (N. Virginia)"
      },
      {
        "type": "TERM_MATCH",
        "field": "operatingSystem",
        "value": "Linux"
      }
    ]
  }'
```

#### 여러 리소스 비용 계산
```bash
curl -X POST http://localhost:5000/api/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "resources": [
      {
        "serviceCode": "AmazonEC2",
        "filters": [
          {
            "type": "TERM_MATCH",
            "field": "instanceType",
            "value": "t2.micro"
          },
          {
            "type": "TERM_MATCH",
            "field": "location",
            "value": "US East (N. Virginia)"
          },
          {
            "type": "TERM_MATCH",
            "field": "operatingSystem",
            "value": "Linux"
          }
        ],
        "quantity": 5,
        "usageType": "Hours",
        "usageValue": 730
      }
    ]
  }'
```

### Python 클라이언트 예제
```python
import requests
import json

# API 서버 URL
base_url = "http://localhost:5000"

# 서비스 목록 조회
response = requests.get(f"{base_url}/api/services")
services = response.json()
print(f"서비스 수: {len(services['services'])}")

# EC2 서비스 속성 조회
response = requests.get(f"{base_url}/api/services/AmazonEC2/attributes")
attributes = response.json()
print(f"EC2 속성: {attributes['attributes']}")

# EC2 인스턴스 타입 조회
response = requests.get(f"{base_url}/api/services/AmazonEC2/attributes/instanceType/values")
instance_types = response.json()
print(f"인스턴스 타입 수: {len(instance_types['values'])}")

# EC2 t2.micro 가격 조회
pricing_request = {
    "serviceCode": "AmazonEC2",
    "filters": [
        {
            "type": "TERM_MATCH",
            "field": "instanceType",
            "value": "t2.micro"
        },
        {
            "type": "TERM_MATCH",
            "field": "location",
            "value": "US East (N. Virginia)"
        },
        {
            "type": "TERM_MATCH",
            "field": "operatingSystem",
            "value": "Linux"
        }
    ]
}
response = requests.post(f"{base_url}/api/pricing", json=pricing_request)
price_info = response.json()
print(f"t2.micro 가격: {price_info['pricing']['pricePerUnit']} {price_info['pricing']['currency']}/{price_info['pricing']['unit']}")
print(f"예상 월 비용: {price_info['estimatedMonthlyCost']} {price_info['pricing']['currency']}")

# 여러 리소스 비용 계산
calculation_request = {
    "resources": [
        {
            "serviceCode": "AmazonEC2",
            "filters": [
                {
                    "type": "TERM_MATCH",
                    "field": "instanceType",
                    "value": "t2.micro"
                },
                {
                    "type": "TERM_MATCH",
                    "field": "location",
                    "value": "US East (N. Virginia)"
                },
                {
                    "type": "TERM_MATCH",
                    "field": "operatingSystem",
                    "value": "Linux"
                }
            ],
            "quantity": 5,
            "usageType": "Hours",
            "usageValue": 730
        }
    ]
}
response = requests.post(f"{base_url}/api/calculate", json=calculation_request)
total_cost = response.json()
print(f"총 비용: {total_cost['totalCost']['amount']} {total_cost['totalCost']['currency']}/{total_cost['totalCost']['timeUnit']}")
```

## AWS 자격 증명 설정

AWS Pricing API를 사용하기 위해서는 AWS 자격 증명이 필요합니다. 다음 방법 중 하나를 선택하여 자격 증명을 설정하세요.

### 1. 환경 변수 설정
```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_REGION=us-east-1  # AWS Pricing API는 us-east-1과 ap-south-1 리전에서만 사용 가능
```

### 2. AWS 자격 증명 파일 설정
`~/.aws/credentials` 파일에 자격 증명을 설정합니다.
```ini
[default]
aws_access_key_id = your_access_key
aws_secret_access_key = your_secret_key
```

`~/.aws/config` 파일에 리전을 설정합니다.
```ini
[default]
region = us-east-1
```

### 3. IAM 역할 사용 (EC2 인스턴스 또는 ECS 컨테이너에서 실행하는 경우)
EC2 인스턴스 또는 ECS 컨테이너에서 실행하는 경우 IAM 역할을 사용하여 자격 증명을 제공할 수 있습니다. 이 경우 별도의 자격 증명 설정이 필요하지 않습니다.

## 문제 해결

### 1. AWS 자격 증명 오류
```
botocore.exceptions.NoCredentialsError: Unable to locate credentials
```
- AWS 자격 증명이 올바르게 설정되어 있는지 확인하세요.
- 환경 변수 또는 자격 증명 파일을 통해 자격 증명을 설정하세요.

### 2. 리전 오류
```
botocore.exceptions.EndpointConnectionError: Could not connect to the endpoint URL
```
- AWS Pricing API는 us-east-1과 ap-south-1 리전에서만 사용 가능합니다.
- 리전을 올바르게 설정했는지 확인하세요.

### 3. 서비스 코드 오류
```
botocore.exceptions.ClientError: An error occurred (InvalidParameterException) when calling the GetProducts operation: Service code is invalid
```
- 서비스 코드가 올바른지 확인하세요.
- `/api/services` 엔드포인트를 호출하여 유효한 서비스 코드 목록을 확인하세요.

### 4. 필터 오류
```
botocore.exceptions.ClientError: An error occurred (InvalidParameterException) when calling the GetProducts operation: Filter is invalid
```
- 필터 형식이 올바른지 확인하세요.
- 필터의 필드와 값이 유효한지 확인하세요.
- `/api/services/{serviceCode}/attributes` 엔드포인트를 호출하여 유효한 속성 목록을 확인하세요.
- `/api/services/{serviceCode}/attributes/{attributeName}/values` 엔드포인트를 호출하여 유효한 속성 값 목록을 확인하세요.

## 기여하기

이 프로젝트에 기여하고 싶으시다면 다음과 같은 방법으로 참여하실 수 있습니다.

### 1. 이슈 등록
- 버그 리포트
- 새로운 기능 제안
- 문서 개선 제안
- 기타 질문이나 의견

### 2. Pull Request 제출
1. 이 저장소를 포크합니다.
2. 새로운 브랜치를 생성합니다 (`git checkout -b feature/amazing-feature`).
3. 변경사항을 커밋합니다 (`git commit -m 'Add some amazing feature'`).
4. 브랜치에 푸시합니다 (`git push origin feature/amazing-feature`).
5. Pull Request를 생성합니다.

### 3. 라이선스
이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.
