# app.py

import streamlit as st
import math
import pandas as pd

st.set_page_config(page_title="HVAC Duct Sizing Calculator", layout="wide")
st.title("🔧 HVAC Duct Sizing Calculator")
st.markdown("This tool estimates **ideal square and rectangular duct sizes** based on airflow rate and pressure drop.")

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

# --- UI Input ---
Q = st.number_input("Enter airflow rate (Q) [L/s]:", min_value=0.0, value=500.0, step=10.0, format="%.1f")
dp = st.number_input("Enter pressure drop (dp) [Pa/m]:", min_value=0.0, value=1.0, step=0.1, format="%.2f")

if Q > 0 and dp > 0:
    st.divider()
    st.subheader("📐 Ideal Square Duct Size")

    square_size = estimate_ideal_square_duct(Q, dp)
    if square_size:
        st.success(f"Ideal Square Duct Size: **{int(square_size)} mm x {int(square_size)} mm**")
        st.markdown("---")

        st.subheader("📏 Recommended Rectangular Duct Sizes")
        initial_height = max(50, math.ceil(((square_size / 2) - 25) / 50) * 50)

        data = []
        for i in range(10):
            height = initial_height + i * 50
            est_width = estimate_rectangular_duct_width(Q, dp, height)

            if est_width:
                width = math.ceil(est_width / 50) * 50
                AR = width / height
                if AR < 1.0:
                    continue

                De = 1.3 * (width * height) ** 0.625 / (width + height) ** 0.25
                f1 = 0.11 * ((0.09 / De + 0.0008043 * De / Q) ** 0.25)
                f = f1 if f1 >= 0.018 else 0.85 * f1 + 0.0028
                pi = math.pi
                calc_const = 9.6e9 / (pi ** 2)
                actual_dp = calc_const * f * Q ** 2 / De ** 5
                velocity = (1000 * Q) / (width * height)
                marker = "✓" if 1.0 <= AR <= 4.0 else "✗"

                data.append({
                    "Option": i + 1,
                    "Note": marker,
                    "Size (WxH mm)": f"{int(width)} x {int(height)}",
                    "AR": round(AR, 2),
                    "Velocity (m/s)": round(velocity, 2),
                    "dp (Pa/m)": round(actual_dp, 3),
                    "De (mm)": round(De, 0)
                })

        if data:
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("No suitable rectangular duct sizes found.")
    else:
        st.error("No square duct size found within constraints.")
