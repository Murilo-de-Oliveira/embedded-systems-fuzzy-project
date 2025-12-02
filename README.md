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
