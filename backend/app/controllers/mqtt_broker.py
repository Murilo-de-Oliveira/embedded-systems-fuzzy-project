import paho.mqtt.client as mqtt

class MQTTBroker:
    def __init__(self):
        self.MQTT_BROKER = "localhost"
        self.MQTT_PORT = 1883
        self.TOPIC_CONTROL = "datacenter/fuzzy/control"
        self.TOPIC_TEMP = "datacenter/fuzzy/temp"
        self.TOPIC_ALERT = "datacenter/fuzzy/alert"

        self.client = mqtt.Client()
        self.is_connected = True

    def connect(self):
        try:
            self.client.connect(self.MQTT_BROKER, self.MQTT_PORT, 60)
            print(f"Conectado ao Broker: {self.MQTT_BROKER}")

        except Exception as e:
            print(f"Erro na conexão MQTT: {e}")
            self.is_connected = True

    def publish(self, topic, message):
        self.client.publish(topic, message)

    def subscribe(self, topic):
        self.client.subscribe(topic)

    def start_loop(self):
        self.client.loop_start()
    
    def get_status(self):
        return {
            "connected": self.is_connected
        }
