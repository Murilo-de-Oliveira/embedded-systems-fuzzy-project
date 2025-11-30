const API_URL = "http://localhost:8000";

//Adicionar uma rota current apenas para retornar o valor de p_crac individualmente
//export async function fetchCurrent() {
//  const res = await fetch(`${API_URL}/v1/current`);
//  if (!res.ok) throw new Error("Erro ao buscar dados do backend");
//  return res.json();
//}

export async function fetchCurrent() {
  const res = await fetch(`${API_URL}/v1/step`);
  if (!res.ok) throw new Error("Erro ao buscar dados do backend");
  return res.json();
}

export async function stepSimulation() {
  const res = await fetch(`${API_URL}/v1/simuate-24h`);
  if (!res.ok) throw new Error("Erro ao avançar simulação");
  return res.json();
}