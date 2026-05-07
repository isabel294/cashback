import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Cashback Business Case", page_icon="🌿", layout="wide")

# ── Sage & Parchment · Cormorant Garamond + Jost ──────────────────────────────
st.markdown(
    '<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;1,300;1,400&family=Jost:wght@300;400;500&display=swap" rel="stylesheet">',
    unsafe_allow_html=True,
)
st.markdown("""<style>
  /* Global font */
  html, body, [class*="css"], .stApp { font-family: 'Jost', sans-serif !important; }

  /* Sidebar */
  [data-testid="stSidebar"] {
    background: #f0f4eb !important;
    border-right: 0.5px solid #d4dbc8 !important;
  }
  [data-testid="stSidebar"] * { font-family: 'Jost', sans-serif !important; }
  [data-testid="stSidebar"] h2 {
    font-family: 'Cormorant Garamond', serif !important;
    font-weight: 400; font-size: 20px; color: #263020; letter-spacing: .01em;
  }

  /* Sidebar section headers */
  .sec-hdr {
    font-family: 'Jost', sans-serif;
    font-size: 10px; font-weight: 500;
    text-transform: uppercase; letter-spacing: .1em;
    color: #7d9070; margin: 20px 0 6px 0;
    padding-bottom: 5px; border-bottom: 0.5px solid #d4dbc8;
  }

  /* Main background */
  .stApp { background: #f8f9f5 !important; }
  .main .block-container { padding-top: 2rem; }

  /* Page title */
  h1 {
    font-family: 'Cormorant Garamond', serif !important;
    font-weight: 400 !important; font-size: 32px !important;
    color: #263020 !important; letter-spacing: .01em !important;
  }

  /* Metric cards */
  .m-card {
    border-bottom: 2px solid #a8c090;
    padding-bottom: 10px; margin-bottom: 4px;
  }
  .m-label {
    font-family: 'Jost', sans-serif;
    font-size: 10px; font-weight: 500;
    text-transform: uppercase; letter-spacing: .08em;
    color: #7d9070; margin-bottom: 5px;
  }
  .m-value {
    font-family: 'Cormorant Garamond', serif;
    font-size: 28px; font-weight: 400; color: #263020;
    line-height: 1.1;
  }
  .m-pos { font-family:'Jost',sans-serif; font-size:11px; font-weight:300; color:#5a8a6a; margin-top:3px; }
  .m-neg { font-family:'Jost',sans-serif; font-size:11px; font-weight:300; color:#c47060; margin-top:3px; }

  /* Tabs */
  .stTabs [data-baseweb="tab-list"] {
    border-bottom: 0.5px solid #d4dbc8 !important;
    gap: 0 !important; background: transparent !important;
  }
  .stTabs [data-baseweb="tab"] {
    font-family: 'Jost', sans-serif !important;
    font-size: 12px !important; font-weight: 400 !important;
    text-transform: uppercase !important; letter-spacing: .07em !important;
    color: #7d9070 !important;
    background: transparent !important;
    border: none !important; padding: 8px 18px !important;
  }
  .stTabs [aria-selected="true"] {
    color: #263020 !important;
    border-bottom: 2px solid #a8c090 !important;
    font-weight: 500 !important;
  }

  /* Caption / subtitles */
  .stCaption, .caption {
    font-family: 'Jost', sans-serif !important;
    font-size: 12px !important; font-weight: 300 !important;
    color: #7d9070 !important; letter-spacing: .02em !important;
  }

  /* Slider and input accents */
  [data-testid="stSlider"] > div > div > div > div {
    background: #a8c090 !important;
  }
  button[kind="primary"] { background: #689050 !important; border-color: #689050 !important; }
</style>
""", unsafe_allow_html=True)

# ── Colour palette (sage & parchment) ─────────────────────────────────────────
SAGE_DARK   = "#263020"
SAGE_MID    = "#689050"
SAGE_LIGHT  = "#a8c090"
SAGE_PALE   = "#ccddc0"
SAGE_MUTED  = "#7d9070"
PARCHMENT   = "#f8f9f5"
PANEL_BG    = "#f0f4eb"
BORDER      = "#d4dbc8"
POS         = "#5a8a6a"
NEG         = "#c47060"

# Plotly chart defaults
PLOT_BG = PARCHMENT
PAPER_BG = PARCHMENT
FONT_FAMILY = "Jost, sans-serif"
AXIS_COLOR = "#b8c4ac"
GRID_COLOR = "#e4ead8"


