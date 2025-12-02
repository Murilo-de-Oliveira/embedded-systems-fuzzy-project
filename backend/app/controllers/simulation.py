import numpy as np
from app.controllers.fuzzy_controller import FuzzyController
from app.controllers.physical_model import modelo_fisico
from app.controllers.mqtt_broker import MQTTBroker

class DataCenterSimulation:
    """Compatibility wrapper that produces a full-series simulation by
    repeatedly calling `DataCenterSimStep.step()`.
    """
    def __init__(self, setpoint=22.0):
        self.stepper = DataCenterSimStep(setpoint=setpoint)

    def run(self, minutes: int = 1440):
        results = []
        for _ in range(minutes):
            results.append(self.stepper.step())
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

        # MQTT
        self.mqtt = MQTTBroker()
        self.mqtt.connect()
        self.mqtt.start_loop()  # essencial para envio de mensagens

        # Contadores para alertas prolongados
        self.crac_max_count = 0
        self.last_alert_temp = None
        self.last_alert_osc = None

    def _temp_externa_profile(self, t):
        Tbase = 20
        A = 10
        Ts = 1440
        ruido = np.random.normal(0, 0.5)
        return Tbase + A * np.sin(2 * np.pi * t / Ts) + ruido

    def _carga_termica_profile(self, t):
        if 0 <= t < 300:
            base = 35
        elif 300 <= t < 1000:
            base = 70
        else:
            base = 50
        return np.clip(base + np.random.uniform(-5, 5), 0, 100)

    def step(self):
        t = self.minuto_atual

        # Perfis externos
        temp_externa = self._temp_externa_profile(t)
        carga_termica = self._carga_termica_profile(t)

        # Cálculo de erro e delta
        erro = self.temp_atual - self.setpoint
        delta = erro - self.erro_anterior
        self.erro_anterior = erro

        # Controle Fuzzy
        try:
            p_crac = self.sim.calcular(erro, delta, temp_externa, carga_termica)
        except Exception:
            p_crac = 50.0

        # Atualiza temperatura pelo modelo físico
        self.temp_atual = modelo_fisico(self.temp_atual, p_crac, carga_termica, temp_externa)

        # --- ALERTAS AUTOMÁTICOS ---

        # Temperatura crítica
        if self.temp_atual > 26.0:
            if self.last_alert_temp != "alta":
                msg = f"ALERTA CRITICO: Alta Temperatura {self.temp_atual:.2f}C"
                self.mqtt.publish(self.mqtt.TOPIC_ALERT, msg)
                print(f">>> {msg}")
                self.last_alert_temp = "alta"
        elif self.temp_atual < 18.0:
            if self.last_alert_temp != "baixa":
                msg = f"ALERTA CRITICO: Baixa Temperatura {self.temp_atual:.2f}C"
                self.mqtt.publish(self.mqtt.TOPIC_ALERT, msg)
                print(f">>> {msg}")
                self.last_alert_temp = "baixa"
        else:
            self.last_alert_temp = None

        if p_crac >= 100:
            self.crac_max_count += 1
        else:
            self.crac_max_count = 0

        if self.crac_max_count >= 10:
            msg = "ALERTA: Potência CRAC máxima por tempo prolongado!"
            self.mqtt.publish(self.mqtt.TOPIC_ALERT, msg)
            print(f">>> {msg}")

        if abs(delta) > 5:
            if self.last_alert_osc != t:
                msg = f"ALERTA: Oscilação excessiva detectada! Delta={delta:.2f}"
                self.mqtt.publish(self.mqtt.TOPIC_ALERT, msg)
                print(f">>> {msg}")
                self.last_alert_osc = t

        # Publica estado atual e controle
        self.mqtt.publish(self.mqtt.TOPIC_TEMP, f"{self.temp_atual:.2f}")
        self.mqtt.publish(self.mqtt.TOPIC_CONTROL, f"{p_crac:.2f}")

        # Print de status atualizado
        print(f">>> STATUS: minuto={t} temp={self.temp_atual:.2f}C p_crac={p_crac:.2f}")

        # Avança 1 minuto
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
        self.crac_max_count = 0
        self.last_alert_temp = None
        self.last_alert_osc = None
