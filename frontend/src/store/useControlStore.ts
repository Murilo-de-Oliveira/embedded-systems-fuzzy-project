import { fetchSimulation } from '@/services/fuzzyService';
import { create } from 'zustand';

interface SimulationData {
  temperature: number[];
  power: number[];
  load: number[];
  external_temp: number[];
}

interface ControlState {
  error: number;
  deltaError: number;
  tempExterna: number;
  cargaTermica: number;
  potenciaCRAC: number;
  isExecuting: boolean;

  // setters
  setInputValue: (
    name: 'error' | 'deltaError' | 'tempExterna' | 'cargaTermica',
    value: number,
  ) => void;
  setPotenciaCRAC: (value: number) => void;
  setExecuting: (status: boolean) => void;
  resetInputs: () => void;

  // simulação
  simulation: SimulationData | null;
  runSimulation: () => Promise<void>;
}

const INITIAL_STATE = {
  error: 0,
  deltaError: 0,
  tempExterna: 25,
  cargaTermica: 40,
  potenciaCRAC: 0,
  isExecuting: false,
};

export const useControlStore = create<ControlState>((set) => ({
  ...INITIAL_STATE,

  setInputValue: (name, value) =>
    set((state) => ({
      ...state,
      [name]: value,
    })),

  setPotenciaCRAC: (value) => set({ potenciaCRAC: value }),

  setExecuting: (status) => set({ isExecuting: status }),

  resetInputs: () =>
    set({
      ...INITIAL_STATE,
      tempExterna: 0,
      cargaTermica: 0,
    }),

  simulation: null,

  runSimulation: async () => {
    const data = await fetchSimulation();
    set({ simulation: data });
  },
}));
