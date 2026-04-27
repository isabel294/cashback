import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Cashback Simulator – Accountable", layout="wide")

st.markdown("""
<style>
    .metric-card { background: #f8f9fa; border-radius: 10px; padding: 1rem 1.25rem; margin-bottom: 0.5rem; }
    .metric-label { font-size: 12px; color: #666; margin-bottom: 2px; }
    .metric-value { font-size: 22px; font-weight: 600; }
    .positive { color: #1a7f5a; }
    .negative { color: #c0392b; }
    .neutral { color: #1a1a1a; }
    .section-header { font-size: 11px; font-weight: 600; text-transform: uppercase;
                      letter-spacing: 0.08em; color: #999; margin: 1rem 0 0.5rem; }
    .divider { border-top: 1px solid #eee; margin: 0.75rem 0; }
</style>
""", unsafe_allow_html=True)

st.title("Cashback program simulator")
st.caption("Germany · Jun 2026 – Dec 2028 · 31 months")

# ── Constants ────────────────────────────────────────────────────────────────
MONTHS = 31
BASE_VERIFIED_START = 7042
BUDGET_ACTIVES = [2357,3320,3888,4120,3941,4198,4749,7380,4981,4258,3245,2680,
                  2574,3630,4252,4083,3506,3730,4211,7380,4981,4258,3245,2680,
                  2574,3630,4252,4083,3506,3730,4211]
PAID_USERS = [19628,20043,20534,21091,21690,22344,23082,24131,25078,25940,26657,
              27169,27551,27919,28347,28797,29229,29681,30181,31025,31784,32475,
              33045,33422,33679,33924,34231,34564,34881,35220,35609]
ESTER       = 0.019
SHARE_NEW   = 0.10
SHARE_PAID  = 0.025
CHURN       = 0.01
CARD_SHARE_BASE   = 0.70
ACTIVE_SHARE_BASE = 0.60
TX_PER_CARD_BASE  = 8.3
AMT_PER_TX        = 52.0
AVG_BAL_BASE      = 2850.0

def interchange_rate(amt):
    tier = (0.4 if amt <= 1e6 else 0.5 if amt <= 2.5e6 else
            0.6 if amt <= 5e6 else 0.7 if amt <= 20e6 else 0.8)
    return ESTER * tier * 0.7

def simulate(acq_up, adopt_up, freq_up, bal_up, card_up, active_up):
    verified = BASE_VERIFIED_START
    monthly = []
    for i in range(MONTHS):
        budget      = BUDGET_ACTIVES[i] * (1 + acq_up)
        verified_in = budget * SHARE_NEW * (1 + adopt_up) + PAID_USERS[i] * SHARE_PAID
        churners    = verified * CHURN
        verified    = verified + verified_in - churners

        active_cards = verified * CARD_SHARE_BASE * (1 + card_up) * ACTIVE_SHARE_BASE * (1 + active_up)
        tx_count     = active_cards * TX_PER_CARD_BASE * (1 + freq_up)
        spend        = tx_count * AMT_PER_TX
        gross_int    = spend * interchange_rate(spend)
        balance      = verified * AVG_BAL_BASE * (1 + bal_up)
        interest     = ESTER * 0.8 * 0.81 * balance / 12

        monthly.append(dict(spend=spend, gross_int=gross_int, interest=interest, active_cards=active_cards))
    return monthly

def cashback_cost(monthly, std_r, boost_r, prem_r, cap, mix_prem, mix_boost):
    mix_std = max(0.0, 1 - mix_prem - mix_boost)
    total = 0.0
    for m in monthly:
        uncapped = (m["spend"] * mix_prem  * prem_r
                  + m["spend"] * mix_boost * boost_r
                  + m["spend"] * mix_std   * std_r)
        total += min(uncapped, cap * m["active_cards"])
    return total

