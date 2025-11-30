import { create } from 'zustand';
import { fetchCurrent } from "@/api";

interface ControlState {
  error: number;
  deltaError: number;
  tempExterna: number;
  cargaTermica: number;
  potenciaCRAC: number;
  isExecuting: boolean;
  setInputValue: (
    name: 'error' | 'deltaError' | 'tempExterna' | 'cargaTermica',
    value: number,
  ) => void;
  setPotenciaCRAC: (value: number) => void;
  setExecuting: (status: boolean) => void;
  resetInputs: () => void;
  syncWithBackend: () => Promise<void>;
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
      error: 0,
      deltaError: 0,
      tempExterna: 0,
      cargaTermica: 0,
      potenciaCRAC: 0,
      isExecuting: false,
    }),
  async syncWithBackend(){
    const data = await fetchCurrent();
    console.log(data);
    set({potenciaCRAC: data.p_crac})
  }
}));
