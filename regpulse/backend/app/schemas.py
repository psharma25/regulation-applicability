"""Pydantic request/response schemas."""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ProfileIn(BaseModel):
    name: str = "My platform"
    markets: List[str] = []
    product_types: List[str] = []
    data_types: List[str] = []
    flags: List[str] = []


class ProfileOut(BaseModel):
    id: int
    name: str
    data: Dict[str, Any]

    class Config:
        from_attributes = True


class ApplicableItem(BaseModel):
    reg_id: str
    name: str
    domain: str
    url: str
    priority: str
    why: str
    emerging: bool
    change_type: Optional[str] = None


class ApplicabilityResult(BaseModel):
    profile: Dict[str, Any]
    applicable: List[ApplicableItem]
    count: int


class RoadmapRequest(BaseModel):
    reg_ids: List[str]
    profile_name: str = "My platform"


class SaveAnalysisIn(BaseModel):
    name: str
    profile: ProfileIn
    applicable: List[Dict[str, Any]]
