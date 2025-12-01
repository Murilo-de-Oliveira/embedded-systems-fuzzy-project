import numpy as np
import math
from app.controllers.fuzzy_controller import FuzzyController
from app.controllers.physical_model import modelo_fisico


# ============================================================
#   SIMULAÇÃO COMPLETA (1440 minutos)
# ============================================================
class DataCenterSimulation:
    def __init__(self, setpoint=22.0):
        self.setpoint = setpoint
        self.sim = FuzzyController()

    # ---------------- Perfis Externos ----------------
    def _temp_externa_profile(self, t):
        Tbase = 22
        A = 10
        Ts = 1440
        ruido = np.random.normal(0, 0.5)
        return Tbase + A * math.sin(2 * math.pi * t / Ts) + ruido

    def _carga_termica_profile(self, t):
        if 0 <= t < 300:
            base = 35
        elif 300 <= t < 1000:
            base = 70
        else:
            base = 50

        return np.clip(base + np.random.uniform(-5, 5), 0, 100)

    def run(self):
        results = []

        temp_atual = 22.0
        erro_anterior = 0.0

        for t in range(1440):

            temp_externa = self._temp_externa_profile(t)
            carga_termica = self._carga_termica_profile(t)

            erro = temp_atual - self.setpoint
            delta = erro - erro_anterior
            erro_anterior = erro

            # --- Fuzzy ---
            try:
                p_crac = self.sim.calcular(
                    float(np.clip(erro, -10, 10)),
                    float(np.clip(delta, -3, 3)),
                    float(np.clip(temp_externa, 10, 40)),
                    float(np.clip(carga_termica, 0, 100))
                )
            except:
                p_crac = 50.0  # fallback seguro

            # --- Física ---
            temp_atual = modelo_fisico(
                temp_atual,
                p_crac,
                carga_termica,
                temp_externa
            )

            # --- Registro ---
            results.append({
                "minuto": t,
                "temp_atual": float(temp_atual),
                "erro": float(erro),
                "delta": float(delta),
                "p_crac": float(p_crac),
                "carga_termica": float(carga_termica),
                "temp_externa": float(temp_externa)
            })

        return results

class DataCenterSimStep:
    def __init__(self, setpoint=22.0):
        self.setpoint = setpoint

        # Estado interno
        self.minuto_atual = 0
        self.temp_atual = 22.0
        self.erro_anterior = 0.0

        # Controlador Fuzzy
        self.sim = FuzzyController()

    # ---------------- Perfis Externos ----------------
    def _temp_externa_profile(self, t):
        Tbase = 22
        A = 10
        Ts = 1440
        ruido = np.random.normal(0, 0.5)
        return Tbase + A * math.sin(2 * math.pi * t / Ts) + ruido

    def _carga_termica_profile(self, t):
        if 0 <= t < 300:
            base = 35
        elif 300 <= t < 1000:
            base = 70
        else:
            base = 50

        return np.clip(base + np.random.uniform(-5, 5), 0, 100)

    # ---------------- Execução por passo ----------------
    def step(self):
        t = self.minuto_atual

        temp_externa = self._temp_externa_profile(t)
        carga_termica = self._carga_termica_profile(t)

        erro = self.temp_atual - self.setpoint
        delta = erro - self.erro_anterior
        self.erro_anterior = erro

        # --- Fuzzy ---
        p_crac = self.sim.calcular(
            float(np.clip(erro, -10, 10)),
            float(np.clip(delta, -3, 3)),
            float(np.clip(temp_externa, 10, 40)),
            float(np.clip(carga_termica, 0, 100))
        )

        # --- Física ---
        self.temp_atual = modelo_fisico(
            self.temp_atual,
            p_crac,
            carga_termica,
            temp_externa
        )

        # Avança o relógio
        self.minuto_atual += 1
        if self.minuto_atual >= 1440:
            self.minuto_atual = 0

        return {
            "minuto": t,
            "temp_atual": float(self.temp_atual),
            "erro": float(erro),
            "delta": float(delta),
            "p_crac": float(p_crac),
            "carga_termica": float(carga_termica),
            "temp_externa": float(temp_externa)
        }

    def reset(self):
        self.minuto_atual = 0
        self.temp_atual = 22.0
        self.erro_anterior = 0.0
