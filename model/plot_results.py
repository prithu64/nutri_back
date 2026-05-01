# scripts/plot_results.py
import matplotlib.pyplot as plt
import seaborn as sns
import os

print("Generating Benchmark Graphs...")

# Hardcode the artifacts directory so the images can be embedded in the chat!
ARTIFACT_DIR = r"C:\Users\prgth\.gemini\antigravity\brain\4c1967ed-d2f2-40bc-9a7c-b5733cbdb222"

algorithms = ['Random Forest', 'HistGradientBoosting', 'XGBoost']
accuracies = [88.30, 93.09, 94.54]
times = [4.2, 12.6, 16.9]

# Set visual style
sns.set_theme(style="whitegrid")
plt.rcParams['font.family'] = 'sans-serif'

# 1. Plot Accuracy Comparison
plt.figure(figsize=(10, 6))
bars = plt.bar(algorithms, accuracies, color=['#ff9999', '#66b3ff', '#99ff99'])
bars[2].set_color('#2ecc71') # Highlight XGBoost in green
bars[2].set_edgecolor('black')
bars[2].set_linewidth(2)

plt.ylim(80, 100)
plt.title('Algorithm Accuracy Comparison (500k Rows)', fontsize=16, fontweight='bold', pad=20)
plt.ylabel('Test Accuracy (%)', fontsize=12, fontweight='bold')
plt.xlabel('Machine Learning Algorithm', fontsize=12, fontweight='bold')

# Add text labels on top of bars
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval + 0.3, f"{yval}%", ha='center', va='bottom', fontsize=11, fontweight='bold')

acc_path = os.path.join(ARTIFACT_DIR, 'accuracy_comparison.png')
plt.tight_layout()
plt.savefig(acc_path, dpi=300)
print(f"Saved: {acc_path}")
plt.close()

# 2. Plot Training Time Comparison
plt.figure(figsize=(10, 6))
bars2 = plt.bar(algorithms, times, color=['#c2c2c2', '#c2c2c2', '#f39c12'])
bars2[2].set_edgecolor('black')
bars2[2].set_linewidth(2)

plt.title('Algorithm Compute Cost (Training Time)', fontsize=16, fontweight='bold', pad=20)
plt.ylabel('Training Time (Seconds)', fontsize=12, fontweight='bold')
plt.xlabel('Machine Learning Algorithm', fontsize=12, fontweight='bold')

for bar in bars2:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval + 0.2, f"{yval} sec", ha='center', va='bottom', fontsize=11, fontweight='bold')

time_path = os.path.join(ARTIFACT_DIR, 'time_comparison.png')
plt.tight_layout()
plt.savefig(time_path, dpi=300)
print(f"Saved: {time_path}")
plt.close()

print("Graphs successfully generated!")
