import streamlit as st
import pandas as pd
import numpy as np

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

# Custom CSS
st.markdown(f"""
    <style>
    .main {{ background-color: #f8fafc; }}
    .header-box {{ text-align: center; padding: 25px; background: white; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 25px; }}
    .total-card {{ background: #0b79d0; color: white; padding: 30px; border-radius: 20px; text-align: center; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); }}
    .calc-details {{ background: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e2e8f0; margin-top: 10px; font-family: monospace; color: #475569; }}
    
    /* Footer Styling */
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
# 2. HELPER FUNCTIONS
# ==========================================
def format_indian(number):
    """Formats number to Indian Rupee System (Commas)"""
    s = str(int(number))
    if len(s) <= 3: return s
    last_three = s[-3:]
    remaining = s[:-3]
    remaining = ",".join([remaining[max(i-2, 0):i] for i in range(len(remaining), 0, -2)][::-1])
    return remaining + "," + last_three

# ==========================================
# 3. CALCULATION LOGIC (CC 51/2024 & 25/2025)
# ==========================================
def calculate_rates(category, load):
    year_factor = 1.06 # 2026 6% increment [cite: 125, 126]
    details = {}
    
    # 1. PROCESSING FEE [cite: 339]
    if load <= 7: 
        p_fee = 35 if category == "DS" else 85
        details['PF'] = f"Fixed Slab: ₹{p_fee}"
    elif load <= 100: 
        p_fee = 180
        details['PF'] = f"LT Three Phase: ₹180"
    elif load <= 150: 
        p_fee = 1000
        details['PF'] = f"HT Normative: ₹1,000"
    else: 
        p_fee = min(load * 12, 4000) 
        details['PF'] = f"HT Variable: {load} kVA x ₹12 (Max 4000) = ₹{format_indian(p_fee)}"
        
    # 2. ACD / SECURITY CONSUMPTION [cite: 342, 346]
    if category == "DS":
        if load <= 7: 
            acd = load * 600
            details['ACD'] = f"{load} kW x ₹600 (Bimonthly)"
        elif load <= 20: 
            acd = load * 300
            details['ACD'] = f"{load} kW x ₹300"
        else: 
            acd = load * 500
            details['ACD'] = f"{load} kVA x ₹500"
    elif category == "NRS":
        if load <= 7: 
            acd = load * 880
            details['ACD'] = f"{load} kW x ₹880"
        elif load <= 20: 
            acd = load * 470
            details['ACD'] = f"{load} kW x ₹470"
        else: 
            acd = load * 700
            details['ACD'] = f"{load} kVA x ₹700"
    elif category == "SP": 
        acd = load * 650
        details['ACD'] = f"{load} kVA x ₹650"
    elif category == "MS": 
        acd = load * 900
        details['ACD'] = f"{load} kVA x ₹900"
    elif category == "LS": 
        acd = load * 1900
        details['ACD'] = f"{load} kVA x ₹1,900"

    # 3. SCC / PROPORTIONATE COST [cite: 195, 201, 207]
    if load <= 100:
        if category == "DS":
            rate = 550 if load <= 2 else (1250 if load <= 7 else 1900)
        elif category == "NRS":
            rate = 1250 if load <= 7 else (2000 if load <= 20 else 2300)
        else: rate = 3250
        scc = load * rate
        details['SCC'] = f"{load} units x ₹{rate} (Fixed SCC)"
    elif load <= 150:
        scc = load * 1400 
        details['SCC'] = f"{load} kVA x ₹1,400 (Normative HT)"
    else:
        prop_rate_2026 = 1230 * year_factor
        scc = load * prop_rate_2026
        details['SCC'] = f"{load} kVA x (₹1,230 x 1.06 increment) = ₹{format_indian(scc)}"

    # 4. METER SECURITY [cite: 346]
    if load <= 7: 
        m_sec = 680
        details['MS'] = "Single Phase Static/Smart Meter: ₹680"
    elif load <= 20: 
        m_sec = 1290
        details['MS'] = "Three Phase Whole Current: ₹1,290"
    elif load <= 100: 
        m_sec = 2460
        details['MS'] = "LT CT Operated Meter: ₹2,460"
    else: 
        m_sec = 83240 
        details['MS'] = "11kV CT/PT Unit: ₹83,240"

    return p_fee, acd, scc, m_sec, details

# ==========================================
# 4. MAIN INTERFACE
# ==========================================
st.markdown(f'<div class="header-box"><img src="{PSPCL_LOGO}" width="140"><h1>💰 PSPCL Rate Calculator</h1><p>Supply Code 2024 & CC 51/2024 | <b>Updated May 2026</b></p></div>', unsafe_allow_html=True)

col_in, col_out = st.columns([1, 1], gap="large")

with col_in:
    st.subheader("📋 Application Data")
    cat = st.selectbox("Consumer Category", ["DS", "NRS", "SP", "MS", "LS"])
    ld = st.number_input("Enter Applied Load (kW/kVA)", min_value=0.1, value=5.0, step=1.0)
    st.info("Note: SCC for >150kVA includes mandatory 6% compounded increase for 2026[cite: 125].")

with col_out:
    pf, ac, sc, ms, calc_text = calculate_rates(cat, ld)
    total = pf + ac + sc + ms
    
    st.markdown('<div class="total-card">', unsafe_allow_html=True)
    st.markdown(f"<h3>Total Estimated Amount</h3><h1>₹ {format_indian(total)}</h1>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.divider()
st.subheader("📊 Breakdown & Formulas")

# Display Breakdown with calculation logic
def show_calc(title, amount, formula):
    st.markdown(f"**{title}**")
    st.markdown(f"Amount: `₹ {format_indian(amount)}`")
    st.markdown(f'<div class="calc-details">Formula: {formula}</div>', unsafe_allow_html=True)
    st.write("")

c1, c2 = st.columns(2)
with c1:
    show_calc("Service Connection Charges (SCC)", sc, calc_text['SCC'])
    show_calc("Security Consumption (ACD)", ac, calc_text['ACD'])
with c2:
    show_calc("Meter Security", ms, calc_text['MS'])
    show_calc("Processing Fee", pf, calc_text['PF'])

# ==========================================
# 5. RESTORED ORIGINAL FOOTER
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

<div style="color: #94a3b8; font-size: 0.85rem; margin-top: 25px;">© 2026 | PSPCL Guidelines | CC 45/2024</div>
</div>
"""
st.markdown(footer_html, unsafe_allow_html=True)
