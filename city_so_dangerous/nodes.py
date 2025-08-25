import json
from dotenv import load_dotenv
from typing import Literal
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from .model import HazardAnalysisState, AnalysisResult, HazardType, DegreeOfRisk
from .hazard_analysis_prompt import SYSTEM_PROMPT, REFACTOR_PROMPT

load_dotenv()


def llm_analysis_node(state: HazardAnalysisState) -> dict:
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.1)
    
    message = HumanMessage(content=[
        {"type": "text", "text": SYSTEM_PROMPT},
        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{state['image_data']}"}}
    ])
    
    response = llm.invoke([message])
    
    return {
        "messages": state["messages"] + [message, response],
        "raw_analysis": {"content": response.content}
    }


def validation_node(state: HazardAnalysisState) -> dict:
    try:
        content = state["raw_analysis"]["content"]
        
        # Extract JSON from markdown code blocks if present
        if "```json" in content:
            start = content.find("```json") + 7
            end = content.find("```", start)
            if end != -1:
                content = content[start:end].strip()
        elif "```" in content:
            start = content.find("```") + 3
            end = content.find("```", start)
            if end != -1:
                content = content[start:end].strip()
        
        data = json.loads(content)
        
        validated_result = AnalysisResult(**data)
        
        return {
            "validated_result": validated_result,
            "needs_retry": False
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "needs_retry": True,
            "retry_count": state["retry_count"] + 1
        }


def refactor_node(state: HazardAnalysisState) -> dict:
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)
    
    content = state["raw_analysis"]["content"]
    prompt = REFACTOR_PROMPT.format(json_text=content)
    
    response = llm.invoke([HumanMessage(content=prompt)])
    
    return {
        "raw_analysis": {"content": response.content}
    }


def route_decision_node(state: HazardAnalysisState) -> Literal["success", "refactor", "error"]:
    if not state["needs_retry"]:
        return "success"
    
    if state["retry_count"] >= 2:
        return "error"
        
    return "refactor"


def error_handler_node(state: HazardAnalysisState) -> dict:
    return {
        "validated_result": AnalysisResult(
            hazards={
                HazardType.OTHER: {
                    "degree_of_risk": DegreeOfRisk.LOW,
                    "description": f"Analysis failed: {state.get('error', 'Unknown error')}"
                }
            }
        ),
        "needs_retry": False
    }


def success_node(state: HazardAnalysisState) -> dict:
    return {"needs_retry": False}