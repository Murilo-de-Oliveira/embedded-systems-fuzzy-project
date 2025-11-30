#import random
#import time
#import numpy as np
#from app.controllers.fuzzy_controller import FuzzyController, modelo_fisico

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import router

app = FastAPI(title="DataCenter Fuzzy API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/v1")

"""
def run_simulation():
    setpoint = 22.0
    temp_atual = 22.0

    erro_anterior = 0.0

    temp_externa = 25.0
    carga_termica = 40.0

    fuzzy_sim = FuzzyController().build()

    print("--- Simulação do Data Center ---")

    try:
        while True:
            #Erro
            erro_atual = temp_atual - setpoint
            delta = erro_atual - erro_anterior
            erro_anterior = erro_anterior

            #Perturbação
            carga_termica = np.clip(carga_termica + random.uniform(-2, 2), 0, 100)
            temp_externa = np.clip(temp_externa + random.uniform(-0.5, 0.5), 10, 35)

            #Fuzzy input
            fuzzy_sim.input['erro'] = erro_atual
            fuzzy_sim.input['delta_erro'] = delta
            fuzzy_sim.input['temp_ext'] = temp_externa
            fuzzy_sim.input['carga_termica'] = carga_termica

            try:
                fuzzy_sim.compute()
                p_crac = fuzzy_sim.output['p_crac']
            except Exception:
                p_crac = 50.0

            temp_atual = modelo_fisico(temp_atual, p_crac, carga_termica, temp_externa)

            print(
                f"T={temp_atual:.2f}°C | Erro={erro_atual:.2f} | "
                f"CRAC={p_crac:.1f}% | Carga={carga_termica:.1f}% | Text={temp_externa:.1f}°C"
            )

            time.sleep(1)
    
    except KeyboardInterrupt:
        print("s\Simulação encerrada")

if __name__ == "__main__":
    run_simulation()
"""