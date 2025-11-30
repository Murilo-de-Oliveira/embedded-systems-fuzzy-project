import numpy as np
import skfuzzy as fuzzy
from skfuzzy import control as ctrl


class FuzzyController:
    def __init__(self):
        #Variáveis de entrada
        self.erro = ctrl.Antecedent(np.arange(-10, 11, 0.1), 'erro')
        self.delta_erro = ctrl.Antecedent(np.arange(-5, 6, 0.1), 'delta_erro')
        self.temp_ext = ctrl.Antecedent(np.arange(10, 36, 1), 'temp_externa')
        self.carga_termica = ctrl.Antecedent(np.arange(0, 101, 1), 'carga_termica')
        
        #Variáveis de saída
        self.p_crac = ctrl.Consequent(np.arange(0, 101, 1), 'p_crac')
        
        #Regras
        self.regras = []

    def _set_membership_functions(self):
        # Erro
        self.erro['MN'] = fuzzy.trapmf(self.erro.universe, [-10, -10, -2, -0.5])
        self.erro['ZE'] = fuzzy.trimf(self.erro.universe, [-1, 0, 1])
        self.erro['MP'] = fuzzy.trapmf(self.erro.universe, [0.5, 2, 10, 10])

        # Delta Erro
        self.delta_erro['N'] = fuzzy.trapmf(self.delta_erro.universe, [-5, -5, -1, 0])
        self.delta_erro['Z'] = fuzzy.trimf(self.delta_erro.universe, [-0.5, 0, 0.5])
        self.delta_erro['P'] = fuzzy.trapmf(self.delta_erro.universe, [0, 1, 5, 5])

        # Temp externa
        self.temp_ext['Fria'] = fuzzy.trimf(self.temp_ext.universe, [10, 10, 20])
        self.temp_ext['Media'] = fuzzy.trimf(self.temp_ext.universe, [15, 22, 30])
        self.temp_ext['Quente'] = fuzzy.trimf(self.temp_ext.universe, [25, 35, 35])

        # Carga térmica
        self.carga_termica['Baixa'] = fuzzy.trimf(self.carga_termica.universe, [0, 0, 40])
        self.carga_termica['Media'] = fuzzy.trimf(self.carga_termica.universe, [20, 50, 80])
        self.carga_termica['Alta'] = fuzzy.trimf(self.carga_termica.universe, [60, 100, 100])

        # Saída CRAC
        self.p_crac['Baixa'] = fuzzy.trimf(self.p_crac.universe, [0, 0, 40])
        self.p_crac['Media'] = fuzzy.trimf(self.p_crac.universe, [30, 50, 70])
        self.p_crac['Alta'] = fuzzy.trimf(self.p_crac.universe, [60, 100, 100])

    def _set_rules(self):
        erro = self.erro
        delta = self.delta_erro
        carga = self.carga_termica
        temp = self.temp_ext
        p = self.p_crac

        self.regras = [
            ctrl.Rule(erro['MP'], p['Alta']),
            ctrl.Rule(erro['ZE'] & delta['Z'], p['Media']),
            ctrl.Rule(erro['MN'], p['Baixa']),
            ctrl.Rule(carga['Alta'] | temp['Quente'], p['Alta']),
        ]

    def build(self):
        self._set_membership_functions()
        self._set_rules()
        sistema_controle = ctrl.ControlSystem(self.regras)
        return ctrl.ControlSystemSimulation(sistema_controle)