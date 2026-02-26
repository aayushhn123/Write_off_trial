"""
Write-Off Portfolio Monitor — Streamlit Dashboard
Run with: streamlit run writeoff_dashboard.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
import warnings
warnings.filterwarnings("ignore")

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Write-Off Portfolio Monitor",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* Main background */
.stApp {
    background: #0F1117;
    color: #E8ECF0;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #161B27 !important;
    border-right: 1px solid #2A3140;
}
[data-testid="stSidebar"] * {
    color: #C8D0DC !important;
}

/* Header */
.dashboard-header {
    background: linear-gradient(135deg, #1A2332 0%, #0F1117 100%);
    border: 1px solid #2A3140;
    border-radius: 12px;
    padding: 24px 32px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.dashboard-title {
    font-size: 26px;
    font-weight: 700;
    color: #E8ECF0;
    letter-spacing: -0.5px;
    margin: 0;
}
.dashboard-subtitle {
    font-size: 13px;
    color: #6B7894;
    margin: 4px 0 0 0;
    font-family: 'DM Mono', monospace;
}

/* Metric cards */
.metric-row {
    display: flex;
    gap: 16px;
    margin-bottom: 24px;
}
.metric-card {
    flex: 1;
    background: #161B27;
    border: 1px solid #2A3140;
    border-radius: 10px;
    padding: 18px 22px;
}
.metric-label {
    font-size: 11px;
    font-weight: 600;
    color: #6B7894;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 6px;
}
.metric-value {
    font-size: 26px;
    font-weight: 700;
    color: #E8ECF0;
    font-family: 'DM Mono', monospace;
}
.metric-delta {
    font-size: 12px;
    color: #4CAF8A;
    margin-top: 4px;
}

/* Filter pills */
.stRadio > div {
    gap: 8px;
}
.stRadio > div > label {
    background: #1E2535 !important;
    border: 1px solid #2A3140 !important;
    border-radius: 8px !important;
    padding: 8px 18px !important;
    cursor: pointer !important;
    transition: all 0.2s !important;
    color: #8B95A8 !important;
    font-size: 13px !important;
    font-weight: 500 !important;
}
.stRadio > div > label:hover {
    border-color: #4A7CFF !important;
    color: #E8ECF0 !important;
}

/* Button */
.stButton > button {
    background: #4A7CFF !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 10px 24px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    transition: all 0.2s !important;
    width: 100% !important;
}
.stButton > button:hover {
    background: #3A6CEE !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 20px rgba(74, 124, 255, 0.3) !important;
}

/* File uploader */
[data-testid="stFileUploader"] {
    background: #161B27 !important;
    border: 2px dashed #2A3140 !important;
    border-radius: 12px !important;
    padding: 20px !important;
}

/* Selectbox */
.stSelectbox > div > div {
    background: #1E2535 !important;
    border: 1px solid #2A3140 !important;
    border-radius: 8px !important;
    color: #E8ECF0 !important;
}

/* Divider */
hr {
    border-color: #2A3140 !important;
    margin: 20px 0 !important;
}

/* Chart container */
.chart-container {
    background: #161B27;
    border: 1px solid #2A3140;
    border-radius: 12px;
    padding: 8px;
}

/* Section title */
.section-title {
    font-size: 13px;
    font-weight: 600;
    color: #6B7894;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 12px;
}

/* Toggle button row */
.toggle-group {
    display: flex;
    gap: 8px;
    margin-bottom: 16px;
}

/* Info tag */
.info-tag {
    display: inline-block;
    background: #1A2845;
    border: 1px solid #2A4A8A;
    color: #7AA5F0;
    border-radius: 6px;
    padding: 3px 10px;
    font-size: 11px;
    font-weight: 600;
    font-family: 'DM Mono', monospace;
}

/* Upload area prompt */
.upload-prompt {
    text-align: center;
    padding: 60px 40px;
    color: #6B7894;
}
.upload-prompt h2 {
    color: #C8D0DC;
    font-size: 22px;
    margin-bottom: 8px;
}
</style>
""", unsafe_allow_html=True)

# ── Column mapping ─────────────────────────────────────────────────────────────
DATE_COLUMN      = "mis_date"
ID_COLUMN        = "cm11"
BALANCE_COLUMN   = "cycle_opening_balance(current_balance)"
RECOVERY_COLUMN  = "last_payment_amount"
CHARGE_OFF_COL   = "charge_off_month"
STATE_COLUMN     = "state"
CIBIL_COLUMN     = "cibil_score"

