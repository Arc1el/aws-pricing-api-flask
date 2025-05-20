# AWS 서비스별 필터 필드 및 값 문서화

이 문서는 AWS Pricing API에서 사용되는 필터 필드와 값에 대한 상세 설명을 제공합니다.

## 필터 구조

AWS Pricing API에서 사용하는 필터의 기본 구조는 다음과 같습니다:

```json
{
  "type": "TERM_MATCH",
  "field": "필드명",
  "value": "필드값"
}
```

- **type**: 필터 유형. 현재 AWS Pricing API는 "TERM_MATCH"만 지원합니다.
- **field**: 필터링할 제품 속성 필드명. 서비스마다 사용 가능한 필드가 다릅니다.
- **value**: 필터링할 값. 대소문자를 구분합니다.

## 공통 필드

모든 AWS 서비스에서 공통적으로 사용되는 필드입니다.

| 필드명 | 설명 | 예시 값 |
|--------|------|---------|
| location | AWS 리전 위치 | US East (N. Virginia), Asia Pacific (Seoul) |
| productFamily | AWS 제품 패밀리 카테고리 | Compute Instance, Database Instance, Storage |
| termType | 가격 책정 조건 유형 | OnDemand, Reserved |

## 서비스별 필드

### Amazon EC2 (AmazonEC2)

Amazon Elastic Compute Cloud 서비스에서 사용되는 필드입니다.

| 필드명 | 설명 | 예시 값 |
|--------|------|---------|
| instanceType | EC2 인스턴스 유형 | t2.micro, m5.large, c5.xlarge |
| operatingSystem | 운영 체제 | Linux, Windows, RHEL, SUSE |
| tenancy | 테넌시 유형 | Shared, Dedicated, Host |
| capacityStatus | 용량 상태 | Used, AllocatedCapacityReservation, AllocatedHost |
| preInstalledSw | 사전 설치된 소프트웨어 | NA, SQL Web, SQL Std, SQL Ent |
| licenseModel | 라이선스 모델 | No License required, License included |
| usagetype | 사용량 유형 | BoxUsage:t2.micro, BoxUsage:m5.large |
| operation | 작업 유형 | RunInstances, RunInstances:0002 |

### Amazon RDS (AmazonRDS)

Amazon Relational Database Service에서 사용되는 필드입니다.

| 필드명 | 설명 | 예시 값 |
|--------|------|---------|
| instanceType | RDS 인스턴스 유형 | db.t3.micro, db.m5.large, db.r6g.large |
| databaseEngine | 데이터베이스 엔진 | MySQL, PostgreSQL, Oracle, SQL Server, MariaDB, Aurora MySQL, Aurora PostgreSQL |
| deploymentOption | 배포 옵션 | Single-AZ, Multi-AZ |
| licenseModel | 라이선스 모델 | license-included, bring-your-own-license, general-public-license |
| databaseEdition | 데이터베이스 에디션 | Enterprise, Standard, Standard One, Standard Two |
| storageType | 스토리지 유형 | General Purpose, Provisioned IOPS, Magnetic |
| volumeType | 볼륨 유형 | General Purpose, Provisioned IOPS |

### Amazon S3 (AmazonS3)

Amazon Simple Storage Service에서 사용되는 필드입니다.

| 필드명 | 설명 | 예시 값 |
|--------|------|---------|
| volumeType | 스토리지 클래스 | Standard, Intelligent-Tiering, Standard-IA, One Zone-IA, Glacier, Glacier Deep Archive |
| storageClass | 스토리지 클래스 (volumeType과 유사) | General Purpose, Infrequent Access, Archive |
| usagetype | 사용량 유형 | TimedStorage-ByteHrs, Requests-Tier1, Requests-Tier2 |
| operation | 작업 유형 | PutObject, GetObject, ListBucket |

### Amazon EBS (AmazonEBS)

Amazon Elastic Block Store에서 사용되는 필드입니다.

| 필드명 | 설명 | 예시 값 |
|--------|------|---------|
| volumeType | EBS 볼륨 유형 | Standard, gp2, gp3, io1, io2, st1, sc1 |
| volumeApiName | 볼륨 API 이름 | standard, gp2, gp3, io1, io2, st1, sc1 |
| maxVolumeSize | 최대 볼륨 크기 | 1 TiB, 16 TiB |
| maxIopsvolume | 볼륨당 최대 IOPS | 3000, 16000, 64000 |
| maxThroughputvolume | 볼륨당 최대 처리량 | 125 MiB/s, 250 MiB/s, 1000 MiB/s |

### Amazon DynamoDB (AmazonDynamoDB)

Amazon DynamoDB에서 사용되는 필드입니다.

