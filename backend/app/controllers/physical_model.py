def modelo_fisico(t_atual, p_crac_val, q_est, t_ext):
    """
    Equação do PDF:
    T[n+1] = 0.9*T[n] - 0.08*Pcrac + 0.05*Qest + 0.02*Text + 3.5
    """
    t_next = (0.9 * t_atual) - (0.08 * p_crac_val) + (0.05 * q_est) + (0.02 * t_ext) + 3.5
    return t_next

#def modelo_fisico(t_atual, p_crac_val, q_est, t_ext):
#    return (
#        0.95 * t_atual
#        - 0.06 * p_crac_val
#        + 0.03 * q_est
#        + 0.01 * t_ext
#        + 1.5
#    )
