

"""
╔══════════════════════════════════════════════════════════════════╗
║   TWS PROJECT EXPORTS  +  PROJECT COMMAND CENTRE  ·  v5.4       ║
║   Page 1 → TWS Form Fill  |  Page 2 → TWS Submissions           ║
║   Page 3 → TWS Dashboard  (with hover tooltips)                 ║
╚══════════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import pandas as pd
from datetime import date, timedelta
import os

# ══════════════════════════════════════════════════════
#  GLOBAL CONFIG
# ══════════════════════════════════════════════════════
CSV_TWS = "tws_submissions.csv"
TODAY    = date.today()

# Milestone codes and base column names
MILESTONES = [
    ("M01","G1 Drg. Release",          "M01 G1 Drg Release"),
    ("M02","G1 Material Avl.",          "M02 G1 Material Avl"),
    ("M03","Proto Fitment",             "M03 Proto Fitment"),
    ("M04","Testing Start",             "M04 Testing Start"),
    ("M05","Interim Testing Go Ahead",  "M05 Interim Testing GoAhead"),
    ("M06","G1 ORC Drg. Release 🔔",   "M06 G1 ORC Drg Release"),
    ("M07","G1 ORC Material Avl. 🔔",  "M07 G1 ORC Material Avl"),
    ("M08","G1 ORC Proto Fitment 🔔",  "M08 G1 ORC Proto Fitment"),
    ("M09","G2 Go Ahead",               "M09 G2 GoAhead"),
    ("M10","G2 Material Avl. 🔔",      "M10 G2 Material Avl"),
    ("M11","5 Tractors Making Online",  "M11 5Tractors Online"),
    ("M12","PRR Sign-off 5 Nos",        "M12 PRR Signoff 5nos"),
    ("M13","Pre ERN",                   "M13 Pre ERN"),
    ("M14","Go Ahead ERN",              "M14 GoAhead ERN"),
    ("M15","BOM Change",                "M15 BOM Change"),
]

# Base columns (without the extra fired/original columns)
BASE_TWS_COLS = [
    "Submission ID","Submitted Date","Email","Project Code","Project Description",
    "Start of Project","Platform HP","Continent Country","SCR No","SCR CFT Date",
    "Model","Aggregate","Aggregate Lead Owner","Implementation Month","RD PMO",
    "Feasibility Report Date","Feasibility GoDate",
    "BCR Number","BCR Date","Cut Off Number","SPC Input Notes",
]

# Add milestone plan/actual columns
for _, _, col_prefix in MILESTONES:
    BASE_TWS_COLS.append(f"{col_prefix} Plan")
    BASE_TWS_COLS.append(f"{col_prefix} Actual")

# New columns for fired status and original plan dates
FIRED_COLS = ["Fired", "Extended"]
for _, _, col_prefix in MILESTONES:
    BASE_TWS_COLS.append(f"{col_prefix} Plan Original")  # stores original plan if extended

# Finally, add the fired status columns
BASE_TWS_COLS.extend(FIRED_COLS)

TWS_COLS = BASE_TWS_COLS  # full list

st.set_page_config(
    page_title="TWS · Hub",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════
#  MASTER CSS (same as before, with minor additions)
# ══════════════════════════════════════════════════════
def inject_css():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=JetBrains+Mono:wght@400;500&family=Lato:wght@300;400;700&display=swap');

:root {
  --bg0:#dbeafe; --bg1:#eff6ff; --bg2:#f0f7ff; --bg3:#bfdbfe;
  --border:#93c5fd; --border2:#60a5fa;
  --txt:#1a2233; --txt2:#4a5568; --txt3:#8899aa;
  --accent:#3b82f6; --accent-g:linear-gradient(135deg,#3b82f6,#06b6d4);
  --tws:#7c3aed; --fire:#ef4444;
  --r6:6px; --r10:10px; --r16:16px;
  --shadow-sm: 0 2px 8px rgba(59,130,246,.10), 0 1px 3px rgba(0,0,0,.06);
  --shadow-md: 0 8px 24px rgba(59,130,246,.12), 0 2px 8px rgba(0,0,0,.08);
  --shadow-lg: 0 20px 60px rgba(59,130,246,.15), 0 8px 20px rgba(0,0,0,.10);
  --shadow-3d: 0 10px 30px rgba(59,130,246,.18), 0 4px 12px rgba(0,0,0,.10), inset 0 1px 0 rgba(255,255,255,.9);
}
*{box-sizing:border-box;}
html,body,[class*="css"]{font-family:'Lato',sans-serif!important;background-color:var(--bg0)!important;color:var(--txt)!important;}
#MainMenu,footer,header{visibility:hidden;}
::-webkit-scrollbar{width:5px;height:5px;background:var(--bg3);}
::-webkit-scrollbar-thumb{background:var(--border2);border-radius:10px;}

/* Sidebar */
[data-testid="stSidebar"]{
  background:linear-gradient(180deg,#eff6ff 0%,#dbeafe 100%)!important;
  border-right:1px solid var(--border)!important;
  box-shadow: 4px 0 20px rgba(59,130,246,.08)!important;
}
[data-testid="stSidebar"] .stRadio label{font-size:13px!important;color:var(--txt2)!important;}
[data-testid="stSidebar"] .stRadio label:hover{color:var(--accent)!important;}
/* Fix sidebar toggle button visibility on light background */
[data-testid="stSidebarCollapseButton"] button,
[data-testid="stSidebarCollapseButton"],
[data-testid="collapsedControl"],
[data-testid="collapsedControl"] button {
  background: #bfdbfe !important;
  color: #1d4ed8 !important;
  border: 1.5px solid #60a5fa !important;
  border-radius: 8px !important;
  visibility: visible !important;
  opacity: 1 !important;
  display: flex !important;
}
[data-testid="stSidebarCollapseButton"] button svg,
[data-testid="collapsedControl"] svg,
[data-testid="collapsedControl"] button svg {
  fill: #1d4ed8 !important;
  color: #1d4ed8 !important;
  stroke: #1d4ed8 !important;
}

/* Inputs */
[data-testid="stTextInput"] input,textarea,select{
  background:#eff6ff!important;
  border:1.5px solid var(--border2)!important;
  border-radius:var(--r6)!important;
  color:var(--txt)!important;
  box-shadow: 0 2px 6px rgba(0,0,0,.05), inset 0 1px 3px rgba(0,0,0,.03)!important;
}
[data-testid="stTextInput"] input:focus,textarea:focus{
  border-color:var(--accent)!important;
  box-shadow: 0 0 0 3px rgba(59,130,246,.15), 0 2px 6px rgba(0,0,0,.06)!important;
}

/* Buttons */
.stButton>button{
  font-family:'Syne',sans-serif!important;font-weight:600!important;
  border-radius:var(--r6)!important;
  box-shadow: 0 4px 12px rgba(0,0,0,.10), 0 2px 4px rgba(0,0,0,.07), inset 0 1px 0 rgba(255,255,255,.5)!important;
  transform: translateY(0);
  transition: transform .15s ease, box-shadow .15s ease!important;
}
.stButton>button:hover{
  transform: translateY(-2px)!important;
  box-shadow: 0 8px 20px rgba(59,130,246,.25), 0 4px 8px rgba(0,0,0,.10)!important;
}
.stButton>button:active{transform: translateY(0px)!important;}
.stButton>button[kind="primary"]{background:var(--accent-g)!important;border:none!important;color:#fff!important;}
.stButton>button:not([kind="primary"]){background:#dbeafe!important;border:1.5px solid var(--border2)!important;color:var(--txt)!important;}

/* Form */
[data-testid="stForm"]{
  background:linear-gradient(145deg,#eff6ff,#dbeafe)!important;
  border:1.5px solid var(--border)!important;
  border-radius:var(--r16)!important;
  padding:24px!important;
  box-shadow: var(--shadow-3d)!important;
}

/* Expander */
[data-testid="stExpander"]{
  background:#eff6ff!important;
  border:1.5px solid var(--border)!important;
  border-radius:var(--r10)!important;
  box-shadow: var(--shadow-sm)!important;
}

/* Top metrics bar */
.top-bar{
  display:flex;align-items:center;gap:10px;flex-wrap:wrap;
  background:linear-gradient(135deg,#eff6ff,#dbeafe);
  border:1.5px solid var(--border);
  border-radius:var(--r10);padding:10px 18px;margin-bottom:22px;
  box-shadow: var(--shadow-3d);
}
.top-bar-title{
  font-family:'Syne',sans-serif;font-size:11px;font-weight:700;
  letter-spacing:.12em;text-transform:uppercase;color:var(--txt3);
  margin-right:6px;white-space:nowrap;
}
.tb-pill{
  display:inline-flex;align-items:center;gap:6px;
  padding:6px 14px;border-radius:30px;
  font-family:'Syne',sans-serif;font-size:12px;font-weight:700;
  border:1.5px solid;white-space:nowrap;
  box-shadow: 0 3px 8px rgba(0,0,0,.08), inset 0 1px 0 rgba(255,255,255,.7);
  transition: transform .15s ease, box-shadow .15s ease;
}
.tb-pill:hover{transform:translateY(-1px);box-shadow: 0 5px 14px rgba(0,0,0,.12);}
.tb-pill .tb-num{font-family:'JetBrains Mono',monospace;font-size:16px;font-weight:700;}
.tb-pill .tb-lbl{font-size:10px;opacity:.8;text-transform:uppercase;}
.tp-tws    {background:rgba(139,92,246,.08); color:#7c3aed; border-color:rgba(139,92,246,.3);}
.tp-total  {background:rgba(59,130,246,.08); color:#2563eb; border-color:rgba(59,130,246,.25);}
.tp-today  {background:rgba(16,185,129,.08); color:#059669; border-color:rgba(16,185,129,.25);}
.tp-month  {background:rgba(249,115,22,.08); color:#ea580c; border-color:rgba(249,115,22,.25);}
.tp-unique {background:rgba(6,182,212,.08);  color:#0891b2; border-color:rgba(6,182,212,.2);}
.tp-fired  {background:rgba(239,68,68,.08);  color:#dc2626; border-color:rgba(239,68,68,.3);}
.tb-sep{width:1px;height:28px;background:var(--border2);margin:0 4px;}

/* KPI cards — 3D lifted */
.kpi-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:24px;}
.kpi-card{
  background:linear-gradient(145deg,#eff6ff,#dbeafe);
  border:1.5px solid var(--border);border-radius:var(--r16);
  padding:20px 16px 14px;position:relative;
  box-shadow: 0 8px 24px rgba(59,130,246,.12), 0 3px 8px rgba(0,0,0,.07), inset 0 1px 0 rgba(255,255,255,1);
  transform: perspective(500px) translateZ(0);
  transition: transform .2s ease, box-shadow .2s ease;
}
.kpi-card:hover{
  transform: perspective(500px) translateZ(6px) translateY(-3px);
  box-shadow: 0 16px 40px rgba(59,130,246,.18), 0 6px 14px rgba(0,0,0,.10), inset 0 1px 0 rgba(255,255,255,1);
}
.kpi-card::before{
  content:'';position:absolute;top:0;left:0;right:0;height:4px;
  background:var(--kpi-accent,var(--accent));border-radius:var(--r16) var(--r16) 0 0;
  opacity:.85;
}
.kpi-card::after{
  content:'';position:absolute;bottom:0;left:10%;right:10%;height:8px;
  background:var(--kpi-accent,var(--accent));filter:blur(10px);opacity:.18;border-radius:50%;
}
.kc-num{font-family:'Syne',sans-serif;font-size:38px;font-weight:800;line-height:1;margin-bottom:6px;}
.kc-lbl{font-size:10px;font-weight:700;letter-spacing:.13em;text-transform:uppercase;color:var(--txt3);}
.kc-icon{position:absolute;bottom:12px;right:14px;font-size:26px;opacity:.15;}

/* Table */
.proj-wrap{
  overflow-x:auto;margin-top:8px;
  border-radius:var(--r16);
  box-shadow: var(--shadow-3d);
  border:1.5px solid var(--border);
}
table.tws{width:100%;border-collapse:collapse;font-size:12px;font-family:'Lato',sans-serif;background:#eff6ff;}
table.tws thead th{
  padding:10px 14px;text-align:left;font-family:'Syne',sans-serif;font-size:9px;
  font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:var(--txt3);
  border-bottom:2px solid var(--border);
  background:linear-gradient(180deg,#dbeafe,#bfdbfe);
  white-space:nowrap;
}
table.tws tbody tr{border-bottom:1px solid var(--border);transition:background .15s;}
table.tws tbody tr:hover{background:rgba(59,130,246,.05)!important;}
table.tws td{padding:10px 14px;vertical-align:middle;}
.chip{
  font-family:'JetBrains Mono',monospace;font-size:11px;
  background:rgba(59,130,246,.08);color:#2563eb;
  padding:2px 8px;border-radius:4px;border:1px solid rgba(59,130,246,.2);
}
.chip-tws{background:rgba(124,58,237,.08);color:#7c3aed;border-color:rgba(124,58,237,.2);}
.badge{
  display:inline-flex;align-items:center;gap:4px;padding:3px 10px;border-radius:20px;
  font-family:'Syne',sans-serif;font-size:10px;font-weight:700;letter-spacing:.08em;
}
.b-fired{background:rgba(239,68,68,.10);color:#dc2626;border:1px solid rgba(239,68,68,.35);}

/* Section heading */
.sh{
  font-family:'Syne',sans-serif;font-size:10px;font-weight:700;letter-spacing:.16em;
  text-transform:uppercase;color:var(--txt2);
  padding-bottom:8px;border-bottom:2px solid var(--border);
  margin:20px 0 16px;display:flex;align-items:center;gap:8px;
}

/* Page title */
.ptitle{
  font-family:'Syne',sans-serif;font-size:28px;font-weight:800;letter-spacing:-.02em;
  background:linear-gradient(135deg,#1e3a5f,#3b82f6);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:2px;
}
.ptitle-tws{background:linear-gradient(135deg,#7c3aed,#0891b2);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
.psub{font-size:12px;color:var(--txt3);margin-bottom:20px;font-family:'JetBrains Mono',monospace;}

/* TWS Form */
.tws-section-title{
  font-family:'Syne',sans-serif;font-size:13px;font-weight:700;letter-spacing:.06em;
  text-transform:uppercase;color:#7c3aed;margin-bottom:14px;display:flex;align-items:center;gap:8px;
}
.field-num{
  display:inline-flex;align-items:center;justify-content:center;width:22px;height:22px;
  background:rgba(124,58,237,.12);border:1.5px solid rgba(124,58,237,.35);border-radius:50%;
  font-family:'JetBrains Mono',monospace;font-size:10px;font-weight:700;color:#7c3aed;
  box-shadow: 0 2px 6px rgba(124,58,237,.15);
}
.milestone-label{font-family:'Syne',sans-serif;font-size:12px;font-weight:700;color:var(--txt2);margin-bottom:8px;display:flex;align-items:center;gap:8px;}

/* Tooltip */
#tws-tip{
  display:none;position:fixed;z-index:99999;
  background:linear-gradient(145deg,#eff6ff,#dbeafe);
  border:1.5px solid var(--border);border-radius:var(--r16);padding:16px 20px;
  min-width:320px;max-width:450px;
  box-shadow: 0 24px 60px rgba(59,130,246,.20), 0 8px 20px rgba(0,0,0,.12), inset 0 1px 0 rgba(255,255,255,1);
  pointer-events:none;font-family:'Lato',sans-serif;font-size:11px;
}
#tws-tip .th{
  font-family:'Syne',sans-serif;font-weight:700;font-size:14px;color:var(--txt);
  margin-bottom:10px;padding-bottom:10px;border-bottom:1px solid var(--border);
}
#tws-tip .tg{display:grid;grid-template-columns:130px 1fr;gap:5px 10px;}
#tws-tip .tk{color:var(--txt3);font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.07em;}
#tws-tip .tv{color:var(--txt);font-family:'JetBrains Mono',monospace;font-size:10px;word-break:break-word;}
#tws-tip hr{grid-column:1/-1;border:none;border-top:1px solid var(--border);margin:3px 0;}

/* Fired card (for dashboard) */
.fired-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:14px;margin-bottom:24px;}
.fired-card{
  background:linear-gradient(145deg,#fff5f5,#fff8f8);
  border:1.5px solid rgba(239,68,68,.25);
  border-radius:var(--r16);padding:18px 20px;
  border-left:4px solid var(--fire);
  box-shadow: 0 8px 24px rgba(239,68,68,.10), 0 3px 8px rgba(0,0,0,.06), inset 0 1px 0 #fff;
  transition: transform .2s ease, box-shadow .2s ease;
}
.fired-card:hover{
  transform: translateY(-2px);
  box-shadow: 0 14px 36px rgba(239,68,68,.16), 0 6px 12px rgba(0,0,0,.08);
}
.fired-card-title{
  font-family:'Syne',sans-serif;font-size:15px;font-weight:700;color:var(--txt);
  margin-bottom:10px;display:flex;align-items:center;gap:8px;
}
.fired-card-code{
  font-family:'JetBrains Mono',monospace;font-size:11px;
  background:rgba(239,68,68,.12);color:#dc2626;padding:2px 7px;border-radius:4px;
}
.fired-card-row{display:flex;justify-content:space-between;align-items:center;padding:4px 0;border-bottom:1px solid rgba(239,68,68,.10);font-size:12px;}
.fck{color:rgba(220,38,38,.7);font-size:10px;font-weight:700;text-transform:uppercase;}
.fcv{color:var(--txt);font-family:'JetBrains Mono',monospace;font-size:11px;}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
#  DATA LAYER — TWS with FIRED logic
# ══════════════════════════════════════════════════════
def load_tws():
    if os.path.exists(CSV_TWS):
        df = pd.read_csv(CSV_TWS, dtype=str)
        # Ensure all required columns exist
        for c in TWS_COLS:
            if c not in df.columns:
                df[c] = ""
    else:
        df = pd.DataFrame(columns=TWS_COLS)
    return df

def save_tws(df):
    df.to_csv(CSV_TWS, index=False)

def next_tws_id(df):
    if df.empty: return "TWS-001"
    nums = []
    for sid in df["Submission ID"].dropna():
        try: nums.append(int(sid.split("-")[1]))
        except: pass
    return f"TWS-{(max(nums)+1 if nums else 1):03d}"

def parse_date(val):
    try:
        return pd.to_datetime(str(val)).date()
    except:
        return None

def apply_fired_logic(df):
    """Check each submission: if any milestone is overdue (plan < today and actual empty)
       and submission not yet extended, then mark as fired, extend all overdue milestones by 5 days,
       store original plan, and set Extended = True."""
    changed = False
    for idx, row in df.iterrows():
        fired = str(row.get("Fired", "")).lower() == "true"
        extended = str(row.get("Extended", "")).lower() == "true"
        if fired and extended:
            continue  # already handled

        any_overdue = False
        updates = {}

        for _, _, col_prefix in MILESTONES:
            plan_col = f"{col_prefix} Plan"
            actual_col = f"{col_prefix} Actual"
            orig_col = f"{col_prefix} Plan Original"

            plan_val = row.get(plan_col, "")
            actual_val = row.get(actual_col, "")
            orig_val = row.get(orig_col, "")

            plan_date = parse_date(plan_val)
            actual_date = parse_date(actual_val)

            # If plan exists, actual empty, and plan < today → overdue
            if plan_date and not actual_date and plan_date < TODAY:
                any_overdue = True
                if not orig_val:  # store original only if not already stored
                    updates[orig_col] = plan_val
                    # extend plan by 5 days
                    new_plan = plan_date + timedelta(days=5)
                    updates[plan_col] = str(new_plan)

        if any_overdue:
            updates["Fired"] = "True"
            if not extended:
                updates["Extended"] = "True"
            # apply updates
            for k, v in updates.items():
                df.at[idx, k] = v
            changed = True

    if changed:
        save_tws(df)
    return df

# ══════════════════════════════════════════════════════
#  UI HELPERS
# ══════════════════════════════════════════════════════
def sh(icon, label):
    st.markdown(f'<div class="sh"><span>{icon}</span>{label}</div>', unsafe_allow_html=True)

def fired_badge():
    return '<span class="badge b-fired">🔥 FIRED</span>'

# Tooltip generation
def build_tws_tooltip(row):
    """Create an HTML tooltip with all fields for a TWS submission."""
    lines = []
    # Header
    proj_code = str(row.get("Project Code", "") or "")
    proj_desc = str(row.get("Project Description", "") or "")
    header = f'<div class="th">{proj_code} — {proj_desc[:50]}{"..." if len(proj_desc)>50 else ""}</div>'
    lines.append(header)

    # Basic fields (two-column grid)
    basic_fields = [
        ("Submission ID", "Submission ID"),
        ("Submitted Date", "Submitted Date"),
        ("Email", "Email"),
        ("Project Code", "Project Code"),
        ("Project Description", "Project Description"),
        ("Start of Project", "Start of Project"),
        ("Platform HP", "Platform HP"),
        ("Continent Country", "Continent Country"),
        ("SCR No", "SCR No"),
        ("SCR CFT Date", "SCR CFT Date"),
        ("Model", "Model"),
        ("Aggregate", "Aggregate"),
        ("Aggregate Lead Owner", "Aggregate Lead Owner"),
        ("Implementation Month", "Implementation Month"),
        ("RD PMO", "RD PMO"),
        ("Feasibility Report Date", "Feasibility Report Date"),
        ("Feasibility GoDate", "Feasibility GoDate"),
        ("BCR Number", "BCR Number"),
        ("BCR Date", "BCR Date"),
        ("Cut Off Number", "Cut Off Number"),
        ("SPC Input Notes", "SPC Input Notes"),
        ("Fired", "Fired"),
        ("Extended", "Extended"),
    ]
    grid = '<div class="tg">'
    for label, col in basic_fields:
        val = str(row.get(col, "")) or "—"
        grid += f'<div class="tk">{label}</div><div class="tv">{val}</div>'
    grid += '</div>'
    lines.append(grid)

    # Milestones section
    lines.append('<hr>')
    lines.append('<div style="font-family:\'Syne\',sans-serif;font-size:12px;font-weight:700;margin:5px 0;color:var(--tws);">Milestones</div>')
    for code, label, col_prefix in MILESTONES:
        plan = row.get(f"{col_prefix} Plan", "")
        actual = row.get(f"{col_prefix} Actual", "")
        original = row.get(f"{col_prefix} Plan Original", "")
        plan_str = plan if plan else "—"
        actual_str = actual if actual else "—"
        orig_str = f" (orig: {original})" if original and original != plan else ""
        lines.append(f'<div style="display:flex;gap:6px;margin:3px 0;"><span style="min-width:45px;color:var(--txt3);">{code}</span>'
                     f'<span style="color:var(--txt2);">Plan: {plan_str}{orig_str}</span>'
                     f'<span style="color:var(--txt2);">Actual: {actual_str}</span></div>')

    html = "".join(lines).replace('"', "&quot;").replace("'", "&#39;").replace("\n", " ")
    return html

# Tooltip JavaScript (adapted)
TOOLTIP_JS = """
<script>
(function boot(){
  var rows=document.querySelectorAll('tr[data-tip]');
  if(!rows.length){setTimeout(boot,350);return;}
  var tip=document.getElementById('tws-tip');
  if(!tip){setTimeout(boot,350);return;}
  rows.forEach(function(row){
    row.addEventListener('mouseenter',function(){tip.innerHTML=row.getAttribute('data-tip');tip.style.display='block';});
    row.addEventListener('mousemove',function(e){
      var x=e.clientX+18,y=e.clientY+14,W=window.innerWidth,H=window.innerHeight;
      var tw=tip.offsetWidth||350,th2=tip.offsetHeight||300;
      if(x+tw>W-10)x=e.clientX-tw-10;
      if(y+th2>H-10)y=e.clientY-th2-10;
      tip.style.left=x+'px';tip.style.top=y+'px';
    });
    row.addEventListener('mouseleave',function(){tip.style.display='none';});
  });
})();
</script>"""

# ══════════════════════════════════════════════════════
#  PAGE 1 — TWS FORM FILL
# ══════════════════════════════════════════════════════
def page_tws_form(tws_df):
    st.markdown('<div class="ptitle ptitle-tws">TWS Project — Exports</div>', unsafe_allow_html=True)
    st.markdown('<div class="psub">// Form Fill · Section A: Basic Details · Section B: Milestones · Section C: Monitoring</div>', unsafe_allow_html=True)

    with st.form("tws_master_form", clear_on_submit=True):

        # Section A — Basic Details
        st.markdown('<div class="tws-section-title">📋 Section A — Basic Details <span style="font-size:10px;color:var(--txt3);font-weight:400;font-family:\'Lato\',sans-serif;text-transform:none;letter-spacing:0;">&nbsp;* = required</span></div>', unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<span class="field-num">1</span> **Email** <span class="req-star">*</span>', unsafe_allow_html=True)
            email = st.text_input("Email", placeholder="name@company.com", label_visibility="collapsed")
        with c2:
            st.markdown('<span class="field-num">2</span> **Project Code** <span class="req-star">*</span>', unsafe_allow_html=True)
            proj_code = st.text_input("Project Code", placeholder="TWS-EXP-2024-001", label_visibility="collapsed")

        st.markdown('<span class="field-num">3</span> **Project Description** <span class="req-star">*</span>', unsafe_allow_html=True)
        proj_desc = st.text_area("Project Description", placeholder="Scope, objective, key deliverables…", height=80, label_visibility="collapsed")

        c3, c4 = st.columns(2)
        with c3:
            st.markdown('<span class="field-num">4</span> **Start of Project** <span class="req-star">*</span>', unsafe_allow_html=True)
            start_date = st.date_input("Start of Project", value=TODAY, label_visibility="collapsed")
        with c4:
            st.markdown('<span class="field-num">5</span> **Platform (HP Range)** <span class="req-star">*</span>', unsafe_allow_html=True)
            platform_hp = st.selectbox("Platform", ["Below 30 HP","30–60 HP","60–101 HP","Above 101 HP"], label_visibility="collapsed")

        c5, c6 = st.columns(2)
        with c5:
            st.markdown('<span class="field-num">6</span> **Continent / Country** <span class="req-star">*</span>', unsafe_allow_html=True)
            continent = st.text_input("Continent Country", placeholder="Asia / India", label_visibility="collapsed")
        with c6:
            st.markdown('<span class="field-num">7</span> **SCR No.** <span class="req-star">*</span>', unsafe_allow_html=True)
            scr_no = st.text_input("SCR No", placeholder="SCR-XXXX", label_visibility="collapsed")

        c7, c8 = st.columns(2)
        with c7:
            st.markdown('<span class="field-num">8</span> **SCR – Issue Discussed in CFT** <span class="req-star">*</span>', unsafe_allow_html=True)
            scr_cft_date = st.date_input("SCR CFT Date", value=TODAY, label_visibility="collapsed")
        with c8:
            st.markdown('<span class="field-num">9</span> **Model** <span class="req-star">*</span>', unsafe_allow_html=True)
            model = st.text_input("Model", placeholder="DI-75 / 8055", label_visibility="collapsed")

        c9, c10 = st.columns(2)
        with c9:
            st.markdown('<span class="field-num">10</span> **Aggregate** <span class="req-star">*</span>', unsafe_allow_html=True)
            aggregate = st.selectbox("Aggregate",
                ["Electrical","Hydraulic","Transmission","Engine","Vehicle","Cabin"],
                label_visibility="collapsed")
        with c10:
            st.markdown('<span class="field-num">11</span> **Aggregate Lead – Project Owner** <span class="req-star">*</span>', unsafe_allow_html=True)
            agg_lead = st.text_input("Aggregate Lead Owner", placeholder="Owner name / ID", label_visibility="collapsed")

        c11, c12 = st.columns(2)
        with c11:
            st.markdown('<span class="field-num">12</span> **Implementation Month** <span class="req-star">*</span>', unsafe_allow_html=True)
            impl_month = st.selectbox("Implementation Month",
                ["January","February","March","April","May","June",
                 "July","August","September","October","November","December"],
                index=TODAY.month-1, label_visibility="collapsed")
        with c12:
            st.markdown('<span class="field-num">13</span> **R&D – PMO** <span class="req-star">*</span> <em style="font-size:10px;color:var(--txt3);">by default</em>', unsafe_allow_html=True)
            rd_pmo = st.radio("RD PMO", ["Mohit Rana","Arashdeep Parmar"], horizontal=True, label_visibility="collapsed")

        st.markdown('<span class="field-num">14</span> **Feasibility Study Report** <span class="req-star">*</span>', unsafe_allow_html=True)
        f1, f2 = st.columns(2)
        with f1:
            st.caption("📅 Report Date")
            feasibility_date = st.date_input("Feasibility Report Date", value=TODAY, label_visibility="collapsed")
        with f2:
            st.caption("🚀 Go-Date")
            feasibility_godate = st.date_input("Feasibility GoDate", value=TODAY+timedelta(days=7), label_visibility="collapsed")

        st.divider()

        # Section B — Milestone Monitoring
        st.markdown('<div class="tws-section-title">📅 Section B — Milestone Monitoring <span style="font-size:10px;color:var(--txt3);font-weight:400;font-family:\'Lato\',sans-serif;text-transform:none;letter-spacing:0;">&nbsp;· Individual Plan &amp; Actual Status</span></div>', unsafe_allow_html=True)
        st.caption("Enter both Plan Date and Actual Date for each milestone. 🔔 = ORC/SPC milestones (Separate Page note).")

        milestone_vals = {}
        for code, label, col_prefix in MILESTONES:
            st.markdown(
                f'<div class="milestone-label">'
                f'<span class="field-num" style="background:rgba(59,130,246,.15);border-color:rgba(59,130,246,.35);color:#93c5fd;">{code}</span>'
                f'&nbsp;{label}</div>',
                unsafe_allow_html=True
            )
            mc1, mc2 = st.columns(2)
            with mc1:
                st.caption("📌 Plan Date")
                plan_val = st.date_input(f"{col_prefix} Plan", value=None, key=f"p_{code}", label_visibility="collapsed")
            with mc2:
                st.caption("✅ Actual Date")
                actual_val = st.date_input(f"{col_prefix} Actual", value=None, key=f"a_{code}", label_visibility="collapsed")
            milestone_vals[f"{col_prefix} Plan"]   = str(plan_val)   if plan_val   else ""
            milestone_vals[f"{col_prefix} Actual"] = str(actual_val) if actual_val else ""

        st.divider()

        # Section C — Monitoring of Project Implementation
        st.markdown(
            '<div class="tws-section-title">🔧 Section C — Monitoring of Project Implementation '
            '<span style="font-size:10px;color:#c4b5fd;font-family:\'JetBrains Mono\',monospace;'
            'font-weight:400;text-transform:none;letter-spacing:0;">&nbsp;← SPC Input</span></div>',
            unsafe_allow_html=True
        )

        mc1, mc2, mc3 = st.columns(3)
        with mc1:
            st.markdown('<span class="field-num">30</span> **BCR Number**', unsafe_allow_html=True)
            bcr_number = st.text_input("BCR Number", placeholder="BCR-XXXX", label_visibility="collapsed")
        with mc2:
            st.markdown('<span class="field-num">31</span> **BCR Date**', unsafe_allow_html=True)
            bcr_date = st.date_input("BCR Date", value=None, label_visibility="collapsed")
        with mc3:
            st.markdown(
                '<span class="field-num">32</span> **Cut Off Number** '
                '<span style="font-size:10px;color:var(--txt3);font-family:\'JetBrains Mono\',monospace;">D2L → SPC update</span>',
                unsafe_allow_html=True
            )
            cutoff_num = st.text_input("Cut off Number", placeholder="Cut-off ref.", label_visibility="collapsed")

        st.markdown('<span class="field-num">+</span> **SPC Input Notes**', unsafe_allow_html=True)
        spc_notes = st.text_area("SPC Input Notes", placeholder="SPC notes / D2L → SPC update remarks…", height=75, label_visibility="collapsed")

        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("🚀  Submit TWS Form", use_container_width=True, type="primary")

    # Handle submission
    if submitted:
        errors = []
        if not email.strip():     errors.append("Email is required")
        if not proj_code.strip(): errors.append("Project Code is required")
        if not proj_desc.strip(): errors.append("Project Description is required")
        if not continent.strip(): errors.append("Continent / Country is required")
        if not scr_no.strip():    errors.append("SCR No. is required")
        if not model.strip():     errors.append("Model is required")
        if not agg_lead.strip():  errors.append("Aggregate Lead is required")

        if errors:
            for e in errors: st.error(f"❌ {e}")
        else:
            sid = next_tws_id(tws_df)
            new_row = {c:"" for c in TWS_COLS}
            new_row.update({
                "Submission ID":        sid,
                "Submitted Date":       str(TODAY),
                "Email":                email.strip(),
                "Project Code":         proj_code.strip().upper(),
                "Project Description":  proj_desc.strip(),
                "Start of Project":     str(start_date),
                "Platform HP":          platform_hp,
                "Continent Country":    continent.strip(),
                "SCR No":               scr_no.strip(),
                "SCR CFT Date":         str(scr_cft_date),
                "Model":                model.strip(),
                "Aggregate":            aggregate,
                "Aggregate Lead Owner": agg_lead.strip(),
                "Implementation Month": impl_month,
                "RD PMO":               rd_pmo,
                "Feasibility Report Date": str(feasibility_date),
                "Feasibility GoDate":   str(feasibility_godate),
                "BCR Number":           bcr_number.strip(),
                "BCR Date":             str(bcr_date) if bcr_date else "",
                "Cut Off Number":       cutoff_num.strip(),
                "SPC Input Notes":      spc_notes.strip(),
                "Fired":                "False",
                "Extended":             "False",
                **milestone_vals,
            })
            tws_df = pd.concat([tws_df, pd.DataFrame([new_row])], ignore_index=True)
            save_tws(tws_df)
            st.success(f"✅ Submission **{sid}** saved! Project Code: `{proj_code.strip().upper()}`")
            st.balloons()
            st.rerun()

# ══════════════════════════════════════════════════════
#  PAGE 2 — TWS SUBMISSIONS (VIEW ALL) with tooltips
# ══════════════════════════════════════════════════════
def page_tws_submissions(tws_df):
    st.markdown('<div class="ptitle ptitle-tws">TWS Submissions</div>', unsafe_allow_html=True)
    st.markdown('<div class="psub">// All submitted TWS Project Export records (🔥 = fired, hover for details)</div>', unsafe_allow_html=True)

    if tws_df.empty:
        st.info("📭 No submissions yet. Fill the TWS Form first.")
        return tws_df

    search = st.text_input("🔍 Search by Code / Email / Model", placeholder="Type to filter…")
    view = tws_df.copy()
    if search:
        mask = (view["Project Code"].str.contains(search,case=False,na=False)|
                view["Email"].str.contains(search,case=False,na=False)|
                view["Model"].str.contains(search,case=False,na=False))
        view = view[mask]

    st.caption(f"Showing **{len(view)}** of **{len(tws_df)}** submissions — hover any row for full details")

    # Display table with fired badge and tooltips
    disp = ["Submission ID","Submitted Date","Project Code","Model","Platform HP",
            "Aggregate","Implementation Month","RD PMO","Fired"]
    disp = [c for c in disp if c in view.columns]
    th = "".join(f"<th>{c}</th>" for c in disp)

    # Start building table with tooltip container
    body = ""
    for i,(_,row) in enumerate(view.iterrows()):
        tip = build_tws_tooltip(row)
        cells=""
        for c in disp:
            if c == "Fired":
                val = row.get(c,"")
                if str(val).lower() == "true":
                    cells += f'<td>{fired_badge()}</td>'
                else:
                    cells += "<td>—</td>"
            else:
                v = str(row.get(c,"")) or "—"
                if c=="Submission ID":
                    cells+=f'<td><span class="chip chip-tws">{v}</span></td>'
                elif c=="Project Code":
                    cells+=f'<td><strong style="color:var(--txt);">{v}</strong></td>'
                else:
                    cells+=f'<td style="color:var(--txt2);font-size:12px;">{v}</td>'
        bg="rgba(139,92,246,.04)" if i%2==0 else ""
        body+=f'<tr class="tws-row" data-tip="{tip}" style="background:{bg};">{cells}</tr>'

    # Wrap with tooltip div and inject JavaScript
    table_html = f'<div id="tws-tip"></div><div class="proj-wrap"><table class="tws"><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table></div>' + TOOLTIP_JS
    st.markdown(table_html, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    sh("🔍","Full Record Viewer (shows original & extended dates)")
    if not view.empty:
        sel_id = st.selectbox("Select Submission", view["Submission ID"].tolist(), label_visibility="collapsed")
        sel_row = view[view["Submission ID"]==sel_id].iloc[0]
        with st.expander(f"📋 {sel_id} — Full Details", expanded=True):
            # Show basic fields
            basic_cols = ["Submission ID","Submitted Date","Email","Project Code","Project Description",
                          "Start of Project","Platform HP","Continent Country","SCR No","SCR CFT Date",
                          "Model","Aggregate","Aggregate Lead Owner","Implementation Month","RD PMO",
                          "Feasibility Report Date","Feasibility GoDate","BCR Number","BCR Date",
                          "Cut Off Number","SPC Input Notes","Fired","Extended"]
            st.markdown("**Basic Information**")
            b1, b2 = st.columns(2)
            for i, col in enumerate(basic_cols):
                if col in sel_row:
                    val = str(sel_row[col]) or "—"
                    with b1 if i%2==0 else b2:
                        st.markdown(f"**{col}:** {val}")

            # Milestones with original/plan/actual
            st.markdown("---")
            st.markdown("**Milestone Details**")
            for code, label, col_prefix in MILESTONES:
                plan = sel_row.get(f"{col_prefix} Plan", "")
                actual = sel_row.get(f"{col_prefix} Actual", "")
                original = sel_row.get(f"{col_prefix} Plan Original", "")
                with st.container():
                    cols = st.columns([1,2,2,2])
                    cols[0].markdown(f"**{code}**")
                    cols[1].markdown(f"📅 Plan: `{plan or '—'}`")
                    if original and original != plan:
                        cols[1].markdown(f"🕒 Original: `{original}`")
                    cols[2].markdown(f"✅ Actual: `{actual or '—'}`")
                    if str(sel_row.get("Fired","")).lower()=="true" and not actual and plan:
                        cols[3].markdown("🔥 *Overdue*")

    with st.expander("⚠️ Danger Zone — Delete Submission"):
        del_id = st.selectbox("Select to delete", view["Submission ID"].tolist() if not view.empty else ["—"], key="del_tws")
        if st.button("🗑 Delete Submission", type="primary") and del_id != "—":
            tws_df = tws_df[tws_df["Submission ID"]!=del_id].reset_index(drop=True)
            save_tws(tws_df)
            st.success(f"🗑 {del_id} deleted.")
            st.rerun()
    return tws_df

# ══════════════════════════════════════════════════════
#  PAGE 3 — TWS DASHBOARD (with fired overview and tooltips)
# ══════════════════════════════════════════════════════
def page_tws_dashboard(tws_df):
    st.markdown('<div class="ptitle ptitle-tws">📊 TWS Dashboard</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="psub">// Live metrics from TWS submissions · {TODAY.strftime("%A, %d %B %Y")}</div>', unsafe_allow_html=True)

    # Compute metrics
    total = len(tws_df)
    unique_projects = tws_df["Project Code"].nunique() if not tws_df.empty else 0
    today_sub = (tws_df["Submitted Date"] == str(TODAY)).sum() if not tws_df.empty else 0
    if not tws_df.empty:
        try:
            sub_dates = pd.to_datetime(tws_df["Submitted Date"], errors='coerce')
            month_sub = (sub_dates.dt.month == TODAY.month).sum()
        except:
            month_sub = 0
    else:
        month_sub = 0
    fired_count = (tws_df["Fired"].astype(str).str.lower() == "true").sum() if not tws_df.empty else 0

    # Top bar
    bar_html = f"""
