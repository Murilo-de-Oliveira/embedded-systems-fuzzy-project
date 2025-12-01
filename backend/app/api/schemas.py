from pydantic import BaseModel

class SimulationResult(BaseModel):
    temperature: list[float]
    power: list[float]
    load: list[float]
    external_temp: list[float]

class FuzzyDashboardInput(BaseModel):
    erro: float
    delta: float
    temp_externa: float
    carga_termica: float

class FuzzyDashboardOutput(BaseModel):
    p_crac: float