import numpy as np
import skfuzzy as fuzzy
from skfuzzy import control as ctrl

class FuzzyController:
    def __init__(self):
        # Variáveis de entrada
        self.erro = ctrl.Antecedent(np.arange(-10, 11, 0.1), 'erro')
        self.delta_erro = ctrl.Antecedent(np.arange(-5, 6, 0.1), 'delta_erro')
        self.temp_externa = ctrl.Antecedent(np.arange(10, 36, 1), 'temp_externa')
        self.carga_termica = ctrl.Antecedent(np.arange(0, 101, 1), 'carga_termica')

        # Variáveis de saída
        self.p_crac = ctrl.Consequent(np.arange(0, 101, 1), 'p_crac')

        # 2. Configuração das Funções e Regras
        self._set_membership_functions()
        self._set_rules()

        # 3. CONSTRUÇÃO ÚNICA (Crucial: fazemos isto aqui, não no loop)
        self.sistema_controle = ctrl.ControlSystem(self.regras)
        self.simulador = ctrl.ControlSystemSimulation(self.sistema_controle)

    def _set_membership_functions(self):
        # --- ENTRADAS ---
        # ERRO: Aumentei um pouco a zona "Zero" para evitar reações a 0.5°C
        self.erro['MN'] = fuzzy.trapmf(self.erro.universe, [-10, -10, -4, -2])
        self.erro['NS'] = fuzzy.trimf(self.erro.universe, [-3, -1.2, 0])
        self.erro['ZE'] = fuzzy.trimf(self.erro.universe, [-0.7, 0, 0.7])
        self.erro['PS'] = fuzzy.trimf(self.erro.universe, [0, 1.2, 3])
        self.erro['MP'] = fuzzy.trapmf(self.erro.universe, [2, 4, 10, 10])

        # ---------- DELTA ERRO ----------
        self.delta_erro['N'] = fuzzy.trapmf(self.delta_erro.universe, [-5, -5, -1, -0.1])
        self.delta_erro['Z'] = fuzzy.trimf(self.delta_erro.universe, [-0.8, 0, 0.8])
        self.delta_erro['P'] = fuzzy.trapmf(self.delta_erro.universe, [0.1, 1, 5, 5])

        # ---------- TEMP. EXTERNA ----------
        self.temp_externa['Fria']   = fuzzy.trimf(self.temp_externa.universe, [10, 10, 18])
        self.temp_externa['Media']  = fuzzy.trimf(self.temp_externa.universe, [17, 22, 29])
        self.temp_externa['Quente'] = fuzzy.trimf(self.temp_externa.universe, [27, 35, 35])

        # ---------- CARGA TÉRMICA ----------
        self.carga_termica['Baixa'] = fuzzy.trimf(self.carga_termica.universe, [0, 0, 35])
        self.carga_termica['Media'] = fuzzy.trimf(self.carga_termica.universe, [20, 50, 80])
        self.carga_termica['Alta']  = fuzzy.trimf(self.carga_termica.universe, [60, 100, 100])

        # ---------- SAÍDA ----------
        self.p_crac['MB'] = fuzzy.trimf(self.p_crac.universe, [0, 0, 35])
        self.p_crac['B']  = fuzzy.trimf(self.p_crac.universe, [20, 35, 50])
        self.p_crac['M']  = fuzzy.trimf(self.p_crac.universe, [40, 55, 70])
        self.p_crac['A']  = fuzzy.trimf(self.p_crac.universe, [60, 75, 90])
        self.p_crac['MA'] = fuzzy.trimf(self.p_crac.universe, [80, 100, 100])

    def _set_rules(self):
        e  = self.erro
        de = self.delta_erro
        t  = self.temp_externa
        q  = self.carga_termica
        p  = self.p_crac

        regras = []

        # ---------------------------------------
        # 1) ERROS GRANDES (resposta forte)
        # ---------------------------------------
        regras.append(ctrl.Rule(e['MP'], p['MA']))
        regras.append(ctrl.Rule(e['MN'], p['MB']))

        # ---------------------------------------
        # 2) AJUSTE FINO (erro leve)
        # ---------------------------------------

        # Levemente quente
        regras.append(ctrl.Rule(e['PS'] & de['P'], p['M']))
        regras.append(ctrl.Rule(e['PS'] & de['Z'], p['M']))
        regras.append(ctrl.Rule(e['PS'] & de['N'], p['M']))

        # Levemente frio
        regras.append(ctrl.Rule(e['NS'] & de['N'], p['B']))
        regras.append(ctrl.Rule(e['NS'] & de['Z'], p['M']))
        regras.append(ctrl.Rule(e['NS'] & de['P'], p['M']))

        # ---------------------------------------
        # 3) ERRO PRATICAMENTE ZERO (feedforward)
        # ---------------------------------------
        regras.append(ctrl.Rule(e['ZE'] & t['Fria'],   p['B']))
        regras.append(ctrl.Rule(e['ZE'] & t['Media'],  p['M']))
        regras.append(ctrl.Rule(e['ZE'] & t['Quente'], p['A']))

        # Ajuste pela carga mesmo com erro leve
        regras.append(ctrl.Rule(e['ZE'] & q['Baixa'], p['B']))
        regras.append(ctrl.Rule(e['ZE'] & q['Media'], p['M']))
        regras.append(ctrl.Rule(e['ZE'] & q['Alta'],  p['A']))

        # ---------------------------------------
        # 4) CORREÇÃO PELA CARGA TÉRMICA QUANDO TEM ERRO
        # ---------------------------------------
        regras.append(ctrl.Rule(e['PS'] & q['Alta'], p['A']))
        regras.append(ctrl.Rule(e['PS'] & q['Media'], p['M']))
        regras.append(ctrl.Rule(e['PS'] & q['Baixa'], p['B']))

        regras.append(ctrl.Rule(e['NS'] & q['Alta'], p['A']))
        regras.append(ctrl.Rule(e['NS'] & q['Media'], p['M']))
        regras.append(ctrl.Rule(e['NS'] & q['Baixa'], p['B']))

        self.regras = regras

    #def build(self):
    #    self._set_membership_functions()
    #    self._set_rules()
    #    sistema_controle = ctrl.ControlSystem(self.regras)
    #    return ctrl.ControlSystemSimulation(sistema_controle)

    def calcular(self, erro, delta, temp_externa, carga_termica):
        # Usa a simulação já criada no __init__
        self.simulador.input['erro'] = erro
        self.simulador.input['delta_erro'] = delta
        self.simulador.input['temp_externa'] = temp_externa
        self.simulador.input['carga_termica'] = carga_termica
        
        try:
            self.simulador.compute()
            return float(self.simulador.output['p_crac'])
        except Exception:
            return 50.0

if __name__ == "__main__":
    controller = FuzzyController()
    # sim = controller.build()
    # controller.erro.view() # Comentado para rodar sem GUI se necessário
    print("Controlador Fuzzy Configurado com Sucesso")