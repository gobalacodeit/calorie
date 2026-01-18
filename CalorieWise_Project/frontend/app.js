// app.js

// DOM Elements
const form = document.getElementById('calorie-form');
const resultsSection = document.getElementById('results');
const tabButtons = document.querySelectorAll('.tab-btn');
const tabContents = document.querySelectorAll('.tab-content');

// Charts
let macrosChart = null;
let projectionChart = null;

// Activity Multipliers
const ACTIVITY_MULTIPLIERS = {
    sedentary: 1.2,
    light: 1.375,
    moderate: 1.55,
    active: 1.725,
    extra_active: 1.9
};

// Goal Adjustments (calories)
const GOAL_ADJUSTMENTS = {
    lose_fast: -1000,
    lose: -500,
    maintain: 0,
    gain: 500,
    gain_fast: 1000
};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initializeTabs();
    initializeUnitToggles();
    loadHistory();
});

// Tab Navigation
function initializeTabs() {
    tabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabId = btn.dataset.tab;
            
            // Update buttons
            tabButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            // Update content
            tabContents.forEach(content => {
                content.classList.remove('active');
                if (content.id === tabId) {
                    content.classList.add('active');
                }
            });
        });
    });
}

// Unit Toggles
function initializeUnitToggles() {
    const heightUnitSelect = document.getElementById('height-unit');
    const heightInput = document.getElementById('height');
    const imperialHeight = document.querySelector('.height-imperial');
    
    heightUnitSelect.addEventListener('change', (e) => {
        if (e.target.value === 'ft') {
            heightInput.parentElement.style.display = 'none';
            imperialHeight.style.display = 'grid';
        } else {
            heightInput.parentElement.style.display = 'flex';
            imperialHeight.style.display = 'none';
        }
    });
}

// Form Submission
form.addEventListener('submit', (e) => {
    e.preventDefault();
    calculateCalories();
});

// Main Calculation Function
    async function calculateCalories() {
    const payload = {
        age: parseInt(document.getElementById('age').value),
        gender: document.querySelector('input[name="gender"]:checked').value,
        weight: parseFloat(document.getElementById('weight').value),
        height: parseFloat(document.getElementById('height').value),
        activity: document.querySelector('input[name="activity"]:checked').value,
        goal: document.querySelector('input[name="goal"]:checked').value
    };

    try {
        const response = await fetch("https://calorie-ybhs.onrender.com/api/calculate", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });

        const result = await response.json();

        if (!result.success) {
            alert(result.error || "Calculation failed");
            return;
        }

        displayResults(result.data);

    } catch (error) {
        alert("Backend not reachable");
        console.error(error);
    }
}

    // Get height in cm
    let height;
    if (heightUnit === 'ft') {
        const feet = parseInt(document.getElementById('height-ft').value) || 0;
        const inches = parseInt(document.getElementById('height-in').value) || 0;
        height = (feet * 30.48) + (inches * 2.54);
    } else {
        height = parseFloat(document.getElementById('height').value);
    }
    
    // Calculate BMR using Mifflin-St Jeor Equation
    let bmr;
    if (gender === 'male') {
        bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5;
    } else {
        bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161;
    }
    
    // Calculate TDEE
    const tdee = bmr * ACTIVITY_MULTIPLIERS[activity];
    
    // Apply goal adjustment
    const dailyCalories = Math.round(tdee + GOAL_ADJUSTMENTS[goal]);
    
    // Calculate BMI
    const heightInMeters = height / 100;
    const bmi = weight / (heightInMeters * heightInMeters);
    
    // Calculate Macros (default: 30% protein, 40% carbs, 30% fat)
    const macros = calculateMacros(dailyCalories);
    
    // Display results
    displayResults({
        bmr: Math.round(bmr),
        tdee: Math.round(tdee),
        dailyCalories,
        bmi: bmi.toFixed(1),
        macros,
        weight,
        goal
    });
}

// Calculate Macronutrients
function calculateMacros(calories, ratios = { protein: 0.30, carbs: 0.40, fats: 0.30 }) {
    return {
        protein: {
            grams: Math.round((calories * ratios.protein) / 4),
            percent: Math.round(ratios.protein * 100)
        },
        carbs: {
            grams: Math.round((calories * ratios.carbs) / 4),
            percent: Math.round(ratios.carbs * 100)
        },
        fats: {
            grams: Math.round((calories * ratios.fats) / 9),
            percent: Math.round(ratios.fats * 100)
        }
    };
}