def chart_layout(title, height=280, yaxis_title="€"):
    return dict(
        title=dict(text=title, font=dict(family="Cormorant Garamond, serif", size=15,
                                          color=SAGE_DARK), x=0, xanchor="left"),
        height=height,
        plot_bgcolor=PANEL_BG,
        paper_bgcolor=PARCHMENT,
        font=dict(family=FONT_FAMILY, color=SAGE_MUTED, size=11),
        yaxis=dict(title=yaxis_title, gridcolor=GRID_COLOR, linecolor=BORDER,
                   tickfont=dict(size=10, color=SAGE_MUTED), title_font=dict(size=11)),
        xaxis=dict(gridcolor="rgba(0,0,0,0)", linecolor=BORDER,
                   tickfont=dict(size=10, color=SAGE_MUTED)),
        legend=dict(font=dict(size=10, family=FONT_FAMILY, color=SAGE_MUTED),
                    bgcolor="rgba(0,0,0,0)", bordercolor="rgba(0,0,0,0)"),
        margin=dict(t=45, b=20, l=55, r=20),
    )


# ── Data ──────────────────────────────────────────────────────────────────────
MONTHS = pd.date_range("2026-06-01", periods=31, freq="MS")

SIGN_UPS_BUDGET = np.array([
    2357.28553550713,3320.18727820901,3888.34799997604,4120.13224201055,
    3941.11005854217,4198.1807111641,4749.4826748831,7379.82589515132,
    4980.63854702887,4257.71525677368,3244.81172048582,2680.20267693284,
    2573.7513856174,3630.49867277501,4251.81318877844,4082.92276038873,
    3506.26393834622,3729.67244853343,4211.03717666877,7379.82589515132,
    4980.63854702887,4257.71525677368,3244.81172048582,2680.20267693284,
    2573.7513856174,3630.49867277501,4251.81318877844,4082.92276038873,
    3506.26393834622,3729.67244853343,4211.03717666877,
])
PAID_USERS_EOM = np.array([
    19628.2392514931,20043.3005587735,20533.7177719302,21091.3763731082,
    21690.1291755324,22343.7578678667,23082.220261086,24130.9590696625,
    25078.4234287188,25940.221875577,26657.4377913277,27169.3572248991,
    27551.420679845,27919.4404118266,28346.5712796371,28797.1903484514,
    29229.1573289075,29680.941073812,30180.8624821454,31025.1875183094,
    31783.9879455532,32474.9573945397,33045.3940971994,33421.8903152632,
    33678.9031084017,33924.3731918123,34231.4054040231,34564.3277903496,
    34880.9520219677,35219.699873011,35608.8461053605,
])
INITIAL_EOM = 7041.75580590816


