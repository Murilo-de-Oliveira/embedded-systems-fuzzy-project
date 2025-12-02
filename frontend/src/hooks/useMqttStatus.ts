import { useEffect, useState } from 'react';
import { mqttService } from '../services/mqttService';
import type { MQTTStatus } from '../services/mqttService';

export const useMqttStatus = (pollingInterval: number = 3000) => {
  const [status, setStatus] = useState<MQTTStatus>({
    connected: false,
  });
  const [loading, setLoading] = useState(true);

  const fetchStatus = async () => {
    try {
      const data = await mqttService.getStatus();
      setStatus(data);
    } catch (error) {
      console.error('Erro ao buscar status MQTT:', error);
      setStatus({ connected: false });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Buscar status inicial
    fetchStatus();

    // Polling periódico para verificar status
    const interval = setInterval(fetchStatus, pollingInterval);

    return () => clearInterval(interval);
  }, [pollingInterval]);

  return {
    status,
    loading,
    refresh: fetchStatus,
  };
};