// Display Results
function displayResults(data) {
    // Show results section
    resultsSection.style.display = 'block';
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    
    // Update calorie values
    animateNumber('daily-calories', data.dailyCalories);
    document.getElementById('bmr-value').textContent = `${data.bmr} kcal`;
    document.getElementById('tdee-value').textContent = `${data.tdee} kcal`;
    
    // Update macros
    document.getElementById('protein-grams').textContent = `${data.macros.protein.grams}g`;
    document.getElementById('protein-percent').textContent = `${data.macros.protein.percent}%`;
    document.getElementById('carbs-grams').textContent = `${data.macros.carbs.grams}g`;
    document.getElementById('carbs-percent').textContent = `${data.macros.carbs.percent}%`;
    document.getElementById('fats-grams').textContent = `${data.macros.fats.grams}g`;
    document.getElementById('fats-percent').textContent = `${data.macros.fats.percent}%`;
    
    // Update BMI
    document.getElementById('bmi-value').textContent = data.bmi;
    const bmiCategory = getBMICategory(parseFloat(data.bmi));
    document.getElementById('bmi-category').textContent = bmiCategory.label;
    document.getElementById('bmi-category').style.color = bmiCategory.color;
    
    // Position BMI indicator
    const bmiIndicator = document.getElementById('bmi-indicator');
    const bmiPosition = Math.min(Math.max((parseFloat(data.bmi) - 15) / 25 * 100, 0), 100);
    bmiIndicator.style.left = `${bmiPosition}%`;
    
    // Update meal breakdown
    document.getElementById('breakfast-cal').textContent = `${Math.round(data.dailyCalories * 0.25)} kcal`;
    document.getElementById('lunch-cal').textContent = `${Math.round(data.dailyCalories * 0.35)} kcal`;
    document.getElementById('dinner-cal').textContent = `${Math.round(data.dailyCalories * 0.30)} kcal`;
    document.getElementById('snacks-cal').textContent = `${Math.round(data.dailyCalories * 0.10)} kcal`;
    
    // Create charts
    createMacrosChart(data.macros);
    createProjectionChart(data);
    
    // Store current results for saving
    window.currentResults = data;
}

// Get BMI Category
function getBMICategory(bmi) {
    if (bmi < 18.5) return { label: 'Underweight', color: '#4ECDC4' };
    if (bmi < 25) return { label: 'Normal', color: '#2ECC71' };
    if (bmi < 30) return { label: 'Overweight', color: '#F39C12' };
    return { label: 'Obese', color: '#E74C3C' };
}

// Animate Number
function animateNumber(elementId, target) {
    const element = document.getElementById(elementId);
    const duration = 1000;
    const start = 0;
    const startTime = performance.now();
    
    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        // Easing function
        const easeOut = 1 - Math.pow(1 - progress, 3);
        const current = Math.round(start + (target - start) * easeOut);
        
        element.textContent = current.toLocaleString();
        
        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }
    
    requestAnimationFrame(update);
}

// Create Macros Chart
function createMacrosChart(macros) {
    const ctx = document.getElementById('macros-canvas').getContext('2d');
    
    if (macrosChart) {
        macrosChart.destroy();
    }
    
    macrosChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Protein', 'Carbs', 'Fats'],
            datasets: [{
                data: [macros.protein.percent, macros.carbs.percent, macros.fats.percent],
                backgroundColor: ['#FF6B6B', '#4ECDC4', '#FFE66D'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            cutout: '65%',
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

// Create Projection Chart
function createProjectionChart(data) {
    const ctx = document.getElementById('projection-chart').getContext('2d');
    
    if (projectionChart) {
        projectionChart.destroy();
    }
    
    // Calculate weekly weight projections
    const weeks = 12;
    const weeklyChange = GOAL_ADJUSTMENTS[data.goal] * 7 / 7700; // kg per week
    const projectedWeights = [];
    const labels = [];
    
    for (let i = 0; i <= weeks; i++) {
        labels.push(`Week ${i}`);
        projectedWeights.push((data.weight + (weeklyChange * i)).toFixed(1));
    }
    
    projectionChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Projected Weight (kg)',
                data: projectedWeights,
                borderColor: '#FF6B6B',
                backgroundColor: 'rgba(255, 107, 107, 0.1)',
                fill: true,
                tension: 0.4,
                pointBackgroundColor: '#FF6B6B',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    grid: {
                        color: 'rgba(0,0,0,0.05)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

// Reset Calculator
function resetCalculator() {
    form.reset();
    resultsSection.style.display = 'none';
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Save Results
function saveResults() {
    if (!window.currentResults) return;
    
    const results = window.currentResults;
    const timestamp = new Date().toLocaleString();
    
    const historyItem = {
        timestamp,
        calories: results.dailyCalories,
        bmi: results.bmi,
        goal: results.goal
    };
    
    let history = JSON.parse(localStorage.getItem('calorieHistory')) || [];
    history.unshift(historyItem);
    history = history.slice(0, 20); // Keep only last 20
    
    localStorage.setItem('calorieHistory', JSON.stringify(history));
    loadHistory();
    
    alert('Results saved successfully!');
}

// Load History
function loadHistory() {
    const historyList = document.getElementById('history-list');
    const history = JSON.parse(localStorage.getItem('calorieHistory')) || [];
    
    if (history.length === 0) {
        historyList.innerHTML = '<p class="empty-state">No calculations saved yet. Complete a calculation and save it!</p>';
        return;
    }
    
    historyList.innerHTML = history.map((item, index) => `
        <div class="history-item">
            <div class="history-info">
                <div class="history-date">${item.timestamp}</div>
                <div class="history-calories">${item.calories} kcal/day</div>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 0.85rem; color: #95A5A6;">BMI: ${item.bmi}</div>
                <div style="font-size: 0.85rem; color: #95A5A6; text-transform: capitalize;">${item.goal}</div>
            </div>
        </div>
    `).join('');
}

// Share Results
function shareResults() {
    if (!window.currentResults) return;
    
    const results = window.currentResults;
    const text = `I calculated my daily calorie needs: ${results.dailyCalories} kcal/day with a BMI of ${results.bmi}. Try CalorieWise to calculate yours!`;
    
    if (navigator.share) {
        navigator.share({
            title: 'CalorieWise Results',
            text: text
        });
    } else {
        alert(text);
    }
}

// Print Results
function printResults() {
    window.print();
}
