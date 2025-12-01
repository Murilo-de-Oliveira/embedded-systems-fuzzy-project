'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

export default function Simulation() {
  const [data, setData] = useState([]);

  // Carrega os dados da simulação
  useEffect(() => {
    fetch('http://localhost:8000/v1/simulate-24h')
      .then((res) => res.json())
      .then((json) => setData(json))
      .catch((err) => console.error('Erro ao carregar simulação:', err));
  }, []);

  return (
    <div className="p-6 space-y-8">
      <h1 className="text-3xl font-bold">Simulação 24h</h1>

      {/* GRID DOS GRÁFICOS */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Temperatura Interna */}
        <Card>
          <CardHeader>
            <CardTitle>Temperatura Interna (°C)</CardTitle>
          </CardHeader>
          <CardContent className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data}>
                <Line type="monotone" dataKey="temp_atual" stroke="#8884d8" dot={false} />
                <XAxis dataKey="minuto" />
                <YAxis />
                <Tooltip />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Potência CRAC */}
        <Card>
          <CardHeader>
            <CardTitle>Potência CRAC (%)</CardTitle>
          </CardHeader>
          <CardContent className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data}>
                <Line type="monotone" dataKey="p_crac" stroke="#82ca9d" dot={false} />
                <XAxis dataKey="minuto" />
                <YAxis domain={[0, 100]} />
                <Tooltip />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Temperatura Externa */}
        <Card>
          <CardHeader>
            <CardTitle>Temperatura Externa (°C)</CardTitle>
          </CardHeader>
          <CardContent className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data}>
                <Line type="monotone" dataKey="temp_externa" stroke="#ff7300" dot={false} />
                <XAxis dataKey="minuto" />
                <YAxis />
                <Tooltip />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Carga Térmica */}
        <Card>
          <CardHeader>
            <CardTitle>Carga Térmica (%)</CardTitle>
          </CardHeader>
          <CardContent className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data}>
                <Line type="monotone" dataKey="carga_termica" stroke="#387908" dot={false} />
                <XAxis dataKey="minuto" />
                <YAxis />
                <Tooltip />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
