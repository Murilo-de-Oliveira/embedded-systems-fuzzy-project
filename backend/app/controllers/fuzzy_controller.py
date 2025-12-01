# app/controllers/fuzzy_controller.py
import numpy as np
import skfuzzy as fuzzy
import matplotlib.pyplot as plt
from skfuzzy import control as ctrl

class FuzzyController:
    """
    Controller fuzzy para potencia CRAC.
    - erro = T_atual - T_set   (range -10 .. 10)
    - delta_erro              (range -3 .. 3)
    - temp_externa            (range 10 .. 40)
    - carga_termica           (range 0 .. 100)
    - saída p_crac            (0 .. 100)
    """

    def __init__(self):
        # universos
        self.erro = ctrl.Antecedent(np.arange(-10, 10.01, 0.1), 'erro')
        self.delta_erro = ctrl.Antecedent(np.arange(-3, 3.01, 0.1), 'delta_erro')
        self.temp_externa = ctrl.Antecedent(np.arange(10, 40.01, 0.1), 'temp_externa')
        self.carga_termica = ctrl.Antecedent(np.arange(0, 100.1, 1), 'carga_termica')
        self.p_crac = ctrl.Consequent(np.arange(0, 100.1, 1), 'p_crac')

        # configurar MFs e regras
        self._set_membership_functions()
        self._set_rules()

        # construir sistema (único)
        self.system = ctrl.ControlSystem(self.regras)
        self.sim = ctrl.ControlSystemSimulation(self.system)

    def _set_membership_functions(self):
        e = self.erro
        de = self.delta_erro
        t = self.temp_externa
        q = self.carga_termica
        p = self.p_crac

        # ERRO: alta resolução na zona próxima de zero
        e['MN'] = fuzzy.trapmf(e.universe, [-10, -10, -6, -3])   # muito negativo (muito frio)
        e['NS'] = fuzzy.trimf(e.universe, [-5, -3, -1])          # negativo suave
        e['ZE'] = fuzzy.trimf(e.universe, [-2, 0, 2])            # zero (alta resolução)
        e['PS'] = fuzzy.trimf(e.universe, [1, 3, 5])             # positivo suave
        e['MP'] = fuzzy.trapmf(e.universe, [3, 6, 10, 10])       # muito positivo (muito quente)

        # DELTA_ERRO: tendência
        de['CR'] = fuzzy.trimf(de.universe, [-3, -3, -1.5])  # caindo rápido
        de['C']  = fuzzy.trimf(de.universe, [-2, -1, 0])     # caindo
        de['E']  = fuzzy.trimf(de.universe, [-0.5, 0, 0.5])  # estável
        de['S']  = fuzzy.trimf(de.universe, [0, 1, 2])       # subindo
        de['SR'] = fuzzy.trimf(de.universe, [1.5, 3, 3])     # subindo rápido

        # TEMP EXTERNA (influência feedforward)
        t['B'] = fuzzy.trimf(t.universe, [10, 10, 20])
        t['M'] = fuzzy.trimf(t.universe, [18, 25, 30])
        t['A'] = fuzzy.trimf(t.universe, [28, 35, 40])

        # CARGA TERMICA
        q['B'] = fuzzy.trimf(q.universe, [0, 0, 35])
        q['M'] = fuzzy.trimf(q.universe, [25, 50, 75])
        q['A'] = fuzzy.trimf(q.universe, [60, 80, 100])

        # SAÍDA POTÊNCIA (suave, overlap)
        p['MB'] = fuzzy.trimf(p.universe, [0, 0, 20])
        p['B']  = fuzzy.trimf(p.universe, [10, 30, 45])
        p['M']  = fuzzy.trimf(p.universe, [35, 50, 65])
        p['A']  = fuzzy.trimf(p.universe, [55, 70, 85])
        p['MA'] = fuzzy.trimf(p.universe, [80, 100, 100])

    def _set_rules(self):
        e = self.erro
        de = self.delta_erro
        t = self.temp_externa
        q = self.carga_termica
        p = self.p_crac

        regras = []

        # 1) ERROS EXTREMOS (dominam)
        regras.append(ctrl.Rule(e['MP'], p['MA']))   # muito quente -> max
        regras.append(ctrl.Rule(e['MN'], p['MB']))   # muito frio -> min

        # 2) ERROS MODERADOS com tendência (suaviza)
        # Quente (PS)
        regras.append(ctrl.Rule(e['PS'] & de['SR'], p['A']))
        regras.append(ctrl.Rule(e['PS'] & de['S'],  p['A']))
        regras.append(ctrl.Rule(e['PS'] & de['E'],  p['M']))
        regras.append(ctrl.Rule(e['PS'] & de['C'],  p['B']))
        regras.append(ctrl.Rule(e['PS'] & de['CR'], p['MB']))

        # Frio (NS)
        regras.append(ctrl.Rule(e['NS'] & de['CR'], p['MB']))
        regras.append(ctrl.Rule(e['NS'] & de['C'],  p['B']))
        regras.append(ctrl.Rule(e['NS'] & de['E'],  p['M']))
        regras.append(ctrl.Rule(e['NS'] & de['S'],  p['A']))
        regras.append(ctrl.Rule(e['NS'] & de['SR'], p['A']))

        # 3) Erro próximo de zero -> feedforward (baseline suave)
        regras.append(ctrl.Rule(e['ZE'] & t['B'], p['B']))
        regras.append(ctrl.Rule(e['ZE'] & t['M'], p['M']))
        regras.append(ctrl.Rule(e['ZE'] & t['A'], p['A']))

        regras.append(ctrl.Rule(e['ZE'] & q['B'], p['B']))
        regras.append(ctrl.Rule(e['ZE'] & q['M'], p['M']))
        regras.append(ctrl.Rule(e['ZE'] & q['A'], p['A']))

        # 4) Interação carga x erro (segunda ordem)
        regras.append(ctrl.Rule(e['PS'] & q['A'], p['A']))
        regras.append(ctrl.Rule(e['PS'] & q['M'], p['M']))
        regras.append(ctrl.Rule(e['PS'] & q['B'], p['B']))

        regras.append(ctrl.Rule(e['NS'] & q['A'], p['A']))
        regras.append(ctrl.Rule(e['NS'] & q['M'], p['M']))
        regras.append(ctrl.Rule(e['NS'] & q['B'], p['MB']))

        # 5) Temp externa influencia moderados
        regras.append(ctrl.Rule(e['PS'] & t['A'], p['A']))
        regras.append(ctrl.Rule(e['PS'] & t['M'], p['M']))
        regras.append(ctrl.Rule(e['PS'] & t['B'], p['B']))

        regras.append(ctrl.Rule(e['NS'] & t['A'], p['A']))
        regras.append(ctrl.Rule(e['NS'] & t['M'], p['M']))
        regras.append(ctrl.Rule(e['NS'] & t['B'], p['MB']))

        self.regras = regras

    def calcular(self, erro: float, delta_erro: float, temp_externa: float, carga_termica: float) -> float:
        # clamp para evitar erro "Unexpected input" e para estabilidade
        self.sim.input['erro'] = float(np.clip(erro, -10, 10))
        self.sim.input['delta_erro'] = float(np.clip(delta_erro, -3, 3))
        self.sim.input['temp_externa'] = float(np.clip(temp_externa, 10, 40))
        self.sim.input['carga_termica'] = float(np.clip(carga_termica, 0, 100))
        self.sim.compute()
        return float(self.sim.output['p_crac'])

