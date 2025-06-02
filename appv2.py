import streamlit as st
import math
import pandas as pd

# --- Duct Calculation Functions ---

def estimate_ideal_square_duct(Q: float, dp: float) -> float | None:
    pi = math.pi
    calc_const = 9.6e9 / (pi ** 2)
    size = 50
    max_size = 3000
    dp_min = dp * 0.8
    dp_max = dp * 1.2

    while size <= max_size:
        De = 1.3 * ((size ** 2) ** 0.625) * ((2 * size) ** -0.25)
        f1 = 0.11 * ((0.09 / De + 0.0008043 * De / Q) ** 0.25)
        f = f1 if f1 >= 0.018 else 0.85 * f1 + 0.0028
        hl = calc_const * f * Q ** 2 * De ** -5

        if dp_min <= hl <= dp_max:
            return float(size)
        size += 1

    return None

def estimate_rectangular_duct_width(Q: float, dp: float, b: float) -> float | None:
    pi = math.pi
    calc_const = 9.6e9 / (pi ** 2)

    for a in range(50, 5001):
        De = 1.3 * (a * b) ** 0.625 / (a + b) ** 0.25
        f1 = 0.11 * ((0.09 / De + 0.0008043 * De / Q) ** 0.25)
        f = f1 if f1 >= 0.018 else 0.85 * f1 + 0.0028
        hl = calc_const * f * Q ** 2 / De ** 5

        if abs(hl - dp) <= 0.005:
            return float(a)

    return None

# --- Streamlit App UI ---

def main():
    st.set_page_config(page_title="HVAC Duct Sizing Calculator", layout="centered")
    st.title("Duct Size Calculator")

    unit_system = st.radio("Select Unit System", ["SI", "IP"], horizontal=True)

    # Set default inputs based on selected unit
    if unit_system == "SI":
        default_Q = 100     # L/s
        default_dp = 0.615  # Pa/m
        Q_label = "Airflow rate: Q (L/s)"
        dp_label = "Pressure drop: dp (Pa/m)"
    else:
        default_Q = 212     # CFM
        default_dp = 0.075  # inch/100ft
        Q_label = "Airflow rate: Q (CFM)"
        dp_label = "Pressure drop: dp (inch/100ft)"

    with st.form("duct_form"):
        col1, col2 = st.columns(2)
        with col1:
            Q_input = st.number_input(Q_label, min_value=float(25), step=float(25), value=float(default_Q), format="%.0f")
        with col2:
            dp_input = st.number_input(dp_label, min_value=0.005, step=0.005, value=float(default_dp), format="%.3f")

        submitted = st.form_submit_button("Calculate")

    if submitted:
        if unit_system == "IP":
            Q = Q_input * 0.471947     # CFM → L/s
            dp = dp_input * 8.172      # inch/100ft → Pa/m
        else:
            Q = Q_input
            dp = dp_input

        square_size = estimate_ideal_square_duct(Q, dp)

        if square_size is None:
            st.error("❌ No suitable square duct size found.")
            return

        st.markdown("#### 📐 Recommended Duct Sizes")
        if unit_system == "IP":
            st.markdown(f"Based on Q = **{Q_input} CFM** and Target dp = **{dp_input} inch/100ft.**")
        else:
            st.markdown(f"Based on Q = **{Q_input} L/s** and Target dp = **{dp_input} Pa/m.**")

        initial_height = max(50, math.ceil(((square_size / 2) - 25) / 50) * 50)
        results = []

        for i in range(10):
            height = initial_height + i * 50
            est_width = estimate_rectangular_duct_width(Q, dp, height)
            if est_width is None:
                continue

            width = math.ceil(est_width / 50) * 50
            AR = width / height
            if AR < 1.0:
                continue

            De = 1.3 * (width * height) ** 0.625 / (width + height) ** 0.25
            f1 = 0.11 * ((0.09 / De + 0.0008043 * De / Q) ** 0.25)
            f = f1 if f1 >= 0.018 else (0.85 * f1 + 0.0028)
            calc_const = 9.6e9 / (math.pi ** 2)
            actual_dp = calc_const * f * Q ** 2 / De ** 5
            velocity = (1000 * Q) / (width * height)
            marker = "✓" if 1.0 <= AR <= 4.0 else "✗"

            if unit_system == "IP":
                width_ip = width / 25
                height_ip = height / 25
                De_ip = De / 25
                results.append({
                    "Option": i + 1,
                    "OK": marker,
                    "W×H (inch)": f"{width_ip:.0f}×{height_ip:.0f}",
                    "Aspect Ratio": f"{AR:.2f}",
                    "Velocity (ft/min)": f"{velocity * 196.85:.0f}",  # m/s to ft/min
                    "dp (inch/100ft)": f"{actual_dp / 8.172:.3f}",
                    "De (inch)": f"{De_ip:.1f}",
                })
            else:
                results.append({
                    "Option": i + 1,
                    "OK": marker,
                    "W×H (mm)": f"{int(width)}×{int(height)}",
                    "Aspect Ratio": f"{AR:.2f}",
                    "Velocity (m/s)": f"{velocity:.2f}",
                    "dp (Pa/m)": f"{actual_dp:.3f}",
                    "De (mm)": f"{De:.0f}",
                })

        if results:
            df = pd.DataFrame(results)

            def highlight_valid(row):
                if row["OK"] == "✓":
                    return ['background-color: #d4edda; font-weight: bold'] * len(row)
                else:
                    return [''] * len(row)

            st.dataframe(df.style.apply(highlight_valid, axis=1), use_container_width=True)
            st.markdown("[Visit somjinnotes.com for more HVAC knowledge sharing](https://somjinnotes.com)")
        else:
            st.warning("⚠ No suitable duct sizes found.")

if __name__ == "__main__":
    main()
