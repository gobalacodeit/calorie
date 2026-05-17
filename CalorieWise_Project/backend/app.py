from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from calculator import CalorieCalculator
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, Literal

app = Flask(__name__)
CORS(app)

# Rate limiting setup
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per hour", "20 per minute"]
)

calculator = CalorieCalculator()


# Pydantic models for request validation
class CalculateRequest(BaseModel):
    age: int = Field(..., ge=15, le=100, description="Age in years (15-100)")
    gender: Literal['male', 'female'] = Field(..., description="Gender")
    weight: float = Field(..., gt=0, le=500, description="Weight value")
    height: float = Field(..., gt=0, description="Height value")
    activity: Literal['sedentary', 'light', 'moderate', 'active', 'extra_active'] = Field(
        ..., description="Activity level"
    )
    goal: Literal['lose_fast', 'lose', 'maintain', 'gain', 'gain_fast'] = Field(
        ..., description="Fitness goal"
    )
    weight_unit: Optional[Literal['kg', 'lbs']] = 'kg'
    height_unit: Optional[Literal['cm', 'ft']] = 'cm'
    
    @field_validator('age')
    @classmethod
    def validate_age(cls, v):
        if v < 15 or v > 100:
            raise ValueError('Age must be between 15 and 100')
        return v
    
    @model_validator(mode='after')
    def validate_weight(self):
        unit = self.weight_unit
        max_weight = 500 if unit == 'lbs' else 300
        min_weight = 30 if unit == 'kg' else 66
        if self.weight < min_weight or self.weight > max_weight:
            raise ValueError(f'Weight must be between {min_weight} and {max_weight} {unit}')
        return self


@app.route('/api/calculate', methods=['POST'])
@limiter.limit("10 per minute")
def calculate():
    """Calculate calories based on user input."""
    try:
        data = request.json
        
        # Validate using Pydantic
        req = CalculateRequest(**data)
        
        result = calculator.calculate_all(
            age=req.age,
            gender=req.gender,
            weight=req.weight,
            height=req.height,
            activity_level=req.activity,
            goal=req.goal,
            weight_unit=req.weight_unit,
            height_unit=req.height_unit
        )
        
        return jsonify({
            'success': True,
            'data': result,
            'timestamp': datetime.now().isoformat()
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': f'Validation error: {str(e)}'
        }), 400
    except KeyError as e:
        return jsonify({
            'success': False,
            'error': f'Missing required field: {str(e)}'
        }), 400
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

