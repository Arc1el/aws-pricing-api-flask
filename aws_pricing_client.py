"""
AWS Pricing Client

AWS Pricing API와 통신하여 가격 정보를 조회하는 클라이언트 모듈입니다.
"""

import boto3
import json
from typing import List, Dict, Any, Optional
from botocore.exceptions import ClientError


class AWSPricingClient:
    """AWS Pricing API와 통신하여 가격 정보를 조회하는 클라이언트 클래스"""

    def __init__(self, region_name: str = "us-east-1"):
        """
        AWSPricingClient 초기화
        
        Args:
            region_name (str): AWS 리전 이름 (기본값: us-east-1)
                               참고: AWS Pricing API는 us-east-1과 ap-south-1 리전에서만 사용 가능
        """
        self.client = boto3.client('pricing', region_name=region_name)
    
    def get_services(self) -> List[Dict[str, str]]:
        """
        모든 서비스 목록을 조회합니다.
        
        Returns:
            List[Dict[str, str]]: 서비스 목록 (서비스 코드와 이름)
        
        Raises:
            ClientError: AWS API 호출 중 오류 발생 시
        """
        services = []
        next_token = None
        
        try:
            while True:
                if next_token:
                    response = self.client.describe_services(
                        FormatVersion='aws_v1',
                        NextToken=next_token
                    )
                else:
                    response = self.client.describe_services(
                        FormatVersion='aws_v1'
                    )
                
                for service in response.get('Services', []):
                    services.append({
                        'serviceCode': service.get('ServiceCode', ''),
                        'serviceName': service.get('ServiceCode', '')  # 실제 서비스 이름은 API에서 제공하지 않음
                    })
                
                next_token = response.get('NextToken')
                if not next_token:
                    break
        
        except ClientError as e:
            print(f"Error getting services: {e}")
            raise
        
        return services
    
    def get_service_attributes(self, service_code: str) -> List[str]:
        """
        특정 서비스의 속성 목록을 조회합니다.
        
        Args:
            service_code (str): 서비스 코드 (예: AmazonEC2)
        
        Returns:
            List[str]: 속성 이름 목록
        
        Raises:
            ClientError: AWS API 호출 중 오류 발생 시
        """
        try:
            response = self.client.describe_services(
                ServiceCode=service_code,
                FormatVersion='aws_v1'
            )
            
            if not response.get('Services'):
                return []
            
            return response['Services'][0].get('AttributeNames', [])
        
        except ClientError as e:
            print(f"Error getting service attributes for {service_code}: {e}")
            raise
    
    def get_attribute_values(self, service_code: str, attribute_name: str) -> List[str]:
        """
        특정 서비스의 특정 속성에 대한 가능한 값 목록을 조회합니다.
        
        Args:
            service_code (str): 서비스 코드 (예: AmazonEC2)
            attribute_name (str): 속성 이름 (예: instanceType)
        
        Returns:
            List[str]: 속성 값 목록
        
        Raises:
            ClientError: AWS API 호출 중 오류 발생 시
        """
        values = []
        next_token = None
        
        try:
            while True:
                if next_token:
                    response = self.client.get_attribute_values(
                        ServiceCode=service_code,
                        AttributeName=attribute_name,
                        NextToken=next_token
                    )
                else:
                    response = self.client.get_attribute_values(
                        ServiceCode=service_code,
                        AttributeName=attribute_name
                    )
                
                for attr_value in response.get('AttributeValues', []):
                    values.append(attr_value.get('Value', ''))
                
                next_token = response.get('NextToken')
                if not next_token:
                    break
        
        except ClientError as e:
            print(f"Error getting attribute values for {service_code}.{attribute_name}: {e}")
            raise
        
        return values
    
    def get_products(self, service_code: str, filters: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        특정 서비스의 특정 필터 조건에 맞는 제품 정보를 조회합니다.
        
        Args:
            service_code (str): 서비스 코드 (예: AmazonEC2)
            filters (List[Dict[str, str]]): 필터 목록
                예: [
                    {
                        'type': 'TERM_MATCH',
                        'field': 'instanceType',
                        'value': 't2.micro'
                    }
                ]
        
        Returns:
            List[Dict[str, Any]]: 제품 정보 목록
        
        Raises:
            ClientError: AWS API 호출 중 오류 발생 시
        """
        products = []
        next_token = None
        
        # boto3 API에 맞게 필터 형식 변환
        formatted_filters = []
        for filter_item in filters:
            formatted_filters.append({
                'Type': filter_item.get('type', 'TERM_MATCH'),
                'Field': filter_item.get('field', ''),
                'Value': filter_item.get('value', '')
            })
        
        try:
            while True:
                if next_token:
                    response = self.client.get_products(
                        ServiceCode=service_code,
                        Filters=formatted_filters,
                        FormatVersion='aws_v1',
                        NextToken=next_token
                    )
                else:
                    response = self.client.get_products(
                        ServiceCode=service_code,
                        Filters=formatted_filters,
                        FormatVersion='aws_v1'
                    )
                
                for price_list in response.get('PriceList', []):
                    # PriceList는 JSON 문자열로 반환되므로 파싱 필요
                    try:
                        product = json.loads(price_list)
                        products.append(product)
                    except json.JSONDecodeError as e:
                        print(f"Error parsing product JSON: {e}")
                
                next_token = response.get('NextToken')
                if not next_token:
                    break
        
        except ClientError as e:
            print(f"Error getting products for {service_code}: {e}")
            raise
        
        return products


class PricingCalculator:
    """AWS 리소스 정보를 기반으로 비용을 계산하는 계산기 클래스"""
    
    def __init__(self, pricing_client: AWSPricingClient):
        """
        PricingCalculator 초기화
        
        Args:
            pricing_client (AWSPricingClient): AWS Pricing 클라이언트 인스턴스
        """
        self.pricing_client = pricing_client
    
    def _extract_price_from_product(self, product: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        제품 정보에서 가격 정보를 추출합니다.
        
        Args:
            product (Dict[str, Any]): 제품 정보
        
        Returns:
            Optional[Dict[str, Any]]: 가격 정보 (없으면 None)
        """
        try:
            # 제품 정보에서 가격 정보 추출
            terms = product.get('terms', {})
            on_demand = terms.get('OnDemand', {})
            
            if not on_demand:
                return None
            
            # 첫 번째 온디맨드 가격 정보 사용
            offer_key = list(on_demand.keys())[0]
            price_dimensions = on_demand[offer_key].get('priceDimensions', {})
            
            if not price_dimensions:
                return None
            
            # 첫 번째 가격 차원 사용
            dimension_key = list(price_dimensions.keys())[0]
            price_dimension = price_dimensions[dimension_key]
            
            price_per_unit = float(price_dimension.get('pricePerUnit', {}).get('USD', 0))
            unit = price_dimension.get('unit', '')
            description = price_dimension.get('description', '')
            
            return {
                'currency': 'USD',
                'pricePerUnit': price_per_unit,
                'unit': unit,
                'description': description
            }
        
        except (KeyError, IndexError, ValueError) as e:
            print(f"Error extracting price from product: {e}")
            return None
    
    def _extract_resource_details(self, product: Dict[str, Any], filters: List[Dict[str, str]]) -> Dict[str, str]:
        """
        제품 정보와 필터를 기반으로 리소스 상세 정보를 추출합니다.
        
        Args:
            product (Dict[str, Any]): 제품 정보
            filters (List[Dict[str, str]]): 필터 목록
        
        Returns:
            Dict[str, str]: 리소스 상세 정보
        """
        resource_details = {}
        
        # 필터에서 필드와 값 추출
        for filter_item in filters:
            field = filter_item.get('field', '')
            value = filter_item.get('value', '')
            if field and value:
                resource_details[field] = value
        
        # 제품 정보에서 추가 속성 추출
        product_attributes = product.get('product', {}).get('attributes', {})
        for key, value in product_attributes.items():
            if key not in resource_details:
                resource_details[key] = value
        
        return resource_details
    
    def calculate_price(self, service_code: str, filters: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        특정 서비스의 특정 필터 조건에 맞는 제품의 가격을 계산합니다.
        
        Args:
            service_code (str): 서비스 코드 (예: AmazonEC2)
            filters (List[Dict[str, str]]): 필터 목록
        
        Returns:
            Dict[str, Any]: 가격 정보
        
        Raises:
            ValueError: 가격 정보를 찾을 수 없는 경우
        """
        products = self.pricing_client.get_products(service_code, filters)
        
        if not products:
            raise ValueError(f"No products found for {service_code} with the given filters")
        
        # 첫 번째 제품 사용
        product = products[0]
        
        # 가격 정보 추출
        pricing = self._extract_price_from_product(product)
        if not pricing:
            raise ValueError(f"No pricing information found for {service_code} with the given filters")
        
        # 리소스 상세 정보 추출
        resource_details = self._extract_resource_details(product, filters)
        
        # 월별 예상 비용 계산 (시간당 가격 * 730시간)
        estimated_monthly_cost = 0
        if pricing['unit'].lower() == 'hrs':
            estimated_monthly_cost = pricing['pricePerUnit'] * 730  # 한 달 평균 시간
        
        return {
            'serviceCode': service_code,
            'resourceDetails': resource_details,
            'pricing': pricing,
            'estimatedMonthlyCost': estimated_monthly_cost
        }
    
    def calculate_total_cost(self, resources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        여러 AWS 리소스의 조합에 대한 총 비용을 계산합니다.
        
        Args:
            resources (List[Dict[str, Any]]): 리소스 요청 목록
                예: [
                    {
                        'serviceCode': 'AmazonEC2',
                        'filters': [
                            {
                                'type': 'TERM_MATCH',
                                'field': 'instanceType',
                                'value': 't2.micro'
                            }
                        ],
                        'quantity': 5,
                        'usageType': 'Hours',
                        'usageValue': 730
                    }
                ]
        
        Returns:
            Dict[str, Any]: 총 비용 정보
        """
        total_cost = 0
        resource_costs = []
        
        for resource in resources:
            service_code = resource.get('serviceCode', '')
            filters = resource.get('filters', [])
            quantity = resource.get('quantity', 1)
            usage_type = resource.get('usageType', '')
            usage_value = resource.get('usageValue', 0)
            
            try:
                # 리소스 가격 계산
                price_info = self.calculate_price(service_code, filters)
                
                # 리소스 비용 계산
                resource_cost = 0
                if price_info['pricing']['unit'].lower() == 'hrs' and usage_type.lower() == 'hours':
                    # 시간당 가격 * 사용 시간 * 수량
                    resource_cost = price_info['pricing']['pricePerUnit'] * usage_value * quantity
                else:
                    # 기본적으로 단위당 가격 * 사용량 * 수량
                    resource_cost = price_info['pricing']['pricePerUnit'] * usage_value * quantity
                
                # 리소스 비용 정보 추가
                resource_costs.append({
                    'serviceCode': service_code,
                    'resourceDetails': price_info['resourceDetails'],
                    'quantity': quantity,
                    'usageDetails': {
                        'type': usage_type,
                        'value': usage_value
                    },
                    'cost': resource_cost
                })
                
                # 총 비용에 추가
                total_cost += resource_cost
            
            except ValueError as e:
                print(f"Error calculating cost for {service_code}: {e}")
                # 오류가 발생해도 계속 진행
        
        return {
            'totalCost': {
                'currency': 'USD',
                'amount': total_cost,
                'timeUnit': 'monthly'
            },
            'resourceCosts': resource_costs
        }


# 테스트 코드
if __name__ == "__main__":
    # AWS Pricing 클라이언트 생성
    pricing_client = AWSPricingClient()
    
    try:
        # 서비스 목록 조회
        print("서비스 목록 조회:")
        services = pricing_client.get_services()
        print(f"서비스 수: {len(services)}")
        print(f"첫 번째 서비스: {services[0]}")
        print()
        
        # EC2 서비스 속성 조회
        print("EC2 서비스 속성 조회:")
        attributes = pricing_client.get_service_attributes("AmazonEC2")
        print(f"속성 수: {len(attributes)}")
        print(f"속성 목록: {attributes[:5]}...")
        print()
        
        # EC2 인스턴스 타입 조회
        print("EC2 인스턴스 타입 조회:")
        instance_types = pricing_client.get_attribute_values("AmazonEC2", "instanceType")
        print(f"인스턴스 타입 수: {len(instance_types)}")
        print(f"인스턴스 타입 목록: {instance_types[:5]}...")
        print()
        
        # EC2 t2.micro 가격 조회
        print("EC2 t2.micro 가격 조회:")
        filters = [
            {
                'type': 'TERM_MATCH',
                'field': 'instanceType',
                'value': 't2.micro'
            },
            {
                'type': 'TERM_MATCH',
                'field': 'operatingSystem',
                'value': 'Linux'
            },
            {
                'type': 'TERM_MATCH',
                'field': 'location',
                'value': 'US East (N. Virginia)'
            }
        ]
        products = pricing_client.get_products("AmazonEC2", filters)
        print(f"제품 수: {len(products)}")
        if products:
            print(f"첫 번째 제품: {json.dumps(products[0], indent=2)}")
        print()
        
        # 가격 계산
        print("가격 계산:")
        calculator = PricingCalculator(pricing_client)
        price_info = calculator.calculate_price("AmazonEC2", filters)
        print(f"가격 정보: {json.dumps(price_info, indent=2)}")
        print()
        
        # 총 비용 계산
        print("총 비용 계산:")
        resources = [
            {
                'serviceCode': 'AmazonEC2',
                'filters': filters,
                'quantity': 5,
                'usageType': 'Hours',
                'usageValue': 730
            }
        ]
        total_cost = calculator.calculate_total_cost(resources)
        print(f"총 비용 정보: {json.dumps(total_cost, indent=2)}")
    
    except Exception as e:
        print(f"오류 발생: {e}")
