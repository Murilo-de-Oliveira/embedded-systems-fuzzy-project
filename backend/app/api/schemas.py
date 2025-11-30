from pydantic import BaseModel

class SimulationResult(BaseModel):
    minuto: int
    temp_atual: float
    erro: float
    delta: float
    p_crac: float
    carga_termica: float
    temp_externa: float

class FuzzyDashboardInput(BaseModel):
    erro: float
    delta: float
    temp_externa: float
    carga_termica: float

class FuzzyDashboardOutput(BaseModel):
    p_crac: float