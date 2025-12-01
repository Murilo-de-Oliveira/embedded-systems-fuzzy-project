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
def simulate_24h(mqtt: bool = False):
    sim = DataCenterSimulation(mqtt_enabled=mqtt, mqtt_use_websocket=False)
    results = sim.run()

    response = {
        "temperature": [r["temp_atual"] for r in results],
        "power": [r["p_crac"] for r in results],
        "load": [r["carga_termica"] for r in results],
        "external_temp": [r["temp_externa"] for r in results],
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