<div class="top-bar">
  <span class="top-bar-title">📊 LIVE METRICS</span>
  <span class="tb-pill tp-tws"><span class="tb-num">{total}</span><span class="tb-lbl">Submissions</span></span>
  <span class="tb-sep"></span>
  <span class="tb-pill tp-unique"><span class="tb-num">{unique_projects}</span><span class="tb-lbl">Unique Projects</span></span>
  <span class="tb-pill tp-today"><span class="tb-num">{today_sub}</span><span class="tb-lbl">Today</span></span>
  <span class="tb-pill tp-month"><span class="tb-num">{month_sub}</span><span class="tb-lbl">This Month</span></span>
  <span class="tb-sep"></span>
  <span class="tb-pill tp-fired"><span class="tb-num">{fired_count}</span><span class="tb-lbl">Fired</span></span>
</div>"""
    st.markdown(bar_html, unsafe_allow_html=True)

    # KPI cards
    cards_html = f"""
<div class="kpi-grid">
  <div class="kpi-card" style="--kpi-accent:#58a6ff;">
    <div class="kc-num" style="color:#58a6ff;">{total}</div>
    <div class="kc-lbl">Total Submissions</div>
    <div class="kc-icon">📋</div>
  </div>
  <div class="kpi-card" style="--kpi-accent:#c4b5fd;">
    <div class="kc-num" style="color:#c4b5fd;">{unique_projects}</div>
    <div class="kc-lbl">Unique Projects</div>
    <div class="kc-icon">🏷️</div>
  </div>
  <div class="kpi-card" style="--kpi-accent:#22c55e;">
    <div class="kc-num" style="color:#22c55e;">{today_sub}</div>
    <div class="kc-lbl">Submitted Today</div>
    <div class="kc-icon">📅</div>
  </div>
  <div class="kpi-card" style="--kpi-accent:#ef4444;">
    <div class="kc-num" style="color:#ef4444;">{fired_count}</div>
    <div class="kc-lbl">Fired Submissions</div>
    <div class="kc-icon">🔥</div>
  </div>
