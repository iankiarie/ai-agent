from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class AIRequest(BaseModel):
    user_id: int
    query: str
    chiller_id: Optional[int] = None
    history: Optional[List[Dict[str, Any]]] = None  # Add this line

class AIResponse(BaseModel):
    text: str
    isReport: bool = False
    isTable: bool = False
    isChart: bool = False
    chartConfig: Optional[dict] = Field(default_factory=dict)
    data: list = Field(default_factory=list)
    analysis: dict = Field(default_factory=dict)
    formats: dict = Field(default_factory=dict)


