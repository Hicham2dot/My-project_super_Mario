import json
import threading
import collections
import queue
import paho.mqtt.client as mqtt
import config
from gesture_classifier import GestureClassifier, Command

command_queue: queue.Queue = queue.Queue(maxsize=50)
sample_queue:  queue.Queue = queue.Queue(maxsize=50)


class IMUSample:
    _SCALE = 1.0 / 16768.0
    def __init__(self, raw_x: float, raw_y: float, raw_z: float):
        self.x = raw_x * self._SCALE  
        self.y = raw_y * self._SCALE
        self.z = raw_z * self._SCALE

    def __repr__(self):
        return f"IMUSample(x={self.x:+.2f}g  y={self.y:+.2f}g  z={self.z:+.2f}g)"


class BLEBridge:
    
    def __init__(self):
        # Circular
        n = config.SENSOR_SMOOTHING_WINDOW
        self._hist_x = collections.deque([config.SENSOR_REST_X] * n, maxlen=n)
        self._hist_y = collections.deque([config.SENSOR_REST_Y] * n, maxlen=n)
        self._hist_z = collections.deque([config.SENSOR_REST_Z] * n, maxlen=n)

        # Lissed values
        self._lock = threading.Lock()
        self._smooth_x = float(config.SENSOR_REST_X)
        self._smooth_y = float(config.SENSOR_REST_Y)
        self._smooth_z = float(config.SENSOR_REST_Z)

        # Gesture Classifier
        self._classifier = GestureClassifier()

        # MQTT client paho
        self._client = mqtt.Client()
        self._client.on_connect = self._on_connect
        self._client.on_message = self._on_message

    # Public interface

    def start(self):
        try:
            self._client.connect(config.MQTT_BROKER, config.MQTT_PORT, keepalive=60)
            self._client.loop_start()
            print(f"--BLEbridge-- Connecté à {config.MQTT_BROKER}:{config.MQTT_PORT}")
        except Exception as exc:
            print(f"--BLEbridge-- Impossible to connect to the broker : {exc}")
            print("--BLEbridge-- Keyboard Mode is active.")

    def stop(self):
        self._client.loop_stop()
        self._client.disconnect()
        print("--BLEbridge-- Disconnected.")

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            client.subscribe(config.MQTT_TOPIC)
            print(f"--BLEbridge-- Following '{config.MQTT_TOPIC}'")
        else:
            print(f"--BLEbridge-- Broker error (rc={rc})")

    def _on_message(self, client, userdata, msg):
    
        try:
            data = json.loads(msg.payload)
            samples = data.get("samples", [])
            if not samples:
                return

            n = len(samples)
            avg_x = sum(s["x"] for s in samples) / n
            avg_y = sum(s["y"] for s in samples) / n
            avg_z = sum(s["z"] for s in samples) / n

            with self._lock:
                self._hist_x.append(avg_x)
                self._hist_y.append(avg_y)
                self._hist_z.append(avg_z)
                sx = sum(self._hist_x) / len(self._hist_x)
                sy = sum(self._hist_y) / len(self._hist_y)
                sz = sum(self._hist_z) / len(self._hist_z)
                self._smooth_x = sx
                self._smooth_y = sy
                self._smooth_z = sz
            cmd = self._classifier.classify(sx, sy, sz)

            if cmd.name != "NONE":
                print(f"--BLEbridge-- x={sx:.0f}  y={sy:.0f}  z={sz:.0f}  → {cmd.name}")

            try:
                command_queue.put_nowait(cmd)
            except queue.Full:
                pass   

            try:
                sample_queue.put_nowait(IMUSample(sx, sy, sz))
            except queue.Full:
                pass

        except Exception as exc:
            print(f"--BLEbridge-- PARSINMG ERROR !!! : {exc}")

