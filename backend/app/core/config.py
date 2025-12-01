from app.controllers.simulation import DataCenterSimStep

sim_step_instance = DataCenterSimStep()

def get_simulation():
    return sim_step_instance