# ── Colour palettes ────────────────────────────────────────────────────────────
POS_COLORS     = {'<1L':'#4A7CFF','1L-5L':'#F5C842','5L-10L':'#E8884F','10L+':'#EF5350'}
VINTAGE_COLORS = {
    'V1':'#4A7CFF','V2':'#7B61FF','V3':'#F5C842',
    'V4':'#E8884F','V5':'#EF5350','V6':'#4CAF8A',
    'V7':'#26C6DA','Unknown':'#455468'
}
STATE_COLORS = {
    'AP':'#4A7CFF','DL':'#7B61FF','GJ':'#F5C842','HR':'#EF5350',
    'KA':'#E8884F','MH':'#4CAF8A','RJ':'#26C6DA','TN':'#FF7043',
    'TG':'#AB47BC','UP':'#EC407A','Others':'#455468'
}
CIBIL_COLORS = {'<500':'#EF5350','500-700':'#F5C842','700+':'#4CAF8A','Unknown':'#455468'}
LINE_COLOR   = '#F5C842'
BG_COLOR     = '#161B27'
GRID_COLOR   = '#2A3140'
TEXT_COLOR   = '#C8D0DC'

# ── Preprocessing ──────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def preprocess(df_raw: pd.DataFrame) -> pd.DataFrame:
    df = df_raw.copy()

    # Force numeric
    for col in [BALANCE_COLUMN, RECOVERY_COLUMN, CIBIL_COLUMN]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Parse dates
    for col in [DATE_COLUMN, CHARGE_OFF_COL]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], dayfirst=True, errors='coerce')

    df = df.dropna(subset=[DATE_COLUMN])
    df['file_month'] = df[DATE_COLUMN].dt.to_period('M')

    # Clip outliers
    df[BALANCE_COLUMN]  = pd.to_numeric(df[BALANCE_COLUMN],  errors='coerce').fillna(0).clip(lower=0)
    df[RECOVERY_COLUMN] = pd.to_numeric(df[RECOVERY_COLUMN], errors='coerce').fillna(0).clip(lower=0)

    # CIBIL: out-of-range → NaN
    mask_bad = ((df[CIBIL_COLUMN] < 300) | (df[CIBIL_COLUMN] > 900)) & df[CIBIL_COLUMN].notna()
    df.loc[mask_bad, CIBIL_COLUMN] = np.nan

    # Vintage (V1–V7, each 30 days, V7 = 181d+)
    df['age_days'] = (df[DATE_COLUMN] - df[CHARGE_OFF_COL]).dt.days
    def assign_vintage(d):
        if pd.isna(d) or d < 0:
            return 'Unknown'
        return f"V{min(int(d // 30) + 1, 7)}"
    df['vintage'] = df['age_days'].apply(assign_vintage)
    v_order = [f'V{i}' for i in range(1, 8)] + ['Unknown']
    df['vintage'] = pd.Categorical(df['vintage'], categories=v_order, ordered=True)

    # POS bucket
    pos_labels = ['<1L', '1L-5L', '5L-10L', '10L+']
    df['pos_bin'] = pd.cut(
        df[BALANCE_COLUMN],
        bins=[0, 100_000, 500_000, 1_000_000, np.inf],
        labels=pos_labels, right=True, include_lowest=True
    )
    df['pos_bin'] = pd.Categorical(df['pos_bin'], categories=pos_labels, ordered=True)

    # CIBIL bucket
    cibil_labels = ['<500', '500-700', '700+', 'Unknown']
    df['cibil_bin'] = pd.Series('Unknown', index=df.index, dtype=object)
    mask_v = df[CIBIL_COLUMN].notna()
    if mask_v.sum() > 0:
        cut = pd.cut(
            df.loc[mask_v, CIBIL_COLUMN].astype(float),
            bins=[300, 500, 700, 901],
            labels=['<500', '500-700', '700+'],
            right=False, include_lowest=True
        )
        df.loc[mask_v, 'cibil_bin'] = cut.astype(str).replace('nan', 'Unknown')
    df['cibil_bin'] = pd.Categorical(df['cibil_bin'], categories=cibil_labels, ordered=True)

    # State
    STATE_MAP = {
        'ANDHRA PRADESH':'AP','DELHI':'DL','GUJARAT':'GJ','HARYANA':'HR',
        'KARNATAKA':'KA','MAHARASHTRA':'MH','RAJASTHAN':'RJ','TAMIL NADU':'TN',
        'TELANGANA':'TG','UTTAR PRADESH':'UP'
    }
    df['state_code'] = df[STATE_COLUMN].astype(str).str.strip().str.upper().map(STATE_MAP).fillna('Others')
    s_order = sorted(STATE_MAP.values()) + ['Others']
    df['state_code'] = pd.Categorical(df['state_code'], categories=s_order, ordered=True)

    # Millions
    df['pos_mio']      = df[BALANCE_COLUMN]  / 1_000_000
    df['recovery_mio'] = df[RECOVERY_COLUMN] / 1_000_000

    return df