# ── Simulation ────────────────────────────────────────────────────────────────
def run_simulation(std_rate, boost_rate, premium_rate, monthly_cap,
                   pct_premium, pct_boosted,
                   acq_uplift, adoption_uplift, tx_uplift, card_uplift,
                   active_card_uplift, balance_uplift,
                   ct_paid_uplift, arpa_uplift,
                   share_sig, share_paid, churn_rate,
                   card_share, act_share, tx_pc, tx_amt, avg_balance, ester_rate,
                   ct_base, arpa_base, sub_churn,
                   ic_r1=0.006650, ic_r2=0.007980, ic_r3=0.009310):

    pct_std    = 1 - pct_premium - pct_boosted
    ester_m    = ester_rate * 0.81 * 0.80 / 12
    monthly_ch = INITIAL_EOM * churn_rate

    cb_card = card_share  * (1 + card_uplift)
    cb_act  = act_share   * (1 + active_card_uplift)
    cb_tx   = tx_pc       * (1 + tx_uplift)
    cb_bal  = avg_balance * (1 + balance_uplift)
    cb_ct   = ct_base     * (1 + ct_paid_uplift)
    cb_arpa = arpa_base   * (1 + arpa_uplift)
    cb_sig  = share_sig   * (1 + adoption_uplift)

    spend_pu_b = card_share * act_share * tx_pc * tx_amt
    spend_pu_c = cb_card    * cb_act    * cb_tx * tx_amt
    base_ic_f = np.array([spend_pu_b*ic_r1]*7  + [spend_pu_b*ic_r2]*13 + [spend_pu_b*ic_r3]*11)
    cash_ic_f = np.array([spend_pu_c*ic_r1]*1  + [spend_pu_c*ic_r2]*7  + [spend_pu_c*ic_r3]*23)

    def _run(cashback):
        eom = INITIAL_EOM; sub_mrr = 0.0; rows = []
        eff_card = cb_card  if cashback else card_share
        eff_act  = cb_act   if cashback else act_share
        eff_tx   = cb_tx    if cashback else tx_pc
        eff_bal  = cb_bal   if cashback else avg_balance
        eff_ct   = cb_ct    if cashback else ct_base
        eff_arpa = cb_arpa  if cashback else arpa_base
        eff_sig  = cb_sig   if cashback else share_sig
        ic_f     = cash_ic_f if cashback else base_ic_f

        for i in range(31):
            actives   = SIGN_UPS_BUDGET[i] * (1 + acq_uplift) if cashback else SIGN_UPS_BUDGET[i]
            new_users = actives * eff_sig + PAID_USERS_EOM[i] * share_paid
            eom       = eom - monthly_ch + new_users
            gross_ic  = eom * ic_f[i]
            act_cards = eom * eff_card * eff_act
            total_sp  = act_cards * eff_tx * tx_amt
            if cashback:
                cb_sp   = total_sp * (pct_std*std_rate + pct_boosted*boost_rate + pct_premium*premium_rate)
                cb_cost = -min(cb_sp, act_cards * monthly_cap)
                net_ic  = gross_ic + cb_cost
            else:
                cb_cost = 0.0; net_ic = gross_ic
            interest = eom * eff_bal * ester_m
            new_conv = actives * eff_ct
            sub_mrr  = sub_mrr*(1-sub_churn) + new_conv*eff_arpa if i > 0 else new_conv*eff_arpa
            rows.append(dict(month=MONTHS[i], verified_eom=eom, active_cards=act_cards,
                             gross_interchange=gross_ic, cashback_cost=cb_cost,
                             net_interchange=net_ic, interest=interest, sub_mrr=sub_mrr))
        return pd.DataFrame(rows)

    return _run(False), _run(True)


def fmt(v):
    if abs(v) >= 1_000_000: return f"€{v/1_000_000:.2f}M"
    if abs(v) >= 1_000:     return f"€{v/1_000:.1f}K"
    return f"€{v:,.0f}"

def mcard(label, value, delta):
    d_cls = "m-pos" if delta >= 0 else "m-neg"
    sign  = "▲" if delta >= 0 else "▼"
    return f"""<div class="m-card">
  <div class="m-label">{label}</div>
  <div class="m-value">{value}</div>
  <div class="{d_cls}">{sign} {fmt(abs(delta))}</div>
</div>"""


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("<h2>Assumptions</h2>", unsafe_allow_html=True)

    st.markdown('<div class="sec-hdr">Cashback rates</div>', unsafe_allow_html=True)
    std_rate     = st.slider("Standard rate",            0.001, 0.010, 0.003, 0.001, format="%.3f")
    boost_rate   = st.slider("Boosted rate",             0.005, 0.050, 0.020, 0.005, format="%.3f")
    premium_rate = st.slider("Premium rate (sellers)",   0.010, 0.080, 0.040, 0.005, format="%.3f")
    monthly_cap  = st.slider("Monthly cap per user (€)", 10, 100, 30, 5)

    st.markdown('<div class="sec-hdr">Spend mix</div>', unsafe_allow_html=True)
    pct_premium = st.slider("% spend – premium sellers",    0.00, 0.10, 0.010, 0.005, format="%.3f")
    pct_boosted = st.slider("% spend – boosted categories", 0.05, 0.20, 0.093, 0.003, format="%.3f")

    st.markdown('<div class="sec-hdr">Banking uplifts</div>', unsafe_allow_html=True)
    acq_uplift         = st.slider("New user acquisition uplift",        0.0, 0.20, 0.02, 0.01, format="%.2f")
    adoption_uplift    = st.slider("Banking adoption uplift (sign-ups)", 0.0, 0.50, 0.20, 0.05, format="%.2f")
    tx_uplift          = st.slider("Transactions / card uplift",         0.0, 1.00, 0.40, 0.05, format="%.2f")
    card_uplift        = st.slider("Card share uplift",                  0.0, 0.20, 0.05, 0.01, format="%.2f")
    active_card_uplift = st.slider("Active card share uplift",           0.0, 0.50, 0.20, 0.05, format="%.2f")
    balance_uplift     = st.slider("Avg. balance uplift",                0.0, 0.20, 0.05, 0.01, format="%.2f")

    st.markdown('<div class="sec-hdr">SaaS uplifts</div>', unsafe_allow_html=True)
    ct_paid_uplift = st.slider("Conversion to paid uplift", 0.0, 0.20, 0.02, 0.01, format="%.2f")
    arpa_uplift    = st.slider("ARPA uplift",               0.0, 0.20, 0.00, 0.01, format="%.2f")

    st.markdown('<div class="sec-hdr">Baseline assumptions</div>', unsafe_allow_html=True)
    share_sig   = st.number_input("Share of adopters – new sign-ups", 0.01, 0.30, 0.100, 0.010, format="%.3f")
    share_paid  = st.number_input("Share of adopters – paid users",   0.005,0.10, 0.025, 0.005, format="%.3f")
    churn_rate  = st.number_input("Monthly banking churn rate",       0.001,0.05, 0.010, 0.001, format="%.3f")
    card_share  = st.number_input("Share of users with card",         0.3,  1.0,  0.70,  0.05,  format="%.2f")
    act_share   = st.number_input("Share of active cards",            0.3,  1.0,  0.60,  0.05,  format="%.2f")
    tx_pc       = st.number_input("Card transactions / card / month", 1.0,  20.0, 8.3,   0.5,   format="%.1f")
    tx_amt      = st.number_input("Avg. transaction amount (€)",      10.0, 150.0,52.0,  5.0)
    avg_balance = st.number_input("Avg. balance – baseline (€)",      500.0,10000.0,2850.0,100.0)
    ester_rate  = st.number_input("ESTER rate",                       0.005,0.05, 0.019, 0.001, format="%.3f")

    st.markdown('<div class="sec-hdr">Subscription conversion & retention</div>', unsafe_allow_html=True)
    ct_base   = st.number_input("Conversion to paid – baseline",     0.10, 0.60, 0.285, 0.005, format="%.3f")
    arpa_base = st.number_input("ARPA – converted sign-ups (€ / mo)",10.0, 60.0, 28.2,  0.5)
    sub_churn = st.number_input("Monthly subscription churn rate",   0.005,0.10, 0.020, 0.005, format="%.3f")


