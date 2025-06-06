import streamlit as st
import math
import pandas as pd

# --- Duct Calculation Functions ---
def estimate_duct_dia_QV(Q: float, V: float) -> float | None:
    pi = math.pi

    if Q <= 0 or V <=0:
        print("Error: Airflow rate and velocity must be positive value.")
        return None

    # 1. Convert Airflow rate from L/s to m^3/s
    airFlowRate_m3s = Q / 1000

    # 2. Calculate cross section area (m^2)
    # Q = A * V => A = Q / V
    ductArea_m2 = airFlowRate_m3s / V

    # 3. Calculate diameter in meters for a round duct
    # A = pi/4 * D^2 => D = sqrt ((4 * A)/pi)
    ductDia_m = math.sqrt((4*ductArea_m2)/math.pi)

    # 4. Convert diameter to millimeters
    ductDia_mm = ductDia_m * 1000

    return float(ductDia_mm)


  

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
    st.markdown("Enter Q and dp (Rec. 0.615-0.820 Pa/m or 0.075-0.100 inch/100ft) to estimate duct sizes.")

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
            #else:
            #    st.success(f"✅ Ideal square duct size: **{int(square_size)} mm**")

            st.markdown("#### 📐 Recommended Duct Sizes")
            st.markdown(f"Based on Q = **{Q} L/s** and Target dp = **{dp} Pa/m.**")

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
                    "Aspect Ratio": f"{AR:.2f}",                # 2 decimals
                    "Velocity (m/s)": f"{velocity:.2f}",       # 2 decimals
                    "dp (Pa/m)": f"{actual_dp:.3f}",           # 3 decimals
                    "De (mm)": f"{De:.0f}",                    # No decimals
                })

            if results:
                df = pd.DataFrame(results)

                def highlight_valid(row):
                    if row["OK"] == "✓":
                        return ['background-color: #d4edda; font-weight: bold'] * len(row)
                    else:
                        return [''] * len(row)

                st.dataframe(df, use_container_width=True)
                #st.dataframe(df.style.apply(highlight_valid, axis=1), use_container_width=True)
                st.markdown("[Visit somjinnotes.com for more HVAC knowledge sharing](https://somjinnotes.com)")
            else:
                st.warning("⚠ No suitable duct sizes found.")
        else:
            st.error("Please enter both Q and dp.")

if __name__ == "__main__":
    main()



