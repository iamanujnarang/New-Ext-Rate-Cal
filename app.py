import streamlit as st
import pandas as pd
import numpy as np

# ==========================================
# 1. PAGE CONFIG & PREMIUM ASSETS
# ==========================================
st.set_page_config(page_title="PSPCL Demand Notice Pro", page_icon="💰", layout="wide")

# Official Assets
PSPCL_LOGO = "https://pspcl.in/assets/images/logo.png"
BEECLUE_LOGO_PNG = "https://raw.githubusercontent.com/iamanujnarang/LDHF/e5748e037b76a52a47d610a88c3a3c70f72f1c9a/BEECLUE.png"
INSTA_ICON = "https://upload.wikimedia.org/wikipedia/commons/a/a5/Instagram_icon.png"
FB_ICON = "https://upload.wikimedia.org/wikipedia/commons/1/1b/Facebook_icon.svg"
X_ICON = "https://upload.wikimedia.org/wikipedia/commons/b/b7/X_logo.jpg"
LINKEDIN_ICON = "https://upload.wikimedia.org/wikipedia/commons/c/ca/LinkedIn_logo_initials.png"

# Custom Premium CSS UI 
st.markdown(f"""
    <style>
    .main {{ background-color: #f8fafc; }}
    
    /* Header Container */
    .header-box {{ 
        text-align: center; 
        padding: 30px 20px; 
        background: #ffffff; 
        border-radius: 20px; 
        box-shadow: 0 10px 25px -5px rgba(0,0,0,0.05); 
        margin-bottom: 35px; 
        border-top: 6px solid #0b79d0;
    }}
    
    /* Modern Dashboard Cards */
    .dashboard-card {{
        background: #ffffff;
        padding: 24px;
        border-radius: 16px;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.03);
        border: 1px solid #e2e8f0;
        margin-bottom: 20px;
    }}
    
    /* Premium Billing Live Panel */
    .total-panel {{ 
        background: linear-gradient(135deg, #1e3a8a 0%, #0b79d0 100%); 
        color: #ffffff; 
        padding: 40px 30px; 
        border-radius: 24px; 
        text-align: center; 
        box-shadow: 0 20px 40px -15px rgba(11, 121, 208, 0.4);
        position: sticky;
        top: 40px;
    }}
    
    /* Technical Formula Styling */
    .formula-text {{ 
        font-family: 'Consolas', 'Courier New', monospace; 
        color: #0f172a; 
        background: #f1f5f9; 
        padding: 12px 16px; 
        border-radius: 10px; 
        font-size: 0.92rem; 
        border-left: 4px solid #0b79d0;
        margin-top: 10px;
        line-height: 1.5;
    }}
    
    .item-title {{
        font-size: 1.1rem;
        font-weight: 700;
        color: #1e293b;
    }}
    
    .item-price {{
        font-size: 1.5rem;
        font-weight: 800;
        color: #0b79d0;
        text-align: right;
    }}
    
    /* Footer Styling */
    .footer-container {{ text-align: center; margin-top: 90px; padding: 40px 20px; border-top: 1px solid #e2e8f0; }}
    .made-with-love {{ font-size: 1.2rem; color: #334155; margin-bottom: 20px; }}
    .heart-symbol {{ color: #e63946; }}
    .social-icon {{ width: 30px; margin: 0 10px; transition: 0.3s; }}
    .social-icon:hover {{ transform: scale(1.2); }}
    .powered-text {{ color: #94a3b8; font-size: 0.7rem; letter-spacing: 2px; margin-bottom: 10px; text-transform: uppercase; }}
    .beeclue-img {{ width: 180px; height: auto; }}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. INDIAN COMPACT CURRENCY SYSTEM
# ==========================================
def format_indian(number):
    s = str(int(round(number)))
    if len(s) <= 3: return s
    last_three = s[-3:]
    remaining = s[:-3]
    remaining = ",".join([remaining[max(i-2, 0):i] for i in range(len(remaining), 0, -2)][::-1])
    return remaining + "," + last_three

# ==========================================
# 3. ADVANCED COMPUTATION (CC 51/2024 & 25/2025)
# ==========================================
def run_rate_engine(app_mode, category, input_load, load_unit, existing_load):
    year_factor = 1.06 # 2026 Compounded Factor [cite: 125, 126]
    meta = {}
    
    # Base configuration targets
    curr_input = input_load if app_mode == "New Connection" else (existing_load + input_load)
    calc_load = input_load # For processing and absolute SCC bounds
    
    # --- Dynamic Power Factor Engine (kW to kVA Rules) ---
    if load_unit == "kW" and curr_input > 20:
        base_load = curr_input / 0.95
        factor_load = input_load / 0.95
        meta['conv_note'] = f"⚠️ Total load ({curr_input:.2f} kW) crossed 20 kW threshold. Calculated using 0.95 Power Factor onto a <b>{base_load:.2f} kVA</b> base framework."
    else:
        base_load = curr_input
        factor_load = input_load
        meta['conv_note'] = f"Target total calculation infrastructure evaluated at <b>{base_load:.2f} {load_unit}</b>."

    # 1. PROCESSING FEE (CC 25/2025 Page 4) 
    # Chargeable on the extension quantum or full new load capacity
    fee_load = factor_load if app_mode == "Extension of Load" else base_load
    if fee_load <= 7: p_fee = 35 if category == "DS" else 85
    elif fee_load <= 100: p_fee = 180
    elif fee_load <= 150: p_fee = 1000
    else: p_fee = min(fee_load * 12, 4000)
    meta['PF_EQ'] = f"Processing Fee Segment Base = ₹{format_indian(p_fee)}"

    # 2. ACD SECURITY DEPOSIT (CC 25/2025 Page 5-6) [cite: 245, 249]
    if category == "DS":
        if base_load <= 7: rate = 600; eq = f"₹600/kW Slab (Bi-monthly Infrastructure)"
        elif base_load <= 20: rate = 300; eq = f"₹300/kW Slab Matrix"
        else: rate = 500; eq = f"₹500/kVA Volumetric Bracket"
    elif category == "NRS":
        if base_load <= 7: rate = 880; eq = f"₹880/kW Slab (Bi-monthly Infrastructure)"
        elif base_load <= 20: rate = 470; eq = f"₹470/kW Slab Matrix"
        else: rate = 700; eq = f"₹700/kVA Volumetric Bracket"
    elif category == "SP": rate = 650; eq = f"₹650/kVA Small Power Standard"
    elif category == "MS": rate = 900; eq = f"₹900/kVA Medium Power Standard"
    elif category == "LS": rate = 1900; eq = f"₹1,900/kVA Large Industry General Base"
    
    if app_mode == "New Connection":
        acd = base_load * rate
        meta['ACD_EQ'] = f"{base_load:.2f} Capacity x {eq}"
    else:
        # Dynamic differential calculation for extension
        prev_calc_load = existing_load / 0.95 if (load_unit == "kW" and existing_load > 20) else existing_load
        acd = (base_load * rate) - (prev_calc_load * rate)
        if acd < 0: acd = 0
        meta['ACD_EQ'] = f"Differential Assessment: [Total {base_load:.2f} - Existing {prev_calc_load:.2f}] x {eq}"

    # 3. SCC / SERVICE CONNECTION CHARGES (CC 51/2024 Annexure-1) [cite: 96, 97]
    # Charged purely on the additional extension load or total new load asset value
    if base_load <= 100:
        if category == "DS":
            s_rate = 550 if base_load <= 2 else (1250 if base_load <= 7 else (1900 if base_load <= 50 else 2100))
        elif category == "NRS":
            s_rate = 1250 if base_load <= 7 else (2000 if base_load <= 20 else 2300)
        else: s_rate = 3250
        scc = factor_load * s_rate
        meta['SCC_EQ'] = f"{factor_load:.2f} Extension/New Units x Active Slab Rate ₹{s_rate}"
    elif base_load <= 150:
        scc = factor_load * 1400 [cite: 104]
        meta['SCC_EQ'] = f"{factor_load:.2f} Extension/New Capacity kVA x Normative Rate ₹1,400" [cite: 104]
    else:
        prop_rate = 1230 * year_factor # Base ₹1230 + 6% compounding 2026 inflation escalation [cite: 110, 125]
        scc = factor_load * prop_rate
        meta['SCC_EQ'] = f"{factor_load:.2f} Extension/New kVA x (₹1,230 Base x 1.06 Inflation Index) = ₹{prop_rate:.2f}/kVA" [cite: 110, 125]

    # 4. INITIAL METER SECURITY (CC 25/2025 Page 6) [cite: 249]
    # Extension only changes meter charges if system threshold shifts hardware category
    if base_load <= 7: m_sec = 680; m_lbl = "Single Phase Static System"
    elif base_load <= 20: m_sec = 1290; m_lbl = "Three Phase Whole Current System"
    elif base_load <= 100: m_sec = 2460; m_lbl = "LT CT Operated Volumetric System"
    else: m_sec = 83240; m_lbl = "11kV Heavy Duty CT/PT Substation Unit"
    
    if app_mode == "Extension of Load":
        m_sec = 0 # Handled if hardware upgrade is explicitly specified by user
        m_lbl += " (Existing structure preserved without hardware revision)"
    meta['MS_EQ'] = m_lbl

    # 5. MCB SECURITY ENCLOSURES (CC 25/2025 Page 6) [cite: 249]
    if base_load <= 7: mcb = 590; mcb_lbl = "Single Phase Standard Enclosure Setup"
    elif base_load <= 100: mcb = 1140; mcb_lbl = "Three Phase/LT CT MMB Box Enclosure"
    else: mcb = 6570; mcb_lbl = "HT Structural Protective Cubicle Installation"
    
    if app_mode == "Extension of Load":
        mcb = 0
        mcb_lbl += " (Enclosure system asset status maintained)"
    meta['MCB_EQ'] = mcb_lbl

    return p_fee, acd, scc, m_sec, mcb, meta, base_load

# ==========================================
# 4. MODERN APPLICATION INTERFACE
# ==========================================
st.markdown(f"""
    <div class="header-box">
        <img src="{PSPCL_LOGO}" width="150">
        <h1 style="color: #0f172a; margin-top: 15px; font-weight: 800;">Demand Notice Estimation Terminal</h1>
        <p style="color: #475569; font-size: 1.1rem; margin-bottom:0;">Fully Compliant with PSERC Supply Code 2024 Framework</p>
    </div>
""", unsafe_allow_html=True)

# Main Two-Column UI Frame
col_panel, col_live = st.columns([1.1, 1], gap="large")

with col_panel:
    st.markdown("### 📋 Configuration Panel")
    with st.container(border=True):
        app_mode = st.selectbox("Application Request Category", ["New Connection", "Extension of Load"])
        cat_select = st.selectbox("Consumer Category Profile", ["DS", "NRS", "SP", "MS", "LS"], 
                                  help="DS=Domestic, NRS=Commercial, SP/MS/LS=Industrial Tiers")
        
        c_unit1, c_unit2 = st.columns([2, 1])
        load_input = c_unit1.number_input("Load Target Quantum (Applied Load)", min_value=0.1, value=5.0, step=1.0)
        unit_select = c_unit2.selectbox("Load Unit", ["kW", "kVA"])
        
        existing_load = 0.0
        if app_mode == "Extension of Load":
            existing_load = st.number_input("Enter Existing Sanctioned Load Capacity", min_value=0.0, value=0.0, step=1.0)
        
    pf, ac, sc, ms, mcb, calc_meta, final_billing_load = run_rate_engine(app_mode, cat_select, load_input, unit_select, existing_load)
    total_dn_amount = pf + ac + sc + ms + mcb

    st.write("")
    st.markdown("### 🔍 Itemized Calculations")
    
    # 1. SCC Expandable Card
    with st.expander("🚠 Service Connection Charges (SCC)", expanded=True):
        st.markdown(f"""
        <table style="width:100%;"><tr>
            <td class="item-title">Calculated Value:</td>
            <td class="item-price">₹ {format_indian(sc)}</td>
        </tr></table>
        <div class="formula-text"><b>PSPCL Logic:</b> {calc_meta['SCC_EQ']}</div>
        """, unsafe_allow_html=True)

    # 2. ACD Expandable Card
    with st.expander("🔒 Security Consumption (ACD)", expanded=True):
        st.markdown(f"""
        <table style="width:100%;"><tr>
            <td class="item-title">Calculated Value:</td>
            <td class="item-price">₹ {format_indian(ac)}</td>
        </tr></table>
        <div class="formula-text"><b>PSPCL Logic:</b> {calc_meta['ACD_EQ']}</div>
        """, unsafe_allow_html=True)

    # 3. Meter & MCB Security Card
    with st.expander("📟 Metering Hardware & Enclosure Security", expanded=False):
        st.markdown(f"""
        <table style="width:100%;">
            <tr><td class="item-title">Meter Base Security:</td><td class="item-price" style="font-size:1.2rem;">₹ {format_indian(ms)}</td></tr>
            <tr><td class="item-title">MCB Box Security:</td><td class="item-price" style="font-size:1.2rem;">₹ {format_indian(mcb)}</td></tr>
            <tr style="border-top:1px solid #ddd;"><td class="item-title" style="padding-top:10px;">Subtotal Hardware:</td><td class="item-price" style="padding-top:10px;">₹ {format_indian(ms+mcb)}</td></tr>
        </table>
        <div class="formula-text"><b>Meter Class:</b> {calc_meta['MS_EQ']}<br><b>Enclosure Type:</b> {calc_meta['MCB_EQ']}</div>
        """, unsafe_allow_html=True)

    # 4. Processing Fee Card
    with st.expander("📑 Processing & Administrative Charges", expanded=False):
        st.markdown(f"""
        <table style="width:100%;"><tr>
            <td class="item-title">Calculated Value:</td>
            <td class="item-price">₹ {format_indian(pf)}</td>
        </tr></table>
        <div class="formula-text"><b>PSPCL Logic:</b> {calc_meta['PF_EQ']}</div>
        """, unsafe_allow_html=True)


with col_live:
    st.markdown("### 📊 Live Summary Status")
    
    # Real-Time Dynamic Total Calculation Dashboard Panel
    st.markdown(f"""
        <div class="total-panel">
            <span style="font-size: 1.15rem; text-transform: uppercase; letter-spacing: 2px; opacity: 0.85; font-weight: 600;">Demand Notice Estimate</span>
            <h1 style="font-size: 4.2rem; font-weight: 900; margin: 15px 0 10px 0; letter-spacing: -1px;">₹ {format_indian(total_dn_amount)}</h1>
            <div style="background: rgba(255,255,255,0.15); padding: 12px 18px; border-radius: 12px; font-size: 0.95rem; line-height: 1.4; text-align: left; margin-top:25px;">
                {calc_meta['conv_note']}
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    # Quick Regulatory Reference Table 
    with st.container(border=True):
        st.markdown("**⚡ Quick Reference Regulatory Thresholds:**")
        ref_data = pd.DataFrame({
            "Load Threshold": ["Upto 100 kW/kVA", "101 to 150 kVA", "Above 150 kVA"],
            "SCC Methodology Base": ["Fixed Category Slabs", "Normative Fixed Cost (₹1,400/kVA)", "Proportionate Cost + 6% Compounded Increase"],
            "System Tier": ["LT System Supply", "HT 11kV Framework", "HT Line Apportionment"]
        })
        st.table(ref_data)

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