# ── Run model ─────────────────────────────────────────────────────────────────
base, cash = run_simulation(
    std_rate, boost_rate, premium_rate, monthly_cap,
    pct_premium, pct_boosted,
    acq_uplift, adoption_uplift, tx_uplift, card_uplift, active_card_uplift, balance_uplift,
    ct_paid_uplift, arpa_uplift,
    share_sig, share_paid, churn_rate,
    card_share, act_share, tx_pc, tx_amt, avg_balance, ester_rate,
    ct_base, arpa_base, sub_churn,
)

d_ic    = cash["net_interchange"].sum()  - base["net_interchange"].sum()
d_int   = cash["interest"].sum()         - base["interest"].sum()
d_sub   = cash["sub_mrr"].sum()          - base["sub_mrr"].sum()
total_d = d_ic + d_int + d_sub


# ── Page header ───────────────────────────────────────────────────────────────
st.title("Cashback business case")
st.markdown(
    '<p class="caption">Germany · Jun 2026 – Dec 2028 · Baseline vs. cashback scenario</p>',
    unsafe_allow_html=True,
)
st.markdown("<br>", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
with c1: st.markdown(mcard("Total Δ vs. baseline",   fmt(total_d), total_d), unsafe_allow_html=True)
with c2: st.markdown(mcard("Δ Subscription revenue", fmt(d_sub),   d_sub),   unsafe_allow_html=True)
with c3: st.markdown(mcard("Δ Net interchange",       fmt(d_ic),    d_ic),    unsafe_allow_html=True)
with c4: st.markdown(mcard("Δ Interest revenue",      fmt(d_int),   d_int),   unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["Charts", "Unit economics"])

with tab1:
    # Monthly delta bar
    md = (cash["net_interchange"] + cash["interest"] + cash["sub_mrr"]) - \
         (base["net_interchange"] + base["interest"] + base["sub_mrr"])
    fig = go.Figure(go.Bar(
        x=MONTHS, y=md,
        marker_color=[SAGE_MID if v >= 0 else NEG for v in md],
        marker_line_width=0,
    ))
    fig.update_layout(**chart_layout("Monthly revenue delta – cashback vs. baseline", height=300))
    st.plotly_chart(fig, use_container_width=True)

    r1, r2 = st.columns(2)
    with r1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=MONTHS, y=base["verified_eom"], name="Baseline",
                                 line=dict(color=SAGE_PALE, width=1.5, dash="dash")))
        fig.add_trace(go.Scatter(x=MONTHS, y=cash["verified_eom"], name="Cashback",
                                 line=dict(color=SAGE_MID, width=2),
                                 fill="tonexty", fillcolor="rgba(168,192,144,0.15)"))
        fig.update_layout(**chart_layout("Banking users (EOM)", yaxis_title="Users"))
        st.plotly_chart(fig, use_container_width=True)

    with r2:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=MONTHS, y=base["sub_mrr"], name="Baseline",
                                 line=dict(color=SAGE_PALE, width=1.5, dash="dash")))
        fig.add_trace(go.Scatter(x=MONTHS, y=cash["sub_mrr"], name="Cashback",
                                 line=dict(color=SAGE_MID, width=2),
                                 fill="tonexty", fillcolor="rgba(168,192,144,0.15)"))
        fig.update_layout(**chart_layout("Subscription MRR"))
        st.plotly_chart(fig, use_container_width=True)

    r3, r4 = st.columns(2)
    with r3:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=MONTHS, y=base["net_interchange"], name="Baseline",
                                 line=dict(color=SAGE_PALE, width=1.5, dash="dash")))
        fig.add_trace(go.Scatter(x=MONTHS, y=cash["net_interchange"], name="Cashback net",
                                 line=dict(color=SAGE_MID, width=2)))
        fig.add_trace(go.Scatter(x=MONTHS, y=cash["gross_interchange"], name="Cashback gross",
                                 line=dict(color=SAGE_MUTED, width=1.5, dash="dot")))
        fig.update_layout(**chart_layout("Net interchange"))
        st.plotly_chart(fig, use_container_width=True)

    with r4:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=MONTHS, y=base["interest"], name="Baseline",
                                 line=dict(color=SAGE_PALE, width=1.5, dash="dash")))
        fig.add_trace(go.Scatter(x=MONTHS, y=cash["interest"], name="Cashback",
                                 line=dict(color=SAGE_MID, width=2),
                                 fill="tonexty", fillcolor="rgba(168,192,144,0.15)"))
        fig.update_layout(**chart_layout("Interest revenue"))
        st.plotly_chart(fig, use_container_width=True)


