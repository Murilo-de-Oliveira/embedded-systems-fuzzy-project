from fastapi import APIRouter, Depends
from app.controllers.simulation import DataCenterSimulation
from app.api.schemas import SimulationResult
from app.core.config import get_simulation

router = APIRouter()


@router.get("/simulate-24h", response_model=list[SimulationResult])
def simulate_24h():
    sim = DataCenterSimulation()
    result = sim.run()
    return result

@router.get("/step", response_model=SimulationResult)
def simulate_step(sim = Depends(get_simulation)):
    return sim.step()

@router.post("/reset")
def reset_sim(sim = Depends(get_simulation)):
    sim.reset()
    return {"status": "ok", "msg": "Simulação reiniciada"}