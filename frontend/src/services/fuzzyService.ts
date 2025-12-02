import { api } from '@/lib/api';

export interface FuzzyManualRequest {
  erro: number;
  delta: number;
  temp_externa: number;
  carga_termica: number;
}

export interface FuzzyManualResponse {
  p_crac: number;
  erro_plot: string;
  delta_plot: string;
  temp_plot: string;
  carga_plot: string;
  pcrac_plot: string;
  rules_plot: string;
}

export async function calcularFuzzyManual(data: FuzzyManualRequest) {
  const resp = await api.post<FuzzyManualResponse>('/fuzzy/manual', data);
  return resp.data;
}
