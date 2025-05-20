"""
AWS Pricing API 서버 - Swagger 문서 통합 버전

AWS Pricing API를 활용하여 AWS 리소스 정보를 입력받으면 비용을 계산해주는 API 서버입니다.
Swagger/OpenAPI 문서가 통합되어 있어 API를 쉽게 탐색하고 테스트할 수 있습니다.
"""

from flask import Flask, request
from flask_restx import Api, Resource, fields, Namespace
import os
import json
from typing import List, Dict, Any
from aws_pricing_client import AWSPricingClient, PricingCalculator

# Flask 애플리케이션 생성
app = Flask(__name__)

# Flask-RestX API 생성
api = Api(
    app,
    version='1.0.0',
    title='AWS Pricing API Server',
    description='AWS Pricing API를 활용하여 AWS 리소스 정보를 입력받으면 비용을 계산해주는 API 서버',
    doc='/swagger',
    default='api',
    default_label='AWS Pricing API 작업'
)

# 네임스페이스 생성
ns = api.namespace('api', description='AWS Pricing API 작업')

# AWS Pricing 클라이언트 및 계산기 초기화
pricing_client = AWSPricingClient()
pricing_calculator = PricingCalculator(pricing_client)

# 모델 정의
service_model = api.model('Service', {
    'serviceCode': fields.String(description='서비스 코드 (예: AmazonEC2)'),
    'serviceName': fields.String(description='서비스 이름 (예: Amazon Elastic Compute Cloud)')
})

services_model = api.model('Services', {
    'services': fields.List(fields.Nested(service_model), description='서비스 목록')
})

filter_model = api.model('Filter', {
    'type': fields.String(required=True, enum=['TERM_MATCH'], description='필터 유형. 현재 AWS Pricing API는 "TERM_MATCH"만 지원합니다.'),
    'field': fields.String(required=True, description='필터링할 제품 속성 필드명. 서비스마다 사용 가능한 필드가 다릅니다.'),
    'value': fields.String(required=True, description='필터링할 값. 대소문자를 구분합니다.')
})

service_attributes_model = api.model('ServiceAttributes', {
    'serviceCode': fields.String(description='서비스 코드 (예: AmazonEC2)'),
    'attributes': fields.List(fields.String, description='속성 목록')
})

attribute_values_model = api.model('AttributeValues', {
    'serviceCode': fields.String(description='서비스 코드 (예: AmazonEC2)'),
    'attributeName': fields.String(description='속성 이름 (예: instanceType)'),
    'values': fields.List(fields.String, description='속성 값 목록')
})

pricing_request_model = api.model('PricingRequest', {
    'serviceCode': fields.String(required=True, description='서비스 코드 (예: AmazonEC2)'),
    'filters': fields.List(fields.Nested(filter_model), description='필터 목록')
})

pricing_info_model = api.model('PricingInfo', {
    'currency': fields.String(description='통화 (예: USD)'),
    'pricePerUnit': fields.Float(description='단위당 가격'),
    'unit': fields.String(description='단위 (예: Hrs)'),
    'description': fields.String(description='설명')
})

pricing_response_model = api.model('PricingResponse', {
    'serviceCode': fields.String(description='서비스 코드 (예: AmazonEC2)'),
    'resourceDetails': fields.Raw(description='리소스 상세 정보'),
    'pricing': fields.Nested(pricing_info_model, description='가격 정보'),
    'estimatedMonthlyCost': fields.Float(description='예상 월 비용')
})

resource_request_model = api.model('ResourceRequest', {
    'serviceCode': fields.String(required=True, description='서비스 코드 (예: AmazonEC2)'),
    'filters': fields.List(fields.Nested(filter_model), required=True, description='필터 목록'),
    'quantity': fields.Integer(description='수량', default=1),
    'usageType': fields.String(description='사용량 유형 (예: Hours)', default='Hours'),
    'usageValue': fields.Float(description='사용량 값 (예: 730)', default=730)
})

calculation_request_model = api.model('CalculationRequest', {
    'resources': fields.List(fields.Nested(resource_request_model), required=True, description='리소스 요청 목록')
})

usage_details_model = api.model('UsageDetails', {
    'type': fields.String(description='사용량 유형 (예: Hours)'),
    'value': fields.Float(description='사용량 값 (예: 730)')
})

