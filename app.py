from flask import Flask, jsonify
from datetime import datetime
import pytz
from kerykeion import AstrologicalSubject
from kerykeion.aspects import NatalAspects

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        'status': 'ok',
        'message': 'Astrology Transit API',
        'endpoints': {
            '/transits': 'GET - Calculate daily transits for Moscow'
        }
    })

@app.route('/transits', methods=['GET'])
def get_transits():
    """
    Рассчитывает транзиты на текущий момент для Москвы
    """
    try:
        # Получаем текущую дату и время для Москвы
        moscow_tz = pytz.timezone('Europe/Moscow')
        now = datetime.now(moscow_tz)
        
        # Создаём астрологический субъект
        transit_chart = AstrologicalSubject(
            name="Daily Transit",
            year=now.year,
            month=now.month,
            day=now.day,
            hour=now.hour,
            minute=now.minute,
            city="Moscow",
            nation="RU",
            lat=55.7558,
            lng=37.6173,
            tz_str="Europe/Moscow"
        )
        
        # Получаем позиции планет
        planets_data = {}
        for planet in transit_chart.planets_list:
            planets_data[planet['name']] = {
                'sign': planet['sign'],
                'position': round(planet['position'], 2),
                'retrograde': planet['retrograde']
            }
        
        # Рассчитываем аспекты
        aspects_calculator = NatalAspects(transit_chart)
        aspects_list = []
        
        for aspect in aspects_calculator.all_aspects:
            aspects_list.append({
                'planet1': aspect['p1_name'],
                'planet2': aspect['p2_name'],
                'aspect': aspect['aspect'],
                'orb': round(aspect['orb'], 2)
            })
        
        # Только значимые аспекты (орб < 3°)
        major_aspects = [a for a in aspects_list if a['orb'] < 3.0]
        
        # Лунная фаза
        moon_phase = transit_chart.lunar_phase
        
        result = {
            'success': True,
            'date': now.strftime('%d.%m.%Y'),
            'time': now.strftime('%H:%M'),
            'planets': planets_data,
            'major_aspects': major_aspects,
            'moon_phase': {
                'phase_name': moon_phase['moon_phase']
            }
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
