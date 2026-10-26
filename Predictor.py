
import pickle
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Customer Satisfaction Predictor",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Customer Satisfaction Predictor")

st.write(
    "Predict customer dissatisfaction using delivery, "
    "shipping, and product information."
)

# Load the previously trained model
@st.cache_resource
def load_model():
    with open("satisfaction_model.pkl", "rb") as f:
        artifacts = pickle.load(f)

    return artifacts["model"], artifacts["scaler"], artifacts["features"]


try:
    model, scaler, FEATURES = load_model()
except FileNotFoundError:
    st.error(
        "Model file not found. Run your model-training notebook "
        "first and save satisfaction_model.pkl in this app's folder."
    )
    st.stop()
except Exception as e:
    st.error(f"Could not load model: {e}")
    st.stop()


st.subheader("Enter Order Details")

with st.form("prediction_form"):

    col1, col2 = st.columns(2)

    with col1:
        delivery_delay = st.number_input(
            "Delivery Delay (Days)",
            min_value=-100,
            max_value=365,
            value=0
        )

        carrier_transit = st.number_input(
            "Carrier Transit (Days)",
            min_value=0,
            max_value=365,
            value=5
        )

        seller_dispatch = st.number_input(
            "Seller Dispatch (Days)",
            min_value=0,
            max_value=365,
            value=2
        )

    with col2:
        freight_value = st.number_input(
            "Freight Value",
            min_value=0.0,
            value=20.0,
            step=5.0
        )

        price = st.number_input(
            "Product Price",
            min_value=0.01,
            value=100.0,
            step=10.0
        )

        weight = st.number_input(
            "Product Weight (grams)",
            min_value=0.0,
            value=1000.0,
            step=100.0
        )

        interstate = st.selectbox(
            "Interstate Order?",
            options=[0, 1],
            format_func=lambda x: "Yes" if x == 1 else "No"
        )

    submitted = st.form_submit_button(
        "Predict Customer Satisfaction",
        type="primary",
        use_container_width=True
    )


if submitted:

    # Calculate the same derived feature used during training
    freight_to_price_ratio = freight_value / price

    input_data = pd.DataFrame([{
        "delivery_delay_days": delivery_delay,
        "carrier_transit_days": carrier_transit,
        "seller_dispatch_days": seller_dispatch,
        "freight_to_price_ratio": freight_to_price_ratio,
        "is_interstate": interstate,
        "product_weight_g": weight
    }])

    # Ensure the same feature order used during training
    input_data = input_data[FEATURES]

    # Apply the saved scaler and model
    input_scaled = scaler.transform(input_data)

    prediction = model.predict(input_scaled)[0]
    probabilities = model.predict_proba(input_scaled)[0]

    # Find the probability associated with class 1
    classes = list(model.classes_)
    positive_index = classes.index(1)
    dissatisfaction_probability = probabilities[positive_index]

    st.divider()
    st.subheader("Prediction Results")

    col1, col2 = st.columns(2)

    with col1:
        if prediction == 1:
            st.error("Predicted: Dissatisfied")
        else:
            st.success("Predicted: Satisfied")

    with col2:
        st.metric(
            "Dissatisfaction Probability",
            f"{dissatisfaction_probability:.1%}"
        )

    st.caption(
        "Predictions are based on your trained Logistic Regression "
        "model. They are estimates, not guarantees of customer behavior."
    )


