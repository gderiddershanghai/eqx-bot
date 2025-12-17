from pydantic import BaseModel, Field
from typing import List, Optional

class CountryMetadata(BaseModel):
    country: str
    iso_code: Optional[str] = Field(None, description="3-letter ISO code")
    region: Optional[str]
    income_group: Optional[str]
    eqx_year: int = 2025
    eqx_rank: Optional[int]
    document_type: str = "country_analysis"
    source: str = "EQx2025"
    themes: List[str] = Field(default_factory=list, description="Key themes discussed, e.g., 'AI', 'Governance'")
    trend_direction: Optional[str] = Field(None, description="Overall trend: stable, improving, declining")
    