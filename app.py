import streamlit as st
import pandas as pd

# ==========================================
# 1. PAGE CONFIG & ASSETS
# ==========================================
st.set_page_config(page_title="PSPCL Rate Calculator 2026", page_icon="💰", layout="wide")

# Assets
PSPCL_LOGO = "https://pspcl.in/assets/images/logo.png"
BEECLUE_LOGO_PNG = "https://raw.githubusercontent.com/iamanujnarang/LDHF/e5748e037b76a52a47d610a88c3a3c70f72f1c9a/BEECLUE.png"
INSTA_ICON = "https://upload.wikimedia.org/wikipedia/commons/a/a5/Instagram_icon.png"
FB_ICON = "https://upload.wikimedia.org/wikipedia/commons/1/1b/Facebook_icon.svg"
X_ICON = "https://upload.wikimedia.org/wikipedia/commons/b/b7/X_logo.jpg"
LINKEDIN_ICON = "https://upload.wikimedia.org/wikipedia/commons/c/ca/LinkedIn_logo_initials.png"

# Custom CSS for uniform UI
st.markdown(f"""
    <style>
    .main {{ background-color: #f8fafc; }}
    .header-box {{ text-align: center; padding: 25px; background: white; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 25px; }}
    
    .total-card {{ background: #0b79d0; color: white; padding: 30px; border-radius: 20px; text-align: center; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); }}
    .result-card {{ background: white; padding: 20px; border-radius: 15px; border-left: 5px solid #0b79d0; margin-bottom: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }}
    
    .footer-container {{ text-align: center; margin-top: 80px; padding: 40px 20px; border-top: 1px solid #ddd; }}
    .made-with-love {{ font-size: 1.2rem; color: #334155; margin-bottom: 20px; }}
    .heart-symbol {{ color: #e63946; }}
    .social-icon {{ width: 30px; margin: 0 10px; transition: 0.3s; }}
    .social-icon:hover {{ transform: scale(1.2); }}
    .powered-text {{ color: #94a3b8; font-size: 0.7rem; letter-spacing: 2px; margin-bottom: 10px; text-transform: uppercase; }}
    .beeclue-img {{ width: 180px; height: auto; }}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. CALCULATION LOGIC (CC 51/2024 & 25/2025)
# ==========================================
def calculate_rates(category, load):
    # 2026 Factor (6% compounded on normative data) [cite: 125, 126]
    year_factor = 1.06 
    
    acd = 0
    scc = 0
    meter_sec = 0
    p_fee = 0
    
    # 1. PROCESSING FEE [cite: 339]
    if load <= 7: p_fee = 35 if category == "DS" else 85
    elif load <= 100: p_fee = 180
    elif load <= 150: p_fee = 1000
    else: p_fee = min(load * 12, 4000) 
        
    # 2. ACD / SECURITY CONSUMPTION [cite: 342, 346]
    if category == "DS":
        if load <= 7: acd = load * 600
        elif load <= 20: acd = load * 300
        else: acd = load * 500
    elif category == "NRS":
        if load <= 7: acd = load * 880
        elif load <= 20: acd = load * 470
        else: acd = load * 700
    elif category == "SP": acd = load * 650
    elif category == "MS": acd = load * 900
    elif category == "LS": acd = load * 1900

    # 3. SCC / PROPORTIONATE COST [cite: 195, 201, 207]
    if load <= 100:
        if category == "DS":
            if load <= 2: scc = load * 550
            elif load <= 7: scc = load * 1250
            else: scc = load * 1900
        elif category == "NRS":
            if load <= 7: scc = load * 1250
            elif load <= 20: scc = load * 2000
            else: scc = load * 2300
        elif category in ["SP", "MS"]: scc = load * 3250
    elif load <= 150:
        scc = load * 1400 # Normative [cite: 201]
    else:
        # 1230 base + 6% for 2026 [cite: 125, 207]
        scc = load * (1230 * year_factor)

    # 4. METER SECURITY [cite: 346]
    if load <= 7: meter_sec = 680
    elif load <= 20: meter_sec = 1290
    elif load <= 100: meter_sec = 2460
    else: meter_sec = 83240 

    return p_fee, acd, scc, meter_sec

# ==========================================
# 3. MAIN APP
# ==========================================
st.markdown(f'<div class="header-box"><img src="{PSPCL_LOGO}" width="140"><h1>💰 PSPCL Rate Calculator</h1><p>Standard Cost Data & General Charges (Updated May 2026)</p></div>', unsafe_allow_html=True)

col_in, col_out = st.columns([1, 1], gap="large")

with col_in:
    st.subheader("📋 Input Parameters")
    cat = st.selectbox("Consumer Category", ["DS", "NRS", "SP", "MS", "LS"])
    ld = st.number_input("Applied Load (kW/kVA)", min_value=0.1, value=5.0, step=1.0)
    type_conn = st.radio("Application Type", ["New Connection", "Extension of Load"])

with col_out:
    pf, ac, sc, ms = calculate_rates(cat, ld)
    total = pf + ac + sc + ms
    
    st.markdown('<div class="total-card">', unsafe_allow_html=True)
    st.markdown(f"<h3>Estimated Demand Amount</h3><h1>₹ {total:,.2f}</h1>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.divider()
st.subheader("📊 Breakdown of Charges")

b1, b2 = st.columns(2)
with b1:
    st.markdown(f'<div class="result-card"><b>Service Connection Charges (SCC):</b><br>₹ {sc:,.2f}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="result-card"><b>Security Consumption (ACD):</b><br>₹ {ac:,.2f}</div>', unsafe_allow_html=True)
with b2:
    st.markdown(f'<div class="result-card"><b>Meter Security:</b><br>₹ {ms:,.2f}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="result-card"><b>Processing Fee:</b><br>₹ {pf:,.2f}</div>', unsafe_allow_html=True)

st.info(f"💡 **Note:** Calculations include the mandatory 6% annual compounded increase for 2026 as per CC 51/2024[cite: 125, 126].")

# ==========================================
# 4. STANDARD FOOTER (Uniform Styling)
# ==========================================
footer_html = f"""
<div class="footer-container">
    <div class="made-with-love">Made with <span class="heart-symbol">❤️</span> by <b>Er. Anuj Narang, JE PSPCL</b></div>
    <div style="margin-bottom: 25px;">
        <a href="https://instagram.com/iamanujnarang" target="_blank"><img src="{INSTA_ICON}" class="social-icon"></a>
        <a href="https://facebook.com/iamanujnarang" target="_blank"><img src="{FB_ICON}" class="social-icon"></a>
        <a href="https://x.com/iamanujnarang" target="_blank"><img src="{X_ICON}" class="social-icon"></a>
        <a href="https://linkedin.com/in/iamanujnarang" target="_blank"><img src="{LINKEDIN_ICON}" class="social-icon"></a>
    </div>

    <div style="margin-top: 25px;">
        <div class="powered-text">In Strategic Collaboration with</div>
        <a href="https://beeclue.com" target="_blank">
            <img src="{BEECLUE_LOGO_PNG}" class="beeclue-img">
        </a>
    </div>

    <div style="color: #94a3b8; font-size: 0.85rem; margin-top: 25px;">© 2026 | PSPCL Guidelines | CC 51/2024 & 25/2025</div>
</div>
"""
st.markdown(footer_html, unsafe_allow_html=True)