def fmt_eur(v, sign=False):
    prefix = ("+" if v >= 0 else "") if sign else ""
    return f"{prefix}€{abs(round(v)):,.0f}".replace(",", ".")

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Cashback rates")
    std_r   = st.slider("Standard rate",          0.05, 1.0,  0.3,  0.05, format="%.2f%%") / 100
    boost_r = st.slider("Boosted rate (4 cats)",  0.5,  6.0,  2.0,  0.25, format="%.2f%%") / 100
    prem_r  = st.slider("Premium rate (sellers)", 1.0,  8.0,  4.0,  0.5,  format="%.2f%%") / 100
    cap     = st.slider("Monthly cap per user (€)", 5, 100, 30, 5)

    st.markdown("---")
    st.markdown("### Spend mix")
    mix_prem  = st.slider("% on premium sellers",     0.0, 10.0, 1.0, 0.5, format="%.1f%%") / 100
    mix_boost = st.slider("% on boosted categories",  1.0, 30.0, 9.3, 0.5, format="%.1f%%") / 100
    st.caption(f"Standard: {max(0,(1-mix_prem-mix_boost)*100):.1f}%")

    st.markdown("---")
    st.markdown("### Adoption uplifts vs. baseline")
    acq_up    = st.slider("New user acquisition",   0, 20, 2,  1, format="+%d%%") / 100
    adopt_up  = st.slider("Banking adoption rate",  0, 50, 20, 5, format="+%d%%") / 100
    freq_up   = st.slider("Transaction frequency",  0, 80, 40, 5, format="+%d%%") / 100
    bal_up    = st.slider("Average balance",         0, 20, 5,  1, format="+%d%%") / 100

# ── Compute ──────────────────────────────────────────────────────────────────
card_up   = adopt_up * 0.25
active_up = adopt_up * 0.5

bl = simulate(0, 0, 0, 0, 0, 0)
cb = simulate(acq_up, adopt_up, freq_up, bal_up, card_up, active_up)
cb_cost = cashback_cost(cb, std_r, boost_r, prem_r, cap, mix_prem, mix_boost)

bl_gross  = sum(m["gross_int"] for m in bl)
cb_gross  = sum(m["gross_int"] for m in cb)
bl_int    = sum(m["interest"]  for m in bl)
cb_int    = sum(m["interest"]  for m in cb)

ni_bl   = bl_gross
ni_cb   = cb_gross - cb_cost
d_ni    = ni_cb - ni_bl
d_int   = cb_int - bl_int
pnl     = d_ni + d_int

# ── KPI row ──────────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
with k1:
    color = "positive" if pnl >= 0 else "negative"
    st.markdown(f"""<div class="metric-card">
        <div class="metric-label">Net P&L vs. baseline</div>
        <div class="metric-value {color}">{fmt_eur(pnl, sign=True)}</div>
    </div>""", unsafe_allow_html=True)
with k2:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-label">Total cashback paid out</div>
        <div class="metric-value negative">-{fmt_eur(cb_cost)}</div>
    </div>""", unsafe_allow_html=True)
with k3:
    color = "positive" if d_ni >= 0 else "negative"
    st.markdown(f"""<div class="metric-card">
        <div class="metric-label">Δ Net interchange</div>
        <div class="metric-value {color}">{fmt_eur(d_ni, sign=True)}</div>
    </div>""", unsafe_allow_html=True)
with k4:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-label">Δ Interest revenue</div>
        <div class="metric-value positive">{fmt_eur(d_int, sign=True)}</div>
    </div>""", unsafe_allow_html=True)

# ── Tabs ─────────────────────────────────────────────────────────────────────
tab_chart, tab_breakdown = st.tabs(["Chart", "Full breakdown"])

