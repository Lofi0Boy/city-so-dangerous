from langgraph.graph import StateGraph, START, END
from .model import HazardAnalysisState
from .nodes import (
    llm_analysis_node,
    validation_node, 
    refactor_node,
    route_decision_node,
    error_handler_node,
    success_node
)


def create_hazard_analysis_graph():
    workflow = StateGraph(HazardAnalysisState)
    
    workflow.add_node("llm_analysis", llm_analysis_node)
    workflow.add_node("validation", validation_node)
    workflow.add_node("refactor", refactor_node)
    workflow.add_node("error_handler", error_handler_node)
    workflow.add_node("success", success_node)
    
    workflow.add_edge(START, "llm_analysis")
    workflow.add_edge("llm_analysis", "validation")
    
    workflow.add_conditional_edges(
        "validation",
        route_decision_node,
        {
            "success": "success",
            "refactor": "refactor", 
            "error": "error_handler"
        }
    )
    
    workflow.add_edge("refactor", "validation")
    workflow.add_edge("success", END)
    workflow.add_edge("error_handler", END)
    
    return workflow.compile()


analyzing_graph = create_hazard_analysis_graph()