# ── Aggregation ────────────────────────────────────────────────────────────────
def aggregate(df: pd.DataFrame, segment_col, mode='value'):
    grp = ['file_month'] + ([segment_col] if segment_col else [])

    if mode == 'value':
        bal = df.groupby(grp, observed=False).agg(total_balance=('pos_mio','sum')).reset_index()
        rec = df.groupby(grp, observed=False).agg(total_recovery=('recovery_mio','sum')).reset_index()
    else:
        bal = df.groupby(grp, observed=False).agg(total_balance=(ID_COLUMN,'nunique')).reset_index()
        rec = df[df[RECOVERY_COLUMN] > 0].groupby(grp, observed=False).agg(total_recovery=(ID_COLUMN,'nunique')).reset_index()

    totals = pd.merge(bal, rec, on=grp, how='left')
    totals['total_recovery'] = totals['total_recovery'].fillna(0)

    all_months = pd.period_range(df['file_month'].min(), df['file_month'].max(), freq='M')
    if segment_col:
        segs = totals[segment_col].cat.categories if hasattr(totals[segment_col], 'cat') else totals[segment_col].unique()
        idx = pd.MultiIndex.from_product([all_months, segs], names=['file_month', segment_col])
        totals = totals.set_index(['file_month', segment_col]).reindex(idx, fill_value=0).reset_index()
        totals = totals.rename(columns={segment_col: 'subsegment'})
    else:
        totals = totals.set_index('file_month').reindex(all_months, fill_value=0).reset_index()
        totals['subsegment'] = 'all'

    totals['recovery_pct'] = np.where(
        totals['total_balance'] > 0,
        totals['total_recovery'] / totals['total_balance'] * 100, 0
    )

    # ATS
    acct = df.groupby('file_month', observed=False)[ID_COLUMN].nunique().reset_index(name='n_acct')
    totals = totals.merge(acct, on='file_month', how='left')
    totals['ats'] = np.where(totals['n_acct'] > 0, totals['total_balance'] / totals['n_acct'], 0)
    totals['month_label'] = totals['file_month'].dt.strftime('%b %Y')
    totals = totals.sort_values('file_month').reset_index(drop=True)
    return totals


def get_segment_info(tab):
    if tab == 'POS':          return 'pos_bin',    ['<1L','1L-5L','5L-10L','10L+'],            POS_COLORS
    elif tab == 'Vintage':    return 'vintage',    [f'V{i}' for i in range(1,8)]+['Unknown'],  VINTAGE_COLORS
    elif tab == 'States':     return 'state_code', sorted(STATE_COLORS.keys()-{'Others'})+['Others'], STATE_COLORS
    elif tab == 'CIBIL':      return 'cibil_bin',  ['<500','500-700','700+','Unknown'],         CIBIL_COLORS
    return None, [], {}