</div>"""
    st.markdown(cards_html, unsafe_allow_html=True)

    # Show fired submissions in detail
    if fired_count > 0:
        sh("🔥", f"Fired Submissions — {fired_count} Require Attention")
        fired_df = tws_df[tws_df["Fired"].astype(str).str.lower() == "true"]
        cards = ""
        for _, row in fired_df.iterrows():
            # Gather overdue milestones info
            overdue_list = []
            for code, label, col_prefix in MILESTONES:
                plan = row.get(f"{col_prefix} Plan", "")
                actual = row.get(f"{col_prefix} Actual", "")
                original = row.get(f"{col_prefix} Plan Original", "")
                if not actual and plan:
                    plan_date = parse_date(plan)
                    if plan_date and plan_date < TODAY:
                        overdue_list.append(f"{code} (Plan: {plan}" + (f", Orig: {original}" if original else "") + ")")
            overdue_str = ", ".join(overdue_list) if overdue_list else "None"
            cards += f"""
<div class="fired-card">
  <div class="fired-card-title">
    🔥 <span class="fired-card-code">{row['Project Code']}</span>
    &nbsp;{row['Project Description'][:50]}…
  </div>
  <div class="fired-card-row">
    <span class="fck">Submission ID</span><span class="fcv">{row['Submission ID']}</span>
  </div>
  <div class="fired-card-row">
    <span class="fck">Model</span><span class="fcv">{row['Model']}</span>
  </div>
  <div class="fired-card-row">
    <span class="fck">Overdue milestones</span>
    <span class="fcv" style="color:#ef4444;">{overdue_str}</span>
  </div>
