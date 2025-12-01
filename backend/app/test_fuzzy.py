from controllers.fuzzy_controller import FuzzyController

def testar_casos():
    fc = FuzzyController()

    casos = [
        {"erro": 5,  "delta": 1,  "temp": 30, "carga": 80},  # Deve dar ALTA
        {"erro": 0,  "delta": 0,  "temp": 22, "carga": 50},  # Deve dar MÉDIA
        {"erro": -5, "delta": -1, "temp": 15, "carga": 20},  # Deve dar BAIXA
        {"erro": 2,  "delta": 0.5,"temp": 35, "carga": 90},  # Muito quente → ALTA
        {"erro": 0,  "delta": -1, "temp": 12, "carga": 10},  # ZE + frio + carga baixa → BAIXA
        {"erro": 0,  "delta": 1,  "temp": 28, "carga": 70},  # ZE + delta P + alta carga → MEDIA/ALTA
    ]

    for caso in casos:
        p = fc.calcular(
            erro=caso["erro"],
            delta=caso["delta"],
            temp_externa=caso["temp"],
            carga_termica=caso["carga"]
        )
        print(
            f"Entrada: erro={caso['erro']}, delta={caso['delta']}, temp={caso['temp']}, carga={caso['carga']} → "
            f"Potência CRAC = {p:.1f}%"
        )


if __name__ == "__main__":
    testar_casos()
