"""
AWS Pricing API 서버 테스트

AWS Pricing API 서버의 기능을 테스트하는 모듈입니다.
"""

import unittest
import json
from unittest.mock import patch, MagicMock
from app import app


class TestAWSPricingAPIServer(unittest.TestCase):
    """AWS Pricing API 서버 테스트 클래스"""

    def setUp(self):
        """테스트 설정"""
        self.app = app.test_client()
        self.app.testing = True

    @patch('app.pricing_client.get_services')
    def test_get_services(self, mock_get_services):
        """서비스 목록 조회 API 테스트"""
        # 목 데이터 설정
        mock_services = [
            {
                'serviceCode': 'AmazonEC2',
                'serviceName': 'Amazon Elastic Compute Cloud'
            },
            {
                'serviceCode': 'AmazonS3',
                'serviceName': 'Amazon Simple Storage Service'
            }
        ]
        mock_get_services.return_value = mock_services

        # API 호출
        response = self.app.get('/api/services')
        data = json.loads(response.data)

        # 응답 검증
        self.assertEqual(response.status_code, 200)
        self.assertIn('services', data)
        self.assertEqual(len(data['services']), 2)
        self.assertEqual(data['services'][0]['serviceCode'], 'AmazonEC2')

    @patch('app.pricing_client.get_service_attributes')
    def test_get_service_attributes(self, mock_get_service_attributes):
        """서비스 속성 조회 API 테스트"""
        # 목 데이터 설정
        mock_attributes = ['instanceType', 'location', 'operatingSystem', 'tenancy']
        mock_get_service_attributes.return_value = mock_attributes

        # API 호출
        response = self.app.get('/api/services/AmazonEC2/attributes')
        data = json.loads(response.data)

        # 응답 검증
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['serviceCode'], 'AmazonEC2')
        self.assertIn('attributes', data)
        self.assertEqual(len(data['attributes']), 4)
        self.assertIn('instanceType', data['attributes'])

    @patch('app.pricing_client.get_attribute_values')
    def test_get_attribute_values(self, mock_get_attribute_values):
        """속성 값 조회 API 테스트"""
        # 목 데이터 설정
        mock_values = ['t2.micro', 't2.small', 't2.medium']
        mock_get_attribute_values.return_value = mock_values

        # API 호출
        response = self.app.get('/api/services/AmazonEC2/attributes/instanceType/values')
        data = json.loads(response.data)

        # 응답 검증
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['serviceCode'], 'AmazonEC2')
        self.assertEqual(data['attributeName'], 'instanceType')
        self.assertIn('values', data)
        self.assertEqual(len(data['values']), 3)
        self.assertIn('t2.micro', data['values'])

    @patch('app.pricing_calculator.calculate_price')
    def test_get_pricing(self, mock_calculate_price):
        """가격 조회 API 테스트"""
        # 목 데이터 설정
        mock_price_info = {
            'serviceCode': 'AmazonEC2',
            'priceInfos': [
                {
                    'serviceCode': 'AmazonEC2',
                    'resourceDetails': {
                        'instanceType': 't2.micro',
                        'location': 'US East (N. Virginia)',
                        'operatingSystem': 'Linux'
                    },
                    'pricing': {
                        'currency': 'USD',
                        'pricePerUnit': 0.0116,
                        'unit': 'Hrs'
                    },
                    'estimatedMonthlyCost': 8.47
                },
                {
                    'serviceCode': 'AmazonEC2',
                    'resourceDetails': {
                        'instanceType': 't2.micro',
                        'location': 'US East (N. Virginia)',
                        'operatingSystem': 'Windows'
                    },
                    'pricing': {
                        'currency': 'USD',
                        'pricePerUnit': 0.0232,
                        'unit': 'Hrs'
                    },
                    'estimatedMonthlyCost': 16.94
                }
            ]
        }
        mock_calculate_price.return_value = mock_price_info

        # 요청 데이터
        request_data = {
            'serviceCode': 'AmazonEC2',
            'filters': [
                {
                    'type': 'TERM_MATCH',
                    'field': 'instanceType',
                    'value': 't2.micro'
                },
                {
                    'type': 'TERM_MATCH',
                    'field': 'location',
                    'value': 'US East (N. Virginia)'
                }
            ]
        }

        # API 호출
        response = self.app.post('/api/pricing', json=request_data)
        data = json.loads(response.data)

        # 응답 검증
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['serviceCode'], 'AmazonEC2')
        self.assertIn('priceInfos', data)
        self.assertEqual(len(data['priceInfos']), 2)
        self.assertEqual(data['priceInfos'][0]['pricing']['pricePerUnit'], 0.0116)
        self.assertEqual(data['priceInfos'][0]['estimatedMonthlyCost'], 8.47)
        self.assertEqual(data['priceInfos'][1]['pricing']['pricePerUnit'], 0.0232)
        self.assertEqual(data['priceInfos'][1]['estimatedMonthlyCost'], 16.94)

    @patch('app.pricing_calculator.calculate_total_cost')
    def test_calculate_cost(self, mock_calculate_total_cost):
        """비용 계산 API 테스트"""
        # 목 데이터 설정
        mock_total_cost = {
            'totalCost': {
                'currency': 'USD',
                'amount': 65.35,
                'timeUnit': 'monthly'
            },
            'resourceCosts': [
                {
                    'serviceCode': 'AmazonEC2',
                    'resourceDetails': {
                        'instanceType': 't2.micro',
                        'location': 'US East (N. Virginia)'
                    },
                    'quantity': 5,
                    'usageDetails': {
                        'type': 'Hours',
                        'value': 730
                    },
                    'cost': 42.35
                },
                {
                    'serviceCode': 'AmazonS3',
                    'resourceDetails': {
                        'volumeType': 'Standard',
                        'location': 'US East (N. Virginia)'
                    },
                    'quantity': 1,
                    'usageDetails': {
                        'type': 'GB-Month',
                        'value': 1000
                    },
                    'cost': 23.00
                }
            ]
        }
        mock_calculate_total_cost.return_value = mock_total_cost

        # 요청 데이터
        request_data = {
            'resources': [
                {
                    'serviceCode': 'AmazonEC2',
                    'filters': [
                        {
                            'type': 'TERM_MATCH',
                            'field': 'instanceType',
                            'value': 't2.micro'
                        },
                        {
                            'type': 'TERM_MATCH',
                            'field': 'location',
                            'value': 'US East (N. Virginia)'
                        }
                    ],
                    'quantity': 5,
                    'usageType': 'Hours',
                    'usageValue': 730
                },
                {
                    'serviceCode': 'AmazonS3',
                    'filters': [
                        {
                            'type': 'TERM_MATCH',
                            'field': 'volumeType',
                            'value': 'Standard'
                        },
                        {
                            'type': 'TERM_MATCH',
                            'field': 'location',
                            'value': 'US East (N. Virginia)'
                        }
                    ],
                    'quantity': 1,
                    'usageType': 'GB-Month',
                    'usageValue': 1000
                }
            ]
        }

        # API 호출
        response = self.app.post('/api/calculate', json=request_data)
        data = json.loads(response.data)

        # 응답 검증
        self.assertEqual(response.status_code, 200)
        self.assertIn('totalCost', data)
        self.assertEqual(data['totalCost']['amount'], 65.35)
        self.assertIn('resourceCosts', data)
        self.assertEqual(len(data['resourceCosts']), 2)
        self.assertEqual(data['resourceCosts'][0]['cost'], 42.35)
        self.assertEqual(data['resourceCosts'][1]['cost'], 23.00)

    def test_index(self):
        """루트 엔드포인트 테스트"""
        # API 호출
        response = self.app.get('/')
        data = json.loads(response.data)

        # 응답 검증
        self.assertEqual(response.status_code, 200)
        self.assertIn('name', data)
        self.assertIn('version', data)
        self.assertIn('description', data)
        self.assertIn('endpoints', data)
        self.assertEqual(len(data['endpoints']), 5)


class TestIntegration(unittest.TestCase):
    """통합 테스트 클래스"""

    def setUp(self):
        """테스트 설정"""
        self.app = app.test_client()
        self.app.testing = True

    def test_integration_flow(self):
        """통합 테스트 흐름 - 단순화된 버전"""
        # 루트 엔드포인트만 테스트
        response = self.app.get('/')
        data = json.loads(response.data)
        
        # 응답 검증
        self.assertEqual(response.status_code, 200)
        self.assertIn('name', data)
        self.assertIn('version', data)
        self.assertIn('description', data)
        self.assertIn('endpoints', data)




if __name__ == '__main__':
    unittest.main()
