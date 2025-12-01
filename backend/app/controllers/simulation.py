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
        self.sim = self.controller.build()
        self.mqtt_enabled = mqtt_enabled
        self.mqtt = None
        if self.mqtt_enabled:
            self.mqtt = MQTTBroker(use_websocket=mqtt_use_websocket)
            self.mqtt.start()

        # for prolonged-power detection
        self._p_crac_history = []
        self._p_crac_window = 10  # minutos consecutivos para considerar "prolongado"
        self._p_crac_threshold = 90.0

        # for oscillation detection
        self._temp_history = []
        self._oscillation_threshold_temp = 1.5  # °C por minuto (ajustável)
        self._oscillation_threshold_power = 20.0  # % por minuto

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

    def _publish_state(self, minute, temp_atual, erro, delta, p_crac, carga_termica, temp_externa):
        payload = {
            "minuto": int(minute),
            "temp_atual": float(temp_atual),
            "erro": float(erro),
            "delta": float(delta),
            "p_crac": float(p_crac),
            "carga_termica": float(carga_termica),
            "temp_externa": float(temp_externa)
        }
        if self.mqtt and self.mqtt.connected:
            # publicar JSON nos tópicos
            self.mqtt.publish_json(self.mqtt.TOPIC_CONTROL, {
                "minuto": payload["minuto"],
                "p_crac": payload["p_crac"],
                "erro": payload["erro"],
                "carga_termica": payload["carga_termica"],
                "temp_atual": payload["temp_atual"]
            })
            self.mqtt.publish_json(self.mqtt.TOPIC_TEMP, {"minuto": payload["minuto"], "temp_atual": payload["temp_atual"]})
        else:
            # modo simulação -> já logado por mqtt.publish_json; nada a fazer
            pass

        return payload

    def _check_alerts(self, minute, temp_atual, p_crac):
        alerts = []

        # 1) temperatura crítica
        if temp_atual > 26.0:
            alerts.append(f"ALERTA_CRITICO_HIGH_TEMP minuto={minute} temp={temp_atual:.2f}")
        elif temp_atual < 18.0:
            alerts.append(f"ALERTA_CRITICO_LOW_TEMP minuto={minute} temp={temp_atual:.2f}")

        # 2) potência prolongada
        self._p_crac_history.append(p_crac)
        if len(self._p_crac_history) > self._p_crac_window:
            self._p_crac_history.pop(0)

        if len(self._p_crac_history) == self._p_crac_window and all(v >= self._p_crac_threshold for v in self._p_crac_history):
            alerts.append(f"ALERTA_POTENCIA_PROLONGADA minutos={self._p_crac_window} p_crac_media={sum(self._p_crac_history)/len(self._p_crac_history):.1f}")

        # 3) oscilações excessivas
        # manter histórico de temperaturas para detectar variações abruptas
        self._temp_history.append(temp_atual)
        if len(self._temp_history) > 5:
            # compute max delta in last 5 points
            deltas = [abs(self._temp_history[i] - self._temp_history[i-1]) for i in range(1, len(self._temp_history))]
            if max(deltas) >= self._oscillation_threshold_temp:
                alerts.append(f"ALERTA_OSCILACAO_TEMP max_delta={max(deltas):.2f}")

        # publicar alertas (JSON) se houver
        for a in alerts:
            if self.mqtt and self.mqtt.connected:
                self.mqtt.publish_json(self.mqtt.TOPIC_ALERT, {"alert": a, "minuto": minute})
            else:
                print(f"[ALERTA - SIM] {a}")

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

            # fuzzy
            # se você tiver controller.calcular, prefira usá-la
            p_crac = self.controller.calcular(erro=erro, delta=delta, temp_externa=temp_externa, carga_termica=carga_termica)

            # modelo físico
            temp_atual = modelo_fisico(temp_atual, p_crac, carga_termica, temp_externa)

            payload = self._publish_state(t, temp_atual, erro, delta, p_crac, carga_termica, temp_externa)

            # checar e publicar alertas extras
            self._check_alerts(t, temp_atual, p_crac)

            results.append(payload)

        self.mqtt.client.loop_stop()
        self.mqtt.client.disconnect()
        return results  


