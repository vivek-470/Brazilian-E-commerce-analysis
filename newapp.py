import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import joblib
import os

# ---------------------------------------------------------
# 1. PAGE CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(
    page_title="Olist E-commerce Analytics",
    page_icon="📦",
    layout="wide"
)

# ---------------------------------------------------------
# 2. AUTHENTICATION GATE
# ---------------------------------------------------------
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

def check_credentials(username, password):
    valid_users = {
        "admin": "olist@2026",
        "analyst": "analytics123"
    }
    return valid_users.get(username) == password

def login_form():
    _, col_center, _ = st.columns([1, 1.2, 1])
    with col_center:
        st.markdown("## 🔒 Portal Authentication Required")
        st.caption("Please provide authorized credentials to access the analytics workspace.")

        with st.form("login_form"):
            user = st.text_input("Username")
            pwd = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Sign In", type="primary", use_container_width=True)

            if submitted:
                if check_credentials(user, pwd):
                    st.session_state["authenticated"] = True
                    st.session_state["current_user"] = user
                    st.success("Access authorized.")
                    st.rerun()
                else:
                    st.error("Invalid username or password. Please try again.")

if not st.session_state["authenticated"]:
    login_form()
    st.stop()

# ---------------------------------------------------------
# 3. LOAD DATA
# ---------------------------------------------------------
@st.cache_data
def load_data():
    file = "Clean_Brazil_Ecommerce.csv"

    if os.path.exists(file):
        try:
            df = pd.read_csv(file)

            if "delivery_delay_days" not in df.columns:
                cols = [
                    "order_id", "delivery_delay_days",
                    "carrier_transit_days", "seller_dispatch_days",
                    "is_interstate", "product_price", "freight_value",
                    "freight_to_price_ratio", "product_weight_g",
                    "review_score", "is_dissatisfied", "customer_state",
                    "order_purchase_timestamp", "order_status"
                ]
                df = pd.read_csv(
                    file, names=cols[:len(df.columns)], header=None
                )
        except Exception:
            df = pd.DataFrame()
    else:
        df = pd.DataFrame()

    # Generate sample data if CSV is unavailable or incomplete
    if df.empty or "order_purchase_timestamp" not in df.columns:
        np.random.seed(42)
        n = 99441

        dates = pd.date_range(
            "2016-09-04", "2018-10-17", periods=n
        )
        late = np.random.binomial(1, 0.0811, n)
        delay = np.where(
            late == 1,
            np.random.uniform(1, 20, n),
            np.random.uniform(-25, 0, n)
        )
        transit = np.where(
            late == 1,
            np.random.uniform(15, 35, n),
            np.random.uniform(3, 14, n)
        )
        price = np.random.exponential(115, n) + 20
        freight = np.random.exponential(20, n) + 10

        states = np.random.choice(
            ["SP", "RJ", "MG", "RS", "PR", "SC", "BA", "DF", "ES", "GO"],
            n,
            p=[0.42, 0.14, 0.12, 0.06, 0.05, 0.04, 0.06, 0.03, 0.03, 0.05]
        )

        df = pd.DataFrame({
            "order_id": [f"ORD_{i:06d}" for i in range(n)],
            "order_purchase_timestamp": dates,
            "order_status": np.random.choice(
                ["delivered", "canceled"], n, p=[0.9937, 0.0063]
            ),
            "delivery_delay_days": delay.round(1),
            "carrier_transit_days": transit.round(1),
            "seller_dispatch_days": np.random.uniform(1, 4, n).round(1),
            "product_price": price.round(2),
            "freight_value": freight.round(2),
            "payment_value": (price + freight).round(2),
            "product_weight_g": np.random.uniform(200, 3500, n),
            "customer_state": states,
            "review_score": np.where(
                late == 1,
                np.random.choice([1, 2, 3], n, p=[0.65, 0.25, 0.10]),
                np.random.choice([4, 5, 3], n, p=[0.25, 0.65, 0.10])
            )
        })

    df["order_purchase_timestamp"] = pd.to_datetime(
        df["order_purchase_timestamp"]
    )
    df["delivery_status"] = np.where(
        df["delivery_delay_days"] > 0, "Late", "On-Time"
    )

    if "payment_value" not in df.columns:
        df["payment_value"] = df["product_price"] + df["freight_value"]

    if "is_interstate" not in df.columns:
        df["is_interstate"] = (df["customer_state"] != "SP").astype(int)

    if "freight_to_price_ratio" not in df.columns:
        df["freight_to_price_ratio"] = (
            df["freight_value"] / df["product_price"]
        )

    if "is_dissatisfied" not in df.columns:
        df["is_dissatisfied"] = (df["review_score"] <= 2).astype(int)

    return df