with tab2:
    st.markdown(
        '<p class="caption" style="margin-bottom:1rem;">Per banking user (EOM) · each month · baseline = dashed, cashback = solid</p>',
        unsafe_allow_html=True,
    )

    b_ic_pu  = base["gross_interchange"] / base["verified_eom"]
    c_ic_pu  = cash["gross_interchange"] / cash["verified_eom"]
    b_int_pu = base["interest"]          / base["verified_eom"]
    c_int_pu = cash["interest"]          / cash["verified_eom"]
    b_cb_pu  = pd.Series(np.zeros(31))
    c_cb_pu  = cash["cashback_cost"].abs() / cash["verified_eom"]
    b_net_pu = base["net_interchange"]   / base["verified_eom"]
    c_net_pu = cash["net_interchange"]   / cash["verified_eom"]
    b_sub_pu = base["sub_mrr"]           / base["verified_eom"]
    c_sub_pu = cash["sub_mrr"]           / cash["verified_eom"]

    def pu_chart(title, b_s, c_s):
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=MONTHS, y=b_s, name="Baseline",
                                 line=dict(color=SAGE_PALE, width=1.5, dash="dash")))
        fig.add_trace(go.Scatter(x=MONTHS, y=c_s, name="Cashback",
                                 line=dict(color=SAGE_MID, width=2),
                                 fill="tonexty", fillcolor="rgba(168,192,144,0.12)"))
        fig.update_layout(**chart_layout(title, height=260, yaxis_title="€ / user / month"))
        return fig

    u1, u2 = st.columns(2)
    with u1:
        st.plotly_chart(pu_chart("Gross interchange per user",    b_ic_pu,  c_ic_pu),  use_container_width=True)
    with u2:
        st.plotly_chart(pu_chart("Interest per user",             b_int_pu, c_int_pu), use_container_width=True)

    u3, u4 = st.columns(2)
    with u3:
        st.plotly_chart(pu_chart("Cashback cost per user",        b_cb_pu,  c_cb_pu),  use_container_width=True)
    with u4:
        st.plotly_chart(pu_chart("Net interchange per user",      b_net_pu, c_net_pu), use_container_width=True)

    st.plotly_chart(pu_chart("Subscription MRR per user",         b_sub_pu, c_sub_pu), use_container_width=True)
