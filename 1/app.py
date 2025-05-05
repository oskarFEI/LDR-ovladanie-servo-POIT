import serial

ser = serial.Serial("/dev/ttyS0", 9600)  # Adjust COM port and baud rate

while True:
    line = ser.readline().decode().strip()
    if line:
        parts = line.split(",")
        if len(parts) == 3:
            analog = int(parts[0])
            lux = float(parts[1])
            angle = int(parts[2])
            print(f"Analog: {analog}, Lux: {lux}, Servo: {angle}")
