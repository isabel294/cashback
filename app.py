import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import pandas as _pd

st.set_page_config(page_title="Cashback Business Case", page_icon="💳", layout="wide")

st.markdown("""
<style>
  [data-testid="stSidebar"] { background: #f5f3ff; }
  .metric-card { background:white; border:1px solid #e5e7eb; border-radius:10px; padding:16px 20px; margin-bottom:8px; }
  .metric-label { font-size:11px; color:#6b7280; font-weight:600; text-transform:uppercase; letter-spacing:.06em; }
  .metric-value { font-size:26px; font-weight:700; color:#111827; margin-top:4px; }
  .delta-pos { font-size:13px; color:#059669; font-weight:600; margin-top:2px; }
  .delta-neg { font-size:13px; color:#dc2626; font-weight:600; margin-top:2px; }
  .section-hdr { background:#351c75; color:white; padding:7px 13px; border-radius:6px; font-weight:600; font-size:12px; margin:18px 0 6px 0; }
  h1 { color:#351c75; }
</style>""", unsafe_allow_html=True)

MONTHS = _pd.date_range("2026-06-01", periods=31, freq="MS")

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


def run_simulation(std_rate, boost_rate, premium_rate, monthly_cap,
                   pct_premium, pct_boosted,
                   acq_uplift, adoption_uplift, tx_uplift, card_uplift, active_card_uplift, balance_uplift,
                   ct_paid_uplift, arpa_uplift,
                   share_sig, share_paid, churn_rate,
                   card_share, act_share, tx_pc, tx_amt, avg_balance, ester_rate,
                   ct_base, arpa_base, sub_churn,
                   ic_r1=0.006650, ic_r2=0.007980, ic_r3=0.009310):

    pct_std    = 1 - pct_premium - pct_boosted
    ester_m    = ester_rate * 0.81 * 0.80 / 12
    monthly_ch = INITIAL_EOM * churn_rate

    cb_card  = card_share  * (1 + card_uplift)
    cb_act   = act_share   * (1 + active_card_uplift)
    cb_tx    = tx_pc       * (1 + tx_uplift)
    cb_bal   = avg_balance * (1 + balance_uplift)
    cb_ct    = ct_base     * (1 + ct_paid_uplift)
    cb_arpa  = arpa_base   * (1 + arpa_uplift)
    cb_sig   = share_sig   * (1 + adoption_uplift)

    # IC factor arrays: same underlying MIF rate, different spend-per-user
    # Tier boundaries reflect volume thresholds crossed faster in cashback scenario
    spend_pu_b = card_share * act_share * tx_pc      * tx_amt
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
                cb_sp   = total_sp*(pct_std*std_rate + pct_boosted*boost_rate + pct_premium*premium_rate)
                cb_cost = -min(cb_sp, act_cards * monthly_cap)
                net_ic  = gross_ic + cb_cost
            else:
                cb_cost = 0.0; net_ic = gross_ic
            interest = eom * eff_bal * ester_m
            new_conv = actives * eff_ct
            sub_mrr  = sub_mrr*(1-sub_churn) + new_conv*eff_arpa if i>0 else new_conv*eff_arpa
            rows.append(dict(month=MONTHS[i], verified_eom=eom, active_cards=act_cards,
                             gross_interchange=gross_ic, cashback_cost=cb_cost,
                             net_interchange=net_ic, interest=interest, sub_mrr=sub_mrr))
        return pd.DataFrame(rows)

    return _run(False), _run(True)


def fmt(v):
    if abs(v) >= 1_000_000: return f"€{v/1_000_000:.2f}M"
    if abs(v) >= 1_000:     return f"€{v/1_000:.1f}K"
    return f"€{v:,.0f}"

def dhtml(v):
    cls = "delta-pos" if v >= 0 else "delta-neg"
    sign = "▲" if v >= 0 else "▼"
    return f'<div class="{cls}">{sign} {fmt(abs(v))}</div>'