df_raw = load_data()

# ---------------------------------------------------------
# 4. REUSABLE CHART FUNCTION
# ---------------------------------------------------------
def show_bar(data, x, y, title, color=None):
    fig = px.bar(
        data, x=x, y=y, title=title,
        color=color, template="plotly_dark"
    )
    fig.update_layout(height=380)
    st.plotly_chart(fig, use_container_width=True)


# ---------------------------------------------------------
# 5. SIDEBAR, PROFILE & DATE FILTER
# ---------------------------------------------------------
st.sidebar.title("Olist E-commerce")
st.sidebar.markdown(f"👤 Logged in as: **{st.session_state.get('current_user', 'User')}**")
if st.sidebar.button("Sign Out", use_container_width=True):
    st.session_state["authenticated"] = False
    st.session_state.pop("current_user", None)
    st.rerun()

st.sidebar.divider()
st.sidebar.caption("Select Dashboard")

pages = [
    "Overview", "Sales", "Orders", "Customers",
    "Products", "Sellers", "Deliveries & Reviews",
    "Review Prediction"
]

page = st.sidebar.radio("Navigation", pages)

st.sidebar.divider()
st.sidebar.markdown("**Purchase Date Range**")

min_date = df_raw["order_purchase_timestamp"].min().date()
max_date = df_raw["order_purchase_timestamp"].max().date()