# ── Chart ──────────────────────────────────────────────────────────────────────
def make_chart(df, segment_col, seg_order, color_map, mode, sub_filter):
    totals     = aggregate(df, segment_col, mode)
    month_labs = sorted(totals['file_month'].unique())
    x_labels   = [m.strftime('%b %Y') for m in month_labs]
    n          = len(x_labels)
    x          = np.arange(n)
    unit       = 'INR Mio' if mode == 'value' else '# Accounts'

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 6))
    fig.patch.set_facecolor(BG_COLOR)

    for ax in [ax1, ax2]:
        ax.set_facecolor(BG_COLOR)
        ax.tick_params(colors=TEXT_COLOR, labelsize=9)
        ax.spines[['top','right','left','bottom']].set_color(GRID_COLOR)
        ax.yaxis.label.set_color(TEXT_COLOR)
        ax.xaxis.label.set_color(TEXT_COLOR)
        ax.grid(axis='y', color=GRID_COLOR, linestyle='--', linewidth=0.6, alpha=0.8)
        ax.set_xticks(x)
        ax.set_xticklabels(x_labels, rotation=45, ha='right', fontsize=8.5, color=TEXT_COLOR)

    def get_series(ax_totals, col, seg):
        if seg and seg != 'All':
            d = ax_totals[ax_totals['subsegment'].astype(str) == str(seg)]
            d = d.set_index('month_label').reindex(x_labels, fill_value=0)
            return d[col].values
        else:
            return ax_totals.groupby('month_label')[col].sum().reindex(x_labels, fill_value=0).values

    # ── LEFT: POS ──────────────────────────────────────────────────────────────
    ax1.set_title('POS Balances & Contribution', color='#E8ECF0',
                  fontsize=13, fontweight='600', loc='left', pad=14)

    if segment_col and sub_filter == 'All':
        bottom = np.zeros(n)
        for seg in seg_order:
            d = totals[totals['subsegment'].astype(str) == str(seg)]
            d = d.set_index('month_label').reindex(x_labels, fill_value=0)
            vals = d['total_balance'].values
            ax1.bar(x, vals, bottom=bottom, color=color_map.get(str(seg),'#455468'),
                    label=str(seg), width=0.62, zorder=3)
            bottom += vals
    else:
        vals = get_series(totals, 'total_balance', sub_filter)
        col  = color_map.get(str(sub_filter), '#4A7CFF')
        ax1.bar(x, vals, color=col, width=0.62, zorder=3, label=str(sub_filter))

    # ATS line
    ax1r = ax1.twinx()
    ats_vals = totals.groupby('month_label')['ats'].mean().reindex(x_labels, fill_value=0).values
    ax1r.plot(x, ats_vals, color=LINE_COLOR, linewidth=2, marker='o',
              markersize=4, zorder=5, label='ATS Value')
    ax1r.set_ylabel('ATS Value', fontsize=9, color=LINE_COLOR)
    ax1r.tick_params(axis='y', labelcolor=LINE_COLOR, labelsize=8)
    ax1r.spines[['top','right','left','bottom']].set_color(GRID_COLOR)
    ax1r.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f'{v:,.2f}'))

    ax1.set_ylabel(unit, fontsize=9)
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f'{v:,.1f}'))

    handles_b = [mpatches.Patch(color=color_map.get(str(s),'#455468'), label=str(s)) for s in seg_order]
    handles_l = [plt.Line2D([0],[0], color=LINE_COLOR, linewidth=2, marker='o', markersize=4, label='ATS Value')]
    ax1.legend(handles=handles_b + handles_l, fontsize=7.5, ncol=min(len(seg_order)+1,5),
               loc='upper left', facecolor='#1E2535', edgecolor=GRID_COLOR,
               labelcolor=TEXT_COLOR, framealpha=0.9)

    # ── RIGHT: Recovery ────────────────────────────────────────────────────────
    ax2.set_title('Recovery (in INR Mio)', color='#E8ECF0',
                  fontsize=13, fontweight='600', loc='left', pad=14)

    if segment_col and sub_filter == 'All':
        bottom = np.zeros(n)
        for seg in seg_order:
            d = totals[totals['subsegment'].astype(str) == str(seg)]
            d = d.set_index('month_label').reindex(x_labels, fill_value=0)
            vals = d['total_recovery'].values
            ax2.bar(x, vals, bottom=bottom, color=color_map.get(str(seg),'#455468'),
                    label=str(seg), width=0.62, zorder=3)
            bottom += vals
    else:
        vals = get_series(totals, 'total_recovery', sub_filter)
        col  = color_map.get(str(sub_filter), '#4A7CFF')
        ax2.bar(x, vals, color=col, width=0.62, zorder=3)

    # RoR % line
    ax2r = ax2.twinx()
    ror_vals = []
    for ml in x_labels:
        g = totals[totals['month_label'] == ml]
        tb = g['total_balance'].sum()
        tr = g['total_recovery'].sum()
        ror_vals.append(tr / tb * 100 if tb > 0 else 0)
    ax2r.plot(x, ror_vals, color=LINE_COLOR, linewidth=2, marker='o',
              markersize=4, zorder=5, label='RoR %')
    ax2r.set_ylabel('Recovery Rate (%)', fontsize=9, color=LINE_COLOR)
    ax2r.tick_params(axis='y', labelcolor=LINE_COLOR, labelsize=8)
    ax2r.spines[['top','right','left','bottom']].set_color(GRID_COLOR)
    ax2r.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f'{v:.2f}%'))

    ax2.set_ylabel(unit, fontsize=9)
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f'{v:,.2f}'))

    handles_r = [mpatches.Patch(color=color_map.get(str(s),'#455468'), label=str(s)) for s in seg_order]
    handles_rl = [plt.Line2D([0],[0], color=LINE_COLOR, linewidth=2, marker='o', markersize=4, label='RoR %')]
    ax2.legend(handles=handles_r + handles_rl, fontsize=7.5, ncol=min(len(seg_order)+1,5),
               loc='upper left', facecolor='#1E2535', edgecolor=GRID_COLOR,
               labelcolor=TEXT_COLOR, framealpha=0.9)

    plt.tight_layout(rect=[0, 0, 1, 0.97])
    return fig


