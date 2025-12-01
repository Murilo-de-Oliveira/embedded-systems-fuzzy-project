# app/services/simulation.py
import numpy as np
import math
import json
from app.controllers.fuzzy_controller import FuzzyController
from app.controllers.physical_model import modelo_fisico
from app.controllers.mqtt_broker import MQTTBroker
from typing import List

class DataCenterSimulation:
    def __init__(self, setpoint=22.0, mqtt_enabled=True, mqtt_use_websocket=False):
        self.setpoint = setpoint
        self.controller = FuzzyController()

        self.mqtt_enabled = mqtt_enabled
        self.mqtt = None

        if self.mqtt_enabled:
            self.mqtt = MQTTBroker(use_websocket=mqtt_use_websocket)
            self.mqtt.start()

        # buffers para alertas
        self._p_crac_history = []
        self._p_crac_window = 10
        self._p_crac_threshold = 90.0

        self._temp_history = []
        self._oscillation_threshold_temp = 1.5

    # ------------------ perfis externos ------------------

    def _temp_externa_profile(self, t):
        Tbase = 20
        A = 10
        ruido = np.random.normal(0, 0.5)
        return Tbase + A * math.sin(2 * math.pi * t / 1440) + ruido

    def _carga_termica_profile(self, t):
        if 0 <= t < 300:
            base = 35
        elif 300 <= t < 1000:
            base = 70
        else:
            base = 50
        return np.clip(base + np.random.uniform(-5, 5), 0, 100)

    # ------------------ publicação ------------------

    def _publish_state(self, minute, payload):
        if self.mqtt and self.mqtt.connected:
            self.mqtt.publish_json(self.mqtt.TOPIC_CONTROL, {
                "minuto": minute,
                "p_crac": payload["p_crac"],
                "erro": payload["erro"],
                "temp_atual": payload["temp_atual"],
                "carga_termica": payload["carga_termica"],
            })
            self.mqtt.publish_json(self.mqtt.TOPIC_TEMP, {
                "minuto": minute,
                "temp_atual": payload["temp_atual"]
            })

    # ------------------ alertas ------------------

    def _check_alerts(self, minute, temp_atual, p_crac):
        alerts = []

        if temp_atual > 26.0:
            alerts.append(f"ALTA_TEMP minuto={minute} temp={temp_atual:.2f}")
        elif temp_atual < 18.0:
            alerts.append(f"BAIXA_TEMP minuto={minute} temp={temp_atual:.2f}")

        # potência prolongada
        self._p_crac_history.append(p_crac)
        if len(self._p_crac_history) > self._p_crac_window:
            self._p_crac_history.pop(0)

        if len(self._p_crac_history) == self._p_crac_window and all(v >= self._p_crac_threshold for v in self._p_crac_history):
            alerts.append(f"POTENCIA_PROLONGADA minutos={self._p_crac_window}")

        # oscilações
        self._temp_history.append(temp_atual)
        if len(self._temp_history) > 5:
            deltas = [abs(self._temp_history[i] - self._temp_history[i-1]) for i in range(1, len(self._temp_history))]
            if max(deltas) >= self._oscillation_threshold_temp:
                alerts.append(f"OSCILACAO_TEMP max_delta={max(deltas):.2f}")

        # publish
        for a in alerts:
            if self.mqtt and self.mqtt.connected:
                self.mqtt.publish_json(self.mqtt.TOPIC_ALERT, {"alert": a})
            else:
                print("[SIM ALERTA]", a)

    # ------------------ simulação principal ------------------

    def run(self):
        results = []
        temp_atual = 22.0
        erro_anterior = 0.0

        for minute in range(1440):
            temp_externa = self._temp_externa_profile(minute)
            carga_termica = self._carga_termica_profile(minute)

            erro = temp_atual - self.setpoint
            delta = erro - erro_anterior
            erro_anterior = erro

            # fuzzy correto
            p_crac = self.controller.calcular(
                erro=erro,
                delta=delta,
                temp_externa=temp_externa,
                carga_termica=carga_termica
            )

            # modelo físico
            temp_atual = modelo_fisico(temp_atual, p_crac, carga_termica, temp_externa)

            payload = {
                "minuto": minute,
                "temp_atual": temp_atual,
                "erro": erro,
                "delta": delta,
                "p_crac": p_crac,
                "carga_termica": carga_termica,
                "temp_externa": temp_externa,
            }

            self._publish_state(minute, payload)
            self._check_alerts(minute, temp_atual, p_crac)

            results.append(payload)

        # ENCERRA MQTT CORRETAMENTE
        if self.mqtt:
            self.mqtt.stop()

        return results


class DataCenterSimStep:
    def __init__(self, setpoint=22.0, mqtt_enabled=False, mqtt_use_websocket=False):
        self.setpoint = setpoint
        self.minuto_atual = 0
        self.temp_atual = 22.0
        self.erro_anterior = 0.0
        self.controller = FuzzyController()

        self.mqtt_enabled = mqtt_enabled
        self.mqtt = None
        if mqtt_enabled:
            self.mqtt = MQTTBroker(use_websocket=mqtt_use_websocket)
            self.mqtt.start()

        self._p_crac_history = []
        self._p_crac_window = 10
        self._p_crac_threshold = 90.0

        self._temp_history = []
        self._oscillation_threshold_temp = 1.5

    def step(self):
        t = self.minuto_atual
        temp_externa = self._temp_externa_profile(t)
        carga_termica = self._carga_termica_profile(t)

        erro = self.temp_atual - self.setpoint
        delta = erro - self.erro_anterior
        self.erro_anterior = erro

        p_crac = self.controller.calcular(
            erro=erro,
            delta=delta,
            temp_externa=temp_externa,
            carga_termica=carga_termica,
        )

        self.temp_atual = modelo_fisico(self.temp_atual, p_crac, carga_termica, temp_externa)

        payload = {
            "minuto": t,
            "temp_atual": self.temp_atual,
            "erro": erro,
            "delta": delta,
            "p_crac": p_crac,
            "carga_termica": carga_termica,
            "temp_externa": temp_externa,
        }

        # publicar e alertas igual...
        # (mesmo que no run())
        
        self.minuto_atual += 1
        if self.minuto_atual >= 1440:
            self.minuto_atual = 0

        return payload