with tab_chart:
    import pandas as pd
    from datetime import date

    dates = [date(2026, 6, 1)]
    for _ in range(MONTHS - 1):
        y, m = dates[-1].year, dates[-1].month
        dates.append(date(y + (m // 12), (m % 12) + 1, 1))

    bl_monthly_ni = [m["gross_int"] for m in bl]
    cb_monthly_ni = [m["gross_int"] - min(
        m["spend"] * mix_prem  * prem_r +
        m["spend"] * mix_boost * boost_r +
        m["spend"] * max(0, 1 - mix_prem - mix_boost) * std_r,
        cap * m["active_cards"]
    ) for m in cb]

    cum_pnl = []
    running = 0
    for i in range(MONTHS):
        running += (cb_monthly_ni[i] - bl_monthly_ni[i]) + (cb[i]["interest"] - bl[i]["interest"])
        cum_pnl.append(running)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=[round(v) for v in cb_monthly_ni],
        name="Net interchange — cashback", line=dict(color="#2563eb", width=2)))
    fig.add_trace(go.Scatter(x=dates, y=[round(v) for v in bl_monthly_ni],
        name="Net interchange — baseline", line=dict(color="#9ca3af", width=1.5, dash="dash")))
    fig.add_trace(go.Scatter(x=dates, y=[round(v) for v in cum_pnl],
        name="Δ P&L cumulative", yaxis="y2",
        line=dict(color="#059669", width=2, dash="dot")))

    fig.update_layout(
        height=360,
        yaxis=dict(title="Monthly net interchange (€)", tickformat=",.0f"),
        yaxis2=dict(title="Cumulative Δ P&L (€)", overlaying="y", side="right",
                    tickformat=",.0f", showgrid=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        margin=dict(l=0, r=0, t=40, b=0),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(size=12)
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="#f0f0f0", gridwidth=1)
    st.plotly_chart(fig, use_container_width=True)

with tab_breakdown:
    c1, c2 = st.columns(2)

    with c1:
        st.markdown('<div class="section-header">Interchange (31 months cumulative)</div>', unsafe_allow_html=True)
        rows = [
            ("Gross interchange — cashback",  fmt_eur(cb_gross),      "neutral"),
            ("Gross interchange — baseline",  fmt_eur(bl_gross),      "neutral"),
            ("Total cashback paid out",       f"-{fmt_eur(cb_cost)}", "negative"),
            None,
            ("Net interchange — cashback",    fmt_eur(ni_cb),         "neutral"),
            ("Net interchange — baseline",    fmt_eur(ni_bl),         "neutral"),
            ("Δ Net interchange",             fmt_eur(d_ni, sign=True), "positive" if d_ni >= 0 else "negative"),
        ]
        for row in rows:
            if row is None:
                st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
            else:
                label, value, color = row
                st.markdown(f"""
                <div style="display:flex;justify-content:space-between;margin-bottom:6px;font-size:13px;">
                    <span style="color:#555">{label}</span>
                    <span class="{color}" style="font-weight:500">{value}</span>
                </div>""", unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="section-header">Interest revenue (31 months cumulative)</div>', unsafe_allow_html=True)
        rows2 = [
            ("Interest revenue — cashback",   fmt_eur(cb_int),        "neutral"),
            ("Interest revenue — baseline",   fmt_eur(bl_int),        "neutral"),
            ("Δ Interest",                    fmt_eur(d_int, sign=True), "positive"),
            None,
            ("Net P&L vs. baseline",          fmt_eur(pnl, sign=True), "positive" if pnl >= 0 else "negative"),
        ]
        for row in rows2:
            if row is None:
                st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
            else:
                label, value, color = row
                weight = "700" if label == "Net P&L vs. baseline" else "500"
                size   = "15px" if label == "Net P&L vs. baseline" else "13px"
                st.markdown(f"""
                <div style="display:flex;justify-content:space-between;margin-bottom:6px;font-size:{size};">
                    <span style="color:#555;font-weight:{weight}">{label}</span>
                    <span class="{color}" style="font-weight:{weight}">{value}</span>
                </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="section-header">Cashback breakdown (first month, Jun 2026)</div>', unsafe_allow_html=True)
    first = cb[0]
    mix_std_pct = max(0, 1 - mix_prem - mix_boost)
    spend_prem  = first["spend"] * mix_prem
    spend_boost = first["spend"] * mix_boost
    spend_std   = first["spend"] * mix_std_pct
    cb_prem     = spend_prem  * prem_r
    cb_boost    = spend_boost * boost_r
    cb_std      = spend_std   * std_r
    uncapped    = cb_prem + cb_boost + cb_std
    capped_val  = min(uncapped, cap * first["active_cards"])

    bk_rows = [
        (f"Premium sellers ({mix_prem*100:.1f}% of spend × {prem_r*100:.1f}%)",   fmt_eur(cb_prem),   "neutral"),
        (f"Boosted categories ({mix_boost*100:.1f}% of spend × {boost_r*100:.1f}%)", fmt_eur(cb_boost), "neutral"),
        (f"Standard ({mix_std_pct*100:.1f}% of spend × {std_r*100:.2f}%)",          fmt_eur(cb_std),    "neutral"),
        None,
        ("Total uncapped cashback",                                                  fmt_eur(uncapped),  "neutral"),
        (f"Cap ceiling (€{cap} × {round(first['active_cards']):,} active cards)",   fmt_eur(cap * first['active_cards']), "neutral"),
        ("Cashback cost (capped)",                                                   f"-{fmt_eur(capped_val)}", "negative"),
    ]
    for row in bk_rows:
        if row is None:
            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        else:
            label, value, color = row
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;margin-bottom:6px;font-size:13px;">
                <span style="color:#555">{label}</span>
                <span class="{color}" style="font-weight:500">{value}</span>
            </div>""", unsafe_allow_html=True)