class DataCenterSimStep:
    def __init__(self, setpoint=22.0, mqtt_enabled=False, mqtt_use_websocket=False):
        self.setpoint = setpoint
        self.minuto_atual = 0
        self.temp_atual = 22.0
        self.erro_anterior = 0.0
        self.controller = FuzzyController()
        self.sim = self.controller.build()

        self.mqtt_enabled = mqtt_enabled
        self.mqtt = None
        if mqtt_enabled:
            self.mqtt = MQTTBroker(use_websocket=mqtt_use_websocket)
            self.mqtt.start()

        # histories
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

        self.sim.input['erro'] = erro
        self.sim.input['delta_erro'] = delta
        self.sim.input['temp_externa'] = temp_externa
        self.sim.input['carga_termica'] = carga_termica

        try:
            self.sim.compute()
            p_crac = float(self.sim.output['p_crac'])
        except Exception:
            p_crac = 50.0

        self.temp_atual = modelo_fisico(self.temp_atual, p_crac, carga_termica, temp_externa)

        payload = {
            "minuto": int(t),
            "temp_atual": float(self.temp_atual),
            "erro": float(erro),
            "delta": float(delta),
            "p_crac": float(p_crac),
            "carga_termica": float(carga_termica),
            "temp_externa": float(temp_externa),
        }

        # publicar estado
        if self.mqtt and self.mqtt.connected:
            self.mqtt.publish_json(self.mqtt.TOPIC_CONTROL, {
                "minuto": payload["minuto"],
                "p_crac": payload["p_crac"],
                "erro": payload["erro"],
                "temp_atual": payload["temp_atual"]
            })
            self.mqtt.publish_json(self.mqtt.TOPIC_TEMP, {"minuto": payload["minuto"], "temp_atual": payload["temp_atual"]})

        # checar alertas
        # temperatura crítica
        if payload["temp_atual"] > 26.0:
            if self.mqtt and self.mqtt.connected:
                self.mqtt.publish_json(self.mqtt.TOPIC_ALERT, {"alert": "ALTA_TEMPERATURA", "minuto": t, "temp": payload["temp_atual"]})
            else:
                print(f"[ALERTA - SIM] ALTA_TEMPERATURA minuto={t} temp={payload['temp_atual']:.2f}")

        if payload["temp_atual"] < 18.0:
            if self.mqtt and self.mqtt.connected:
                self.mqtt.publish_json(self.mqtt.TOPIC_ALERT, {"alert": "BAIXA_TEMPERATURA", "minuto": t, "temp": payload["temp_atual"]})
            else:
                print(f"[ALERTA - SIM] BAIXA_TEMPERATURA minuto={t} temp={payload['temp_atual']:.2f}")

        # potência prolongada
        self._p_crac_history.append(payload["p_crac"])
        if len(self._p_crac_history) > self._p_crac_window:
            self._p_crac_history.pop(0)
        if len(self._p_crac_history) == self._p_crac_window and all(v >= self._p_crac_threshold for v in self._p_crac_history):
            if self.mqtt and self.mqtt.connected:
                self.mqtt.publish_json(self.mqtt.TOPIC_ALERT, {"alert": "POTENCIA_PROLONGADA", "minuto": t})
            else:
                print(f"[ALERTA - SIM] POTENCIA_PROLONGADA minuto={t}")

        # detectar oscilações
        self._temp_history.append(payload["temp_atual"])
        if len(self._temp_history) > 5:
            deltas = [abs(self._temp_history[i] - self._temp_history[i-1]) for i in range(1, len(self._temp_history))]
            if max(deltas) >= self._oscillation_threshold_temp:
                if self.mqtt and self.mqtt.connected:
                    self.mqtt.publish_json(self.mqtt.TOPIC_ALERT, {"alert": "OSCILACAO_TEMPERATURA", "minuto": t, "max_delta": max(deltas)})
                else:
                    print(f"[ALERTA - SIM] OSCILACAO_TEMPERATURA minuto={t} max_delta={max(deltas):.2f}")

        # avançar
        self.minuto_atual += 1
        if self.minuto_atual >= 1440:
            self.minuto_atual = 0

        return payload
