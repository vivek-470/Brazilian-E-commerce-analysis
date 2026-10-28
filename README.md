# 📦 Brazilian E-Commerce: Commercial Health & Delivery Performance Analysis

An end-to-end data engineering, business intelligence, and predictive machine learning pipeline analyzing 99,000+ customer orders from the Olist Brazilian E-commerce ecosystem. This project uncovers logistical bottlenecks, evaluates fulfillment latency across states, and deploys a live customer satisfaction risk predictor.

---

## 🔗 Live Application & Artifacts
- 🌐 **Live Web Application:** [Customer Satisfaction Predictor (Streamlit)](https://brazilian-e-commerce-analysis-470.streamlit.app)
- 📊 **Power BI Template:** [Download `Brazilian-Ecommerce analysis.pbit`](./Brazilian-Ecommerce%20analysis.pbit)
- 🗄️ **SQL Auditing & Cleaning Script:** [View `Brazilian-Ecommerce.sql`](./Brazilian-Ecommerce.sql)

---

## 📊 Interactive Dashboards & Live Deployment

### 1. Logistics & Delivery Performance Dashboard
> Analyzes transit durations, national SLA adherence (91.89% on-time rate), and the critical **satisfaction drop-off** from 4.29 to 1.70 stars on delayed shipments.

<p align="center">
  <img src="https://github.com/user-attachments/assets/f76fd54c-550a-434f-be1d-ab87860bfe24" width="100%" alt="Logistics and Delivery Performance Dashboard" />
</p>

---

### 2. E-Commerce Executive Commercial Performance Dashboard
> Tracks R$ 13.59M gross revenue, monthly transaction trends, payment method preferences (credit card dominance at 75.3%), and state-level market distribution.

<p align="center">
  <img src="https://github.com/user-attachments/assets/e7bf87c6-2ff1-443e-9566-04fc3639f8ac" width="100%" alt="Executive Performance Dashboard" />
</p>

---

## 🏗️ Architecture & Technology Stack

| Layer | Tools & Libraries | Key Responsibilities |
| :--- | :--- | :--- |
| **Data Engineering & Auditing** | SQL Server, T-SQL | Auditing 9 relational tables, duplicate checks, zero/negative payment checks, foreign key join validation. |
| **Data Modeling & BI** | Power BI Desktop, DAX | Clean Star-Schema modeling, date dimension hierarchy, automated KPI measures, and dynamic executive reports. |
| **Predictive Modeling** | Python (`pandas`, `scikit-learn`, `numpy`) | Balanced class weighting (handling 85/15 target imbalance), feature importance extraction, Logistic Regression (ROC-AUC: 0.6862). |
| **Web Deployment** | Streamlit Community Cloud | Interactive production web interface for real-time customer dissatisfaction probability scoring. |

---

## 💡 Key Business Insights

- **The "Satisfaction Cliff":** Orders delivered on time maintain an average review score of **4.29 / 5.00**. Scores drop drastically to **2.56 stars** for 1–3 day delays and collapse to **1.70 stars** when shipments exceed 8+ days of delay.
- **Regional Bottlenecks:** While national delivery averages **12.50 days**, distant northern and northeastern states (Roraima `RR`, Amapá `AP`, Amazonas `AM`) experience severe fulfillment latency averaging **25–29 days**.
- **Commercial Dominance:** The Southeastern metropolitan corridor (São Paulo `SP`, Rio de Janeiro `RJ`, Minas Gerais `MG`) drives over **70%** of total order volume and revenue.
- **Payment Behavior:** Credit cards represent **75.32%** of all customer transactions, followed by Boleto bancário (**19.44%**).

---

## 🚀 Running the Streamlit App Locally

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/vivek-470/Brazilian-E-commerce-analysis.git](https://github.com/vivek-470/Brazilian-E-commerce-analysis.git)
   cd Brazilian-E-commerce-analysis
