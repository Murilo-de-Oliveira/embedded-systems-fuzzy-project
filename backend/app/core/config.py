from app.controllers.simulation import DataCenterSimStep

_sim_instance = None

def get_simulation():
    global _sim_instance
    if _sim_instance is None:
        _sim_instance = DataCenterSimStep()
    return _sim_instance