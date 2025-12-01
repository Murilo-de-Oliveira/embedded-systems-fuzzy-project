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
        A = 5
        Ts = 1440

        ruido = np.random.normal(0, 0.5)
        return Tbase + A * math.sin(2 * math.pi * t / Ts) + ruido

    def _carga_termica_profile(self, t):
        """
        Perfil típico de Data Center:
        - madrugada → 30–40%
        - horário comercial → 60–80%
        - fim do dia → 50%
        """
        if 0 <= t < 300:      # madrugada
            base = 35
        elif 300 <= t < 1000: # horário comercial
            base = 70
        else:                 # fim do dia
            base = 50
    
        return np.clip(base + np.random.uniform(-5, 5), 0, 100)
    
    def _filtro(self, value, filt, alpha):
        """Filtro exponencial simples."""
        if filt is None:
            return value
        return alpha * value + (1 - alpha) * filt

    def run(self):
        results = []

        temp_atual = 22.0
        erro_anterior = 0.0

        #1440 minutos = 24 horas
        for t in range(1440):
            #Perfis externos
            temp_externa_raw = self._temp_externa_profile(t)
            carga_termica_raw = self._carga_termica_profile(t)

            #temp_externa_raw = 27
            #carga_termica_raw = 20

            self.temp_ext_f = self._filtro(temp_externa_raw, self.temp_ext_f, 0.15)
            self.carga_f = self._filtro(carga_termica_raw, self.carga_f, 0.15)

            temp_externa = self.temp_ext_f
            carga_termica = self.carga_f

            #Erro
            erro = temp_atual - self.setpoint
            delta = erro - erro_anterior
            erro_anterior = erro

            #try:
            #    p_crac = self.sim.calcular(erro, delta, temp_externa, carga_termica)
            #except:
            #    p_crac = 50.0

            p_crac_raw = self.sim.calcular(erro, delta, temp_externa, carga_termica)

            self.p_crac_f = self._filtro(p_crac_raw, self.p_crac_f, 0.10)
            p_crac = self.p_crac_f

            #p_crac = self.sim.calcular(0, 0, temp_externa, carga_termica)

            # 4. Modelo físico
            temp_atual = modelo_fisico(temp_atual, p_crac, carga_termica, temp_externa)

            if temp_atual > 26.0:
                msg_alerta = f"ALERTA CRITICO: Alta Temperatura {temp_atual:.2f}C"
                self.mqtt.publish(self.mqtt.TOPIC_ALERT, msg_alerta)
                print(f">>> {msg_alerta}")
            elif temp_atual < 18.0:
                msg_alerta = f"ALERTA CRITICO: Baixa Temperatura {temp_atual:.2f}C"
                self.mqtt.publish(self.mqtt.TOPIC_ALERT, msg_alerta)
                print(f">>> {msg_alerta}")

            self.mqtt.publish(self.mqtt.TOPIC_TEMP, f"{temp_atual:.2f}")
            self.mqtt.publish(self.mqtt.TOPIC_CONTROL, f"{p_crac:.2f}")

            # 5. Salvar resultado
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

    def _temp_externa_profile(self, t):
        Tbase = 20
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