if __name__ == "__main__":    
    fc = FuzzyController()
    cases = [
        {"erro": 0.0, "delta_erro": 0.0, "temp_externa": 22.0, "carga_termica": 40},
        {"erro": 3.0, "delta_erro": 1.0, "temp_externa": 30.0, "carga_termica": 80},
        {"erro": -4.0, "delta_erro": -1.5, "temp_externa": 12.0, "carga_termica": 10},
    ]
    for c in cases:
        p = fc.calcular(c["erro"], c["delta_erro"], c["temp_externa"], c["carga_termica"])
        print(c, "-> p_crac =", round(p, 2))

    fc.erro.view()
    #fc.delta_erro.view()
    #fc.temp_externa.view()
    #fc.carga_termica.view()
    #fc.p_crac.view()
    plt.show()

    print("Temperatura Estável (Erro = 0, ΔErro = 0)") 
    potencia = fc.calcular(erro=3.0, delta_erro=0.0, temp_externa=25.0, carga_termica=40.0) 
    print(f"Potência CRAC: {potencia}%") 
    
    print("Temperatura Acima do Setpoint (Erro Negativo)") 
    potencia = fc.calcular(erro=5, delta_erro=1, temp_externa=30, carga_termica=80) 
    print(f"Potência CRAC: {potencia:.2f}%") 
    
    print("Temperatura Abaixo do Setpoint (Erro Positivo)") 
    potencia = fc.calcular(erro=-4, delta_erro=-1, temp_externa=15, carga_termica=20) 
    print(f"Potência CRAC: {potencia:.2f}%") 
    
    print("Temperatura Subindo Rápido (ΔErro Negativo)") 
    potencia = fc.calcular(erro=5, delta_erro=-3, temp_externa=28, carga_termica=60) 
    print(f"Potência CRAC: {potencia:.2f}%") 
    
    print("Temperatura Caindo Rápido (ΔErro Positivo)") 
    potencia = fc.calcular(erro=1, delta_erro=3, temp_externa=20, carga_termica=30) 
    print(f"Potência CRAC: {potencia:.2f}%") 
    
    print("Temperatura Externa Alta e Carga Térmica Alta") 
    potencia = fc.calcular(erro=13, delta_erro=0, temp_externa=35, carga_termica=90) 
    print(f"Potência CRAC: {potencia:.2f}%") 
    
    print("Temperatura Externa Baixa e Carga Térmica Baixa") 
    potencia = fc.calcular(erro=-12, delta_erro=0, temp_externa=10, carga_termica=10) 
    print(f"Potência CRAC: {potencia:.2f}%") 