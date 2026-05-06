import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# 1. The Raw Data from our Benchmarking Deathmatch
data = {
    'Algorithm': ['Random Forest', 'HistGradient', 'XGBoost'],
    'Accuracy (%)': [88.3, 93.1, 94.54],
    'Training Time (s)': [4.2, 12.6, 16.9]
}

df = pd.DataFrame(data)

# 2. Set the Visual Style
sns.set_theme(style="whitegrid")
plt.rcParams['font.family'] = 'sans-serif'

# 3. Create Accuracy Plot
plt.figure(figsize=(10, 6))
colors = ['#ff9999','#66b3ff','#2ecc71'] # Matching the presentation colors
ax = sns.barplot(x='Algorithm', y='Accuracy (%)', data=df, palette=colors)

# Add value labels on top of bars
for p in ax.patches:
    ax.annotate(f'{p.get_height()}%', 
                (p.get_x() + p.get_width() / 2., p.get_height()), 
                ha='center', va='center', 
                xytext=(0, 9), 
                textcoords='offset points',
                fontsize=12, fontweight='bold')

plt.title('ML Model Accuracy Comparison', fontsize=16, fontweight='bold', pad=20)
plt.ylim(80, 100) # Zoom in to see the difference clearly
plt.ylabel('Test Accuracy (%)', fontsize=12)
plt.xlabel('Algorithm', fontsize=12)
plt.tight_layout()
plt.savefig('accuracy_comparison.png', dpi=300)
print("Saved: accuracy_comparison.png")

# 4. Create Training Time Plot
plt.figure(figsize=(10, 6))
time_colors = ['#bdc3c7', '#95a5a6', '#f39c12'] # Grey to Orange (Winning Edge)
ax2 = sns.barplot(x='Algorithm', y='Training Time (s)', data=df, palette=time_colors)

for p in ax2.patches:
    ax2.annotate(f'{p.get_height()}s', 
                 (p.get_x() + p.get_width() / 2., p.get_height()), 
                 ha='center', va='center', 
                 xytext=(0, 9), 
                 textcoords='offset points',
                 fontsize=12, fontweight='bold')

plt.title('Training Latency (500k Rows)', fontsize=16, fontweight='bold', pad=20)
plt.ylabel('Time (Seconds)', fontsize=12)
plt.xlabel('Algorithm', fontsize=12)
plt.tight_layout()
plt.savefig('training_time_comparison.png', dpi=300)
print("Saved: training_time_comparison.png")