</div>"""
        st.markdown(f'<div class="fired-grid">{cards}</div>', unsafe_allow_html=True)

    # Show all submissions table with tooltips
    sh("📋", "All Submissions (hover for details)")
    if tws_df.empty:
        st.info("No submissions yet.")
        return

    view_cols = ["Submission ID","Submitted Date","Project Code","Model","Platform HP","Aggregate","RD PMO","Fired"]
    view = tws_df[view_cols].sort_values("Submitted Date", ascending=False).reset_index(drop=True)
    th = "".join(f"<th>{c}</th>" for c in view_cols)

    body = ""
    for i, (_, row) in enumerate(view.iterrows()):
        tip = build_tws_tooltip(row)
        cells = ""
        for c in view_cols:
            if c == "Fired":
                val = row.get(c,"")
                cells += f'<td>{"🔥" if str(val).lower()=="true" else "—"}</td>'
            else:
                v = str(row[c]) if pd.notna(row[c]) else "—"
                if c == "Submission ID":
                    cells += f'<td><span class="chip chip-tws">{v}</span></td>'
                elif c == "Project Code":
                    cells += f'<td><strong style="color:var(--txt);">{v}</strong></td>'
                else:
                    cells += f'<td style="color:var(--txt2);">{v}</td>'
        bg = "rgba(139,92,246,.04)" if i % 2 == 0 else ""
        body += f'<tr class="tws-row" data-tip="{tip}" style="background:{bg};">{cells}</tr>'

    table_html = f'<div id="tws-tip"></div><div class="proj-wrap"><table class="tws"><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table></div>' + TOOLTIP_JS
    st.markdown(table_html, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
#  SIDEBAR (only three options)
# ══════════════════════════════════════════════════════
def render_sidebar(tws_df):
    with st.sidebar:
        st.markdown("""
