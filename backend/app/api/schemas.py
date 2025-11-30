from pydantic import BaseModel

class SimulationResult(BaseModel):
    minuto: int
    temp_atual: float
    erro: float
    delta: float
    p_crac: float
    carga_termica: float
    temp_externa: float