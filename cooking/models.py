from typing import List, Optional
from pydantic import BaseModel, Field, validator

class CookingQuery(BaseModel):
    """Input query model."""
    query: str = Field(..., description="The cooking-related query")

    @validator("query")
    def validate_query(cls, v: str) -> str:
        """Ensure query is not empty."""
        if not v.strip():
            raise ValueError("Query cannot be empty")
        return v.strip()

class CookingResponse(BaseModel):
    """API response model."""
    response: str = Field(
        ...,
        description="The generated response",
        min_length=1
    )
    relevant: bool = Field(
        ...,
        description="Whether the query was cooking-related"
    )
    reasoning_chain: List[str] = Field(
        default_factory=list,
        description="Steps taken to generate the response"
    )

    @validator("response")
    def validate_response(cls, v: str) -> str:
        """Ensure response is not empty and is a string."""
        if not isinstance(v, str):
            v = str(v)
        v = v.strip()
        if not v:
            v = "No response generated"
        return v

    @validator("reasoning_chain")
    def validate_reasoning_chain(cls, v: List[str]) -> List[str]:
        """Ensure reasoning chain contains valid strings."""
        if not v:
            return ["Direct response generated"]
        # Convert any non-string items to strings
        return [str(item).strip() for item in v if item]

    class Config:
        """Pydantic model configuration."""
        validate_assignment = True
        extra = "ignore"  # Ignore extra fields
        str_strip_whitespace = True  # Strip whitespace from strings
        arbitrary_types_allowed = True  # Allow arbitrary types

class Recipe(BaseModel):
    """Recipe model with all required fields."""
    name: str
    ingredients: List[str]
    steps: List[str]
    required_tools: List[str]
    cooking_time: str
    difficulty: str
    servings: int

    @validator("difficulty")
    def validate_difficulty(cls, v: str) -> str:
        """Ensure difficulty is one of the allowed values."""
        allowed = {"easy", "medium", "hard"}
        v = v.lower()
        if v not in allowed:
            raise ValueError(f"Difficulty must be one of: {', '.join(allowed)}")
        return v

    @validator("servings")
    def validate_servings(cls, v: int) -> int:
        """Ensure servings is positive."""
        if v < 1:
            raise ValueError("Servings must be a positive number")
        return v

    @validator("cooking_time")
    def validate_cooking_time(cls, v: str) -> str:
        """Ensure cooking time ends with 'minutes'."""
        if not v.strip().endswith("minutes"):
            v = v.strip() + " minutes"
        return v

class ToolSet(BaseModel):
    """Available kitchen tools."""
    available_tools: List[str] = [
        "Spatula",
        "Frying Pan", 
        "Little Pot", 
        "Stovetop", 
        "Whisk",
        "Knife",
        "Ladle",
        "Spoon"
    ]

    def can_cook_recipe(self, recipe: Optional[Recipe]) -> bool:
        """Check if all required tools for a recipe are available."""
        if not recipe:
            return True
        required_tools = set(tool.lower() for tool in recipe.required_tools)
        available_tools = set(tool.lower() for tool in self.available_tools)
        return required_tools.issubset(available_tools)

class AgentState(BaseModel):
    """State maintained across agent steps."""
    query: str
    is_cooking_related: bool = False
    needs_research: bool = False
    research_results: List[str] = Field(default_factory=list)
    recipe: Optional[Recipe] = None
    reasoning_chain: List[str] = Field(default_factory=list)
    final_response: Optional[str] = None 