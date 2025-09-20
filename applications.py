# app.py
# Streamlit prototype: AI-Driven LCA Tool (India-centric) -- extended version
# Save as app.py and run: streamlit run app.py
# Note: many numbers here are illustrative defaults. Replace with validated data if available.

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import textwrap

st.set_page_config(page_title="SustainaMine - LCA for Metals", layout="wide")

# ---------------------------
# Helper / metadata (sources)
# ---------------------------
SOURCES = {
    "CPCB_RedMud_Guidelines": "https://cpcb.nic.in/uploads/hwmd/Guidelines_HW_6.pdf",
    "Hazardous_Waste_Rules_2016": "https://www.npcindia.gov.in/NPC/Files/delhiOFC/EM/Hazardous-waste-management-rules-2016.pdf",
    "Minerals_Aluminium_page": "https://mines.gov.in/webportal/content/Aluminium",
    "RedMud_Brochure_JNARDDC": "https://www.jnarddc.gov.in/Files/Red_Mud_Brochure.pdf",
    "Indian_Minerals_Yearbook_Copper": "https://ibm.gov.in/writereaddata/files/1715685346664347e2b0816Copper_2022.pdf",
    "CPCB_Technical_Guidelines": "https://cpcb.nic.in/technical-guidelines/"
}

# ---------------------------
# Informational / context data
# ---------------------------
st.title("SustainaMine — AI-Driven LCA for Metals (India)")
st.markdown("""
**Purpose:** Demonstration prototype for Smart India Hackathon by Team ADAPT — an AI-assisted Life Cycle Assessment (LCA)
tool tailored for **Aluminium** and **Copper** with circularity, by-product valorization, and regulatory
compliance support for India.

**Note:** Default numbers are *illustrative*. Replace with validated local data for final deployment.
""")

# Quick policy / pro-government statement
st.info("""
**Pro-government framing:** This tool is built to _support_ Government of India objectives — it helps industry
adhere to CPCB / MoEFCC guidelines, follow the Hazardous & Other Wastes Rules (2016), and advance circularity
aligned with National Mineral Policy goals. It **does not** replace statutory approvals — it **assists** compliance.
""")

# ---------------------------
# India context (states + production)
# ---------------------------
st.header("India Context & Production (quick snapshot)")

col1, col2 = st.columns([2,3])
with col1:
    st.subheader("Major Aluminium-producing states (India)")
    st.write("""
    Typical top-producing states (industry & reports): **Odisha, Gujarat, Maharashtra, Chhattisgarh, Jharkhand**.
    Source: compilation of industry and government reports (see sources panel below).  
    These states host large alumina/aluminium complexes (NALCO, Hindalco, Vedanta, BALCO).
    """)
    st.write("Source links:")
    st.write(f"- CPCB / Guidelines: {SOURCES['CPCB_RedMud_Guidelines']}")
    st.write(f"- Ministry of Mines info: {SOURCES['Minerals_Aluminium_page']}")

with col2:
    st.subheader("Major Copper-producing regions (India)")
    st.write("""
    Copper ore/concentrate and refined copper production has strong footprints in **Rajasthan, Madhya Pradesh** and
    several large smelter/plant clusters (recent developments also in Gujarat due to new smelters). India imports a
    large share of concentrates; domestic production varies year to year.
    Sources: Indian Minerals Yearbook & industry reports.
    """)
    st.write(f"- Copper Yearbook (IBM): {SOURCES['Indian_Minerals_Yearbook_Copper']}")
    st.write(f"- Industry reports (news & ministry pages): {SOURCES['Minerals_Aluminium_page']}")

st.markdown("---")

# ---------------------------
# Default lifecycle factors (illustrative)
# ---------------------------
st.header("Default LCA parameters (illustrative defaults)")
st.write("These are example baseline factors you can edit in code or replace with your datasets. Values shown are typical estimates used for demonstration.")

default_factors = {
    # kg CO2e per kg metal (stage-summed rough)
    "aluminium_virgin_kgco2_per_kg": 16.0,   # typical range varies widely; aluminium smelting is energy intensive
    "aluminium_recycled_kgco2_per_kg": 4.0,
    "copper_virgin_kgco2_per_kg": 8.0,
    "copper_recycled_kgco2_per_kg": 2.0,
    # red mud generation per tonne aluminium (tons red mud / ton Al) - typical literature range ~1 - 1.8
    "red_mud_t_per_t_aluminium": 1.5,
    # SO2 estimate per tonne copper smelted (kg SO2 / t copper) - illustrative
    "so2_kg_per_t_copper": 25.0,
    # transport emission per ton-km (kg CO2e)
    "transport_kgco2_per_tkm": 0.05,
    # recycling energy cost estimate (USD per ton processed) - illustrative
    "recycle_cost_usd_per_t_aluminium": 200.0,
    "recycle_cost_usd_per_t_copper": 300.0
}