# ── Summary table ──────────────────────────────────────────────────────────────
def summary_table(df, segment_col, seg_label):
    totals = aggregate(df, segment_col, mode='value')
    latest = totals[totals['file_month'] == totals['file_month'].max()].copy()
    latest = latest[['subsegment','total_balance','total_recovery','recovery_pct']].copy()
    latest.columns = [seg_label, 'POS (Mio)', 'Recovery (Mio)', 'RoR (%)']
    latest['POS (Mio)']      = latest['POS (Mio)'].round(2)
    latest['Recovery (Mio)'] = latest['Recovery (Mio)'].round(2)
    latest['RoR (%)']        = latest['RoR (%)'].round(2)
    return latest.reset_index(drop=True)


# ══════════════════════════════════════════════════════════════════════════════
# MAIN APP
# ══════════════════════════════════════════════════════════════════════════════

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="dashboard-header">
    <div>
        <p class="dashboard-title">📊 Write-Off Portfolio Monitor</p>
        <p class="dashboard-subtitle">CREDIT RECOVERY ANALYTICS DASHBOARD · ALL BALANCES IN INR MILLIONS</p>
    </div>
    <span class="info-tag">WRITE OFF</span>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<p class="section-title">📁 Data Source</p>', unsafe_allow_html=True)
    uploaded = st.file_uploader("Upload your CSV file", type=["csv"],
                                 help="Upload the portfolio CSV with charge-off data")

    st.markdown("---")
    st.markdown('<p class="section-title">🗂 Column Mapping</p>', unsafe_allow_html=True)
    st.caption("Update these if your column names differ:")
    DATE_COLUMN      = st.text_input("MIS Date column",      value="mis_date")
    ID_COLUMN        = st.text_input("Account ID column",    value="cm11")
    BALANCE_COLUMN   = st.text_input("POS column",           value="cycle_opening_balance(current_balance)")
    RECOVERY_COLUMN  = st.text_input("Recovery column",      value="last_payment_amount")
    CHARGE_OFF_COL   = st.text_input("Charge-off date col",  value="charge_off_month")
    STATE_COLUMN     = st.text_input("State column",         value="state")
    CIBIL_COLUMN     = st.text_input("CIBIL score column",   value="cibil_score")

    st.markdown("---")
    st.markdown('<p class="section-title">ℹ️ Vintage Buckets</p>', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:12px;color:#6B7894;line-height:1.8">
    V1 = 0–30 days<br>V2 = 31–60 days<br>V3 = 61–90 days<br>
    V4 = 91–120 days<br>V5 = 121–150 days<br>V6 = 151–180 days<br>
    <b style="color:#C8D0DC">V7 = 181+ days (V7+)</b>
    </div>
    """, unsafe_allow_html=True)

# ── Main content ──────────────────────────────────────────────────────────────
if uploaded is None:
    st.markdown("""
    <div class="upload-prompt">
        <div style="font-size:56px;margin-bottom:16px">📂</div>
        <h2>Upload your portfolio CSV to get started</h2>
        <p style="font-size:14px">Use the sidebar to upload your charge-off data file.<br>
        The dashboard will auto-generate charts with interactive filters.</p>
        <br>
        <p style="font-size:12px;color:#455468">Expected columns: mis_date · cm11 · cycle_opening_balance · 
        last_payment_amount · charge_off_month · state · cibil_score</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── Load & process ─────────────────────────────────────────────────────────────
with st.spinner("Loading and processing data..."):
    try:
        df_raw = pd.read_csv(uploaded)
        df     = preprocess(df_raw)
    except Exception as e:
        st.error(f"❌ Error loading file: {e}")
        st.stop()

# ── KPI row ────────────────────────────────────────────────────────────────────
total_pos      = df['pos_mio'].sum()
total_recovery = df['recovery_mio'].sum()
total_accounts = df[ID_COLUMN].nunique()
overall_ror    = (total_recovery / total_pos * 100) if total_pos > 0 else 0
months_covered = df['file_month'].nunique()

k1, k2, k3, k4, k5 = st.columns(5)
with k1:
    st.metric("Total POS", f"₹{total_pos:,.1f}M")
with k2:
    st.metric("Total Recovery", f"₹{total_recovery:,.2f}M")
with k3:
    st.metric("Overall RoR", f"{overall_ror:.2f}%")
with k4:
    st.metric("Unique Accounts", f"{total_accounts:,}")
with k5:
    st.metric("Months Covered", str(months_covered))

st.markdown("---")

# ── Filter controls ────────────────────────────────────────────────────────────
st.markdown('<p class="section-title">⚙️ Chart Controls</p>', unsafe_allow_html=True)

ctrl1, ctrl2, ctrl3 = st.columns([2, 2, 3])

with ctrl1:
    mode_sel = st.radio("View Mode", ['$ Value', '# Accounts'], horizontal=True)

with ctrl2:
    tab_sel = st.radio("Dimension", ['POS', 'Vintage', 'States', 'CIBIL'], horizontal=True)

with ctrl3:
    seg_col, seg_order, color_map = get_segment_info(tab_sel)
    sub_options = ['All'] + [str(s) for s in seg_order if str(s) != 'nan']
    sub_sel = st.radio("Sub-filter", sub_options, horizontal=True)

mode = 'value' if mode_sel == '$ Value' else 'account'

st.markdown("---")

# ── Charts ─────────────────────────────────────────────────────────────────────
with st.spinner("Rendering charts..."):
    try:
        fig = make_chart(df, seg_col, seg_order, color_map, mode, sub_sel)
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)
    except Exception as e:
        st.error(f"❌ Chart error: {e}")
        import traceback
        st.code(traceback.format_exc())

