import os
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from langchain.chat_models import ChatOpenAI
from loguru import logger
from dotenv import load_dotenv
from pydantic import ValidationError

from cooking.models import CookingQuery, CookingResponse, AgentState
from cooking.agents import create_cooking_graph

# Load environment variables
load_dotenv()

# Configure logging
logger.add(
    "cooking_assistant.log",
    rotation="500 MB",
    level="INFO",
    format="{time} | {level} | {module}:{function}:{line} - {message}"
)

# Initialize FastAPI app
app = FastAPI(
    title="Cooking Assistant API",
    description="An AI-powered cooking assistant that helps with recipes and cooking advice",
    version="1.0.0"
)

# Initialize LLM and workflow graph
try:
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY environment variable is not set")
        
    llm = ChatOpenAI(
        temperature=0.7,
        model="gpt-3.5-turbo"
    )
    cooking_graph = create_cooking_graph(llm)
    logger.info("Successfully initialized LLM and workflow graph")
except Exception as e:
    logger.error(f"Failed to initialize application: {str(e)}")
    raise

async def generate_cooking_response(query: str) -> Dict[str, Any]:
    """Generate a response for a cooking-related query using the workflow graph.
    
    Args:
        query: The user's cooking-related question
        
    Returns:
        Dict containing response, relevance, and reasoning chain
    """
    try:
        # Initialize agent state with query
        state = AgentState(query=query)
        logger.debug(f"Created initial state: {dict(state)}")
        
        # Execute workflow
        try:
            final_state = cooking_graph.invoke(state)
            logger.debug(f"Workflow final state: {dict(final_state)}")
        except Exception as workflow_error:
            logger.error("Error executing workflow", exc_info=True)
            raise RuntimeError(f"Workflow execution failed: {str(workflow_error)}") from workflow_error
        
        # Ensure we have the required fields
        if not isinstance(final_state, dict):
            logger.error(f"Expected dict state, got {type(final_state)}")
            raise TypeError(f"Invalid state type: {type(final_state)}")
            
        # Extract values from state with detailed logging
        response_data = {
            "response": str(final_state.get("final_response", "No response generated")),
            "relevant": bool(final_state.get("is_cooking_related", False)),
            "reasoning_chain": list(final_state.get("reasoning_chain", []))
        }
        logger.debug(f"Extracted response data: {response_data}")
        return response_data
        
    except Exception as e:
        logger.error("Error generating cooking response", exc_info=True)
        # Re-raise with context but preserve original error
        raise ValueError(f"Failed to generate response: {str(e)}") from e

@app.post("/cooking/query", response_model=CookingResponse)
async def process_cooking_query(query: CookingQuery) -> CookingResponse:
    """Process a cooking-related query."""
    try:
        # Get response from cooking agent
        response = await generate_cooking_response(query.query)
        
        # Create response object with validation
        try:
            cooking_response = CookingResponse(
                response=response.get("response", "No response generated"),
                relevant=response.get("relevant", False),
                reasoning_chain=response.get("reasoning_chain", [])
            )
            logger.info(f"Successfully created CookingResponse: {cooking_response.dict()}")
            return cooking_response
            
        except ValidationError as ve:
            logger.error(f"Validation error creating CookingResponse: {ve}")
            # Attempt to create a fallback response
            return CookingResponse(
                response=str(response.get("response", "Error processing response")),
                relevant=bool(response.get("relevant", False)),
                reasoning_chain=["Error in response validation", str(ve)]
            )
            
    except Exception as e:
        logger.exception("Error processing cooking query")
        error_msg = f"Error processing query: {str(e)}"
        return CookingResponse(
            response=error_msg,
            relevant=False,
            reasoning_chain=["Error occurred", str(e)]
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 