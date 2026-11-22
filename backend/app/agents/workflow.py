from langgraph.graph import StateGraph, START, END
from app.agents.state import InvestigationState
from app.agents.data_quality_agent import data_quality_agent
from app.agents.anomaly_agent import anomaly_investigation_agent
from app.agents.schema_agent import schema_analysis_agent
from app.agents.root_cause_agent import root_cause_analysis_agent
from app.agents.remediation_agent import remediation_agent
from app.agents.report_agent import report_generation_agent
from app.core.logging import logger

def build_investigation_graph():
    """Construct and compile the LangGraph multi-agent investigation workflow."""
    workflow = StateGraph(InvestigationState)

    # Register the 6 specialized agent nodes
    workflow.add_node("data_quality", data_quality_agent)
    workflow.add_node("anomaly_investigation", anomaly_investigation_agent)
    workflow.add_node("schema_analysis", schema_analysis_agent)
    workflow.add_node("root_cause_analysis", root_cause_analysis_agent)
    workflow.add_node("remediation", remediation_agent)
    workflow.add_node("report_generation", report_generation_agent)

    # Define execution graph sequence
    workflow.add_edge(START, "data_quality")
    workflow.add_edge("data_quality", "anomaly_investigation")
    workflow.add_edge("anomaly_investigation", "schema_analysis")
    workflow.add_edge("schema_analysis", "root_cause_analysis")
    workflow.add_edge("root_cause_analysis", "remediation")
    workflow.add_edge("remediation", "report_generation")
    workflow.add_edge("report_generation", END)

    app = workflow.compile()
    return app

investigation_workflow = build_investigation_graph()

def run_investigation(initial_state: InvestigationState) -> InvestigationState:
    """Execute the full compiled LangGraph workflow with error capture."""
    logger.info(f"Initiating LangGraph autonomous investigation for dataset '{initial_state.get('dataset_name')}'...")
    try:
        final_state = investigation_workflow.invoke(initial_state)
        logger.info(f"LangGraph investigation concluded with {len(final_state.get('agent_traces', []))} agent traces.")
        return final_state
    except Exception as e:
        logger.error(f"LangGraph investigation error: {str(e)}")
        initial_state["errors"].append(str(e))
        return initial_state