| 필드명 | 설명 | 예시 값 |
|--------|------|---------|
| group | DynamoDB 그룹 | DDB-ReadUnits, DDB-WriteUnits, DDB-StorageUsage |
| groupDescription | 그룹 설명 | ReadCapacityUnit-Hrs, WriteCapacityUnit-Hrs, GB-Month |
| capacityMode | 용량 모드 | Provisioned, On-Demand |
| readCapacityUnits | 읽기 용량 단위 | 5, 10, 100 |
| writeCapacityUnits | 쓰기 용량 단위 | 5, 10, 100 |

### Amazon CloudFront (AmazonCloudFront)

Amazon CloudFront에서 사용되는 필드입니다.

| 필드명 | 설명 | 예시 값 |
|--------|------|---------|
| originType | 오리진 유형 | AWS Origin, Non-AWS Origin |
| dataTransferType | 데이터 전송 유형 | DataTransfer-Out-Bytes, DataTransfer-In-Bytes |
| requestType | 요청 유형 | HTTPS, HTTP |
| priceClass | 가격 클래스 | PriceClass_All, PriceClass_100, PriceClass_200 |
| region | 리전 | Global, US, Europe, Asia, South America |

### AWS Lambda (AmazonLambda)

AWS Lambda에서 사용되는 필드입니다.

| 필드명 | 설명 | 예시 값 |
|--------|------|---------|
| group | Lambda 그룹 | AWS-Lambda-Requests, AWS-Lambda-Duration |
| groupDescription | 그룹 설명 | Lambda-GB-Second, Lambda-Requests |
| memorySize | 메모리 크기 | 128 MB, 256 MB, 512 MB, 1024 MB, 2048 MB |
| architecture | 아키텍처 | x86_64, arm64 |
| usagetype | 사용량 유형 | Lambda-GB-Second, Request |

## 예약 인스턴스 관련 필드

예약 인스턴스 가격 조회 시 사용되는 필드입니다.

| 필드명 | 설명 | 예시 값 |
|--------|------|---------|
| termType | 가격 책정 조건 유형 | Reserved |
| leaseContractLength | 예약 인스턴스 계약 기간 | 1yr, 3yr |
| purchaseOption | 예약 인스턴스 구매 옵션 | No Upfront, Partial Upfront, All Upfront |
| offeringClass | 예약 인스턴스 제공 클래스 | Standard, Convertible |
| reservedInstancePaymentOption | 결제 옵션 | All Upfront, Partial Upfront, No Upfront |

## 필터 사용 예시

### EC2 t2.micro 인스턴스 온디맨드 가격 조회

```json
[
  {
    "type": "TERM_MATCH",
    "field": "instanceType",
    "value": "t2.micro"
  },
  {
    "type": "TERM_MATCH",
    "field": "operatingSystem",
    "value": "Linux"
  },
  {
    "type": "TERM_MATCH",
    "field": "location",
    "value": "US East (N. Virginia)"
  },
  {
    "type": "TERM_MATCH",
    "field": "tenancy",
    "value": "Shared"
  },
  {
    "type": "TERM_MATCH",
    "field": "preInstalledSw",
    "value": "NA"
  }
]
```

### RDS MySQL db.r6g.large 인스턴스 예약 인스턴스(올업프론트) 가격 조회

```json
[
  {
    "type": "TERM_MATCH",
    "field": "instanceType",
    "value": "db.r6g.large"
  },
  {
    "type": "TERM_MATCH",
    "field": "databaseEngine",
    "value": "MySQL"
  },
  {
    "type": "TERM_MATCH",
    "field": "deploymentOption",
    "value": "Single-AZ"
  },
  {
    "type": "TERM_MATCH",
    "field": "location",
    "value": "US East (N. Virginia)"
  },
  {
    "type": "TERM_MATCH",
    "field": "termType",
    "value": "Reserved"
  },
  {
    "type": "TERM_MATCH",
    "field": "leaseContractLength",
    "value": "1yr"
  },
  {
    "type": "TERM_MATCH",
    "field": "purchaseOption",
    "value": "All Upfront"
  }
]
```

### S3 Standard 스토리지 가격 조회

```json
[
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
]
```

## 참고 사항

- 필드 값은 대소문자를 구분합니다.
- 서비스마다 사용 가능한 필드가 다릅니다.
- 특정 서비스에서 사용 가능한 모든 필드와 값을 확인하려면 API 서버의 다음 엔드포인트를 사용하세요:
  - 서비스의 모든 속성 조회: `GET /api/services/{serviceCode}/attributes`
  - 특정 속성의 가능한 값 조회: `GET /api/services/{serviceCode}/attributes/{attributeName}/values`
