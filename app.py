"""
import streamlit as st
import math

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

def main():
    st.set_page_config(page_title="HVAC Duct Sizing Calculator", layout="centered")
    st.title("Duct Size Calculator")
    st.markdown("Enter airflow and pressure drop to estimate duct sizes.")
    # Set default value for Q and dp
    default_Q = 100
    default_dp = 0.615

    col1, col2 = st.columns(2)

    with col1:
        Q = st.number_input("Airflow rate: Q (L/s)", min_value=25, step=25, format="%d", value=default_Q)

    with col2:
        dp = st.number_input("Pressure drop: dp (Pa/m)", min_value=0.005, step=0.005, format="%.3f", value=default_dp)


    if st.button("Calculate"):
        if Q and dp:
            square_size = estimate_ideal_square_duct(Q, dp)
            if square_size is None:
                st.error("❌ No suitable square duct size found.")
                return
            else:
                st.success(f"✅ Ideal square duct size: **{int(square_size)} mm**")

            st.markdown("### 📐 Recommended Duct Sizes")
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

                results.append({
                    "Option": i + 1,
                    "OK": marker,
                    "W×H (mm)": f"{int(width)}×{int(height)}",
                    "AR": round(AR, 2),
                    "Velocity (m/s)": round(velocity, 2),
                    "dp (Pa/m)": round(actual_dp, 3),
                    "De (mm)": round(De, 0),
                })

            if results:
                st.dataframe(results, use_container_width=True)
            else:
                st.warning("⚠ No suitable duct sizes found.")

        else:
            st.error("Please enter both Q and dp.")

if __name__ == "__main__":
    main()
"""

import streamlit as st
import math

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
    st.markdown("Enter airflow and pressure drop to estimate duct sizes.")

    default_Q = 100
    default_dp = 0.615

    # Use a form to capture "Enter" submission
    with st.form("duct_form"):
        col1, col2 = st.columns(2)
        with col1:
            Q = st.number_input("Airflow rate: Q (L/s)", min_value=25, step=25, format="%d", value=default_Q)
        with col2:
            dp = st.number_input("Pressure drop: dp (Pa/m)", min_value=0.005, step=0.005, format="%.3f", value=default_dp)

        submitted = st.form_submit_button("Calculate")

    if submitted:
        if Q and dp:
            square_size = estimate_ideal_square_duct(Q, dp)

            if square_size is None:
                st.error("❌ No suitable square duct size found.")
                return
            else:
                st.success(f"✅ Ideal square duct size: **{int(square_size)} mm**")

            st.markdown("### 📐 Recommended Duct Sizes")

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

                results.append({
                    "Option": i + 1,
                    "OK": marker,
                    "W×H (mm)": f"{int(width)}×{int(height)}",
                    "Aspect Ratio": round(AR, 2),
                    "Velocity (m/s)": round(velocity, 2),
                    "dp (Pa/m)": round(actual_dp, 3),
                    "De (mm)": round(De, 0),
                })
"""
            if results:
                st.dataframe(results, use_container_width=True)

"""
import pandas as pd

            if results:
                df = pd.DataFrame(results)

                def highlight_valid(row):
                    if row["OK"] == "✓":
                        return ['background-color: #d4edda; font-weight: bold'] * len(row)
                    else:
                        return [''] * len(row)

                st.dataframe(df.style.apply(highlight_valid, axis=1), use_container_width=True)

            else:
                st.warning("⚠ No suitable duct sizes found.")
        else:
            st.error("Please enter both Q and dp.")

if __name__ == "__main__":
    main()


