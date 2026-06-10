import json
import struct

# PACKET TYPES
TEMPERATURE = 10
FLASH_INFO = 12
DATALOSS = 15
SYSTEM_INFO = 16
BATTERY_INFO = 3
AUDIO_LEVEL = 6
ACC_GYRO_WAVEFORM = 17
PCK_BABY_ORIENTATION_INFO = 4
BREATH_WAVEFORM = 18
ECG_WAVEFORM_SIGNED = 19
R2R = 31
FIRMWARE_VERSION_TYPE_2 = 20
RECORDING_SESSION = 21
PLAYBACK_MEMORY = 22
SESSION_LISTING = 25
STRAINGAUGES_WAVEFORM = 27
BREATH_ANNOTATION = 28
STRAINGAUGES_MIXED_WAVEFORM = 29
AUDIO_SPECTRUM_HYSTOGRAM = 30


class AbstractPacketHandler():
    def __call__(self, data):
        # raise NotImplementedError(f"The handler for type {data[0]} is not implemented")
        print(f"The handler for type {data[0]} is not implemented")

    def to_json(self):
        # raise NotImplementedError()
        pass

class DataLossPacketHandler(AbstractPacketHandler):
    TYPE = DATALOSS
    TYPE_NAME = "dataloss"
    ID = "DATALOSS"

    def __call__(self, data):
        if data[0] != DataLossPacketHandler.TYPE:
            raise Exception(f"Wrong handler for type {data[0]} - expected {DataLossPacketHandler.TYPE}")
        self._value = data[1]
        return True

    def to_json(self):
        jsondict = {
            "type": DataLossPacketHandler.TYPE_NAME,
            "value": self._value
        }
        return json.dumps(jsondict)


class TemperaturePacketHandler(AbstractPacketHandler):
    TYPE = TEMPERATURE
    TYPE_NAME = "temperature"
    ID = "TEMPERATURE"

    def __call__(self, data):
        if data[0] != TemperaturePacketHandler.TYPE:
            raise Exception(f"Wrong handler for type {data[0]} - expected {TemperaturePacketHandler.TYPE}")
        self._timestamp = int.from_bytes(data[1:5], byteorder='little')
        self._temperature = int.from_bytes(data[5:7], byteorder='little')
        return True

    def to_json(self):
        jsondict = {
            "type": TemperaturePacketHandler.TYPE_NAME,
            "timestamp": self._timestamp,
            "temperature": self._temperature
        }
        return json.dumps(jsondict)

class FlashInfoPacketHandler(AbstractPacketHandler):
    TYPE = FLASH_INFO
    TYPE_NAME = "flash_info"
    ID = "FLASH_INFO"

    def __call__(self, data):
        if data[0] != FlashInfoPacketHandler.TYPE:
            raise Exception(f"Wrong handler for type {data[0]} - expected {FlashInfoPacketHandler.TYPE}")
        self._status = data[1]
        self._device_status = data[2]
        self._total_bytes = int.from_bytes(data[3:7], byteorder='little')
        self._ndx_wrpointer = int.from_bytes(data[7:11], byteorder='little')
        return True

    def to_json(self):
        jsondict = {
            "type": FlashInfoPacketHandler.TYPE_NAME,
            "status": self._status,
            "device status": self._device_status,
            "total bytes": self._total_bytes,
            "pointer": self._ndx_wrpointer
        }
        return json.dumps(jsondict)

class BabyOrientationPacketHandler(AbstractPacketHandler):
    TYPE = PCK_BABY_ORIENTATION_INFO
    TYPE_NAME = "baby orientation"
    ID = "BABY_ORIENTATION"

    def __call__(self, data):
        if data[0] != BabyOrientationPacketHandler.TYPE:
            raise Exception(f"Wrong handler for type {data[0]} - expected {BabyOrientationPacketHandler.TYPE}")
        self._timestamp = int.from_bytes(data[1:5], byteorder='little')
        self._orientation = data[5]
        return True

    def to_json(self):
        jsondict = {
            "type": BabyOrientationPacketHandler.TYPE_NAME,
            "timestamp": self._timestamp,
            "orientation": self._orientation
        }
        return json.dumps(jsondict)


