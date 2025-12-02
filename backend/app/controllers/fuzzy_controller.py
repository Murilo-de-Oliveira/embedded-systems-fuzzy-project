import logging
import numpy as np
import skfuzzy as fuzzy
from skfuzzy import control as ctrl

class FuzzyController:
    """
    Fuzzy AGRESSIVO para controle de CRAC.
    Mantém temperatura extremamente perto do setpoint (22°C).
    """

    def __init__(self):
        # Universos
        self.erro = ctrl.Antecedent(np.arange(-10, 10.01, 0.1), "erro")
        self.delta_erro = ctrl.Antecedent(np.arange(-3, 3.01, 0.1), "delta_erro")
        self.temp_externa = ctrl.Antecedent(np.arange(10, 35.01, 0.1), "temp_externa")
        self.carga_termica = ctrl.Antecedent(np.arange(0, 100.01, 1), "carga_termica")
        self.p_crac = ctrl.Consequent(np.arange(0, 100.1, 1), "p_crac")

        self._set_membership_functions()
        self._set_rules()

        self.system = ctrl.ControlSystem(self.regras)
        self.sim = ctrl.ControlSystemSimulation(self.system)
    def _set_membership_functions(self):
        e = self.erro
        de = self.delta_erro
        t = self.temp_externa
        q = self.carga_termica
        p = self.p_crac

        # ERRO
        e["MN"] = fuzzy.trapmf(e.universe, [-10, -10, -6, -3])
        e["NS"] = fuzzy.trimf(e.universe, [-5, -3, -1])
        e["ZE"] = fuzzy.trimf(e.universe, [-0.8, 0, 0.8]) 
        e["PS"] = fuzzy.trimf(e.universe, [1, 3, 5])
        e["MP"] = fuzzy.trapmf(e.universe, [3, 6, 10, 10])

        # DELTA_ ERRO
        de["CR"] = fuzzy.trimf(de.universe, [-3, -3, -1.5])
        de["C"] = fuzzy.trimf(de.universe, [-2, -1, 0])
        de["E"] = fuzzy.trimf(de.universe, [-0.4, 0, 0.4])
        de["S"] = fuzzy.trimf(de.universe, [0, 1, 2])
        de["SR"] = fuzzy.trimf(de.universe, [1.5, 3, 3])

        # TEMP EXTERNA
        t["B"] = fuzzy.trimf(t.universe, [10, 10, 20])
        t["M"] = fuzzy.trimf(t.universe, [18, 25, 30])
        t["A"] = fuzzy.trimf(t.universe, [28, 35, 35])

        # CARGA TÉRMICA
        q["B"] = fuzzy.trimf(q.universe, [0, 0, 35])
        q["M"] = fuzzy.trimf(q.universe, [25, 50, 75])
        q["A"] = fuzzy.trimf(q.universe, [60, 100, 100])

        # SAÍDA – MAIS AGRESSIVA
        p["MB"] = fuzzy.trimf(p.universe, [0, 0, 15])
        p["B"] = fuzzy.trimf(p.universe, [10, 25, 40])
        p["M"] = fuzzy.trimf(p.universe, [35, 55, 75])
        p["A"] = fuzzy.trimf(p.universe, [65, 80, 95])
        p["MA"] = fuzzy.trimf(p.universe, [90, 100, 100])

    # ---------------------------------------------------------
    # REGRAS — CONTROLADOR AGRESSIVO
    # ---------------------------------------------------------
    def _set_rules(self):
        e = self.erro
        de = self.delta_erro
        t = self.temp_externa
        q = self.carga_termica
        p = self.p_crac

        regras = []

        # ERROS EXTREMOS
        regras.append(ctrl.Rule(e["MP"], p["MA"]))
        regras.append(ctrl.Rule(e["MN"], p["MB"]))

        # ERROS POSITIVOS (muito quente)
        regras.append(ctrl.Rule(e["PS"] & de["SR"], p["MA"]))
        regras.append(ctrl.Rule(e["PS"] & de["S"], p["A"]))
        regras.append(ctrl.Rule(e["PS"] & de["E"], p["A"]))
        regras.append(ctrl.Rule(e["PS"] & de["C"], p["M"]))
        regras.append(ctrl.Rule(e["PS"] & de["CR"], p["B"]))

        # ERROS NEGATIVOS (muito frio)
        regras.append(ctrl.Rule(e["NS"] & de["CR"], p["MB"]))
        regras.append(ctrl.Rule(e["NS"] & de["C"], p["MB"]))
        regras.append(ctrl.Rule(e["NS"] & de["E"], p["B"]))
        regras.append(ctrl.Rule(e["NS"] & de["S"], p["M"]))
        regras.append(ctrl.Rule(e["NS"] & de["SR"], p["A"]))

        # FEEDFORWARD (muito reforçado)
        regras.append(ctrl.Rule(e["ZE"] & q["A"], p["A"]))
        regras.append(ctrl.Rule(e["ZE"] & q["M"], p["M"]))
        regras.append(ctrl.Rule(e["ZE"] & q["B"], p["B"]))

        regras.append(ctrl.Rule(e["ZE"] & t["A"], p["A"]))
        regras.append(ctrl.Rule(e["ZE"] & t["M"], p["M"]))
        regras.append(ctrl.Rule(e["ZE"] & t["B"], p["B"]))

        # Interações combinadas
        regras.append(ctrl.Rule(e["PS"] & q["A"], p["MA"]))
        regras.append(ctrl.Rule(e["PS"] & t["A"], p["MA"]))

        self.regras = regras

    def calcular(self, erro, delta_erro, temp_externa, carga_termica):
        sim = ctrl.ControlSystemSimulation(self.system)

        sim.input["erro"] = float(np.clip(erro, -10, 10))
        sim.input["delta_erro"] = float(np.clip(delta_erro, -3, 3))
        sim.input["temp_externa"] = float(np.clip(temp_externa, 10, 40))
        sim.input["carga_termica"] = float(np.clip(carga_termica, 0, 100))

        try:
            sim.compute()
        except Exception as exc:
            logging.warning("FuzzyController.compute() failed: %s", exc)
            return 50.0

        try:
            return float(sim.output["p_crac"])
        except KeyError:
            if sim.output:
                first_val = next(iter(sim.output.values()))
                return float(first_val)
            return 50.0
