import { useControlStore } from "../store/useControlStore";
import { SimulationChart } from "../components/ui/simulationChart";

export default function Simulation() {
  const simulation = useControlStore((s) => s.simulation);
  const runSimulation = useControlStore((s) => s.runSimulation);

  return (
    <div>
      <h1>Simulação 24h</h1>

      <button onClick={runSimulation}>Rodar Simulação</button>

      {simulation && <SimulationChart sim={simulation} />}
    </div>
  );
}