class BreathAnnotationPacketHandler(AbstractPacketHandler):
    TYPE = BREATH_ANNOTATION
    TYPE_NAME = "breath"
    ID = "BREATH_ANNOTATION"

    def __call__(self, data):
        if data[0] != BreathAnnotationPacketHandler.TYPE:
            raise Exception(f"Wrong handler for type {data[0]} - expected {BreathAnnotationPacketHandler.TYPE}")

        self._timestamp = int.from_bytes(data[1:5], byteorder='little')
        self._samplenum = int.from_bytes(data[5:9], byteorder='little')
        self._breathreate = int.from_bytes(data[9:11], byteorder='little')
        self._filter_type = data[11]
        return True

    def to_json(self):
        jsondict = {
            "type": BreathAnnotationPacketHandler.TYPE_NAME,
            "timestamp": self._timestamp,
            "samplenum": self._samplenum,
            "breathrate": self._breathreate,
            "filter type": self._filter_type
        }
        return json.dumps(jsondict)

class BatteryInfoPacketHandler(AbstractPacketHandler):
    TYPE = BATTERY_INFO
    TYPE_NAME = "battery"
    ID = "BATTERY_INFO"

    def __call__(self, data):
        if data[0] != BatteryInfoPacketHandler.TYPE:
            raise Exception(f"Wrong handler for type {data[0]} - expected {BatteryInfoPacketHandler.TYPE}")
        self._charging = data[1]
        self._temperature = int.from_bytes(data[2:4], byteorder='little')
        self._voltage = int.from_bytes(data[4:6], byteorder='little')
        self._fac = int.from_bytes(data[6:8], byteorder='little')
        self._nac = int.from_bytes(data[8:10], byteorder='little')
        self._rm = int.from_bytes(data[10:12], byteorder='little')
        self._ai = int.from_bytes(data[12:14], byteorder='little')
        self._soc = int.from_bytes(data[14:16], byteorder='little')
        return True

    def to_json(self):
        jsondict = {
            "type": BatteryInfoPacketHandler.TYPE_NAME,
            "charging": self._charging,
            "temperature": self._temperature,
            "voltage": self._voltage,
            "full actual capacity": self._fac,
            "nominal capacity": self._nac,
            "remaining capacity": self._rm,
            "average current":self._ai,
            "state of charge": self._soc
        }
        return json.dumps(jsondict)


class R2RPacketHandler(AbstractPacketHandler):
    TYPE = R2R
    TYPE_NAME = "r2r"
    ID = "R2R"

    def __call__(self, data):
        if data[0] != R2RPacketHandler.TYPE:
            raise Exception(f"Wrong handler for type {data[0]} - expected {R2RPacketHandler.TYPE}")

        self._timestamp = int.from_bytes(data[1:5], byteorder='little')
        self._samplenum = int.from_bytes(data[5:9], byteorder='little')
        self._heartrate = int.from_bytes(data[9:11], byteorder='little')
        self._period = int.from_bytes(data[11:13], byteorder='little')
        self._status = data[13]
        return True

    def to_json(self):
        jsondict = {
            "type": R2RPacketHandler.TYPE_NAME,
            "timestamp": self._timestamp,
            "samplenum": self._samplenum,
            "heartrate": self._heartrate,
            "period": self._period,
            "status": self._status
        }
        return json.dumps(jsondict)


class FirmwareVersionPacketHandler(AbstractPacketHandler):
    TYPE = FIRMWARE_VERSION_TYPE_2
    TYPE_NAME = "firmware version"
    ID = "FIRMWARE_VERSION"

    def __call__(self, data):
        if data[0] != FirmwareVersionPacketHandler.TYPE:
            raise Exception(f"Wrong handler for type {data[0]} - expected {FirmwareVersionPacketHandler.TYPE}")

        self._major = data[1]
        self._minor = data[2]
        self._revision = data[3]
        self._blmajor = data[4]
        self._blminor = data[5]
        self._blrevision = data[6]
        self._hw = data[7]

        return True

    def to_json(self):
        jsondict = {
            "type": FirmwareVersionPacketHandler.TYPE_NAME,
            "major": self._major,
            "minor": self._minor,
            "revision": self._revision,
            "bootloader major": self._blmajor,
            "bootloader minor": self._blminor,
            "bootloader revision": self._blrevision,
            "hardware": self._hw,
        }
        return json.dumps(jsondict)


