import serial

SERIAL_PORT = "COM3"
BAUD_RATE = 9600

def get_sensor_value():
    """
    Open serial, read one value, close immediately.
    Returns int on success, None on any failure.
    timeout=1 ensures no blocking.
    """
    ser = None
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        raw = ser.readline().decode("utf-8", errors="ignore").strip()
        if raw.replace(".", "", 1).lstrip("-").isdigit():
            return int(float(raw))
        return None
    except:
        return None
    finally:
        try:
            if ser and ser.is_open:
                ser.close()
        except Exception:
            pass
