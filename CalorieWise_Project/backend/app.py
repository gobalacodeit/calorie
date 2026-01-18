from flask import Flask, request, jsonify
from flask_cors import CORS
from calculator import CalorieCalculator
from datetime import datetime

app = Flask(__name__)
CORS(app)

calculator = CalorieCalculator()

@app.route('/api/calculate', methods=['POST'])
def calculate():
    """Calculate calories based on user input."""
    try:
        data = request.json
        
        result = calculator.calculate_all(
            age=data['age'],
            gender=data['gender'],
            weight=data['weight'],
            height=data['height'],
            activity_level=data['activity'],
            goal=data['goal'],
            weight_unit=data.get('weight_unit', 'kg'),
            height_unit=data.get('height_unit', 'cm')
        )
        
        return jsonify({
            'success': True,
            'data': result,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/macros', methods=['POST'])
def custom_macros():
    """Calculate custom macro distribution."""
    try:
        data = request.json
        calories = data['calories']
        ratios = data.get('ratios', {'protein': 0.30, 'carbs': 0.40, 'fats': 0.30})
        
        macros = calculator.calculate_macros(calories, ratios)
        
        return jsonify({
            'success': True,
            'data': macros
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/meal-plan', methods=['POST'])
def meal_plan():
    """Generate a meal plan based on calorie target."""
    try:
        data = request.json
        calories = data['calories']
        meals = data.get('meals', 4)
        
        plan = calculator.generate_meal_plan(calories, meals)
        
        return jsonify({
            'success': True,
            'data': plan
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'version': '1.0.0'})

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)

