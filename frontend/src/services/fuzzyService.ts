import { api } from '@/lib/api';

export interface FuzzyManualRequest {
  erro: number;
  delta: number;
  temp_externa: number;
  carga_termica: number;
}

export interface FuzzyManualResponse {
  p_crac: number;
}

export async function calcularFuzzyManual(data: FuzzyManualRequest) {
  const resp = await api.post<FuzzyManualResponse>('/fuzzy/manual', data);
  return resp.data;
}

export async function fetchSimulation() {
  const res = await fetch("http://localhost:8000/v1/simulate-24h");
  return res.json();
}