def mcard(label, value, delta=None):
    d = dhtml(delta) if delta is not None else ""
    return f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{value}</div>{d}</div>'


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Assumptions")

    st.markdown('<div class="section-hdr">💳 Cashback rates</div>', unsafe_allow_html=True)
    std_rate     = st.slider("Standard rate",           0.001,0.010,0.003,0.001,format="%.3f")
    boost_rate   = st.slider("Boosted rate",            0.005,0.050,0.020,0.005,format="%.3f")
    premium_rate = st.slider("Premium rate (sellers)",  0.010,0.080,0.040,0.005,format="%.3f")
    monthly_cap  = st.slider("Monthly cap per user (€)",10,100,30,5)

    st.markdown('<div class="section-hdr">🛍️ Spend mix</div>', unsafe_allow_html=True)
    pct_premium  = st.slider("% spend – premium sellers",      0.00,0.10,0.010,0.005,format="%.3f")
    pct_boosted  = st.slider("% spend – boosted categories",   0.05,0.20,0.093,0.003,format="%.3f")

    st.markdown('<div class="section-hdr">📈 Banking uplifts</div>', unsafe_allow_html=True)
    acq_uplift         = st.slider("New user acquisition uplift",       0.0,0.20,0.02,0.01,format="%.2f")
    adoption_uplift    = st.slider("Banking adoption uplift (sign-ups)",0.0,0.50,0.20,0.05,format="%.2f")
    tx_uplift          = st.slider("Transactions/card uplift",          0.0,1.00,0.40,0.05,format="%.2f")
    card_uplift        = st.slider("Card share uplift",                 0.0,0.20,0.05,0.01,format="%.2f")
    active_card_uplift = st.slider("Active card share uplift",          0.0,0.50,0.20,0.05,format="%.2f")
    balance_uplift     = st.slider("Avg. balance uplift",               0.0,0.20,0.05,0.01,format="%.2f")

    st.markdown('<div class="section-hdr">🔄 SaaS uplifts</div>', unsafe_allow_html=True)
    ct_paid_uplift = st.slider("Conversion to paid uplift", 0.0,0.20,0.02,0.01,format="%.2f")
    arpa_uplift    = st.slider("ARPA uplift",               0.0,0.20,0.00,0.01,format="%.2f")

    st.markdown('<div class="section-hdr">🏦 Baseline assumptions</div>', unsafe_allow_html=True)
    share_sig   = st.number_input("Share of adopters – new sign-ups",0.01,0.30,0.100,0.010,format="%.3f")
    share_paid  = st.number_input("Share of adopters – paid users",  0.005,0.10,0.025,0.005,format="%.3f")
    churn_rate  = st.number_input("Monthly banking churn rate",      0.001,0.05,0.010,0.001,format="%.3f")
    card_share  = st.number_input("Share of users with card",        0.3,1.0,0.70,0.05,format="%.2f")
    act_share   = st.number_input("Share of active cards",           0.3,1.0,0.60,0.05,format="%.2f")
    tx_pc       = st.number_input("Card transactions/card/month",    1.0,20.0,8.3,0.5,format="%.1f")
    tx_amt      = st.number_input("Avg. transaction amount (€)",     10.0,150.0,52.0,5.0)
    avg_balance = st.number_input("Avg. balance – baseline (€)",     500.0,10000.0,2850.0,100.0)
    ester_rate  = st.number_input("ESTER rate",                      0.005,0.05,0.019,0.001,format="%.3f")

    st.markdown('<div class="section-hdr">📊 Subscription conversion & retention</div>', unsafe_allow_html=True)
    ct_base   = st.number_input("Conversion to paid – baseline",    0.10,0.60,0.285,0.005,format="%.3f")
    arpa_base = st.number_input("ARPA – converted sign-ups (€/mo)", 10.0,60.0,28.2,0.5)
    sub_churn = st.number_input("Monthly subscription churn rate",  0.005,0.10,0.020,0.005,format="%.3f")


# ── Run ───────────────────────────────────────────────────────────────────────
base, cash = run_simulation(
    std_rate,boost_rate,premium_rate,monthly_cap,
    pct_premium,pct_boosted,
    acq_uplift,adoption_uplift,tx_uplift,card_uplift,active_card_uplift,balance_uplift,
    ct_paid_uplift,arpa_uplift,
    share_sig,share_paid,churn_rate,
    card_share,act_share,tx_pc,tx_amt,avg_balance,ester_rate,
    ct_base,arpa_base,sub_churn,
)

cum_net_ic_b  = base["net_interchange"].sum()
cum_net_ic_c  = cash["net_interchange"].sum()
cum_gross_ic_c= cash["gross_interchange"].sum()
cum_int_b     = base["interest"].sum()
cum_int_c     = cash["interest"].sum()
cum_sub_b     = base["sub_mrr"].sum()
cum_sub_c     = cash["sub_mrr"].sum()
cum_cb        = cash["cashback_cost"].sum()
d_ic  = cum_net_ic_c - cum_net_ic_b
d_int = cum_int_c    - cum_int_b
d_sub = cum_sub_c    - cum_sub_b
total_d = d_ic + d_int + d_sub

DEC26 = 6
b26 = base.iloc[DEC26]; c26 = cash.iloc[DEC26]


# ── Page ──────────────────────────────────────────────────────────────────────
st.title("💳 Cashback Business Case – Germany")
st.caption("Jun 2026 – Dec 2028 · Baseline vs. Cashback scenario")

