import React, { useEffect, useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/card';
import { Label } from '../ui/label';
import { Input } from '../ui/input';
import { Button } from '../ui/button';
import { useControlStore } from '@/store/useControlStore';
import { calcularFuzzyManual } from '@/services/fuzzyService';

interface InputField {
  id: 'error' | 'deltaError' | 'tempExterna' | 'cargaTermica';
  label: string;
  unit: string;
  min: number;
  max: number;
  description?: string;
}

const inputFields: InputField[] = [
  { id: 'error', label: 'Erro (e)', unit: '°C', min: -15, max: 15 },
  { id: 'deltaError', label: 'Variação do Erro (Δe)', unit: '°C/min', min: -5, max: 5 },
  {
    id: 'tempExterna',
    label: 'Temperatura Externa',
    unit: '°C',
    min: 0,
    max: 35,
    description: 'Varia entre 10°C e 35°C',
  },
  {
    id: 'cargaTermica',
    label: 'Carga Térmica',
    unit: '%',
    min: 0,
    max: 100,
    description: 'Potência térmica dos servidores',
  },
];

export const InputPanel = () => {
  const error = useControlStore((state) => state.error);
  const deltaError = useControlStore((state) => state.deltaError);
  const tempExterna = useControlStore((state) => state.tempExterna);
  const cargaTermica = useControlStore((state) => state.cargaTermica);

  const setInputValue = useControlStore((state) => state.setInputValue);
  const setPotenciaCRAC = useControlStore((state) => state.setPotenciaCRAC);
  const setExecuting = useControlStore((state) => state.setExecuting);
  const setPlots = useControlStore((state) => state.setPlots);

  const resetInputs = useControlStore((state) => state.resetInputs);
  const isExecuting = useControlStore((state) => state.isExecuting);

  const [localValues, setLocalValues] = useState<Record<string, string>>({
    error: String(error),
    deltaError: String(deltaError),
    tempExterna: String(tempExterna),
    cargaTermica: String(cargaTermica),
  });

  useEffect(() => setLocalValues((s) => ({ ...s, error: String(error) })), [error]);
  useEffect(() => setLocalValues((s) => ({ ...s, deltaError: String(deltaError) })), [deltaError]);
  useEffect(
    () => setLocalValues((s) => ({ ...s, tempExterna: String(tempExterna) })),
    [tempExterna],
  );
  useEffect(
    () => setLocalValues((s) => ({ ...s, cargaTermica: String(cargaTermica) })),
    [cargaTermica],
  );

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>, id: InputField['id']) => {
    const v = e.target.value;
    setLocalValues((s) => ({ ...s, [id]: v }));

    const value = parseFloat(v);
    if (!isNaN(value)) {
      setInputValue(id, value);
    }
  };

  const handleBlur = (id: InputField['id']) => {
    const v = localValues[id];
    if (v === '' || v == null) {
      setInputValue(id, 0);
      setLocalValues((s) => ({ ...s, [id]: '0' }));
    } else {
      const parsed = parseFloat(v);
      if (!isNaN(parsed)) setInputValue(id, parsed);
    }
  };

  const executeFuzzy = async () => {
    setExecuting(true);

    try {
      const result = await calcularFuzzyManual({
        erro: error,
        delta: deltaError,
        temp_externa: tempExterna,
        carga_termica: cargaTermica,
      });

      setPotenciaCRAC(result.p_crac);

      setPlots({
        erro: result.erro_plot,
        delta: result.delta_plot,
        temp: result.temp_plot,
        carga: result.carga_plot,
        pcrac: result.pcrac_plot,
      });
    } catch (err) {
      console.error('Erro ao executar cálculo fuzzy:', err);
    } finally {
      setExecuting(false);
    }
  };

  return (
    <Card className="shadow-lg">
      <CardHeader>
        <CardTitle>Painel de Entradas do Controlador Fuzzy</CardTitle>
      </CardHeader>

      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {inputFields.map((field) => (
            <div key={field.id} className="space-y-2">
              <Label htmlFor={field.id}>
                {field.label} ({field.unit})
              </Label>

              <Input
                id={field.id}
                type="number"
                min={field.min}
                max={field.max}
                placeholder={`Entre ${field.min} e ${field.max}`}
                value={localValues[field.id] ?? ''}
                onChange={(e) => handleInputChange(e, field.id)}
                onBlur={() => handleBlur(field.id)}
              />

              <p className="text-xs text-muted-foreground">{field.description}</p>
            </div>
          ))}
        </div>

        <div className="flex justify-start space-x-4 mt-8 pt-4 border-t">
          <Button onClick={executeFuzzy} disabled={isExecuting}>
            {isExecuting ? 'Calculando...' : 'Executar Cálculo Fuzzy'}
          </Button>

          <Button onClick={resetInputs} variant="outline">
            Limpar
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};
