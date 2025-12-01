def modelo_fisico(t_atual, p_crac_val, q_est, t_ext):
    """
    Equação do PDF:
    T[n+1] = 0.9*T[n] - 0.08*Pcrac + 0.05*Qest + 0.02*Text + 3.5
    """
    t_next = (0.9 * t_atual) - (0.08 * p_crac_val) + (0.05 * q_est) + (0.02 * t_ext) + 3.5
    return t_next

#def modelo_fisico(t_atual, p_crac, q_est, t_ext):
#    """
#    Modelo térmico corrigido e estabilizado.
#    Ajustado para o fuzzy atual.
#    """
#    # resposta térmica mais lenta e estável
#    alpha = 0.97         # inércia térmica (97% mantém a temperatura)
#    
#    # influência mais suave e realista
#    efeito_crac = -0.015 * p_crac            # resfriamento
#    efeito_carga = 0.010 * q_est             # carga térmica
#    efeito_externa = 0.004 * (t_ext - t_atual)  # difusão térmica realista
#
#    # nova temperatura
#    t_next = alpha * t_atual + efeito_crac + efeito_carga + efeito_externa
#
#    return t_next