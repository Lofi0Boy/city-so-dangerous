from enum import Enum
from typing import Dict, TypedDict, Optional, Type, Union, Any, get_type_hints, get_origin, get_args
import inspect

class DegreeOfRisk(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class HazardType(Enum):
    FIRE = "fire"
    WIND = "wind"
    EARTHQUAKE = "earthquake"
    RAIN = "rain"
    SNOW = "snow"
    CRIME = "crime"
    OTHER = "other"

class HazardInfo(TypedDict):
    degree_of_risk: DegreeOfRisk
    description: str


class EngineInput(TypedDict):
    image_bytes: bytes
    image_url: Optional[str]
    description: Optional[str]


class EngineOutput(TypedDict):
    hazards: Dict[HazardType, HazardInfo]


# 자동 매핑을 위한 헬퍼 함수들
def safe_enum_lookup(enum_class: Type[Enum], value: Union[str, Enum], default: Enum = None) -> Enum:
    """
    안전하게 enum 값을 찾아서 반환. 찾지 못하면 default 반환
    """
    if isinstance(value, enum_class):
        return value
    
    if isinstance(value, str):
        # 대소문자 구분 없이 찾기
        for enum_item in enum_class:
            if enum_item.value.lower() == value.lower():
                return enum_item
        
        # 이름으로도 찾기 (FIRE, WIND 등)
        try:
            return enum_class[value.upper()]
        except KeyError:
            pass
    
    return default


def get_enum_value_mapping(enum_class: Type[Enum]) -> Dict[str, Enum]:
    """
    Enum의 모든 값들을 소문자로 매핑한 딕셔너리 반환
    """
    return {item.value.lower(): item for item in enum_class}


def get_enum_name_mapping(enum_class: Type[Enum]) -> Dict[str, Enum]:
    """
    Enum의 모든 이름들을 소문자로 매핑한 딕셔너리 반환
    """
    return {item.name.lower(): item for item in enum_class}


# TypedDict 기반 자동 검증 시스템
class SchemaValidator:
    """TypedDict 스키마를 기반으로 자동 검증하는 클래스"""
    
    def __init__(self, typed_dict_class: Type):
        self.schema_class = typed_dict_class
        self.type_hints = get_type_hints(typed_dict_class)
        self._enum_mappings = self._build_enum_mappings()
    
    def _build_enum_mappings(self) -> Dict[Type[Enum], Dict[str, Enum]]:
        """스키마에서 사용된 모든 Enum들의 매핑을 자동 생성"""
        mappings = {}
        
        for field_name, field_type in self.type_hints.items():
            enum_types = self._extract_enum_types(field_type)
            for enum_type in enum_types:
                if enum_type not in mappings:
                    mappings[enum_type] = {
                        **{item.value.lower(): item for item in enum_type},
                        **{item.name.lower(): item for item in enum_type}
                    }
        
        return mappings
    
    def _extract_enum_types(self, type_annotation) -> set:
        """타입 어노테이션에서 모든 Enum 타입들을 추출"""
        enum_types = set()
        
        # 직접 Enum인 경우
        if inspect.isclass(type_annotation) and issubclass(type_annotation, Enum):
            enum_types.add(type_annotation)
        
        # Dict[EnumType, SomeType] 형태인 경우
        elif get_origin(type_annotation) is dict:
            dict_args = get_args(type_annotation)
            if dict_args:
                # Dict의 키 타입 확인
                key_type = dict_args[0]
                if inspect.isclass(key_type) and issubclass(key_type, Enum):
                    enum_types.add(key_type)
                
                # Dict의 값 타입도 재귀적으로 확인
                if len(dict_args) > 1:
                    enum_types.update(self._extract_enum_types(dict_args[1]))
        
        # Union, Optional 등의 경우
        elif hasattr(type_annotation, '__args__'):
            for arg in getattr(type_annotation, '__args__', []):
                enum_types.update(self._extract_enum_types(arg))
        
        return enum_types
    
    def safe_enum_convert(self, enum_type: Type[Enum], value: Any, default: Enum = None) -> Enum:
        """안전하게 값을 Enum으로 변환"""
        if isinstance(value, enum_type):
            return value
        
        if isinstance(value, str) and enum_type in self._enum_mappings:
            return self._enum_mappings[enum_type].get(value.lower(), default)
        
        return default
    
    def validate_and_convert(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """데이터를 스키마에 맞게 검증하고 변환"""
        result = {}
        
        for field_name, expected_type in self.type_hints.items():
            if field_name not in data:
                continue
            
            field_value = data[field_name]
            converted_value = self._convert_field(field_value, expected_type)
            result[field_name] = converted_value
        
        return result
    
    def _convert_field(self, value: Any, expected_type: Any) -> Any:
        """필드 값을 예상 타입으로 변환"""
        # Dict[EnumType, TypedDict] 형태 처리
        if get_origin(expected_type) is dict:
            return self._convert_dict_field(value, expected_type)
        
        # 직접 Enum 타입인 경우
        elif inspect.isclass(expected_type) and issubclass(expected_type, Enum):
            return self.safe_enum_convert(expected_type, value, list(expected_type)[0])
        
        # 기본적으로 그대로 반환
        return value
    
    def _convert_dict_field(self, value: Any, dict_type: Any) -> Dict[Any, Any]:
        """Dict 필드를 변환"""
        if not isinstance(value, dict):
            return {}
        
        dict_args = get_args(dict_type)
        if not dict_args:
            return value
        
        key_type, value_type = dict_args[0], dict_args[1]
        result = {}
        
        for k, v in value.items():
            # 키 변환
            if inspect.isclass(key_type) and issubclass(key_type, Enum):
                converted_key = self.safe_enum_convert(key_type, k, list(key_type)[0])
            else:
                converted_key = k
            
            # 값 변환 (TypedDict인 경우)
            if hasattr(value_type, '__annotations__'):
                # 중첩된 TypedDict 처리
                nested_validator = SchemaValidator(value_type)
                converted_value = nested_validator.validate_and_convert(v)
            else:
                converted_value = self._convert_field(v, value_type)
            
            result[converted_key] = converted_value
        
        return result


# EngineOutput용 글로벌 검증기
engine_output_validator = SchemaValidator(EngineOutput)