resource_cost_model = api.model('ResourceCost', {
    'serviceCode': fields.String(description='서비스 코드 (예: AmazonEC2)'),
    'resourceDetails': fields.Raw(description='리소스 상세 정보'),
    'quantity': fields.Integer(description='수량'),
    'usageDetails': fields.Nested(usage_details_model, description='사용량 상세 정보'),
    'cost': fields.Float(description='비용')
})

total_cost_model = api.model('TotalCost', {
    'currency': fields.String(description='통화 (예: USD)'),
    'amount': fields.Float(description='금액'),
    'timeUnit': fields.String(description='시간 단위 (예: monthly)')
})

calculation_response_model = api.model('CalculationResponse', {
    'totalCost': fields.Nested(total_cost_model, description='총 비용 정보'),
    'resourceCosts': fields.List(fields.Nested(resource_cost_model), description='리소스별 비용 정보')
})

error_model = api.model('Error', {
    'error': fields.String(description='오류 메시지')
})

# API 엔드포인트 정의
@ns.route('/services')
class ServiceList(Resource):
    @ns.doc('get_services')
    @ns.response(200, '성공', services_model)
    @ns.response(500, '서버 오류', error_model)
    def get(self):
        """
        모든 서비스 목록을 반환합니다.
        
        AWS에서 제공하는 모든 서비스 목록을 조회하여 반환합니다.
        """
        try:
            services = pricing_client.get_services()
            return {
                'services': services
            }
        except Exception as e:
            return {
                'error': str(e)
            }, 500


@ns.route('/services/<string:service_code>/attributes')
@ns.param('service_code', '서비스 코드 (예: AmazonEC2)')
class ServiceAttributes(Resource):
    @ns.doc('get_service_attributes')
    @ns.response(200, '성공', service_attributes_model)
    @ns.response(500, '서버 오류', error_model)
    def get(self, service_code):
        """
        특정 서비스의 속성 목록을 반환합니다.
        
        지정된 서비스 코드에 대한 모든 속성 목록을 조회하여 반환합니다.
        이 속성들은 필터링에 사용될 수 있습니다.
        """
        try:
            attributes = pricing_client.get_service_attributes(service_code)
            return {
                'serviceCode': service_code,
                'attributes': attributes
            }
        except Exception as e:
            return {
                'error': str(e)
            }, 500


@ns.route('/services/<string:service_code>/attributes/<string:attribute_name>/values')
@ns.param('service_code', '서비스 코드 (예: AmazonEC2)')
@ns.param('attribute_name', '속성 이름 (예: instanceType)')
class AttributeValues(Resource):
    @ns.doc('get_attribute_values')
    @ns.response(200, '성공', attribute_values_model)
    @ns.response(500, '서버 오류', error_model)
    def get(self, service_code, attribute_name):
        """
        특정 서비스의 특정 속성에 대한 가능한 값 목록을 반환합니다.
        
        지정된 서비스 코드와 속성 이름에 대한 모든 가능한 값 목록을 조회하여 반환합니다.
        이 값들은 필터링에 사용될 수 있습니다.
        """
        try:
            values = pricing_client.get_attribute_values(service_code, attribute_name)
            return {
                'serviceCode': service_code,
                'attributeName': attribute_name,
                'values': values
            }
        except Exception as e:
            return {
                'error': str(e)
            }, 500


@ns.route('/pricing')
class Pricing(Resource):
    @ns.doc('get_pricing')
    @ns.expect(pricing_request_model)
    @ns.response(200, '성공', pricing_response_model)
    @ns.response(400, '잘못된 요청', error_model)
    @ns.response(404, '리소스를 찾을 수 없음', error_model)
    @ns.response(500, '서버 오류', error_model)
    def post(self):
        """
        입력받은 AWS 리소스 정보를 기반으로 가격을 계산하여 반환합니다.
        
        서비스 코드와 필터 목록을 입력받아 해당 리소스의 가격 정보를 조회하고,
        예상 월 비용을 계산하여 반환합니다.
        """
        try:
            data = request.get_json()
            
            if not data:
                return {
                    'error': 'No data provided'
                }, 400
            
            service_code = data.get('serviceCode')
            filters = data.get('filters', [])
            
            if not service_code:
                return {
                    'error': 'Service code is required'
                }, 400
            
            price_info = pricing_calculator.calculate_price(service_code, filters)
            return price_info
        
        except ValueError as e:
            return {
                'error': str(e)
            }, 404
        
        except Exception as e:
            return {
                'error': str(e)
            }, 500


