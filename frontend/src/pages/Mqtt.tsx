// src/pages/MQTTMonitor.tsx
import { useEffect, useState, useRef } from "react";
import mqtt from "mqtt";
import { SimulationChart } from "@/components/ui/simulationChart"; // opcional

export default function MQTTMonitor() {
  const [connected, setConnected] = useState(false);
  const [lastTemp, setLastTemp] = useState<number | null>(null);
  const [lastPower, setLastPower] = useState<number | null>(null);
  const [alerts, setAlerts] = useState<string[]>([]);
  const [historyTemp, setHistoryTemp] = useState<number[]>([]);
  const [historyPower, setHistoryPower] = useState<number[]>([]);
  const clientRef = useRef<any | null>(null);

  useEffect(() => {
    // URL do broker ws: ajuste conforme o seu broker
    const BROKER_WS = "ws://test.mosquitto.org:8080/mqtt";
    const client = mqtt.connect(BROKER_WS, {
      reconnectPeriod: 3000,
      connectTimeout: 4000,
    });

    clientRef.current = client;

    client.on("connect", () => {
      console.log("[MQTT-UI] conectado");
      setConnected(true);
      client.subscribe("datacenter/fuzzy/#", (err) => {
        if (err) console.warn("[MQTT-UI] subscribe error", err);
      });
    });

    client.on("reconnect", () => {
      console.log("[MQTT-UI] tentando reconectar...");
    });

    client.on("error", (err) => {
      console.error("[MQTT-UI] erro", err);
    });

    client.on("offline", () => {
      setConnected(false);
      console.log("[MQTT-UI] offline");
    });

    client.on("message", (topic, payloadBuffer) => {
      const payloadStr = payloadBuffer.toString();
      
      try {
        // 1. Tenta interpretar como JSON
        const data = JSON.parse(payloadStr); 

        if (topic.endsWith("/temp")) {
          // O Python manda {"temp_atual": ...}
          const t = data.temp_atual; 
          if (typeof t === 'number') {
            setLastTemp(t);
            setHistoryTemp((h) => [...(h.length > 600 ? h.slice(-599) : h), t]);
          }
        } 
        else if (topic.endsWith("/control")) {
          // O Python manda {"p_crac": ...}
          const p = data.p_crac;
          if (typeof p === 'number') {
            setLastPower(p);
            setHistoryPower((h) => [...(h.length > 600 ? h.slice(-599) : h), p]);
          }
        } 
        else if (topic.endsWith("/alert")) {
          // O Python manda {"alert": "MENSAGEM...", ...}
          const a = data.alert || JSON.stringify(data);
          setAlerts((arr) => [a, ...arr].slice(0, 50));
        }
      } catch (e) {
        console.debug("[MQTT-UI] Erro ao ler JSON", e);
      }
    });
  }, []);

  return (
    <div className="p-4">
      <h1>Monitor MQTT</h1>
      <p>Status: {connected ? "Conectado" : "Desconectado (modo simulação)"}</p>

      <div style={{ display: "flex", gap: 24 }}>
        <div>
          <h3>Últimos</h3>
          <p>Temperatura: {lastTemp !== null ? lastTemp.toFixed(2) + "°C" : "-"}</p>
          <p>Potência CRAC: {lastPower !== null ? lastPower.toFixed(1) + "%" : "-"}</p>
        </div>

        <div>
          <h3>Alertas recentes</h3>
          <ul>
            {alerts.map((a, i) => (
              <li key={i}>{a}</li>
            ))}
          </ul>
        </div>
      </div>

      <div style={{ marginTop: 24 }}>
        <h3>Histórico (preview)</h3>
        {historyTemp.length > 0 || historyPower.length > 0 ? (
          <div style={{ height: 300 }}>
            {/* Reuse seu SimulationChart (ajuste props se preciso) */}
            <SimulationChart
              sim={{
                temperature: historyTemp.length ? historyTemp : [0],
                power: historyPower.length ? historyPower : [0],
                load: [],
                external_temp: [],
              }}
            />
          </div>
        ) : (
          <p>Sem histórico ainda.</p>
        )}
      </div>
    </div>
  );
}
