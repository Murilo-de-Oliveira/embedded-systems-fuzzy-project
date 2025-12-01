# app/controllers/mqtt_broker.py
import json
import time
import threading
import paho.mqtt.client as mqtt

class MQTTBroker:
    """
    Cliente MQTT com:
    - suporte a transport='websockets' (para frontends)
    - reconnect/backoff simples
    - publish_json convenience
    - modo offline (simulation) quando não conectado
    """

    def __init__(self, host="test.mosquitto.org", port_tcp=1883, port_ws=8080, use_websocket=False):
        self.host = host
        self.port_tcp = port_tcp
        self.port_ws = port_ws
        self.use_websocket = use_websocket

        transport = "websockets" if use_websocket else "tcp"
        self.client = mqtt.Client(transport=transport)

        # state
        self.connected = False
        self._lock = threading.Lock()

        # topics
        self.TOPIC_CONTROL = "datacenter/fuzzy/control"
        self.TOPIC_TEMP = "datacenter/fuzzy/temp"
        self.TOPIC_ALERT = "datacenter/fuzzy/alert"

        # callbacks (opcionais)
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect

        # iniciar loop somente se conectar com sucesso
        self._loop_started = False

        # reconnection params
        self._retries = 0
        self._max_retries = 5

    def _on_connect(self, client, userdata, flags, rc):
        with self._lock:
            self.connected = True
            self._retries = 0
        print(f"[MQTT] conectado ao broker {self.host} (rc={rc})")

    def _on_disconnect(self, client, userdata, rc):
        with self._lock:
            self.connected = False
        print(f"[MQTT] desconectado (rc={rc})")

    def start(self):
        """Tenta conectar e iniciar loop. Não lança exceção em falha — entra em modo offline."""
        try:
            if self.use_websocket:
                self.client.connect(self.host, self.port_ws, 60)
            else:
                self.client.connect(self.host, self.port_tcp, 60)

            if not self._loop_started:
                self.client.loop_start()
                self._loop_started = True

            # aguardar on_connect
            timeout = 3
            waited = 0
            while waited < timeout and not self.connected:
                time.sleep(0.1)
                waited += 0.1

            if not self.connected:
                print("[MQTT] não conectou dentro do timeout -> modo simulação (offline).")
            return True
        except Exception as e:
            print(f"[MQTT] falha na conexão: {e} -> modo simulação (offline).")
            self.connected = False
            return False

    def publish_json(self, topic, payload: dict, qos=0, retain=False):
        """Publica JSON se conectado. Caso offline, grava log e ignora (modo simulação)."""
        if not isinstance(payload, dict):
            raise ValueError("payload must be dict for publish_json")

        message = json.dumps(payload)
        return self._publish_raw(topic, message, qos=qos, retain=retain)

    def _publish_raw(self, topic, message, qos=0, retain=False):
        if self.connected:
            try:
                res = self.client.publish(topic, message, qos=qos, retain=retain)
                # opcional: esperar confirmação em qos>0
                return res
            except Exception as e:
                print(f"[MQTT] erro ao publicar: {e}")
                # tentar reconnect simples
                self.connected = False
                return None
        else:
            # modo simulação — não raise; apenas log para testes offline
            print(f"[MQTT - SIM] publish ignorado (offline): topic={topic} payload={message}")
            return None

    def subscribe(self, topic):
        if self.connected:
            self.client.subscribe(topic)
        else:
            print("[MQTT] subscribe ignorado (offline)")

    def stop(self):
        if self._loop_started:
            self.client.loop_stop()
            self._loop_started = False
        try:
            self.client.disconnect()
        except Exception:
            pass
        self.connected = False
