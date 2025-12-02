import { create } from 'zustand';

interface ControlState {
  error: number;
  deltaError: number;
  tempExterna: number;
  cargaTermica: number;

  potenciaCRAC: number;
  isExecuting: boolean;

  plots: {
    erro?: string;
    delta?: string;
    temp?: string;
    carga?: string;
    pcrac?: string;
    rules?: string;
  };

  setInputValue: (
    name: 'error' | 'deltaError' | 'tempExterna' | 'cargaTermica',
    value: number,
  ) => void;

  setPotenciaCRAC: (value: number) => void;
  setExecuting: (status: boolean) => void;

  setPlots: (plots: ControlState['plots']) => void;

  resetInputs: () => void;
}

const INITIAL_STATE = {
  error: 0,
  deltaError: 0,
  tempExterna: 25,
  cargaTermica: 40,
  potenciaCRAC: 0,
  isExecuting: false,
  plots: {},
};

export const useControlStore = create<ControlState>((set) => ({
  ...INITIAL_STATE,

  setInputValue: (name, value) =>
    set((state) => ({
      ...state,
      [name]: value,
    })),

  setPotenciaCRAC: (value) => set({ potenciaCRAC: value }),

  setExecuting: (s) => set({ isExecuting: s }),

  setPlots: (plots) => set({ plots }),

  resetInputs: () =>
    set({
      ...INITIAL_STATE,
      tempExterna: 25,
      cargaTermica: 40,
    }),
}));
