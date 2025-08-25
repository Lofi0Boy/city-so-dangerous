
import base64
from io import BytesIO
from PIL import Image
from typing import Dict, Any
from .engine_io import EngineOutput, HazardType, DegreeOfRisk, engine_output_validator
from .graph import analyzing_graph


def analyze_image(image_bytes: bytes) -> EngineOutput:
    try:
        # 1. 이미지 로드
        image = Image.open(BytesIO(image_bytes))
        
        # 이미지가 유효한지 확인
        image.verify()
        
        # 이미지를 다시 열어서 사용 (verify() 후에는 이미지가 닫힘)
        image = Image.open(BytesIO(image_bytes))
        
        # 이미지를 base64로 인코딩 (graph에 전달하기 위해)
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')

        # 2. 이미지데이터를 graph에 invoke
        initial_state = {
            "image_data": image_base64,
            "messages": [],
            "raw_analysis": None,
            "validated_result": None,
            "needs_retry": False,
            "retry_count": 0,
            "error": None
        }
        
        final_state = analyzing_graph.invoke(initial_state)
        graph_result = final_state["validated_result"].model_dump() if final_state["validated_result"] else {}

        # 3. 결과값 검증
        validated_result = _validate_result(graph_result)

        # 4. 결과값 정상일 시 반환
        return validated_result
        
    except Exception as e:
        # 에러 발생 시 기본값 반환
        return {
            "error": {
                    "description": f"이미지 분석 중 오류가 발생했습니다: {str(e)}"
            }
        }


def _get_dummy_graph_result() -> Dict[str, Any]:
    """
    테스트용 더미 데이터 - 다양한 형태의 키/값을 포함하여 자동 변환 테스트
    """
    return {
        "hazards": {
            # 다양한 형태의 키/값으로 자동 변환 테스트
            "FIRE": {  # 대문자 이름
                "degree_of_risk": "HIGH",  # 대문자 값
                "description": "화재 위험이 감지되었습니다."
            },
            "wind": {  # 소문자 값
                "degree_of_risk": "medium",  # 소문자 값
                "description": "강풍 주의보입니다."
            },
            "Crime": {  # 혼합 케이스
                "degree_of_risk": "Low",  # 혼합 케이스
                "description": "주변에 범죄 위험 요소가 있습니다."
            },
            "unknown_hazard": {  # 알 수 없는 위험 타입 (OTHER로 변환될 것)
                "degree_of_risk": "invalid_risk",  # 잘못된 위험도 (LOW로 변환될 것)
                "description": "알 수 없는 위험입니다."
            }
        }
    }


def _validate_result(graph_result: Dict[str, Any]) -> EngineOutput:
    """
    graph 결과를 검증하고 EngineOutput 형태로 변환
    EngineOutput 스키마를 기반으로 자동 검증 및 변환
    """
    try:
        # 스키마 기반 자동 검증 및 변환
        validated_result = engine_output_validator.validate_and_convert(graph_result)
        
        # 결과가 비어있으면 기본값 설정
        if not validated_result.get("hazards"):
            validated_result["hazards"] = {
                HazardType.OTHER: {
                    "degree_of_risk": DegreeOfRisk.LOW,
                    "description": "특별한 위험 요소가 감지되지 않았습니다."
                }
            }
        
        return validated_result
        
    except Exception as e:
        # 검증 실패 시 기본값 반환
        return {
            "hazards": {
                HazardType.OTHER: {
                    "degree_of_risk": DegreeOfRisk.LOW,
                    "description": f"결과 검증 중 오류가 발생했습니다: {str(e)}"
                }
            }
        }