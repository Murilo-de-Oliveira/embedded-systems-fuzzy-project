from fastapi import APIRouter, Depends
from app.controllers.simulation import DataCenterSimulation
from app.api.schemas import SimulationResult
from app.core.config import get_simulation
from app.api.schemas import FuzzyDashboardInput
from app.api.schemas import FuzzyDashboardOutput
from app.controllers.fuzzy_controller import FuzzyController
import matplotlib.pyplot as plt
import io
import base64
import matplotlib
matplotlib.use("Agg")

router = APIRouter()

def fig_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")

def plot_mf(variable, value, title: str):
    """
    Gera gráfico de pertinência + linha vertical do valor atual.
    """
    fig, ax = plt.subplots(figsize=(6, 4))
    for label, term in variable.terms.items():
        ax.plot(variable.universe, term.mf, label=label, linewidth=2)

    ax.axvline(value, color="red", linestyle="--", linewidth=2)

    ax.set_title(title)
    ax.set_xlabel("Valor")
    ax.set_ylabel("Grau de pertinência")
    ax.legend()
    ax.grid(True, alpha=0.3)

    return fig_to_base64(fig)

def plot_rule_strengths(strengths):
    labels = [s["rule"] for s in strengths]
    values = [s["strength"] for s in strengths]

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.bar(range(len(values)), values)

    ax.set_xticks(range(len(values)))
    ax.set_xticklabels(labels, rotation=90)

    ax.set_ylim(0, 1)
    ax.set_title("Ativação das Regras Fuzzy")
    ax.set_ylabel("Força (0 a 1)")

    return fig_to_base64(fig)

@router.get("/simulate-24h", response_model=list[SimulationResult])
def simulate_24h():
    sim = DataCenterSimulation()
    resultados = sim.run()
    return resultados

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
        delta_erro=data.delta,
        temp_externa=data.temp_externa,
        carga_termica=data.carga_termica
    )

    erro_plot = plot_mf(controller.erro, data.erro, "Pertinência — ERRO")
    delta_plot = plot_mf(controller.delta_erro, data.delta, "Pertinência — DELTA ERRO")
    temp_plot = plot_mf(controller.temp_externa, data.temp_externa, "Pertinência — TEMP EXTERNA")
    carga_plot = plot_mf(controller.carga_termica, data.carga_termica, "Pertinência — CARGA TÉRMICA")
    pcrac_plot = plot_mf(controller.p_crac, p, "Saída Fuzzy — P_CRAC")

    return {
        "p_crac": p,
        "erro_plot": erro_plot,
        "delta_plot": delta_plot,
        "temp_plot": temp_plot,
        "carga_plot": carga_plot,
        "pcrac_plot": pcrac_plot,
    }
