from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

class ActivityLevel(Enum):
    SEDENTARY = 1.2
    LIGHT = 1.375
    MODERATE = 1.55
    ACTIVE = 1.725
    EXTRA_ACTIVE = 1.9

class Goal(Enum):
    LOSE_FAST = -1000
    LOSE = -500
    MAINTAIN = 0
    GAIN = 500
    GAIN_FAST = 1000

@dataclass
class NutritionResult:
    bmr: float
    tdee: float
    daily_calories: int
    bmi: float
    bmi_category: str
    macros: Dict[str, Any]
    meal_plan: Dict[str, int]
    weekly_deficit_surplus: int
    projected_weekly_change_kg: float

class CalorieCalculator:
    """
    Professional-grade calorie calculator using scientifically 
    validated formulas for accurate nutrition planning.
    """
    
    def __init__(self):
        self.activity_multipliers = {
            'sedentary': 1.2,
            'light': 1.375,
            'moderate': 1.55,
            'active': 1.725,
            'extra_active': 1.9
        }
        
        self.goal_adjustments = {
            'lose_fast': -1000,
            'lose': -500,
            'maintain': 0,
            'gain': 500,
            'gain_fast': 1000
        }
    
    def convert_weight(self, weight: float, from_unit: str) -> float:
        """Convert weight to kg."""
        if from_unit == 'lbs':
            return weight * 0.453592
        return weight
    
    def convert_height(self, height: float, from_unit: str, 
                       feet: int = 0, inches: int = 0) -> float:
        """Convert height to cm."""
        if from_unit == 'ft':
            return (feet * 30.48) + (inches * 2.54)
        return height
    
    def calculate_bmr_mifflin(self, weight_kg: float, height_cm: float, 
                               age: int, gender: str) -> float:
        """
        Calculate BMR using Mifflin-St Jeor Equation.
        Most accurate for most individuals.
        """
        if gender.lower() == 'male':
            bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
        else:
            bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161
        return bmr
    
    def calculate_tdee(self, bmr: float, activity_level: str) -> float:
        """Calculate Total Daily Energy Expenditure."""
        multiplier = self.activity_multipliers.get(activity_level, 1.2)
        return bmr * multiplier
    
    def calculate_bmi(self, weight_kg: float, height_cm: float) -> float:
        """Calculate Body Mass Index."""
        height_m = height_cm / 100
        return weight_kg / (height_m ** 2)
    
    def get_bmi_category(self, bmi: float) -> str:
        """Get BMI category based on value."""
        if bmi < 18.5:
            return 'Underweight'
        elif bmi < 25:
            return 'Normal'
        elif bmi < 30:
            return 'Overweight'
        else:
            return 'Obese'
    
    def calculate_macros(self, calories: int, 
                        ratios: Optional[Dict[str, float]] = None) -> Dict[str, Dict[str, Any]]:
        """Calculate macronutrient breakdown."""
        if ratios is None:
            ratios = {'protein': 0.30, 'carbs': 0.40, 'fats': 0.30}
        
        return {
            'protein': {
                'grams': round((calories * ratios['protein']) / 4),
                'percent': round(ratios['protein'] * 100)
            },
            'carbs': {
                'grams': round((calories * ratios['carbs']) / 4),
                'percent': round(ratios['carbs'] * 100)
            },
            'fats': {
                'grams': round((calories * ratios['fats']) / 9),
                'percent': round(ratios['fats'] * 100)
            }
        }
    
    def generate_meal_plan(self, calories: int, meals: int = 4) -> Dict[str, int]:
        """Generate a basic meal plan distribution."""
        if meals == 3:
            return {
                'breakfast': round(calories * 0.30),
                'lunch': round(calories * 0.40),
                'dinner': round(calories * 0.30)
            }
        elif meals == 5:
            return {
                'breakfast': round(calories * 0.25),
                'snack1': round(calories * 0.10),
                'lunch': round(calories * 0.30),
                'snack2': round(calories * 0.10),
                'dinner': round(calories * 0.25)
            }
        else:  # 4 meals (default)
            return {
                'breakfast': round(calories * 0.25),
                'lunch': round(calories * 0.35),
                'dinner': round(calories * 0.30),
                'snacks': round(calories * 0.10)
            }
    
    def calculate_weekly_change(self, daily_deficit_surplus: int) -> float:
        """Calculate projected weekly weight change in kg."""
        # 1 kg = 7700 calories
        return (daily_deficit_surplus * 7) / 7700
    
    def calculate_all(self, age: int, gender: str, weight: float, height: float,
                     activity_level: str, goal: str, 
                     weight_unit: str = 'kg', height_unit: str = 'cm') -> Dict[str, Any]:
        """
        Calculate all nutrition metrics at once.
        
        Args:
            age: Age in years
            gender: 'male' or 'female'
            weight: Weight value
            height: Height value
            activity_level: 'sedentary', 'light', 'moderate', 'active', 'extra_active'
            goal: 'lose_fast', 'lose', 'maintain', 'gain', 'gain_fast'
            weight_unit: 'kg' or 'lbs'
            height_unit: 'cm' or 'ft'
        
        Returns:
            Dictionary containing all calculated metrics
        """
        # Convert units
        weight_kg = self.convert_weight(weight, weight_unit)
        height_cm = self.convert_height(height, height_unit)
        
        # Calculate basic metrics
        bmr = self.calculate_bmr_mifflin(weight_kg, height_cm, age, gender)
        tdee = self.calculate_tdee(bmr, activity_level)
        bmi = self.calculate_bmi(weight_kg, height_cm)
        bmi_category = self.get_bmi_category(bmi)
        
        # Apply goal adjustment
        goal_adjustment = self.goal_adjustments.get(goal, 0)
        daily_calories = round(tdee + goal_adjustment)
        
        # Calculate macros
        macros = self.calculate_macros(daily_calories)
        
        # Generate meal plan
        meal_plan = self.generate_meal_plan(daily_calories)
        
        # Calculate weekly projections
        weekly_change = self.calculate_weekly_change(goal_adjustment)
        
        return {
            'bmr': round(bmr),
            'tdee': round(tdee),
            'daily_calories': daily_calories,
            'bmi': round(bmi, 1),
            'bmi_category': bmi_category,
            'macros': macros,
            'meal_plan': meal_plan,
            'weekly_deficit_surplus': goal_adjustment,
            'projected_weekly_change_kg': round(weekly_change, 2),
            'weight_kg': round(weight_kg, 1),
            'height_cm': round(height_cm, 1)
        }
