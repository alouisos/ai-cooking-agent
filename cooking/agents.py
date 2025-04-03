from typing import Annotated, Sequence, TypedDict, Union
from langchain.chat_models import ChatOpenAI
from langgraph.graph import Graph, StateGraph
from loguru import logger
from .models import AgentState, ToolSet
from .tools import create_tools

def create_cooking_graph(llm: ChatOpenAI) -> Graph:
    """Create the cooking assistant workflow graph."""
    
    # Create tools
    tools = create_tools(llm)
    toolset = ToolSet()
    
    # Define workflow steps
    def classify_query(state: AgentState) -> AgentState:
        """Determine if the query is cooking-related."""
        try:
            logger.info(f"Classifying query: {state.query}")
            is_cooking = tools[0].func(state.query)
            state.is_cooking_related = is_cooking
            state.reasoning_chain.append(
                f"Query classification: {'cooking-related' if is_cooking else 'not cooking-related'}"
            )
            logger.info(f"Query classified as: {'cooking-related' if is_cooking else 'not cooking-related'}")
            return state
        except Exception as e:
            logger.error(f"Error in classify_query: {str(e)}")
            raise

    def check_research_needed(state: AgentState) -> AgentState:
        """Check if research is needed."""
        try:
            if not state.is_cooking_related:
                logger.info("Skipping research check for non-cooking query")
                return state
                
            logger.info("Checking if research is needed")
            needs_research = tools[1].func(state.query)
            state.needs_research = needs_research
            state.reasoning_chain.append(
                f"Research {'needed' if needs_research else 'not needed'}"
            )
            logger.info(f"Research needed: {needs_research}")
            return state
        except Exception as e:
            logger.error(f"Error in check_research_needed: {str(e)}")
            raise

    def do_research(state: AgentState) -> AgentState:
        """Perform recipe research."""
        try:
            if not state.needs_research:
                logger.info("Skipping research - not needed")
                return state
                
            logger.info("Performing recipe research")
            results = tools[2].func(state.query)
            if not results:
                logger.warning("No research results found")
                state.research_results = []
                return state
                
            state.research_results = results
            state.reasoning_chain.append("Performed recipe research")
            logger.info(f"Found {len(results)} research results")
            return state
        except Exception as e:
            logger.error(f"Error in do_research: {str(e)}")
            raise

    def parse_results(state: AgentState) -> AgentState:
        """Parse research results into a recipe."""
        try:
            if not state.research_results:
                logger.info("No research results to parse")
                return state
                
            logger.info("Parsing research results into recipe")
            recipe = tools[3].func(state.research_results)
            state.recipe = recipe
            state.reasoning_chain.append(
                f"Recipe {'parsed successfully' if recipe else 'parsing failed'}"
            )
            logger.info(f"Recipe parsing {'successful' if recipe else 'failed'}")
            return state
        except Exception as e:
            logger.error(f"Error in parse_results: {str(e)}")
            raise

    def generate_response(state: AgentState) -> AgentState:
        """Generate the final response."""
        try:
            logger.info("Generating final response")
            if not state.is_cooking_related:
                logger.info("Generating non-cooking response")
                state.final_response = "I apologize, but I can only help with cooking-related questions. Please ask me about recipes, cooking techniques, or kitchen tools."
                return state
                
            logger.info("Generating cooking response")
            response = tools[4].func(state.query, state.recipe, toolset)
            if not response:
                logger.error("Failed to generate response")
                raise ValueError("Response generation failed")
                
            state.final_response = response
            state.reasoning_chain.append("Generated final response")
            logger.info("Response generated successfully")
            return state
        except Exception as e:
            logger.error(f"Error in generate_response: {str(e)}")
            raise

    # Create the workflow graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("classify", classify_query)
    workflow.add_node("check_research", check_research_needed)
    workflow.add_node("research", do_research)
    workflow.add_node("parse", parse_results)
    workflow.add_node("respond", generate_response)
    
    # Add edges
    workflow.add_edge("classify", "check_research")
    workflow.add_edge("check_research", "research")
    workflow.add_edge("research", "parse")
    workflow.add_edge("parse", "respond")
    
    # Set entry and end points
    workflow.set_entry_point("classify")
    workflow.set_finish_point("respond")
    
    logger.info("Workflow graph created successfully")
    return workflow.compile() 