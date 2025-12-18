from pydantic import BaseModel, Field
from typing import List, Optional, Literal

# --- EXISTING MODELS ---
class CountryMetadata(BaseModel):
    country: str
    iso_code: Optional[str] = Field(None, description="3-letter ISO code")
    region: Optional[str]
    income_group: Optional[str] = Field(None, description="World Bank Income Group")
    eqx_year: int = 2025
    eqx_rank: Optional[int]
    other_countries_mentioned: List[str] = Field(default_factory=list)
    document_type: str = "country_analysis"
    source: str = "EQx2025"
    themes: List[str] = Field(default_factory=list)
    trend_direction: Optional[str] = Field(None)

# --- NEW ROUTER MODELS ---

class QueryFilters(BaseModel):
    """Specific filters extracted from the user query."""
    income_group: Optional[str] = Field(None, description="e.g., 'High Income', 'Upper Middle Income'")
    region: Optional[str] = Field(None, description="e.g., 'East Asia', 'Europe'")
    themes: List[str] = Field(default_factory=list, description="Specific themes like 'Governance', 'Trade'")

class QueryIntent(BaseModel):
    category: Literal["specific_country", "comparison", "general_concept"] = Field(
        ..., description="The broad category of the user's intent."
    )
    
    # 1. Complexity (Determines if we need a 'thinking' model later)
    complexity: Literal["low", "medium", "high"] = Field(
        "low", description="High complexity requires multi-step reasoning or synthesis."
    )
    
    # 2. Visualization Needs
    chart_needed: bool = Field(
        False, description="True if the user asks for trends, comparisons, or data that benefits from a chart."
    )
    
    # 3. Data Source Routing
    requires_sql_lookup: bool = Field(
        False, description="True if the query asks for precise rankings, raw numbers, or aggregations (e.g., 'Top 5 countries')."
    )
    
    # 4. Retrieval Parameters
    target_countries: List[str] = Field(
        default_factory=list, description="Standardized country names (e.g., 'PRC' -> 'China')."
    )
    filters: QueryFilters = Field(
        default_factory=QueryFilters, description="Structured filters to apply to the vector search."
    )