class SystemInfoPacketHandler(AbstractPacketHandler):
    TYPE = SYSTEM_INFO
    TYPE_NAME = "system info"
    ID = "SYSTEM_INFO"

    def __call__(self, data):
        if data[0] != SystemInfoPacketHandler.TYPE:
            raise Exception(f"Wrong handler for type {data[0]} - expected {SystemInfoPacketHandler.TYPE}")

        self._timestamp = int.from_bytes(data[1:5], byteorder='little')
        self._sampleperiod = int.from_bytes(data[5:7], byteorder='little')
        self._demo_mode = data[7]
        self._acc_enabled = data[8]
        self._enable_battery = data[9]
        self._mems_mode = data[10]
        self._led_mode = data[11]
        self._enable_press = data[12]
        self._enable_temperature = data[13]
        self._enable_ecg = data[14]
        self._enable_bio = data[15]
        self._ecg_frequency = data[16]
        self._egc_dhpf_filter_enabled = data[17]
        self._ecg_dlpf_filter = data[18]
        self._ecg_gain = data[19]
        self._ecg_polarity = data[20]
        self._bio_rnom = data[21]
        self._bio_rmod = data[22]
        self._bio_fcgen = data[23]
        self._bio_dhpf = data[24]
        self._bio_dlpf = data[25]
        self._bio_gain = data[26]
        self._bio_frequency = data[27]
        self._bio_cmag = data[28]
        self._bio_phoff = data[29]
        self._r_gain = data[30]
        self._bio_ahpf = data[31]
        self._press_filter_type = data[32]
        self._press_data_type = data[33]
        self._press_type_packet_to_send = data[34]
        self._press_thr_filter = data[35]
        self._enable_spectrum = data[36]
        self._enable_r2r = data[37]
        self._enable_orientation = data[38]
        self._lead_on = data[39]
        self._lead_off = data[40]
        self._sensor_status = data[41]
        self._lead_on_counter = data[42]
        self._lead_off_counter = data[43]
        return True

    def to_json(self):
        jsondict = {
            "type": SystemInfoPacketHandler.TYPE_NAME,
            "timestamp": self._timestamp,
            "demo": self._demo_mode,
            "accelerometer": self._acc_enabled,
            "battery": self._enable_battery,
            "mems mode": self._mems_mode,
            "led mode": self._led_mode,
            "pressure": self._enable_press,
            "temperature": self._enable_temperature,
            "ecg": self._enable_ecg,
            "bio": self._enable_bio,
            "r2r": self._enable_r2r,
            "orientation": self._enable_orientation,
            "spectrum": self._enable_spectrum,
            "ecg frequency": self._ecg_frequency,
            "ecg dhpf filter": self._egc_dhpf_filter_enabled,
            "ecg dlpf filter": self._ecg_dlpf_filter,
            "ecg gain": self._ecg_gain,
            "ecg polarity": self._ecg_polarity,
            "bio rnom": self._bio_rnom,
            "bio rmod": self._bio_rmod,
            "bio fcgen": self._bio_fcgen,
            "bio dhpf": self._bio_dhpf,
            "bio dlpf": self._bio_dlpf,
            "lead on": self._lead_on,
            "lead off": self._lead_off
        }
        return json.dumps(jsondict)


class ECGPacketHandler(AbstractPacketHandler):
    TYPE = ECG_WAVEFORM_SIGNED
    TYPE_NAME = "ecg"
    ID = "ECG"
    SAMPLES = 128
    VREF = 1000
    BITADC = 17
    ECGGAIN = 20

    def __call__(self, data):
        if data[0] != ECGPacketHandler.TYPE:
            raise Exception(f"Wrong handler for type {data[0]} - expected {ECGPacketHandler.TYPE}")

        self._timestamp = int.from_bytes(data[1:5], byteorder='little')
        self._samplenum = int.from_bytes(data[5:9], byteorder='little')
        self._frequency = int.from_bytes(data[9:11], byteorder='little')
        self._heartrate = int.from_bytes(data[11:13], byteorder='little')
        self._period = int.from_bytes(data[13:15], byteorder='little')
        self._status = data[15]

        self._samples = []

        datacount = 16
        for n in range(ECGPacketHandler.SAMPLES):
            value = int.from_bytes(data[datacount:datacount + 4], byteorder='little', signed=True)
            ecgmv = (value * ECGPacketHandler.VREF)/(pow(2,ECGPacketHandler.BITADC)*ECGPacketHandler.ECGGAIN)
            self._samples.append(ecgmv)
            datacount += 4

        return True

    def to_json(self):
        jsondict = {
            "type": ECGPacketHandler.TYPE_NAME,
            "timestamp": self._timestamp,
            "samplenum": self._samplenum,
            "frequency:": self._frequency,
            "heartrate": self._heartrate,
            "period": self._period,
            "status": self._status,
            "samples": self._samples
        }
        return json.dumps(jsondict)


