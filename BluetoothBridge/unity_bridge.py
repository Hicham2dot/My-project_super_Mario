import json
import time
import queue
import socket
import threading
import collections

import paho.mqtt.client as mqtt

import config
from gesture_classifier import GestureClassifier, Command

STICKY_HOLD = 0.35
UNITY_HOST  = "127.0.0.1"
UNITY_PORT  = 5005


class UnityBridge:

    def __init__(self):
        n = config.SENSOR_SMOOTHING_WINDOW
        self.t_x = collections.deque([config.SENSOR_REST_X] * n, maxlen=n)
        self.t_y = collections.deque([config.SENSOR_REST_Y] * n, maxlen=n)
        self.t_z = collections.deque([config.SENSOR_REST_Z] * n, maxlen=n)
        self._lock       = threading.Lock()
        self._classifier = GestureClassifier()
        self._cmd_queue  = queue.Queue(maxsize=50)
        self.running     = False

        self.client = mqtt.Client()
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print(f"--Unity-- UDP ready → {UNITY_HOST}:{UNITY_PORT}")

    def start(self):
        try:
            self.client.connect(config.MQTT_BROKER, config.MQTT_PORT, keepalive=60)
            self.client.loop_start()
            print(f"--Unity-- Connected to broker {config.MQTT_BROKER}:{config.MQTT_PORT}")
        except Exception as exc:
            print(f"--Unity-- Broker unavailable : {exc}")

        self.running = True
        threading.Thread(target=self._loop, daemon=True).start()

    def stop(self):
        self.running = False
        self.client.loop_stop()
        self.client.disconnect()
        self.sock.close()

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            client.subscribe(config.MQTT_TOPIC)
            print(f"--Unity-- Subscribed to '{config.MQTT_TOPIC}'")
        else:
            print(f"--Unity-- Broker error rc={rc}")

    def _on_message(self, client, userdata, msg):
        try:
            data    = json.loads(msg.payload)
            samples = data.get("samples", [])
            if not samples:
                return
            n     = len(samples)
            avg_x = sum(s["x"] for s in samples) / n
            avg_y = sum(s["y"] for s in samples) / n
            avg_z = sum(s["z"] for s in samples) / n
            with self._lock:
                self.t_x.append(avg_x)
                self.t_y.append(avg_y)
                self.t_z.append(avg_z)
                sx = sum(self.t_x) / len(self.t_x)
                sy = sum(self.t_y) / len(self.t_y)
                sz = sum(self.t_z) / len(self.t_z)
            cmd = self._classifier.classify(sx, sy, sz)
            if cmd != Command.NONE:
                print(f"--Unity-- x={sx:.0f}  y={sy:.0f}  → {cmd.name}")
            try:
                self._cmd_queue.put_nowait(cmd)
            except queue.Full:
                pass
        except Exception as exc:
            print(f"--Unity-- Parsing error : {exc}")

    def _loop(self):
        sticky      = Command.NONE
        sticky_time = 0.0
        last_sent   = None

        while self.running:
            try:
                while True:
                    cmd = self._cmd_queue.get_nowait()
                    if cmd != Command.NONE:
                        sticky      = cmd
                        sticky_time = time.time()
            except queue.Empty:
                pass

            if time.time() - sticky_time > STICKY_HOLD:
                sticky = Command.NONE

            if sticky != last_sent:
                self.sock.sendto(sticky.name.encode(), (UNITY_HOST, UNITY_PORT))
                last_sent = sticky

            time.sleep(0.016)


if __name__ == "__main__":
    bridge = UnityBridge()
    bridge.start()
    print("--Unity-- Started — press Ctrl+C to stop")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    bridge.stop()
    print("--Unity-- Stopped")
