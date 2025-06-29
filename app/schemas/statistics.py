from pydantic import BaseModel
from typing import List


class VariantStat(BaseModel):
    variant_id: int
    variant_key: str
    count: int
    percentage: float
    weight: float


class ExperimentStat(BaseModel):
    experiment_id: int
    experiment_key: str
    experiment_name: str
    total_devices: int
    variants: List[VariantStat]
