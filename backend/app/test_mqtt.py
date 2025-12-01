from controllers.mqtt_broker import MQTTBroker
import time

def main():
    broker = MQTTBroker()

    # Callback para receber mensagens
    def on_message(client, userdata, msg):
        print(f"RECEBIDO > {msg.topic}: {msg.payload.decode()}")

    broker.client.on_message = on_message

    broker.connect()
    broker.subscribe(broker.TOPIC_CONTROL)
    broker.start_loop()

    print("Esperando mensagens... envie algo para o tópico datacenter/fuzzy/control")
    time.sleep(60)   # fica escutando por 1 minuto

if __name__ == "__main__":
    main()
