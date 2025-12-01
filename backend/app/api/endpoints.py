from fastapi import APIRouter, Depends
from app.controllers.simulation import DataCenterSimulation
from app.api.schemas import SimulationResult
from app.core.config import get_simulation
from app.api.schemas import FuzzyDashboardInput
from app.api.schemas import FuzzyDashboardOutput
from app.controllers.fuzzy_controller import FuzzyController

router = APIRouter()

#ajustar o responde model depois
@router.get("/simulate-24h")
def simulate_24h():
    sim = DataCenterSimulation()
    data = sim.run()

    response = {
        "temperature": [d["temp_atual"] for d in data],
        "power": [d["p_crac"] for d in data],
        "load": [d["carga_termica"] for d in data],
        "external_temp": [d["temp_externa"] for d in data],
    }

    return response

@router.get("/step", response_model=SimulationResult)
def simulate_step(sim = Depends(get_simulation)):
    return sim.step()

@router.post("/reset")
def reset_sim(sim = Depends(get_simulation)):
    sim.reset()
    return {"status": "ok", "msg": "Simulação reiniciada"}


@router.post("/fuzzy/manual", response_model=FuzzyDashboardOutput)
def fuzzy_manual(data: FuzzyDashboardInput):
    controller = FuzzyController()
    p = controller.calcular(
        erro=data.erro,
        delta=data.delta,
        temp_externa=data.temp_externa,
        carga_termica=data.carga_termica
    )
    return {"p_crac": p}