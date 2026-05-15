# NutriSnap: Clinical-Grade Nutritional Intelligence 🍎📸

NutriSnap is an advanced AI-powered health assistant designed to bridge the gap between complex food labels and actionable clinical insights. By combining **Deep Learning OCR**, **XGBoost Gradient Boosting**, and **Generative AI (Llama-3)**, NutriSnap transforms a simple photo of a nutrition label into a comprehensive metabolic health assessment.

---

## 🚀 Key Features

*   **Multi-Pass OCR Engine:** Utilizes a custom OpenCV preprocessing pipeline (CLAHE, Adaptive Thresholding) and EasyOCR to extract data from skewed, crinkled, or poorly lit labels.
*   **XGBoost Classification:** A high-precision machine learning model trained on 500,000+ products, achieving **94.54% accuracy** in health grading (A-E).
*   **Clinical LLM Contextualization:** Leverages Llama-3 (via OpenRouter) to provide personalized clinical assessments and wellness recommendations.
*   **Human-in-the-Loop Architecture:** Features an editable data verification layer to ensure ground-truth accuracy before ML inference.
*   **Historical Dashboard:** Persistent storage (Zustand) to track nutritional intake and past scans.

---

## 🛠️ Technical Stack

### Backend (Python/FastAPI)
*   **FastAPI:** High-performance asynchronous API framework.
*   **EasyOCR:** Deep Learning-based optical character recognition.
*   **XGBoost:** Gradient boosting library for tabular data classification.
*   **OpenCV:** Advanced image preprocessing and morphology.

### Frontend (React/Tailwind)
*   **React.js (Vite):** Modern component-based UI.
*   **Tailwind CSS & Shadcn UI:** Sleek, responsive design with glassmorphism.
*   **Zustand:** Lightweight state management with local persistence.
*   **Framer Motion:** Smooth micro-animations for an interactive experience.

---

## ⚙️ Installation & Setup (Backend)

```bash
# Clone the repository
cd nutrisnap-back

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate # or .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file and add your OpenRouter API Key
echo "OPENROUTER_API_KEY=your_key_here" > .env

# Run the FastAPI server
uvicorn main:app --reload
```

---

## 📊 Benchmarking Performance

Our ML engine was benchmarked against several standard algorithms to ensure clinical reliability:

| Algorithm | Test Accuracy | Training Time (500k rows) |
| :--- | :--- | :--- |
| **XGBoost** | **94.54%** | 16.9s |
| HistGradient | 93.10% | 12.6s |
| Random Forest | 88.30% | 4.2s |

---

## 🛡️ Future Roadmap
- [ ] **Full Offline Mode:** Migrating ML/OCR to TFLite for edge computing.
- [ ] **Personalized Health Profiles:** Custom grading for Diabetes and Hypertension.
- [ ] **Hybrid Barcode Integration:** Fallback to OCR only if barcode database lookup fails.

---

## 👨‍💻 Project Developer
**Developed as a B.Tech Final Year Project.**
*"Transforming Nutritional Data into Clinical Intelligence."*
