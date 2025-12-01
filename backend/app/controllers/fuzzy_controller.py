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
        # ERRO: alta resolução perto de zero (zona crítica)
        self.erro['MN'] = fuzzy.trapmf(self.erro.universe, [-10, -10, -3, -1])
        self.erro['NS'] = fuzzy.trimf(self.erro.universe, [-3, -1.5, 0])   # negativo suave
        self.erro['ZE'] = fuzzy.trimf(self.erro.universe, [-1, 0, 1])
        self.erro['PS'] = fuzzy.trimf(self.erro.universe, [0, 1.5, 3])     # positivo suave
        self.erro['MP'] = fuzzy.trapmf(self.erro.universe, [1, 3, 10, 10]) # muito positivo

        # DELTA_ERRO: prever tendência (mantive formato conservador)
        self.delta_erro['N'] = fuzzy.trapmf(self.delta_erro.universe, [-5, -5, -1, -0.2])
        self.delta_erro['Z'] = fuzzy.trimf(self.delta_erro.universe, [-0.5, 0, 0.5])
        self.delta_erro['P'] = fuzzy.trapmf(self.delta_erro.universe, [0.2, 1, 5, 5])

        # TEMP EXTERNA (suave, impacto pequeno)
        self.temp_ext['Fria'] = fuzzy.trimf(self.temp_ext.universe, [10, 12, 18])
        self.temp_ext['Media'] = fuzzy.trimf(self.temp_ext.universe, [15, 22, 28])
        self.temp_ext['Quente'] = fuzzy.trimf(self.temp_ext.universe, [25, 35, 35])

        # CARGA TERMICA
        self.carga_termica['Baixa'] = fuzzy.trimf(self.carga_termica.universe, [0, 0, 30])
        self.carga_termica['Media'] = fuzzy.trimf(self.carga_termica.universe, [20, 50, 80])
        self.carga_termica['Alta'] = fuzzy.trimf(self.carga_termica.universe, [60, 100, 100])

        # SAIDA PCRAC (conservador: overlap maior para suavizar mudanças)
        self.p_crac['Baixa'] = fuzzy.trimf(self.p_crac.universe, [0, 0, 35])
        self.p_crac['Media'] = fuzzy.trimf(self.p_crac.universe, [25, 50, 75])
        self.p_crac['Alta'] = fuzzy.trimf(self.p_crac.universe, [60, 85, 100])

    def _set_rules(self):
        e = self.erro
        de = self.delta_erro
        t = self.temp_ext
        q = self.carga_termica
        p = self.p_crac

        regras = []

        # Prioridade 1: Erro (mais crítico)
        regras.append(ctrl.Rule(e['MP'], p['Alta']))
        regras.append(ctrl.Rule(e['PS'] & de['P'], p['Alta']))   # Petit aumento + tendência positiva => reagir
        regras.append(ctrl.Rule(e['PS'] & de['Z'], p['Media']))  # leve desvio -> média
        regras.append(ctrl.Rule(e['ZE'] & de['P'], p['Media']))  # prever aquecimento => média
        regras.append(ctrl.Rule(e['ZE'] & de['Z'], p['Media']))  # manutenção
        regras.append(ctrl.Rule(e['ZE'] & de['N'], p['Baixa']))  # tendência de resfriar -> reduzir

        regras.append(ctrl.Rule(e['NS'], p['Baixa']))            # erro negativo suave -> reduzir
        regras.append(ctrl.Rule(e['MN'], p['Baixa']))            # muito negativo -> mínimo

        # Prioridade 2: Condições externas (modulação conservadora)
        regras.append(ctrl.Rule((q['Alta'] | t['Quente']) & e['ZE'], p['Media'])) # quando critico, não deixar em Baixa
        regras.append(ctrl.Rule((q['Alta'] | t['Quente']) & e['PS'], p['Alta']))

        # Economia de energia e continuidade
        regras.append(ctrl.Rule(e['ZE'] & q['Baixa'] & t['Fria'], p['Baixa']))

        # Garantir continuidade: combinar múltiplas evidências
        regras.append(ctrl.Rule((e['PS'] & q['Media']) | (de['P'] & q['Alta']), p['Alta']))
        regras.append(ctrl.Rule((e['NS'] & q['Baixa']) | (de['N'] & t['Fria']), p['Baixa']))

        self.regras = regras

    def build(self):
        self._set_membership_functions()
        self._set_rules()
        sistema_controle = ctrl.ControlSystem(self.regras)
        return ctrl.ControlSystemSimulation(sistema_controle)

    def calcular(self, erro, delta, temp_externa, carga_termica):
        sim = self.build()

        sim.input['erro'] = erro
        sim.input['delta_erro'] = delta
        sim.input['temp_externa'] = temp_externa
        sim.input['carga_termica'] = carga_termica

        sim.compute()
        return float(sim.output['p_crac'])