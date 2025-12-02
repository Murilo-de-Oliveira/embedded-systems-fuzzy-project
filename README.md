# embedded-systems-fuzzy-project
Repositório dedicado ao projeto "Sistema de Controle Fuzzy MISO para Refrigeração em Centros de Dados" da disciplina de Sistemas Embarcados (C213))

O objetivo é simular 24 horas de operação de um Data Center, avaliando a estabilidade térmica e a eficiência do controle.

Como executar o projeto (backend):
Utilizando UV (recomendado):
    pip install uv
    cd backend
    uv sync
    uv run uvicorn app.main:app --reload
    A API ficará disponível em http://127.0.0.1:8000

Como executar o projeto (frontend):
    npm run dev
    O frontend ficará disponível em http://localhost:5173/

Arquitetura do projeto:
O projeto é composto por duas partes principais:
Backend:
Feito utilizando FastAPI e Pydantic
Módulo Fuzzy Controller -> Possui a lógica fuzzy, juntamente com regras e funções de pertinência
Modelo Físico -> Equação que calcula a temperatura no minuto seguinte
Simulador de 24h -> Gera o resultado de 24h simuladas do refrigeramento do datacenter, além de enviar publicações MQTT
MQTT Broker -> Classe que organiza e gerencia a implementação do protocolo MQTT
Endpoints de API -> Meio pelo qual o frontend recebe e envia os dados

Frontend:
Feito utilizando React, Vite e Typescript
Tela Home -> Permite o usuário calcular a Potência CRAC utilizando parâmetros específicos
Tela Membership -> Mostra as funções de pertinência da classe FuzzyController
Tela MQTT -> Recebe e exibe as mensagens recebidas do broker MQTT
Tela Simulation -> Recebe dados de 24h simuladas

Fluxo Geral:
O simulador calcula temperatura minuto a minuto.
O controlador Fuzzy calcula a potência ideal do CRAC.
O modelo físico calcula a nova temperatura.
Backend publica dados via MQTT.
Frontend consome via API e WebSocket/MQTT.

Módulo de Controle Fuzzy
Entradas:
Erro: diferença entre temperatura atual e setpoint.
Delta Erro: variação do erro entre ciclos.
Temperatura Externa: influencia o aquecimento natural.
Carga Térmica: representa o uso computacional.
Saída:
p_crac: potência do sistema de climatização (0–100%).

Regras Fuzzy:
e = erro
de = delta do erro
t = temperatura externa
q = carga térmica
p = potência CRAC

Condições extremas:
| Condição | Interpretação            | Saída  |
| -------- | ------------------------ | ------ |
| e = MP   | Muito acima do setpoint  | p = MA |
| e = MN   | Muito abaixo do setpoint | p = MB |

Ambiente quente:
| Condição         | Significado Físico            | Ação |
| ---------------- | ----------------------------- | ---- |
| e = PS & de = SR | Quente e subindo muito rápido | MA   |
| e = PS & de = S  | Quente e subindo              | A    |
| e = PS & de = E  | Quente mas estável            | A    |
| e = PS & de = C  | Quente mas caindo             | M    |
| e = PS & de = CR | Quente mas caindo rápido      | B    |

Ambiente frio:
| Condição         | Significado Físico            | Ação |
| ---------------- | ----------------------------- | ---- |
| e = NS & de = CR | Frio e esfriando rápido       | MB   |
| e = NS & de = C  | Frio e esfriando              | MB   |
| e = NS & de = E  | Frio mas estável              | B    |
| e = NS & de = S  | Frio e subindo                | M    |
| e = NS & de = SR | Frio mas subindo muito rápido | A    |

Carga alta e erro zero:
| Condição       | Significado | Ação |
| -------------- | ----------- | ---- |
| e = ZE & q = A | Carga alta  | A    |
| e = ZE & q = M | Carga média | M    |
| e = ZE & q = B | Carga baixa | B    |

Temperatura externa com erro zero:
| Condição       | Significado          | Ação |
| -------------- | -------------------- | ---- |
| e = ZE & t = A | Externo muito quente | A    |
| e = ZE & t = M | Externo moderado     | M    |
| e = ZE & t = B | Externo frio         | B    |

Interações críticas:
| Condição       | Significado             | Ação |
| -------------- | ----------------------- | ---- |
| e = PS & q = A | Quente + carga alta     | MA   |
| e = PS & t = A | Quente + externo quente | MA   |

Nas simulações, foi utilizado um módulo de filtro para suavisar a resposta:
def _filtro(self, value, filt, alpha):
        """Filtro exponencial simples."""
        if filt is None:
            return value
        return alpha * value + (1 - alpha) * filt

Modelo físico:
O modelo físico utilizado para realizar a predição da temperatura foi:
def modelo_fisico(t_atual, p_crac_val, q_est, t_ext):
    """
    Equação do PDF:
    T[n+1] = 0.9*T[n] - 0.08*Pcrac + 0.05*Qest + 0.02*Text + 3.5
    """
    t_next = (0.9 * t_atual) - (0.08 * p_crac_val) + (0.05 * q_est) + (0.02 * t_ext) + 3.5
    return t_next

MQTT
Tópicos utilizados:
/app/temperature
/app/control
/app/alert

O sistema já apresenta:
Controle fuzzy completo e estável.
Simulação térmica consistente.
Telemetria funcionando.
Dashboard analítico operacional.

Colaboradores:
Murilo de Oliveira Domingos Figueiredo
Petterson Ikaro Bento de Souza