st.json(default_factors)

st.markdown("---")

# ---------------------------
# Input panel
# ---------------------------
st.header("Run an LCA Estimate (Demo Input)")
with st.form(key='input_form'):
    col1, col2, col3 = st.columns(3)
    with col1:
        metal = st.selectbox("Select metal", ["Aluminium", "Copper"])
        production_route = st.selectbox("Production route", ["Virgin/Raw", "Recycled", "Mixed"])
        recycled_pct = st.slider("Recycled content (%)", 0, 100, 30)
    with col2:
        energy_source = st.selectbox("Energy source (select nearest)", ["Coal-based grid", "Mixed grid", "Renewable-heavy"])
        transport_km = st.number_input("Transport distance (km)", min_value=0, max_value=5000, value=200)
        transport_tonnes = st.number_input("Transport quantity (tonnes of metal)", min_value=1, max_value=10000, value=1)
    with col3:
        eol_option = st.selectbox("End-of-life option", ["Landfill", "Recycling", "Reuse"])
        storage_practice = st.selectbox("Storage / residue handling", ["Proper authorized storage", "Temporary open storage", "Untreated disposal"])
        run_button = st.form_submit_button("Run LCA estimate")

if run_button:
    # ---------------------------
    # Gap-filling logic (simple AI-style rule-based with provenance info)
    # ---------------------------
    missing_info_notes = []
    # Choose baseline CO2 per kg
    if metal == "Aluminium":
        if production_route == "Virgin/Raw":
            baseline = default_factors["aluminium_virgin_kgco2_per_kg"]
        elif production_route == "Recycled":
            baseline = default_factors["aluminium_recycled_kgco2_per_kg"]
        else: # Mixed
            baseline = (default_factors["aluminium_virgin_kgco2_per_kg"]*(100-recycled_pct)/100 +
                        default_factors["aluminium_recycled_kgco2_per_kg"]*(recycled_pct)/100)
        # red mud generation:
        red_mud_t = default_factors["red_mud_t_per_t_aluminium"] * transport_tonnes
    else:
        if production_route == "Virgin/Raw":
            baseline = default_factors["copper_virgin_kgco2_per_kg"]
        elif production_route == "Recycled":
            baseline = default_factors["copper_recycled_kgco2_per_kg"]
        else:
            baseline = (default_factors["copper_virgin_kgco2_per_kg"]*(100-recycled_pct)/100 +
                        default_factors["copper_recycled_kgco2_per_kg"]*(recycled_pct)/100)
        red_mud_t = 0

    # energy adjustment (approx)
    if energy_source == "Coal-based grid":
        energy_factor_multiplier = 1.2
        provenance_energy = "Assumed national average coal-heavy grid factor (illustrative)."
    elif energy_source == "Mixed grid":
        energy_factor_multiplier = 1.0
        provenance_energy = "Assumed mixed grid emissions factor (illustrative)."
    else:
        energy_factor_multiplier = 0.8
        provenance_energy = "Assumed renewable-heavy grid factor (illustrative)."

    # compute kg CO2 per kg metal
    kgco2_per_kg = baseline * energy_factor_multiplier
    # add transport emissions (per kg basis)
    transport_emission_per_kg = default_factors["transport_kgco2_per_tkm"] * (transport_km) * (transport_tonnes / (transport_tonnes if transport_tonnes>0 else 1)) / transport_tonnes
    # above simplifies to per-tonne basis; easier compute per ton then convert
    transport_kgco2_per_ton = default_factors["transport_kgco2_per_tkm"] * transport_km
    # total per tonne
    total_co2_per_tonne = (kgco2_per_kg * 1000) + transport_kgco2_per_ton

    # circularity score (simple composite)
    circularity = recycled_pct * 0.5
    if eol_option == "Recycling":
        circularity += 30
    elif eol_option == "Reuse":
        circularity += 40
    circularity = min(100, circularity)

    # toxicity/by-product estimates
    so2_kg_total = 0
    if metal == "Copper":
        # simple estimate
        so2_kg_total = default_factors["so2_kg_per_t_copper"] * transport_tonnes

    # cost estimates to recycle/reuse waste (rough)
    if metal == "Aluminium":
        recycle_cost = default_factors["recycle_cost_usd_per_t_aluminium"] * transport_tonnes
    elif metal == "Copper":
        recycle_cost = default_factors["recycle_cost_usd_per_t_copper"] * transport_tonnes
    else:
        recycle_cost = 0

    # ---------------------------
    # Show results
    # ---------------------------
    st.header("Estimated Results (Illustrative)")
    colA, colB = st.columns(2)
    with colA:
        st.metric("CO₂ (per kg of metal) - estimated", f"{kgco2_per_kg:.2f} kg CO₂e / kg")
        st.metric("CO₂ (per tonne incl transport) - est.", f"{total_co2_per_tonne:.0f} kg CO₂e / t (incl transport)")
    with colB:
        st.metric("Circularity Score (0-100)", f"{circularity:.1f}")
        st.metric("Estimated recycling cost (USD)", f"{recycle_cost:,.2f} (for {transport_tonnes} t)")

    st.subheader("Breakdown (per tonne basis)")
    breakdown_df = pd.DataFrame({
        "Stage": ["Production+smelting (kg CO2e/kg *1000)", "Transport (kg CO2e/t)", "Total (kg CO2e/t)"],
        "Value": [kgco2_per_kg*1000, transport_kgco2_per_ton, total_co2_per_tonne]
    })
    st.table(breakdown_df)

    st.subheader("By-product / Toxic emissions (illustrative)")
    if metal == "Aluminium":
        st.write(f"Red mud estimate: **{red_mud_t:.2f} tonnes** of red mud produced for {transport_tonnes} t of aluminium (typical literature estimate ~1.5 t red mud / t Al).")
        st.write("Valuable routes: cement substitute, pigment (iron oxides), rare earth recovery (pilot scale). See CPCB red mud guidelines (sources).")
    else:
        st.write(f"Estimated SO₂ generation: **{so2_kg_total:.1f} kg** for {transport_tonnes} t of copper smelted (illustrative).")
        st.write("Captured SO₂ can be converted to sulfuric acid (H2SO4) — valuable industrial chemical (fertilizers, chemicals).")

    st.markdown("---")
    st.subheader("Compliance card (quick flags)")
    # compliance logic (simple)
    flags = []
    if storage_practice != "Proper authorized storage":
        flags.append(("Storage practice", "⚠️ Not authorized/temporary storage — requires review under Hazardous & Other Wastes Rules (2016)"))
    if metal == "Aluminium" and red_mud_t > 0:
        flags.append(("Red mud handling", "ℹ️ Red mud generation flagged — follow CPCB Guidelines for Handling & Management of Red Mud"))
    if metal == "Copper" and so2_kg_total > 0:
        flags.append(("Air emissions", "ℹ️ SO₂ emissions estimated — recommend gas capture & conversion to sulfuric acid; ensure air emission controls"))
    if circularity < 40:
        flags.append(("Circularity", "⚠️ Low circularity score — consider increasing recycled input or recycling infrastructure"))
    for f in flags:
        st.warning(f"{f[0]}: {f[1]}")

    st.markdown("---")
    st.subheader("Recommendations (illustrative & pro-government)")
    recs = []
    recs.append("Increase recycled feedstock where feasible — reduces primary extraction & supports National Mineral Policy objectives.")
    recs.append("Invest in RED MUD neutralization & valorization (cement substitution/pigments/REE recovery) — follow CPCB technical guidelines.")
    if metal == "Copper":
        recs.append("Install SO₂ capture + contact process to convert to sulphuric acid and supply local fertilizer/chemical plants.")
    recs.append("Engage with local SPCB/CPCB for authorization and safe handling steps (the tool generates a compliance checklist).")
    for r in recs:
        st.info(r)

    st.markdown("---")
    st.subheader("Export report")
    if st.button("Export PDF Summary"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 8, "SustainaMine - LCA Summary (Illustrative)", ln=True, align="C")
        pdf.ln(4)
        pdf.multi_cell(0, 6, f"Inputs:\nMetal: {metal}\nRoute: {production_route}\nRecycled%: {recycled_pct}\nEnergy: {energy_source}\nTransport: {transport_km} km x {transport_tonnes} t\nEnd-of-life: {eol_option}\nStorage: {storage_practice}\n")
        pdf.ln(2)
        pdf.multi_cell(0, 6, f"Estimated outputs (illustrative):\nCO2 per kg: {kgco2_per_kg:.2f} kg CO2/kg\nCO2 per t (incl transport): {total_co2_per_tonne:.0f} kg CO2/t\nCircularity score: {circularity:.1f}/100\n")
        if metal == "Aluminium":
            pdf.multi_cell(0,6,f"Red mud generation estimate: {red_mud_t:.2f} t (per {transport_tonnes} t Al) — consider CPCB-recommended valorization paths (cement, pigments, REE extraction).\n")
        else:
            pdf.multi_cell(0,6,f"SO2 estimate: {so2_kg_total:.1f} kg — recommend capture and conversion to sulfuric acid.\n")
        pdf.output("SustainaMine_LCA_Summary.pdf")
        st.success("SustainaMine_LCA_Summary.pdf generated (download from working directory).")

st.markdown("---")
st.header("Data sources & references (open links)")
for k, v in SOURCES.items():
    st.write(f"- **{k}** : {v}")

st.markdown("**Important note:** This prototype provides *illustrative* computations and policy references. Replace default parameters with validated process data and local SPCB thresholds before using for compliance submission. This tool **assists** compliance — it does not replace statutory approvals.")