c1,c2,c3,c4 = st.columns(4)
with c1: st.markdown(mcard("Total Δ vs. Baseline",    fmt(total_d), total_d),  unsafe_allow_html=True)
with c2: st.markdown(mcard("Δ Subscription revenue",  fmt(d_sub),   d_sub),    unsafe_allow_html=True)
with c3: st.markdown(mcard("Δ Net interchange",        fmt(d_ic),    d_ic),     unsafe_allow_html=True)
with c4: st.markdown(mcard("Δ Interest revenue",       fmt(d_int),   d_int),    unsafe_allow_html=True)

PURPLE="351c75"; LAV="a78bfa"; RED="ef4444"
P="#"+PURPLE; L="#"+LAV; R="#"+RED

tab1,tab2,tab3 = st.tabs(["📊 Charts","📋 Results table","🔍 Per-user view (Dec 2026)"])

with tab1:
    md = (cash["net_interchange"]+cash["interest"]+cash["sub_mrr"]) - \
         (base["net_interchange"]+base["interest"]+base["sub_mrr"])
    fig = go.Figure(go.Bar(x=MONTHS,y=md,marker_color=[P if v>=0 else R for v in md]))
    fig.update_layout(title="Monthly revenue delta – Cashback vs. Baseline (€)",
                      height=300,plot_bgcolor="white",paper_bgcolor="white",
                      yaxis_title="€",margin=dict(t=40,b=20,l=60,r=20))
    st.plotly_chart(fig,use_container_width=True)

    r1,r2=st.columns(2)
    with r1:
        fig=go.Figure()
        fig.add_trace(go.Scatter(x=MONTHS,y=base["verified_eom"],name="Baseline",line=dict(color=L,dash="dash")))
        fig.add_trace(go.Scatter(x=MONTHS,y=cash["verified_eom"],name="Cashback",line=dict(color=P),fill="tonexty",fillcolor="rgba(167,139,250,0.12)"))
        fig.update_layout(title="Banking users (EOM)",height=270,plot_bgcolor="white",paper_bgcolor="white",yaxis_title="Users",margin=dict(t=35,b=20,l=60,r=20))
        st.plotly_chart(fig,use_container_width=True)
    with r2:
        fig=go.Figure()
        fig.add_trace(go.Scatter(x=MONTHS,y=base["sub_mrr"],name="Baseline",line=dict(color=L,dash="dash")))
        fig.add_trace(go.Scatter(x=MONTHS,y=cash["sub_mrr"],name="Cashback",line=dict(color=P),fill="tonexty",fillcolor="rgba(167,139,250,0.12)"))
        fig.update_layout(title="Subscription MRR (€)",height=270,plot_bgcolor="white",paper_bgcolor="white",yaxis_title="€",margin=dict(t=35,b=20,l=60,r=20))
        st.plotly_chart(fig,use_container_width=True)

    r3,r4=st.columns(2)
    with r3:
        fig=go.Figure()
        fig.add_trace(go.Scatter(x=MONTHS,y=base["net_interchange"],name="Baseline",line=dict(color=L,dash="dash")))
        fig.add_trace(go.Scatter(x=MONTHS,y=cash["net_interchange"],name="Cashback net",line=dict(color=P)))
        fig.add_trace(go.Scatter(x=MONTHS,y=cash["gross_interchange"],name="Cashback gross",line=dict(color=P,dash="dot")))
        fig.update_layout(title="Net interchange (€/month)",height=270,plot_bgcolor="white",paper_bgcolor="white",yaxis_title="€",margin=dict(t=35,b=20,l=60,r=20))
        st.plotly_chart(fig,use_container_width=True)
    with r4:
        fig=go.Figure()
        fig.add_trace(go.Scatter(x=MONTHS,y=base["interest"],name="Baseline",line=dict(color=L,dash="dash")))
        fig.add_trace(go.Scatter(x=MONTHS,y=cash["interest"],name="Cashback",line=dict(color=P),fill="tonexty",fillcolor="rgba(167,139,250,0.12)"))
        fig.update_layout(title="Interest revenue (€/month)",height=270,plot_bgcolor="white",paper_bgcolor="white",yaxis_title="€",margin=dict(t=35,b=20,l=60,r=20))
        st.plotly_chart(fig,use_container_width=True)