@ns.route('/calculate')
class Calculate(Resource):
    @ns.doc('calculate_cost')
    @ns.expect(calculation_request_model)
    @ns.response(200, '성공', calculation_response_model)
    @ns.response(400, '잘못된 요청', error_model)
    @ns.response(500, '서버 오류', error_model)
    def post(self):
        """
        여러 AWS 리소스의 조합에 대한 총 비용을 계산하여 반환합니다.
        
        여러 리소스 요청 목록을 입력받아 각 리소스의 비용을 계산하고,
        총 비용을 계산하여 반환합니다.
        """
        try:
            data = request.get_json()
            
            if not data:
                return {
                    'error': 'No data provided'
                }, 400
            
            resources = data.get('resources', [])
            
            if not resources:
                return {
                    'error': 'Resources are required'
                }, 400
            
            total_cost = pricing_calculator.calculate_total_cost(resources)
            return total_cost
        
        except Exception as e:
            return {
                'error': str(e)
            }, 500


@ns.route('/filter-documentation')
class FilterDocumentation(Resource):
    @ns.doc('get_filter_documentation')
    def get(self):
        """
        AWS 서비스별 필터 필드와 값에 대한 상세 설명을 제공합니다.
        
        주요 AWS 서비스에 대한 필터 필드와 값의 설명을 제공하여
        API 사용자가 필터를 쉽게 구성할 수 있도록 도와줍니다.
        """
        filter_docs = {
            "filterDocumentation": {
                "general": {
                    "description": "AWS Pricing API 필터 사용 가이드",
                    "filterType": "TERM_MATCH (현재 유일하게 지원되는 필터 유형)",
                    "caseSensitive": "필드 값은 대소문자를 구분합니다."
                },
                "commonFields": {
                    "location": {
                        "description": "AWS 리전 위치",
                        "examples": [
                            "US East (N. Virginia)",
                            "US West (Oregon)",
                            "Asia Pacific (Seoul)",
                            "Europe (Frankfurt)"
                        ]
                    },
                    "productFamily": {
                        "description": "AWS 제품 패밀리 카테고리",
                        "examples": [
                            "Compute Instance",
                            "Database Instance",
                            "Storage",
                            "Data Transfer"
                        ]
                    }
                },
                "services": {
                    "AmazonEC2": {
                        "description": "Amazon Elastic Compute Cloud",
                        "fields": {
                            "instanceType": {
                                "description": "EC2 인스턴스 유형",
                                "examples": ["t2.micro", "m5.large", "c5.xlarge"]
                            },
                            "operatingSystem": {
                                "description": "운영 체제",
                                "examples": ["Linux", "Windows", "RHEL", "SUSE"]
                            },
                            "tenancy": {
                                "description": "테넌시 유형",
                                "examples": ["Shared", "Dedicated", "Host"]
                            },
                            "capacityStatus": {
                                "description": "용량 상태",
                                "examples": ["Used", "AllocatedCapacityReservation", "AllocatedHost"]
                            },
                            "preInstalledSw": {
                                "description": "사전 설치된 소프트웨어",
                                "examples": ["NA", "SQL Web", "SQL Std", "SQL Ent"]
                            }
                        }
                    },
                    "AmazonRDS": {
                        "description": "Amazon Relational Database Service",
                        "fields": {
                            "instanceType": {
                                "description": "RDS 인스턴스 유형",
                                "examples": ["db.t3.micro", "db.m5.large", "db.r6g.large"]
                            },
                            "databaseEngine": {
                                "description": "데이터베이스 엔진",
                                "examples": ["MySQL", "PostgreSQL", "Oracle", "SQL Server", "MariaDB", "Aurora MySQL", "Aurora PostgreSQL"]
                            },
                            "deploymentOption": {
                                "description": "배포 옵션",
                                "examples": ["Single-AZ", "Multi-AZ"]
                            },
                            "licenseModel": {
                                "description": "라이선스 모델",
                                "examples": ["license-included", "bring-your-own-license", "general-public-license"]
                            }
                        }
                    },
                    "AmazonS3": {
                        "description": "Amazon Simple Storage Service",
                        "fields": {
                            "volumeType": {
                                "description": "스토리지 클래스",
                                "examples": ["Standard", "Intelligent-Tiering", "Standard-IA", "One Zone-IA", "Glacier", "Glacier Deep Archive"]
                            },
                            "storageClass": {
                                "description": "스토리지 클래스 (volumeType과 유사)",
                                "examples": ["General Purpose", "Infrequent Access", "Archive"]
                            }
                        }
                    },
                    "AmazonEBS": {
                        "description": "Amazon Elastic Block Store",
                        "fields": {
                            "volumeType": {
                                "description": "EBS 볼륨 유형",
                                "examples": ["Standard", "gp2", "gp3", "io1", "io2", "st1", "sc1"]
                            },
                            "volumeApiName": {
                                "description": "볼륨 API 이름",
                                "examples": ["standard", "gp2", "gp3", "io1", "io2", "st1", "sc1"]
                            }
                        }
                    },
                    "AmazonDynamoDB": {
                        "description": "Amazon DynamoDB",
                        "fields": {
                            "group": {
                                "description": "DynamoDB 그룹",
                                "examples": ["DDB-ReadUnits", "DDB-WriteUnits", "DDB-StorageUsage"]
                            },
                            "groupDescription": {
                                "description": "그룹 설명",
                                "examples": ["ReadCapacityUnit-Hrs", "WriteCapacityUnit-Hrs", "GB-Month"]
                            }
                        }
                    },
                    "AmazonCloudFront": {
                        "description": "Amazon CloudFront",
                        "fields": {
                            "originType": {
                                "description": "오리진 유형",
                                "examples": ["AWS Origin", "Non-AWS Origin"]
                            },
                            "dataTransferType": {
                                "description": "데이터 전송 유형",
                                "examples": ["DataTransfer-Out-Bytes", "DataTransfer-In-Bytes"]
                            }
                        }
                    },
                    "AmazonLambda": {
                        "description": "AWS Lambda",
                        "fields": {
                            "group": {
                                "description": "Lambda 그룹",
                                "examples": ["AWS-Lambda-Requests", "AWS-Lambda-Duration"]
                            },
                            "groupDescription": {
                                "description": "그룹 설명",
                                "examples": ["Lambda-GB-Second", "Lambda-Requests"]
                            }
                        }
                    }
                },
                "pricingTerms": {
                    "termType": {
                        "description": "가격 책정 조건 유형",
                        "examples": ["OnDemand", "Reserved"]
                    },
                    "leaseContractLength": {
                        "description": "예약 인스턴스 계약 기간",
                        "examples": ["1yr", "3yr"]
                    },
                    "purchaseOption": {
                        "description": "예약 인스턴스 구매 옵션",
                        "examples": ["No Upfront", "Partial Upfront", "All Upfront"]
                    },
                    "offeringClass": {
                        "description": "예약 인스턴스 제공 클래스",
                        "examples": ["Standard", "Convertible"]
                    }
                }
            }
        }
        return filter_docs


