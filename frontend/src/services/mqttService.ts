import axios from 'axios';

const API_URL = 'http://localhost:8000/v1';

export interface MQTTStatus {
  connected: boolean;
}

export const mqttService = {
  // Obter status da conexão MQTT
  getStatus: async (): Promise<MQTTStatus> => {
    const response = await axios.get<MQTTStatus>(`${API_URL}/mqtt/status`);
    return response.data;
  },
};