class BreathWaveformPacketHandler(AbstractPacketHandler):
    TYPE = BREATH_WAVEFORM
    TYPE_NAME = "breath waveform"
    ID = "BREATH_WAVEFORM"
    SAMPLES = 64

    def __call__(self, data):
        if data[0] != BreathWaveformPacketHandler.TYPE:
            raise Exception(f"Wrong handler for type {data[0]} - expected {BreathWaveformPacketHandler.TYPE}")

        self._timestamp = int.from_bytes(data[1:5], byteorder='little')
        self._samplenum = int.from_bytes(data[5:9], byteorder='little')
        self._frequency = int.from_bytes(data[9:11], byteorder='little')
        self._breathrate = int.from_bytes(data[11:13], byteorder='little')
        self._status = data[13]
        self._samples = []

        datacount = 14
        for n in range(BreathWaveformPacketHandler.SAMPLES):
            self._samples.append(int.from_bytes(data[datacount:datacount + 4], byteorder='little'))
            datacount += 4

        return True

    def to_json(self):
        jsondict = {
            "type": BreathWaveformPacketHandler.TYPE_NAME,
            "timestamp": self._timestamp,
            "samplenum": self._samplenum,
            "frequency:": self._frequency,
            "breathrate": self._breathrate,
            "status": self._status,
            "samples": self._samples
        }
        return json.dumps(jsondict)


class StraingaugesWaveformPacketHandler(AbstractPacketHandler):
    TYPE = STRAINGAUGES_WAVEFORM
    TYPE_NAME = "straingauges waveform"
    ID = "STRAINGAUGES_WAVEFORM"
    SAMPLES = 13

    def __call__(self, data):
        if data[0] != StraingaugesWaveformPacketHandler.TYPE:
            raise Exception(f"Wrong handler for type {data[0]} - expected {StraingaugesWaveformPacketHandler.TYPE}")

        self._timestamp = int.from_bytes(data[1:5], byteorder='little')
        self._samplenum = int.from_bytes(data[5:9], byteorder='little')
        self._sample_period_press = int.from_bytes(data[9:11], byteorder='little')
        self._breathrate = int.from_bytes(data[11:13], byteorder='little')
        self._filter_type = data[13]
        self._data_type = data[14]
        self._samples = []

        datacount = 15
        for n in range(StraingaugesWaveformPacketHandler.SAMPLES):
            self._samples.append(int.from_bytes(data[datacount:datacount + 4], byteorder='little'))
            datacount += 4

        return True

    def to_json(self):
        jsondict = {
            "type": StraingaugesWaveformPacketHandler.TYPE_NAME,
            "timestamp": self._timestamp,
            "samplenum": self._samplenum,
            "sample period press:": self._sample_period_press,
            "breathrate": self._breathrate,
            "filter type": self._filter_type,
            "data type": self._data_type,
            "samples": self._samples
        }
        return json.dumps(jsondict)


