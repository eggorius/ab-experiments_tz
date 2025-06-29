from pydantic import BaseModel
from typing import List, Optional


class VariantCreate(BaseModel):
    key: str
    payload: str
    weight: float


class ExperimentCreate(BaseModel):
    key: str
    name: str
    variants: List[VariantCreate]


class StatusUpdate(BaseModel):
    is_active: bool


class VariantOut(BaseModel):
    id: int
    key: str
    payload: str
    weight: float


class ExperimentOut(BaseModel):
    id: int
    key: str
    name: str
    is_active: bool
    variants: List[VariantOut]


class ActiveExperimentOut(BaseModel):
    experiment_id: int
    experiment_key: str
    experiment_name: str
    variant: VariantOut
