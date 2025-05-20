# AWS Pricing API 서버 아키텍처 설계

## 개요
AWS Pricing API를 활용하여 AWS 리소스 정보를 입력받으면 비용을 계산해주는 API 서버를 설계합니다. 이 서버는 사용자로부터 AWS 리소스 정보를 받아 AWS Pricing API를 통해 가격 정보를 조회하고, 이를 기반으로 비용을 계산하여 응답합니다.

## API 엔드포인트 설계

### 1. 서비스 목록 조회 API
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

### 2. 서비스 속성 조회 API
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

### 3. 속성 값 조회 API
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

### 4. 가격 조회 API
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

### 5. 비용 계산 API
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

## 데이터 모델 설계

### 1. Service 모델
AWS 서비스 정보를 나타내는 모델입니다.
```python
class Service:
    service_code: str  # 서비스 코드 (예: AmazonEC2)
    service_name: str  # 서비스 이름 (예: Amazon Elastic Compute Cloud)
```

### 2. Attribute 모델
서비스 속성 정보를 나타내는 모델입니다.
```python
class Attribute:
    service_code: str  # 서비스 코드
    name: str  # 속성 이름 (예: instanceType)
    values: List[str]  # 가능한 속성 값 목록
```

### 3. Filter 모델
가격 조회 시 사용되는 필터 정보를 나타내는 모델입니다.
```python
class Filter:
    type: str  # 필터 타입 (예: TERM_MATCH)
    field: str  # 필터 필드 (예: instanceType)
    value: str  # 필터 값 (예: t2.micro)
```

### 4. PricingRequest 모델
가격 조회 요청 정보를 나타내는 모델입니다.
```python
class PricingRequest:
    service_code: str  # 서비스 코드
    filters: List[Filter]  # 필터 목록
```

### 5. PricingResponse 모델
가격 조회 응답 정보를 나타내는 모델입니다.
```python
class PricingResponse:
    service_code: str  # 서비스 코드
    resource_details: Dict[str, str]  # 리소스 상세 정보
    pricing: Dict[str, Any]  # 가격 정보
    estimated_monthly_cost: float  # 예상 월 비용
```

### 6. CalculationRequest 모델
비용 계산 요청 정보를 나타내는 모델입니다.
```python
class ResourceRequest:
    service_code: str  # 서비스 코드
    filters: List[Filter]  # 필터 목록
    quantity: int  # 수량
    usage_type: str  # 사용량 유형 (예: Hours)
    usage_value: float  # 사용량 값 (예: 730)

class CalculationRequest:
    resources: List[ResourceRequest]  # 리소스 요청 목록
```

### 7. CalculationResponse 모델
비용 계산 응답 정보를 나타내는 모델입니다.
```python
class ResourceCost:
    service_code: str  # 서비스 코드
    resource_details: Dict[str, str]  # 리소스 상세 정보
    quantity: int  # 수량
    usage_details: Dict[str, Any]  # 사용량 상세 정보
    cost: float  # 비용

class CalculationResponse:
    total_cost: Dict[str, Any]  # 총 비용 정보
    resource_costs: List[ResourceCost]  # 리소스별 비용 정보
```

## 컴포넌트 설계

### 1. AWS Pricing Client
AWS Pricing API와 통신하여 가격 정보를 조회하는 클라이언트입니다.
- `get_services()`: 모든 서비스 목록을 조회합니다.
- `get_service_attributes(service_code)`: 특정 서비스의 속성 목록을 조회합니다.
- `get_attribute_values(service_code, attribute_name)`: 특정 서비스의 특정 속성에 대한 가능한 값 목록을 조회합니다.
- `get_products(service_code, filters)`: 특정 서비스의 특정 필터 조건에 맞는 제품 정보를 조회합니다.

### 2. Pricing Calculator
AWS 리소스 정보를 기반으로 비용을 계산하는 계산기입니다.
- `calculate_price(service_code, filters)`: 특정 서비스의 특정 필터 조건에 맞는 제품의 가격을 계산합니다.
- `calculate_total_cost(resources)`: 여러 AWS 리소스의 조합에 대한 총 비용을 계산합니다.

### 3. API Controller
API 요청을 처리하는 컨트롤러입니다.
- `get_services()`: 서비스 목록 조회 API를 처리합니다.
- `get_service_attributes(service_code)`: 서비스 속성 조회 API를 처리합니다.
- `get_attribute_values(service_code, attribute_name)`: 속성 값 조회 API를 처리합니다.
- `get_pricing(pricing_request)`: 가격 조회 API를 처리합니다.
- `calculate_cost(calculation_request)`: 비용 계산 API를 처리합니다.

## 기술 스택
- **언어**: Python 3.10
- **웹 프레임워크**: Flask
- **AWS SDK**: boto3
- **테스트 프레임워크**: pytest
- **문서화**: Swagger/OpenAPI

## 아키텍처 다이어그램
```
+------------------+     +------------------+     +------------------+
|                  |     |                  |     |                  |
|  API Controller  |---->| Pricing Calculator|---->| AWS Pricing Client|
|                  |     |                  |     |                  |
+------------------+     +------------------+     +------------------+
         |                                               |
         v                                               v
+------------------+                           +------------------+
|                  |                           |                  |
|  Data Models     |                           |  AWS Pricing API |
|                  |                           |                  |
+------------------+                           +------------------+
```

## 구현 계획
1. AWS Pricing Client 구현
2. Pricing Calculator 구현
3. API Controller 구현
4. 테스트 코드 작성
5. 문서화 및 배포