st.markdown("---")

# ── Summary table ──────────────────────────────────────────────────────────────
tab_label_map = {'POS':'POS Bucket','Vintage':'Vintage','States':'State','CIBIL':'CIBIL Band'}
with st.expander(f"📋 Summary Table — Latest Month by {tab_label_map.get(tab_sel, tab_sel)}", expanded=False):
    try:
        tbl = summary_table(df, seg_col, tab_label_map.get(tab_sel,'Segment'))
        st.dataframe(
            tbl.style
               .format({'POS (Mio)':'₹{:,.2f}','Recovery (Mio)':'₹{:,.2f}','RoR (%)':'{:.2f}%'})
               .background_gradient(subset=['RoR (%)'], cmap='RdYlGn'),
            use_container_width=True,
            hide_index=True
        )
    except Exception as e:
        st.warning(f"Table error: {e}")

# ── All-tabs static view ───────────────────────────────────────────────────────
with st.expander("🗂 View All Dimensions at Once", expanded=False):
    for tab in ['POS', 'Vintage', 'States', 'CIBIL']:
        st.markdown(f"#### {tab}")
        sc, so, cm = get_segment_info(tab)
        try:
            fig2 = make_chart(df, sc, so, cm, mode, 'All')
            st.pyplot(fig2, use_container_width=True)
            plt.close(fig2)
        except Exception as e:
            st.warning(f"Could not render {tab}: {e}")

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:24px 0 8px;color:#455468;font-size:12px;
font-family:'DM Mono',monospace;border-top:1px solid #2A3140;margin-top:24px">
    WRITE-OFF PORTFOLIO MONITOR · CREDIT RECOVERY ANALYTICS
</div>
""", unsafe_allow_html=True)
