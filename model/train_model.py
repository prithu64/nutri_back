# scripts/train_model.py
"""
ML Benchmarking Script for NutriSnap
Compares RandomForest, HistGradientBoosting, and XGBoost!
"""

import pandas as pd
import time
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline

# The Contenders
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from xgboost import XGBClassifier

print("=" * 60)
print("NUTRISNAP - AUTOMATED ML BENCHMARKING ENGINE")
print("=" * 60)

print("\n[STEP 1] Loading Massive Dataset from Kaggle (500k rows)...")
df = pd.read_csv('data/en.openfoodfacts.org.products.tsv', 
                 delimiter='\t', 
                 nrows=500000,
                 on_bad_lines='skip',
                 low_memory=False)
print(f"  Loaded {len(df)} products!")

print("\n[STEP 2] Selecting 8 Features & Cleaning Data...")
features = ['energy_100g', 'fat_100g', 'sugars_100g', 'sodium_100g', 
            'proteins_100g', 'fiber_100g', 'saturated-fat_100g', 'carbohydrates_100g']

available_features = [f for f in features if f in df.columns]
if len(available_features) < 8:
    features = available_features

# Drop rows where the target grade is missing
df = df.dropna(subset=['nutrition_grade_fr'])

# Convert Labels (A=4, B=3, C=2, D=1, E=0)
grade_map = {'a': 4, 'b': 3, 'c': 2, 'd': 1, 'e': 0}
df['target'] = df['nutrition_grade_fr'].str.lower().map(grade_map)
df = df.dropna(subset=['target'])
print(f"  Final usable products for training: {len(df)}")

print("\n[STEP 3] Splitting Data into Training and Testing Sets...")
X = df[features]
y = df['target'].astype(int)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("\n[STEP 4] Initiating Algorithm Deathmatch...")

# Define Models
models = {
    "Random Forest": Pipeline([
        ('imputer', SimpleImputer(strategy='mean')), # RF crashes on missing data, so we impute!
        ('model', RandomForestClassifier(n_estimators=50, max_depth=12, n_jobs=-1, random_state=42))
    ]),
    "HistGradientBoosting": HistGradientBoostingClassifier(
        learning_rate=0.1, max_iter=150, max_depth=12, random_state=42
    ),
    "XGBoost": XGBClassifier(
        n_estimators=150, max_depth=8, learning_rate=0.1, 
        n_jobs=-1, random_state=42, use_label_encoder=False, eval_metric='mlogloss'
    )
}

results = []
best_model = None
best_accuracy = 0
best_model_name = ""

for name, model in models.items():
    print(f"\n  Training {name}...")
    start_time = time.time()
    
    # Train the model
    model.fit(X_train, y_train)
    
    # Evaluate
    accuracy = model.score(X_test, y_test)
    train_time = time.time() - start_time
    
    print(f"  -> Accuracy: {accuracy:.2%} | Time: {train_time:.1f} sec")
    
    results.append({
        "Algorithm": name,
        "Accuracy": accuracy,
        "Time (sec)": train_time
    })
    
    if accuracy > best_accuracy:
        best_accuracy = accuracy
        best_model = model
        best_model_name = name

print("\n" + "=" * 60)
print("BENCHMARK RESULTS")
print("=" * 60)
results_df = pd.DataFrame(results).sort_values(by="Accuracy", ascending=False)
print(results_df.to_string(index=False))

print(f"\n[STEP 5] Winner Selected: {best_model_name.upper()}!")
print("Saving the best performing model to disk...")
os.makedirs('models', exist_ok=True)
joblib.dump(best_model, 'models/nutrition_model.pkl')
print("Model saved successfully as models/nutrition_model.pkl")

print("\n[STEP 6] Testing Winner against Sample Label...")
# Features: [energy, fat, sugars, sodium, protein, fiber, sat_fat, carbs]
test_samples = [
    [480, 22.0, 35.0, 450, 5.0, 2.0, 12.0, 65.0], # Unhealthy Biscuits
]
category_map = {4: 'A (Healthy)', 3: 'B (Healthy)', 2: 'C (Moderate)',  
                1: 'D (Unhealthy)', 0: 'E (Unhealthy)'}                  
for i, sample in enumerate(test_samples):
    pred = best_model.predict([sample])[0]
    print(f"  Test: Unhealthy Biscuits -> Predicted: {category_map[pred]}")

print("=" * 60)