with tab2:
    st.markdown("#### Cumulative totals – Jun 2026 to Dec 2028")
    rows_t=[
        ("Gross interchange – Cashback","",fmt(cum_gross_ic_c),""),
        ("Cashback cost","",fmt(cum_cb),""),
        ("Net interchange – Baseline",fmt(cum_net_ic_b),"",""),
        ("Net interchange – Cashback","",fmt(cum_net_ic_c),fmt(d_ic)),
        ("Interest revenue – Baseline",fmt(cum_int_b),"",""),
        ("Interest revenue – Cashback","",fmt(cum_int_c),fmt(d_int)),
        ("Subscription MRR – Baseline",fmt(cum_sub_b),"",""),
        ("Subscription MRR – Cashback","",fmt(cum_sub_c),fmt(d_sub)),
        ("─────────────────────","","",""),
        ("Δ Net interchange","","",fmt(d_ic)),
        ("Δ Interest revenue","","",fmt(d_int)),
        ("Δ Subscription revenue","","",fmt(d_sub)),
        ("Total Δ vs. Baseline","","",fmt(total_d)),
    ]
    st.dataframe(pd.DataFrame(rows_t,columns=["Metric","Baseline","Cashback","Delta"]),use_container_width=True,hide_index=True)

    st.markdown("#### Monthly detail")
    det=pd.DataFrame({
        "Month":[m.strftime("%b %Y") for m in MONTHS],
        "Banking users – Base":base["verified_eom"].round(0).astype(int),
        "Banking users – CB":cash["verified_eom"].round(0).astype(int),
        "Gross IC – CB (€)":cash["gross_interchange"].round(0),
        "Cashback cost (€)":cash["cashback_cost"].round(0),
        "Net IC – Base (€)":base["net_interchange"].round(0),
        "Net IC – CB (€)":cash["net_interchange"].round(0),
        "Interest – Base (€)":base["interest"].round(0),
        "Interest – CB (€)":cash["interest"].round(0),
        "Sub MRR – Base (€)":base["sub_mrr"].round(0),
        "Sub MRR – CB (€)":cash["sub_mrr"].round(0),
    })
    st.dataframe(det,use_container_width=True,hide_index=True)

with tab3:
    st.markdown("#### Per Banking user – December 2026")
    st.caption("Point-in-time snapshot for Dec 2026 (month 7 of the model).")

    b_u=b26["verified_eom"]; c_u=c26["verified_eom"]
    b_ic_pu  = b26["gross_interchange"] / b_u
    c_ic_pu  = c26["gross_interchange"] / c_u
    b_int_pu = b26["interest"] / b_u
    c_int_pu = c26["interest"] / c_u
    b_sub_pu = b26["sub_mrr"] / PAID_USERS_EOM[DEC26]
    c_sub_pu = c26["sub_mrr"] / PAID_USERS_EOM[DEC26]
    b_cb_pu  = 0.0
    c_cb_pu  = abs(c26["cashback_cost"]) / c26["active_cards"] if c26["active_cards"]>0 else 0
    b_net = b_ic_pu+b_int_pu+b_sub_pu
    c_net = c_ic_pu+c_int_pu+c_sub_pu-c_cb_pu

    pu_rows=[
        ("Avg. Banking users (EOM)",         f"{b_u:,.0f}",   f"{c_u:,.0f}",   f"{c_u-b_u:+,.0f}"),
        ("Gross interchange/user (€/mo)",    f"{b_ic_pu:.4f}",f"{c_ic_pu:.4f}",f"{c_ic_pu-b_ic_pu:+.4f}"),
        ("Interest revenue/user (€/mo)",     f"{b_int_pu:.4f}",f"{c_int_pu:.4f}",f"{c_int_pu-b_int_pu:+.4f}"),
        ("Subscription MRR/user (€/mo)",     f"{b_sub_pu:.4f}",f"{c_sub_pu:.4f}",f"{c_sub_pu-b_sub_pu:+.4f}"),
        ("Cashback cost/active card (€/mo)", "–",             f"{c_cb_pu:.4f}",f"{c_cb_pu:+.4f}"),
        ("Net revenue/user (€/mo)",           f"{b_net:.4f}",  f"{c_net:.4f}",  f"{c_net-b_net:+.4f}"),
    ]
    st.dataframe(pd.DataFrame(pu_rows,columns=["Metric","Baseline","Cashback","Delta"]),use_container_width=True,hide_index=True)

    cats=["Gross IC","Interest","Sub MRR","Cashback cost","Net/user"]
    fig=go.Figure(data=[
        go.Bar(name="Baseline",x=cats,y=[b_ic_pu,b_int_pu,b_sub_pu,0,b_net],marker_color=L),
        go.Bar(name="Cashback",x=cats,y=[c_ic_pu,c_int_pu,c_sub_pu,-c_cb_pu,c_net],marker_color=P),
    ])
    fig.update_layout(barmode="group",title="Revenue per user – Dec 2026 (€/month)",
                      height=360,plot_bgcolor="white",paper_bgcolor="white",
                      yaxis_title="€/user/month",margin=dict(t=40,b=20,l=60,r=20))
    st.plotly_chart(fig,use_container_width=True)
