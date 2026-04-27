import streamlit as st
import plotly.graph_objects as go

st.set_page_config(
    page_title="Cashback Simulator – Accountable Banking",
    page_icon="💳",
    layout="wide"
)

# Accountable brand: purple #6C5DD3, dark #1A1A2E, clean whites
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&display=swap');

    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #1A1A2E;
        border-right: none;
    }
    [data-testid="stSidebar"] * { color: #E8E8F0 !important; }
    [data-testid="stSidebar"] .stSlider label { color: #A0A0C0 !important; font-size: 13px !important; }
    [data-testid="stSidebar"] h3 { color: #FFFFFF !important; font-size: 13px !important;
        text-transform: uppercase; letter-spacing: 0.1em; font-weight: 600; }
    [data-testid="stSidebar"] hr { border-color: #2E2E4E !important; }

    /* Slider accent */
    [data-testid="stSlider"] [data-baseweb="slider"] [role="slider"] {
        background: #6C5DD3 !important;
        border-color: #6C5DD3 !important;
    }

    /* Main area */
    .main .block-container { padding-top: 2rem; max-width: 1100px; }

    /* Logo bar */
    .brand-bar {
        display: flex; align-items: center; gap: 10px;
        margin-bottom: 0.25rem;
    }
    .brand-dot {
        width: 28px; height: 28px; border-radius: 7px;
        background: #6C5DD3;
        display: flex; align-items: center; justify-content: center;
        font-size: 14px; font-weight: 700; color: white;
    }
    .brand-name { font-size: 16px; font-weight: 600; color: #1A1A2E; letter-spacing: -0.01em; }
    .brand-sub  { font-size: 13px; color: #8A8AAA; margin-top: 2px; }

    /* KPI cards */
    .kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin: 1.5rem 0; }
    .kpi-card {
        background: white;
        border: 1px solid #EEEEF5;
        border-radius: 12px;
        padding: 1rem 1.25rem;
        position: relative;
        overflow: hidden;
    }
    .kpi-card::before {
        content: '';
        position: absolute; top: 0; left: 0; right: 0; height: 3px;
        background: #6C5DD3;
        border-radius: 12px 12px 0 0;
    }
    .kpi-card.pos::before { background: #22C55E; }
    .kpi-card.neg::before { background: #EF4444; }
    .kpi-card.warn::before { background: #F59E0B; }
    .kpi-label { font-size: 11px; font-weight: 600; text-transform: uppercase;
                 letter-spacing: 0.08em; color: #8A8AAA; margin-bottom: 6px; }
    .kpi-value { font-size: 24px; font-weight: 600; color: #1A1A2E; letter-spacing: -0.02em; }
    .kpi-value.pos { color: #16A34A; }
    .kpi-value.neg { color: #DC2626; }

    /* Breakdown rows */
    .breakdown-row {
        display: flex; justify-content: space-between; align-items: baseline;
        padding: 7px 0; border-bottom: 1px solid #F4F4F8; font-size: 13px;
    }
    .breakdown-row:last-child { border-bottom: none; }
    .row-lbl { color: #555570; }
    .row-lbl.bold { color: #1A1A2E; font-weight: 600; }
    .row-val { font-weight: 500; color: #1A1A2E; }
    .row-val.pos { color: #16A34A; }
    .row-val.neg { color: #DC2626; }
    .row-val.big { font-size: 16px; font-weight: 600; }

    .section-card {
        background: white; border: 1px solid #EEEEF5;
        border-radius: 12px; padding: 1.25rem 1.5rem; margin-bottom: 12px;
    }
    .section-title {
        font-size: 11px; font-weight: 600; text-transform: uppercase;
        letter-spacing: 0.08em; color: #8A8AAA; margin-bottom: 12px;
    }

    /* Tab bar */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0; border-bottom: 1px solid #EEEEF5;
        background: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        font-family: 'DM Sans', sans-serif !important;
        font-size: 13px !important; font-weight: 500 !important;
        color: #8A8AAA !important; background: transparent !important;
        border-radius: 0 !important; padding: 8px 20px !important;
        border-bottom: 2px solid transparent !important;
    }
    .stTabs [aria-selected="true"] {
        color: #6C5DD3 !important;
        border-bottom-color: #6C5DD3 !important;
    }
</style>
""", unsafe_allow_html=True)

# ── Constants ────────────────────────────────────────────────────────────────
MONTHS = 31
BASE_VERIFIED_START = 7041.75580590816

BUDGET_ACTIVES = [
    2357.28553550713,3320.18727820901,3888.34799997604,4120.13224201055,
    3941.11005854217,4198.1807111641,4749.4826748831,7379.82589515132,
    4980.63854702887,4257.71525677368,3244.81172048582,2680.20267693284,
    2573.7513856174,3630.49867277501,4251.81318877844,4082.92276038873,
    3506.26393834622,3729.67244853343,4211.03717666877,7379.82589515132,
    4980.63854702887,4257.71525677368,3244.81172048582,2680.20267693284,
    2573.7513856174,3630.49867277501,4251.81318877844,4082.92276038873,
    3506.26393834622,3729.67244853343,4211.03717666877
]
PAID_USERS = [
    19628.2392514931,20043.3005587735,20533.7177719302,21091.3763731082,
    21690.1291755324,22343.7578678667,23082.220261086,24130.9590696625,
    25078.4234287188,25940.221875577,26657.4377913277,27169.3572248991,
    27551.420679845,27919.4404118266,28346.5712796371,28797.1903484514,
    29229.1573289075,29680.941073812,30180.8624821454,31025.1875183094,
    31783.9879455532,32474.9573945397,33045.3940971994,33421.8903152632,
    33678.9031084017,33924.3731918123,34231.4054040231,34564.3277903496,
    34880.9520219677,35219.699873011,35608.8461053605
]

ESTER=0.019; SHARE_NEW=0.10; SHARE_PAID=0.025; CHURN=0.01
CARD_SHARE_BASE=0.70; ACTIVE_SHARE_BASE=0.60; TX_PER_CARD_BASE=8.3
AMT_PER_TX=52.0; AVG_BAL_BASE=2850.0

def interchange_rate(amt):
    tier = (0.4 if amt<=1e6 else 0.5 if amt<=2.5e6 else
            0.6 if amt<=5e6 else 0.7 if amt<=20e6 else 0.8)
    return ESTER * tier * 0.7

def simulate(acq_up, adopt_up, freq_up, bal_up, card_up, active_up):
    verified = BASE_VERIFIED_START
    monthly = []
    for i in range(MONTHS):
        budget      = BUDGET_ACTIVES[i] * (1 + acq_up)
        verified_in = budget * SHARE_NEW * (1 + adopt_up) + PAID_USERS[i] * SHARE_PAID
        churners    = BASE_VERIFIED_START * CHURN
        verified    = verified + verified_in - churners
        active_cards = verified * CARD_SHARE_BASE * (1+card_up) * ACTIVE_SHARE_BASE * (1+active_up)
        tx_count     = active_cards * TX_PER_CARD_BASE * (1 + freq_up)
        spend        = tx_count * AMT_PER_TX
        gross_int    = spend * interchange_rate(spend)
        balance      = verified * AVG_BAL_BASE * (1 + bal_up)
        interest     = ESTER * 0.8 * 0.81 * balance / 12
        monthly.append(dict(spend=spend, gross_int=gross_int,
                            interest=interest, active_cards=active_cards))
    return monthly

def cashback_cost(monthly, std_r, boost_r, prem_r, cap, mix_prem, mix_boost):
    mix_std = max(0.0, 1 - mix_prem - mix_boost)
    total = 0.0
    for m in monthly:
        uncapped = (m["spend"]*mix_prem*prem_r
                  + m["spend"]*mix_boost*boost_r
                  + m["spend"]*mix_std*std_r)
        total += min(uncapped, cap * m["active_cards"])
    return total

def fmt(v, sign=False):
    prefix = ("+" if v >= 0 else "") if sign else ""
    return f"{prefix}€{abs(round(v)):,.0f}".replace(",", ".")

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Cashback rates")
    std_r   = st.slider("Standard rate",            0.05, 1.0, 0.3,  0.05, format="%.2f%%") / 100
    boost_r = st.slider("Boosted rate (4 cats)",    0.5,  6.0, 2.0,  0.25, format="%.2f%%") / 100
    prem_r  = st.slider("Premium rate (sellers)",   1.0,  8.0, 4.0,  0.5,  format="%.2f%%") / 100
    cap     = st.slider("Monthly cap per user (€)", 5,  100,  30,    5)

    st.markdown("---")
    st.markdown("### Spend mix")
    mix_prem  = st.slider("% on premium sellers",    0.0, 10.0, 1.0, 0.5, format="%.1f%%") / 100
    mix_boost = st.slider("% on boosted categories", 1.0, 30.0, 9.3, 0.5, format="%.1f%%") / 100
    st.caption(f"Standard: {max(0,(1-mix_prem-mix_boost)*100):.1f}%")

    st.markdown("---")
    st.markdown("### Adoption uplifts")
    acq_up    = st.slider("New user acquisition",     0, 20, 2,  1, format="+%d%%") / 100
    adopt_up  = st.slider("Banking adoption rate",    0, 50, 20, 5, format="+%d%%") / 100
    freq_up   = st.slider("Transaction frequency",    0, 80, 40, 5, format="+%d%%") / 100
    bal_up    = st.slider("Average balance",           0, 20,  5, 1, format="+%d%%") / 100
    card_up   = st.slider("Card share uplift",         0, 20,  5, 1, format="+%d%%") / 100
    active_up = st.slider("Active card share uplift",  0, 50, 20, 5, format="+%d%%") / 100

# ── Compute ──────────────────────────────────────────────────────────────────
bl = simulate(0, 0, 0, 0, 0, 0)
cb = simulate(acq_up, adopt_up, freq_up, bal_up, card_up, active_up)

cb_cost  = cashback_cost(cb, std_r, boost_r, prem_r, cap, mix_prem, mix_boost)
bl_gross = sum(m["gross_int"] for m in bl)
cb_gross = sum(m["gross_int"] for m in cb)
bl_int   = sum(m["interest"]  for m in bl)
cb_int   = sum(m["interest"]  for m in cb)

ni_bl = bl_gross
ni_cb = cb_gross - cb_cost
d_ni  = ni_cb - ni_bl
d_int = cb_int - bl_int
pnl   = d_ni + d_int

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="brand-bar">
    <div class="brand-dot">A</div>
    <div>
        <div class="brand-name">Accountable Banking</div>
    </div>
</div>
<div class="brand-sub">Cashback program simulator &nbsp;·&nbsp; Germany &nbsp;·&nbsp; Jun 2026 – Dec 2028 &nbsp;·&nbsp; 31 months</div>
""", unsafe_allow_html=True)

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

# ── KPI cards ────────────────────────────────────────────────────────────────
pnl_class = "pos" if pnl >= 0 else "neg"
dni_class  = "pos" if d_ni >= 0 else "neg"

st.markdown(f"""
<div class="kpi-grid">
    <div class="kpi-card {pnl_class}">
        <div class="kpi-label">Net P&L vs. baseline</div>
        <div class="kpi-value {pnl_class}">{fmt(pnl, sign=True)}</div>
    </div>
    <div class="kpi-card warn">
        <div class="kpi-label">Total cashback paid out</div>
        <div class="kpi-value" style="color:#D97706">-{fmt(cb_cost)}</div>
    </div>
    <div class="kpi-card {dni_class}">
        <div class="kpi-label">Δ Net interchange</div>
        <div class="kpi-value {dni_class}">{fmt(d_ni, sign=True)}</div>
    </div>
    <div class="kpi-card pos">
        <div class="kpi-label">Δ Interest revenue</div>
        <div class="kpi-value pos">{fmt(d_int, sign=True)}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Tabs ─────────────────────────────────────────────────────────────────────
tab_chart, tab_breakdown = st.tabs(["📈  Chart", "📊  Full breakdown"])

with tab_chart:
    from datetime import date
    dates = []
    for i in range(MONTHS):
        y, m = 2026, 6 + i
        while m > 12: y += 1; m -= 12
        dates.append(date(y, m, 1))

    bl_ni_m, cb_ni_m = [], []
    for i, m in enumerate(cb):
        mix_std = max(0, 1 - mix_prem - mix_boost)
        unc = m["spend"]*mix_prem*prem_r + m["spend"]*mix_boost*boost_r + m["spend"]*mix_std*std_r
        cost_m = min(unc, cap * m["active_cards"])
        cb_ni_m.append(m["gross_int"] - cost_m)
    for m in bl:
        bl_ni_m.append(m["gross_int"])

    cum_pnl, running = [], 0
    for i in range(MONTHS):
        running += (cb_ni_m[i] - bl_ni_m[i]) + (cb[i]["interest"] - bl[i]["interest"])
        cum_pnl.append(running)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates, y=[round(v) for v in cb_ni_m],
        name="Net interchange — cashback",
        line=dict(color="#6C5DD3", width=2.5),
        fill="tozeroy", fillcolor="rgba(108,93,211,0.06)"
    ))
    fig.add_trace(go.Scatter(
        x=dates, y=[round(v) for v in bl_ni_m],
        name="Net interchange — baseline",
        line=dict(color="#C4C4D4", width=1.5, dash="dash")
    ))
    fig.add_trace(go.Scatter(
        x=dates, y=[round(v) for v in cum_pnl],
        name="Δ P&L cumulative", yaxis="y2",
        line=dict(color="#22C55E", width=2, dash="dot")
    ))

    fig.update_layout(
        height=340,
        paper_bgcolor="white", plot_bgcolor="white",
        font=dict(family="DM Sans, sans-serif", size=12, color="#555570"),
        yaxis=dict(
            title="Monthly net interchange (€)", tickformat=",.0f",
            gridcolor="#F4F4F8", gridwidth=1, zeroline=False
        ),
        yaxis2=dict(
            title="Cumulative Δ P&L (€)", overlaying="y", side="right",
            tickformat=",.0f", showgrid=False, zeroline=False,
            tickfont=dict(color="#16A34A")
        ),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
            font=dict(size=12)
        ),
        margin=dict(l=0, r=0, t=40, b=0),
        xaxis=dict(showgrid=False, zeroline=False)
    )
    st.plotly_chart(fig, use_container_width=True)

with tab_breakdown:
    c1, c2 = st.columns(2)

    with c1:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Interchange · 31 months cumulative</div>', unsafe_allow_html=True)
        rows1 = [
            ("Gross interchange — cashback",  fmt(cb_gross),       "", False),
            ("Gross interchange — baseline",  fmt(bl_gross),       "", False),
            ("Total cashback paid out",        f"-{fmt(cb_cost)}", "neg", False),
            None,
            ("Net interchange — cashback",    fmt(ni_cb),          "", True),
            ("Net interchange — baseline",    fmt(ni_bl),          "", True),
            ("Δ Net interchange",             fmt(d_ni, sign=True), "pos" if d_ni>=0 else "neg", True),
        ]
        for row in rows1:
            if row is None:
                st.markdown('<hr style="border:none;border-top:1px solid #F4F4F8;margin:6px 0">', unsafe_allow_html=True)
            else:
                lbl, val, cls, bold = row
                lb = "bold" if bold else ""
                vc = f' {cls}' if cls else ''
                st.markdown(f'<div class="breakdown-row"><span class="row-lbl {lb}">{lbl}</span><span class="row-val{vc}">{val}</span></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Interest & P&L · 31 months cumulative</div>', unsafe_allow_html=True)
        rows2 = [
            ("Interest revenue — cashback",  fmt(cb_int),           "", False),
            ("Interest revenue — baseline",  fmt(bl_int),           "", False),
            ("Δ Interest",                   fmt(d_int, sign=True), "pos", False),
            None,
            ("Net P&L vs. baseline",         fmt(pnl, sign=True),   "pos" if pnl>=0 else "neg", True),
        ]
        for row in rows2:
            if row is None:
                st.markdown('<hr style="border:none;border-top:1px solid #F4F4F8;margin:6px 0">', unsafe_allow_html=True)
            else:
                lbl, val, cls, bold = row
                lb = "bold" if bold else ""
                sz = " big" if bold else ""
                vc = f' {cls}{sz}' if cls else sz
                st.markdown(f'<div class="breakdown-row"><span class="row-lbl {lb}">{lbl}</span><span class="row-val{vc}">{val}</span></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Cashback breakdown
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Cashback breakdown · first month (Jun 2026)</div>', unsafe_allow_html=True)
    first = cb[0]
    mix_std_pct = max(0, 1 - mix_prem - mix_boost)
    cb_prem  = first["spend"] * mix_prem      * prem_r
    cb_boost = first["spend"] * mix_boost     * boost_r
    cb_std   = first["spend"] * mix_std_pct   * std_r
    uncapped = cb_prem + cb_boost + cb_std
    capped_v = min(uncapped, cap * first["active_cards"])

    bk = [
        (f"Premium sellers ({mix_prem*100:.1f}% × {prem_r*100:.1f}%)",    fmt(cb_prem),  "", False),
        (f"Boosted categories ({mix_boost*100:.1f}% × {boost_r*100:.1f}%)", fmt(cb_boost), "", False),
        (f"Standard ({mix_std_pct*100:.1f}% × {std_r*100:.2f}%)",           fmt(cb_std),   "", False),
        None,
        ("Total uncapped cashback",                                          fmt(uncapped), "", False),
        (f"Cap ceiling (€{cap} × {round(first['active_cards']):,} cards)",  fmt(cap*first["active_cards"]), "", False),
        ("Cashback cost (capped)",                                           f"-{fmt(capped_v)}", "neg", True),
    ]
    for row in bk:
        if row is None:
            st.markdown('<hr style="border:none;border-top:1px solid #F4F4F8;margin:6px 0">', unsafe_allow_html=True)
        else:
            lbl, val, cls, bold = row
            lb = "bold" if bold else ""
            vc = f' {cls}' if cls else ''
            st.markdown(f'<div class="breakdown-row"><span class="row-lbl {lb}">{lbl}</span><span class="row-val{vc}">{val}</span></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