<div style="padding:4px 0 20px;">
  <div style="font-family:'Syne',sans-serif;font-size:20px;font-weight:800;color:#dde4ef;">📋 TWS · Hub</div>
  <div style="font-family:'JetBrains Mono',monospace;font-size:9px;color:#4a5568;margin-top:2px;letter-spacing:.06em;">
    TWS EXPORTS · v5.4
  </div>
</div>""", unsafe_allow_html=True)

        tws_n = len(tws_df)
        fired_n = (tws_df["Fired"].astype(str).str.lower() == "true").sum() if not tws_df.empty else 0

        page = st.radio("nav", [
            "📋 TWS Form Fill",
            f"📊 TWS Submissions [{tws_n}]",
            "🖥️ Dashboard",
        ], label_visibility="collapsed")

        st.divider()

        # Mini stats
        for lbl,val,clr in [
            ("Total Submissions", tws_n, "#7c3aed"),
            ("Fired 🔥", fired_n, "#dc2626"),
            ("Unique Projects", tws_df["Project Code"].nunique() if not tws_df.empty else 0, "#2563eb"),
        ]:
            st.markdown(
                f'<div style="display:flex;justify-content:space-between;padding:5px 0;'
                f'border-bottom:1px solid var(--border);font-size:12px;">'
                f'<span style="color:var(--txt3);">{lbl}</span>'
                f'<span style="color:{clr};font-family:\'JetBrains Mono\',monospace;font-weight:700;">{val}</span>'
                f'</div>', unsafe_allow_html=True)

        st.divider()
        st.markdown(
            f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:10px;color:var(--txt3);">'
            f'Today: {TODAY}<br>Fire rule: plan < today & no actual<br>Extension: +5 days</div>',
            unsafe_allow_html=True)
    return page

# ══════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════
def main():
    inject_css()

    # Load TWS data and apply fired logic
    tws_df = load_tws()
    tws_df = apply_fired_logic(tws_df)

    # Sidebar navigation
    page = render_sidebar(tws_df)

    # Route to page
    if page == "📋 TWS Form Fill":
        page_tws_form(tws_df)
    elif page.startswith("📊 TWS Submissions"):
        page_tws_submissions(tws_df)
    elif page == "🖥️ Dashboard":
        page_tws_dashboard(tws_df)

if __name__ == "__main__":
    main()


    