@ns.route('/')
class Index(Resource):
    @ns.doc('get_index')
    def get(self):
        """
        API 서버 루트 엔드포인트
        
        API 서버의 기본 정보와 사용 가능한 엔드포인트 목록을 반환합니다.
        """
        return {
            'name': 'AWS Pricing API Server',
            'version': '1.0.0',
            'description': 'AWS Pricing API를 활용하여 AWS 리소스 정보를 입력받으면 비용을 계산해주는 API 서버',
            'endpoints': [
                {
                    'path': '/api/services',
                    'method': 'GET',
                    'description': '모든 서비스 목록을 반환'
                },
                {
                    'path': '/api/services/{serviceCode}/attributes',
                    'method': 'GET',
                    'description': '특정 서비스의 속성 목록을 반환'
                },
                {
                    'path': '/api/services/{serviceCode}/attributes/{attributeName}/values',
                    'method': 'GET',
                    'description': '특정 서비스의 특정 속성에 대한 가능한 값 목록을 반환'
                },
                {
                    'path': '/api/pricing',
                    'method': 'POST',
                    'description': '입력받은 AWS 리소스 정보를 기반으로 가격을 계산하여 반환'
                },
                {
                    'path': '/api/calculate',
                    'method': 'POST',
                    'description': '여러 AWS 리소스의 조합에 대한 총 비용을 계산하여 반환'
                },
                {
                    'path': '/api/filter-documentation',
                    'method': 'GET',
                    'description': 'AWS 서비스별 필터 필드와 값에 대한 상세 설명을 제공'
                },
                {
                    'path': '/swagger',
                    'method': 'GET',
                    'description': 'Swagger UI를 통한 API 문서 및 테스트 인터페이스'
                }
            ]
        }


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 7777))
    
    # 디버그 모드로 서버 실행 (개발 환경에서만 사용)
    app.run(host='0.0.0.0', port=port, debug=True)
