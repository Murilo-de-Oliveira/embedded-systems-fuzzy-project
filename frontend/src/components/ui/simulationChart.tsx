import { Line } from "react-chartjs-2";

type SimulationData = {
  temperature: number[];
  power: number[];
  load: number[];
  external_temp: number[];
};

export function SimulationChart({ sim }: { sim: SimulationData }) {
  const labels = [...Array(sim.temperature.length).keys()];

  const data = {
    labels,
    datasets: [
      //{ label: "Temperatura (°C)", data: sim.temperature },
      { label: "Potência CRAC (%)", data: sim.power },
      //{ label: "Carga Térmica (%)", data: sim.load },
      //{ label: "Temp Externa (°C)", data: sim.external_temp },
    ],
  };

  return <Line data={data} />;
}