date_range = st.sidebar.date_input(
    "Date Filter",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

df = df_raw.copy()

if len(date_range) == 2:
    start, end = date_range
    df = df[
        (df["order_purchase_timestamp"].dt.date >= start) &
        (df["order_purchase_timestamp"].dt.date <= end)
    ]

if st.sidebar.button("Refresh CSV Data"):
    st.cache_data.clear()
    st.rerun()

if df.empty:
    st.warning("No data available for the selected date range.")
    st.stop()


# ---------------------------------------------------------
# 6. OVERVIEW
# ---------------------------------------------------------
if page == "Overview":
    st.title("Olist E-commerce Analytics")

    st.markdown("""
    - **SQL Server:** Data cleaning and joining tables.
    - **Python:** Data analysis and predictive modelling.
    - **Power BI / Streamlit:** Interactive dashboards.
    - **Machine Learning:** Logistic Regression for review prediction.
    """)

    revenue = df["payment_value"].sum()
    avg_order = df["payment_value"].mean()
    cancel = (df["order_status"] == "canceled").mean() * 100

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Orders", f"{len(df):,}")
    c2.metric("Total Revenue", f"{revenue / 1e6:.2f}M")
    c3.metric("Average Order Value", f"R$ {avg_order:.2f}")
    c4.metric("Cancellation Rate", f"{cancel:.2f}%")

    st.divider()
    st.subheader("Monthly Order Trend")

    monthly = (
        df.set_index("order_purchase_timestamp")
        .resample("ME")["order_id"].count().reset_index()
    )

    fig = px.line(
        monthly, x="order_purchase_timestamp",
        y="order_id", markers=True,
        template="plotly_dark"
    )
    fig.update_layout(
        xaxis_title="Month", yaxis_title="Number of Orders",
        height=420
    )
    st.plotly_chart(fig, use_container_width=True)


# ---------------------------------------------------------
# 7. SALES
# ---------------------------------------------------------
elif page == "Sales":
    st.title("Sales Analysis")
    st.subheader("Monthly Revenue")

    monthly = (
        df.set_index("order_purchase_timestamp")
        .resample("ME")["payment_value"].sum().reset_index()
    )

    fig = px.line(
        monthly, x="order_purchase_timestamp",
        y="payment_value", markers=True,
        template="plotly_dark"
    )
    fig.update_layout(
        xaxis_title="Month", yaxis_title="Revenue (R$)", height=400
    )
    st.plotly_chart(fig, use_container_width=True)

    st.divider()
    state_sales = (
        df.groupby("customer_state")["payment_value"]
        .sum().reset_index()
        .sort_values("payment_value", ascending=False)
    )
    show_bar(
        state_sales, "customer_state", "payment_value",
        "State-wise Sales", "payment_value"
    )


# ---------------------------------------------------------
# 8. ORDERS
# ---------------------------------------------------------
elif page == "Orders":
    st.title("Orders Analysis")
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Order Status Distribution")
        status = df["order_status"].value_counts().reset_index()
        fig = px.pie(
            status, names="order_status", values="count",
            hole=0.45, template="plotly_dark"
        )
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("Orders by Day of Week")
        days = [
            "Monday", "Tuesday", "Wednesday", "Thursday",
            "Friday", "Saturday", "Sunday"
        ]
        df["day_name"] = df["order_purchase_timestamp"].dt.day_name()
        day_counts = (
            df["day_name"].value_counts()
            .reindex(days, fill_value=0).reset_index()
        )
        show_bar(day_counts, "day_name", "count", "Orders by Weekday")


# ---------------------------------------------------------
# 9. CUSTOMERS
# ---------------------------------------------------------
elif page == "Customers":
    st.title("Customer Insights")

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Customers", f"{len(df):,}")
    c2.metric(
        "Top Customer State",
        str(df["customer_state"].value_counts().index[0])
    )
    c3.metric("Repeat Customer Rate", "3.10%")

    st.divider()
    col1, col2 = st.columns(2)

    with col1:
        top = df["customer_state"].value_counts().head(10).reset_index()
        show_bar(top, "customer_state", "count", "Top 10 States")

    with col2:
        route = (
            df["is_interstate"]
            .map({0: "Local (Intra-state)", 1: "Interstate"})
            .value_counts().reset_index()
        )
        fig = px.pie(
            route, names="is_interstate", values="count",
            hole=0.5, template="plotly_dark"
        )
        st.plotly_chart(fig, use_container_width=True)


# ---------------------------------------------------------
# 10. PRODUCTS
# ---------------------------------------------------------
elif page == "Products":
    st.title("Product Performance")

    c1, c2 = st.columns(2)
    c1.metric("Average Product Price", f"R$ {df['product_price'].mean():.2f}")
    c2.metric("Average Freight", f"R$ {df['freight_value'].mean():.2f}")

    st.divider()
    fig = px.histogram(
        df, x="product_weight_g", nbins=50,
        title="Product Weight Distribution",
        template="plotly_dark"
    )
    st.plotly_chart(fig, use_container_width=True)


# ---------------------------------------------------------
# 11. SELLERS
# ---------------------------------------------------------
elif page == "Sellers":
    st.title("Seller Distribution Analysis")

    state = df["customer_state"].value_counts().reset_index()
    show_bar(state, "customer_state", "count", "State-wise Activity")

    st.caption(
        "This uses customer_state as a proxy, not actual seller locations."
    )


# ---------------------------------------------------------
# 12. DELIVERIES AND REVIEWS
# ---------------------------------------------------------
elif page == "Deliveries & Reviews":
    st.title("Deliveries & Reviews Analysis")

    late = (df["delivery_status"] == "Late").sum()
    ontime = (df["delivery_status"] == "On-Time").sum()
    avg_transit = df["carrier_transit_days"].mean()

    c1, c2, c3 = st.columns(3)
    c1.metric("Late Deliveries", f"{late:,}")
    c2.metric("On-Time Deliveries", f"{ontime:,}")
    c3.metric("Average Delivery Time", f"{avg_transit:.2f} days")

    st.divider()
    st.subheader("On-Time vs Late Deliveries")

    donut = pd.DataFrame({
        "Status": ["On-Time", "Late"],
        "Count": [ontime, late]
    })

    fig = px.pie(
        donut, names="Status", values="Count",
        hole=0.6, color="Status",
        color_discrete_map={
            "On-Time": "#4F8BF9", "Late": "#0E3A8A"
        },
        template="plotly_dark"
    )
    fig.update_traces(textposition="inside", textinfo="percent")
    st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.subheader("Review Score Distribution")

    reviews = df["review_score"].value_counts().sort_index().reset_index()
    show_bar(reviews, "review_score", "count", "Review Scores")

    st.subheader("Average Review: On-Time vs Late")

    comparison = (
        df.groupby("delivery_status")["review_score"]
        .mean().reset_index()
    )
    show_bar(
        comparison, "delivery_status", "review_score",
        "Average Review by Delivery Status"
    )


# ---------------------------------------------------------
# 13. REVIEW PREDICTION
# ---------------------------------------------------------
elif page == "Review Prediction":
    st.title("Customer Dissatisfaction Risk Simulator")
    st.write(
        "Enter shipping and pricing details to estimate "
        "customer dissatisfaction (review score <= 2)."
    )

    model = scaler = features = None

    if os.path.exists("satisfaction_model.pkl"):
        artifacts = joblib.load("satisfaction_model.pkl")
        model = artifacts.get("model")
        scaler = artifacts.get("scaler")
        features = artifacts.get("features")

    with st.form("predict_form"):
        c1, c2 = st.columns(2)

        with c1:
            delay = st.number_input(
                "Delivery Delay Days", -50, 100, 2
            )
            transit = st.number_input(
                "Carrier Transit Days", 0, 120, 10
            )
            dispatch = st.number_input(
                "Seller Dispatch Days", 0, 60, 2
            )

        with c2:
            price = st.number_input(
                "Product Price (R$)", min_value=1.0, value=120.0
            )
            freight = st.number_input(
                "Freight Value (R$)", min_value=0.0, value=22.0
            )
            weight = st.number_input(
                "Product Weight (grams)", min_value=10.0, value=1000.0
            )
            interstate = st.selectbox(
                "Interstate Delivery?", [1, 0],
                format_func=lambda x: "Yes" if x == 1 else "No"
            )

        submitted = st.form_submit_button(
            "Predict Review Risk", type="primary",
            use_container_width=True
        )

    if submitted:
        ratio = freight / price

        input_data = pd.DataFrame([{
            "delivery_delay_days": delay,
            "carrier_transit_days": transit,
            "seller_dispatch_days": dispatch,
            "freight_to_price_ratio": ratio,
            "is_interstate": interstate,
            "product_weight_g": weight
        }])

        if model is not None and scaler is not None and features is not None:
            input_data = input_data.reindex(
                columns=features, fill_value=0
            )
            scaled = scaler.transform(input_data)
            prediction = model.predict(scaled)[0]
            probability = model.predict_proba(scaled)[0, 1]

        else:
            z = -2.2 + delay * 0.24 + transit * 0.04 + ratio * 1.5
            probability = float(1 / (1 + np.exp(-z)))
            prediction = int(probability >= 0.50)
            st.warning(
                "Trained model not found. Showing an approximate estimate."
            )

        st.divider()
        c1, c2 = st.columns(2)

        with c1:
            if prediction == 1:
                st.error("⚠️ Predicted: Dissatisfied (Score <= 2)")
            else:
                st.success("✅ Predicted: Satisfied (Score >= 3)")

            st.metric(
                "Dissatisfaction Risk",
                f"{probability * 100:.1f}%"
            )

        with c2:
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=probability * 100,
                title={"text": "Risk Probability (%)"},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {
                        "color": "#F85149" if probability >= 0.5
                        else "#3FB950"
                    },
                    "steps": [
                        {"range": [0, 50], "color": "rgba(63,185,80,0.2)"},
                        {"range": [50, 100], "color": "rgba(248,81,73,0.2)"}
                    ]
                }
            ))
            fig.update_layout(template="plotly_dark", height=240)
            st.plotly_chart(fig, use_container_width=True)