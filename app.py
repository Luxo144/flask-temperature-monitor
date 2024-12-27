from flask import Flask, jsonify
import random
import time
from threading import Thread
from datetime import datetime
from collections import deque

app = Flask(__name__)

# Variable global para almacenar la temperatura actual
current_temperature = 20.0

# Deque para almacenar el historial de temperaturas (máximo 100 registros)
temperature_history = deque(maxlen=100)

class TemperatureRecord:
    def __init__(self, temperature, timestamp):
        self.temperature = temperature
        self.timestamp = timestamp

    def to_dict(self):
        return {
            'temperature': self.temperature,
            'timestamp': self.timestamp.isoformat()
        }

def update_temperature():
    """Función que actualiza la temperatura cada 5 segundos"""
    global current_temperature
    while True:
        # Generar una temperatura aleatoria entre 15 y 35 grados
        current_temperature = round(random.uniform(15.0, 35.0), 1)
        # Guardar en el historial
        temperature_history.append(
            TemperatureRecord(current_temperature, datetime.now())
        )
        time.sleep(5)

# Iniciar el thread para actualizar la temperatura
temperature_thread = Thread(target=update_temperature, daemon=True)
temperature_thread.start()

@app.route('/temperature', methods=['GET'])
def get_temperature():
    """Endpoint para obtener la temperatura actual"""
    return jsonify({
        'temperature': current_temperature,
        'unit': 'Celsius',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/temperature/history', methods=['GET'])
def get_temperature_history():
    """Endpoint para obtener el historial de temperaturas"""
    history = [record.to_dict() for record in temperature_history]
    return jsonify({
        'history': history,
        'unit': 'Celsius',
        'count': len(history)
    })

@app.route('/temperature/statistics', methods=['GET'])
def get_temperature_statistics():
    """Endpoint para obtener estadísticas de temperatura"""
    if not temperature_history:
        return jsonify({
            'error': 'No hay datos suficientes para calcular estadísticas'
        }), 404
    
    temperatures = [record.temperature for record in temperature_history]
    return jsonify({
        'current': current_temperature,
        'average': round(sum(temperatures) / len(temperatures), 2),
        'minimum': min(temperatures),
        'maximum': max(temperatures),
        'sample_count': len(temperatures),
        'unit': 'Celsius'
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)