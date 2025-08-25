"""
City So Dangerous - 위험 상황 이미지 분석 패키지

이 패키지는 이미지를 분석하여 다양한 위험 요소를 감지하고 분류합니다.

공개 API:
- analyze_image: 이미지 분석 메인 함수
- EngineOutput, HazardType, DegreeOfRisk: 타입 정의
- engine_output_validator: 스키마 검증기
"""

# 공개 API만 export
from .analyzer import analyze_image
from .engine_io import (
    EngineOutput,
    HazardType, 
    DegreeOfRisk,
    HazardInfo,
    SchemaValidator,
    engine_output_validator
)

# __all__을 사용하여 명시적으로 공개할 항목들을 정의
__all__ = [
    # 메인 함수
    'analyze_image',
    
    # 데이터 타입들
    'EngineOutput',
    'HazardType',
    'DegreeOfRisk', 
    'HazardInfo',
    
    # 유틸리티
    'SchemaValidator',
    'engine_output_validator'
]

# 패키지 메타데이터 - pyproject.toml에서 자동으로 읽어옴
try:
    # Python 3.8+에서 사용 가능
    from importlib.metadata import version, metadata
    __version__ = version("city-so-dangerous")
    
    # 추가 메타데이터도 자동으로 가져오기
    _metadata = metadata("city-so-dangerous")
    __author__ = _metadata.get("Author", "City So Dangerous Team")
    __description__ = _metadata.get("Summary", "위험 상황 이미지 분석 패키지")
except ImportError:
    # 개발 환경이나 패키지가 설치되지 않은 경우 fallback
    __version__ = "0.1.0"
    __author__ = "City So Dangerous Team"
    __description__ = "위험 상황 이미지 분석 패키지"

# 내부 모듈들은 의도적으로 export하지 않음
# - langgraph: 내부 구현 세부사항
# - analyzer의 내부 함수들: _validate_result, _get_dummy_graph_result 등
