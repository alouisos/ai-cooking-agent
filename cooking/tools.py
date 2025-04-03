from typing import List, Optional
import json
from langchain.tools import Tool
#from langchain.chat_models import ChatOpenAI
from langchain_community.chat_models import ChatOpenAI
from duckduckgo_search import DDGS
from langchain.schema import HumanMessage
from .prompts import (
    QUERY_CLASSIFIER_PROMPT,
    RESEARCH_NEEDED_PROMPT,
    RECIPE_PARSER_PROMPT,
    FINAL_RESPONSE_PROMPT,
    GENERAL_COOKING_PROMPT
)
from .models import Recipe, ToolSet
import logging

logger = logging.getLogger(__name__)

def search_recipes(query: str) -> List[str]:
    """Search for recipes and cooking information using DuckDuckGo."""
    with DDGS() as ddgs:
        results = list(ddgs.text(f"recipe {query}", max_results=3))
    return [result['body'] for result in results]

def classify_query(query: str, llm: ChatOpenAI) -> bool:
    """Determine if a query is cooking-related."""
    response = llm.invoke([HumanMessage(content=QUERY_CLASSIFIER_PROMPT.format(query=query))])
    return response.content.lower().strip() == 'true'

def needs_research(query: str, llm: ChatOpenAI) -> bool:
    """Determine if research is needed to answer the query."""
    response = llm.invoke([HumanMessage(content=RESEARCH_NEEDED_PROMPT.format(query=query))])
    return response.content.lower().strip() == 'true'

def parse_recipe(research_results: List[str], llm: ChatOpenAI) -> Optional[Recipe]:
    """Parse research results into a structured recipe."""
    try:
        response = llm.invoke([HumanMessage(content=RECIPE_PARSER_PROMPT.format(
            research_results="\n".join(research_results)
        ))])
        
        # Clean the response content to ensure valid JSON
        content = response.content.strip()
        if content.startswith('```json'):
            content = content[7:]
        if content.endswith('```'):
            content = content[:-3]
        content = content.strip()
        
        recipe_dict = json.loads(content)
        return Recipe(**recipe_dict)
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Error parsing recipe: {str(e)}")
        return None

def generate_cooking_response(
    query: str,
    recipe: Optional[Recipe],
    toolset: ToolSet,
    llm: ChatOpenAI
) -> str:
    """Generate the final response to a cooking query."""
    try:
        can_cook = True if recipe and toolset.can_cook_recipe(recipe) else False
        
        if recipe:
            # We have a specific recipe to share
            response = llm.invoke([HumanMessage(content=FINAL_RESPONSE_PROMPT.format(
                query=query,
                recipe=recipe.model_dump_json(),
                can_cook=can_cook,
                available_tools=toolset.available_tools
            ))])
        else:
            # General cooking advice
            if "how to cook" in query.lower():
                # For general "how to cook X" queries, provide basic cooking instructions
                response = llm.invoke([HumanMessage(content=f"""You are a helpful cooking assistant providing basic cooking instructions.
The user wants to know how to cook {query.lower().replace('how to cook ', '')}.
Provide clear, step-by-step instructions that use their available tools: {toolset.available_tools}.
Format your response in markdown and include:
1. Basic ingredients needed
2. Preparation steps
3. Cooking method
4. Tips for best results
5. How to tell when it's done

Keep the instructions simple and suitable for beginners.""")])
            else:
                # For other general cooking queries
                response = llm.invoke([HumanMessage(content=GENERAL_COOKING_PROMPT.format(query=query))])
        
        if not response or not response.content:
            raise ValueError("Failed to generate response content")
            
        return response.content.strip()
        
    except Exception as e:
        logger.error(f"Error generating cooking response: {str(e)}")
        raise

def create_tools(llm: ChatOpenAI) -> List[Tool]:
    """Create the tool set for the cooking assistant."""
    return [
        Tool(
            name="classify_query",
            func=lambda q: classify_query(q, llm),
            description="Determine if a query is cooking-related"
        ),
        Tool(
            name="needs_research",
            func=lambda q: needs_research(q, llm),
            description="Determine if research is needed to answer the query"
        ),
        Tool(
            name="search_recipes",
            func=search_recipes,
            description="Search for recipes and cooking information"
        ),
        Tool(
            name="parse_recipe",
            func=lambda r: parse_recipe(r, llm),
            description="Parse research results into a structured recipe"
        ),
        Tool(
            name="generate_response",
            func=lambda q, r, t: generate_cooking_response(q, r, t, llm),
            description="Generate the final response to a cooking query"
        )
    ] 