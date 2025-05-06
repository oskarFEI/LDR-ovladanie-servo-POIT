from threading import Lock
from flask import Flask, render_template, session, request, jsonify, url_for
from flask_socketio import SocketIO, emit, disconnect    
import time
import random
import math 
import serial   # potrebne na seriovu komunikaciu

async_mode = None

app = Flask(__name__)   # nastavenie flasku
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock() 
sendData = False #
systemOpen = False

ser = serial.Serial("/dev/ttyS0", 9600)  # Adjust COM port and baud rate

def background_thread(args):
    count = 0    
    dataList = []          
    while True:
        line = ser.readline().decode().strip()
        if line:
            parts = line.split(",")
            if len(parts) == 3:
                analog = int(parts[0])
                lux = int(parts[1])
                angle = int(parts[2])
                print(f"Analog: {analog}, Lux: {lux}, Servo: {angle}")

        count += 1

        dataDict = {
          "RES": analog,
          "LUX": lux,
          "ANG": angle}

        if sendData and systemOpen:  
            socketio.emit('my_response',
                        {'data': str(dataDict), 'count': count},
                        namespace='/test')

@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)
  
@socketio.on('my_event', namespace='/test')
def test_message(message):   
    session['receive_count'] = session.get('receive_count', 0) + 1 
    session['A'] = message['value']    
    emit('my_response',
         {'data': message['value'], 'count': session['receive_count']})
 
@socketio.on('disconnect_request', namespace='/test')
def disconnect_request():
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'Disconnected!', 'count': session['receive_count']})
    disconnect()

@socketio.on('connect', namespace='/test')
def test_connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=background_thread, args=session._get_current_object())
    emit('my_response', {'data': 'Connected', 'count': 0})

@socketio.on('click_event', namespace='/test')
def db_message(message):   
    session['btn_value'] = message['value']    

@socketio.on('send_data', namespace='/test')
def start_sending_data(message):
    global sendData
    sendData = True  # Set send_data to True to start sending data
    emit('my_response', {'data': 'Started sending data', 'count': 0})

@socketio.on('stop_data', namespace='/test')
def stop_sending_data(message):
    global sendData
    sendData = False  # Set send_data to False to stop sending data
    emit('my_response', {'data': 'Stopped sending data', 'count': 0})

@socketio.on('open_system', namespace='/test')
def open_system_handler(message):
    global systemOpen
    systemOpen = True
    emit('my_response', {'data': 'System initialized, receiving enabled.', 'count': 0})

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected', request.sid)


if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=80, debug=True)
