import random
from physical_model import modelo_fisico
import numpy as np
import math
import matplotlib.pyplot as plt
from fuzzy_controller import FuzzyController

# Configurações
horas = 24
minutos_por_hora = 60
total_minutos = horas * minutos_por_hora

# Listas
temperaturas = []
potencias = []
tempo = list(range(total_minutos))

# Inicialização
temp_atual = 22.0
T_SET = 22.0

fuzzy_controller = FuzzyController()

# Filtros
erro_f = 0.0
delta_f = 0.0
pot_f = 0.0
erro_passado = 0.0

alpha_erro  = 0.25
alpha_delta = 0.35
alpha_pot   = 0.20

def temp_externa_profile(t):
    Tbase = 20
    A = 10
    Ts = 1440
    ruido = np.random.normal(0, 0.5)
    return Tbase + A * math.sin(2 * math.pi * t / Ts) + ruido

def carga_termica_profile(t):
    if 0 <= t < 300:      
        base = 35
    elif 300 <= t < 1000:
        base = 70
    else:
        base = 50
    return np.clip(base + np.random.uniform(-5, 5), 0, 100)

for k in range(total_minutos):

    # perfis
    temp_externa = temp_externa_profile(k)
    carga_termica = carga_termica_profile(k)

    # erro
    erro = temp_atual - T_SET

    # filtro erro
    erro_f = alpha_erro * erro + (1 - alpha_erro) * erro_f

    # delta_erro filtrado
    delta_raw = erro_f - erro_passado
    delta_f = alpha_delta * delta_raw + (1 - alpha_delta) * delta_f
    erro_passado = erro_f

    # potência bruta
    pot_raw = fuzzy_controller.calcular(
        erro=float(erro_f),
        delta_erro=float(delta_f),
        temp_externa=float(temp_externa),
        carga_termica=float(carga_termica)
    )

    # potência filtrada
    pot_f = alpha_pot * pot_raw + (1 - alpha_pot) * pot_f

    # modelo físico
    temp_atual = modelo_fisico(temp_atual, pot_f, carga_termica, temp_externa)

    # limites físicos
    temp_atual = float(np.clip(temp_atual, 17, 30))

    temperaturas.append(temp_atual)
    potencias.append(pot_f)

# plots
plt.figure(figsize=(14, 8))
plt.subplot(2, 1, 1)
plt.plot(tempo, temperaturas)
plt.axhline(22, color='red', linestyle='--')
plt.title("Temperatura 24h")
plt.grid()

plt.subplot(2, 1, 2)
plt.plot(tempo, potencias, color='orange')
plt.title("Potência CRAC 24h")
plt.grid()

plt.tight_layout()
plt.show()