class StraingaugesMixedWaveformPacketHandler(AbstractPacketHandler):
    TYPE = STRAINGAUGES_MIXED_WAVEFORM
    TYPE_NAME = "straingauges waveform"
    ID = "STRAINGAUGES_MIXED"
    SAMPLES = 13

    def __call__(self, data):
        if data[0] != StraingaugesMixedWaveformPacketHandler.TYPE:
            raise Exception(f"Wrong handler for type {data[0]} - expected {StraingaugesMixedWaveformPacketHandler.TYPE}")

        self._timestamp = int.from_bytes(data[1:5], byteorder='little')
        self._samplenum = int.from_bytes(data[5:9], byteorder='little')
        self._sample_period_press = int.from_bytes(data[9:11], byteorder='little')
        self._breathrate = int.from_bytes(data[11:13], byteorder='little')
        self._filter_type = data[13]
        self._data_type = data[14]
        self._samples_1 = []
        self._samples_2 = []
        self._samples_3 = []

        datacount = 15
        for n in range(StraingaugesMixedWaveformPacketHandler.SAMPLES):
            self._samples_1.append(int.from_bytes(data[datacount:datacount + 4], byteorder='little'))
            datacount += 4

        for n in range(StraingaugesMixedWaveformPacketHandler.SAMPLES):
            self._samples_2.append(int.from_bytes(data[datacount:datacount + 4], byteorder='little'))
            datacount += 4

        for n in range(StraingaugesMixedWaveformPacketHandler.SAMPLES):
            self._samples_3.append(int.from_bytes(data[datacount:datacount + 4], byteorder='little'))
            datacount += 4

        return True

    def to_json(self):
        jsondict = {
            "type": StraingaugesMixedWaveformPacketHandler.TYPE_NAME,
            "timestamp": self._timestamp,
            "samplenum": self._samplenum,
            "sample period press:": self._sample_period_press,
            "breathrate": self._breathrate,
            "filter type": self._filter_type,
            "data type": self._data_type,
            "samples 1": self._samples_1,
            "samples 2": self._samples_2,
            "samples 3": self._samples_3
        }
        return json.dumps(jsondict)


class AccGyroWaveform(AbstractPacketHandler):
    TYPE = ACC_GYRO_WAVEFORM
    TYPE_NAME = "accgyro"
    ID = "ACC_GYRO"
    SAMPLES = 16

    def __call__(self, data):
        if data[0] != AccGyroWaveform.TYPE:
            raise Exception(f"Wrong handler for type {data[0]} - expected {AccGyroWaveform.TYPE}")

        self._timestamp = int.from_bytes(data[1:5], byteorder='little')
        self._samplenum = int.from_bytes(data[5:9], byteorder='little')
        self._sample_frequency_mems = data[9]
        self._orientation = data[10]
        self._samples = []

        datacount = 11
        for n in range(AccGyroWaveform.SAMPLES):
            value = struct.unpack('<hhh', data[datacount:datacount + 6])
            self._samples.append(value)
            datacount += 6

        return True


    def to_json(self):
        jsondict = {
            "type": AccGyroWaveform.TYPE_NAME,
            "timestamp": self._timestamp,
            "samplenum": self._samplenum,
            "sampling frequency": self._sample_frequency_mems,
            "orientation": self._orientation,
            "samples" : []
        }

        for sample in  self._samples:
            jsondict['samples'].append(
                {
                    "x": sample[0],
                    "y": sample[1],
                    "z": sample[2],
                }
            )

        return json.dumps(jsondict)

handler_factory_table = {
    TEMPERATURE: TemperaturePacketHandler,
    FLASH_INFO: FlashInfoPacketHandler,
    DATALOSS: DataLossPacketHandler,
    SYSTEM_INFO: SystemInfoPacketHandler,
    BATTERY_INFO: BatteryInfoPacketHandler,
    ACC_GYRO_WAVEFORM: AccGyroWaveform,
    PCK_BABY_ORIENTATION_INFO: BabyOrientationPacketHandler,
    BREATH_WAVEFORM: BreathWaveformPacketHandler,
    ECG_WAVEFORM_SIGNED: ECGPacketHandler,
    R2R: R2RPacketHandler,
    FIRMWARE_VERSION_TYPE_2: FirmwareVersionPacketHandler,
    RECORDING_SESSION: AbstractPacketHandler,
    PLAYBACK_MEMORY: AbstractPacketHandler,
    SESSION_LISTING: AbstractPacketHandler,
    STRAINGAUGES_WAVEFORM: StraingaugesWaveformPacketHandler,
    BREATH_ANNOTATION: BreathAnnotationPacketHandler,
    STRAINGAUGES_MIXED_WAVEFORM: StraingaugesMixedWaveformPacketHandler,
    AUDIO_SPECTRUM_HYSTOGRAM: AbstractPacketHandler,
}
