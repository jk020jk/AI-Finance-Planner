import streamlit as st
import plotly.graph_objects as go
from financial_engine import (
    FinancialGoal,
    generate_financial_plan,
    generate_local_advisor_report,
)

# ----------------------------------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="AI Financial Planner",
    page_icon="📊",
    layout="wide",
)

NAVY = "#0F172A"
NAVY_SOFT = "#475569"
GREEN = "#16A34A"
GREEN_BG = "#ECFDF5"
AMBER = "#D97706"
AMBER_BG = "#FFFBEB"
RED = "#DC2626"
RED_BG = "#FEF2F2"
GREY = "#64748B"
GREY_BG = "#F1F5F9"
BORDER = "#E2E8F0"

# ----------------------------------------------------------------------------
# GLOBAL STYLE
# ----------------------------------------------------------------------------
st.markdown(
    f"""
    <style>
    .stApp {{ background-color: #F8FAFC; }}
    #MainMenu, footer {{ visibility: hidden; }}

    .app-header {{
        display:flex; align-items:center; justify-content:space-between;
        margin-bottom: 4px;
    }}
    .app-title {{
        font-size: 30px; font-weight: 700; color:{NAVY}; margin:0;
    }}
    .app-subtitle {{
        font-size: 14px; color:{NAVY_SOFT}; margin-top:2px;
    }}
    .badge-proto {{
        display:inline-block; padding:4px 12px; border-radius:999px;
        background:{GREY_BG}; color:{NAVY_SOFT}; font-size:12px; font-weight:600;
        border:1px solid {BORDER};
    }}
    .privacy-note {{
        font-size:12px; color:{GREY}; margin-top:10px; margin-bottom:18px;
        padding:8px 14px; background:{GREY_BG}; border-radius:8px; display:inline-block;
    }}

    .section-title {{
        font-size:18px; font-weight:700; color:{NAVY};
        margin-top:28px; margin-bottom:10px;
        border-bottom: 1px solid {BORDER}; padding-bottom:6px;
    }}

    .kpi-card {{
        background:white; border:1px solid {BORDER}; border-radius:12px;
        padding:14px 16px; height:92px;
    }}
    .kpi-label {{
        font-size:11px; font-weight:600; color:{GREY}; text-transform:uppercase;
        letter-spacing:0.04em; margin-bottom:6px;
    }}
    .kpi-value {{ font-size:22px; font-weight:700; color:{NAVY}; }}
    .kpi-sub {{ font-size:11px; color:{GREY}; margin-top:2px;}}

    .goal-card {{
        background:white; border:1px solid {BORDER}; border-radius:12px;
        padding:16px 18px; margin-bottom:14px;
    }}
    .goal-title-row {{ display:flex; justify-content:space-between; align-items:center; }}
    .goal-name {{ font-size:16px; font-weight:700; color:{NAVY}; }}
    .goal-metrics {{ display:flex; gap:28px; margin-top:12px; flex-wrap:wrap; }}
    .goal-metric-label {{ font-size:11px; color:{GREY}; text-transform:uppercase; }}
    .goal-metric-value {{ font-size:15px; font-weight:600; color:{NAVY}; }}

    .pill {{
        display:inline-block; padding:3px 11px; border-radius:999px;
        font-size:11px; font-weight:700; letter-spacing:0.02em;
    }}
    .pill-green {{ background:{GREEN_BG}; color:{GREEN}; }}
    .pill-amber {{ background:{AMBER_BG}; color:{AMBER}; }}
    .pill-red {{ background:{RED_BG}; color:{RED}; }}
    .pill-grey {{ background:{GREY_BG}; color:{GREY}; }}

    .alert-card {{
        border-radius:10px; padding:12px 16px; margin-bottom:10px;
        border-left:4px solid;
    }}
    .alert-red {{ background:{RED_BG}; border-color:{RED}; }}
    .alert-amber {{ background:{AMBER_BG}; border-color:{AMBER}; }}
    .alert-green {{ background:{GREEN_BG}; border-color:{GREEN}; }}
    .alert-title {{ font-weight:700; font-size:13px; color:{NAVY}; margin-bottom:2px; }}
    .alert-body {{ font-size:13px; color:{NAVY_SOFT}; }}

    .action-row {{
        display:flex; align-items:center; gap:14px;
        background:white; border:1px solid {BORDER}; border-radius:10px;
        padding:12px 16px; margin-bottom:8px;
    }}
    .action-num {{
        font-size:16px; font-weight:700; color:{NAVY_SOFT}; min-width:26px;
    }}
    .action-text {{ font-size:14px; font-weight:600; color:{NAVY}; flex:1; }}

    .priority-row {{
        background:white; border:1px solid {BORDER}; border-radius:10px;
        padding:12px 16px; margin-bottom:10px;
    }}
    .priority-head {{ display:flex; justify-content:space-between; margin-bottom:6px; }}
    .priority-name {{ font-weight:700; color:{NAVY}; font-size:14px;}}
    .priority-sub {{ font-size:12px; color:{GREY}; margin-top:6px; }}

    .disclaimer {{
        font-size:11px; color:{GREY}; margin-top:30px; padding-top:12px;
        border-top:1px solid {BORDER};
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ----------------------------------------------------------------------------
# HELPERS (presentation only — no financial logic)
# ----------------------------------------------------------------------------
def pill_class(status: str) -> str:
    mapping = {
        "Fully Funded": "pill-green",
        "Feasible": "pill-green",
        "Aligned": "pill-green",
        "Partially Funded": "pill-amber",
        "Review Recommended": "pill-amber",
        "Deferred": "pill-grey",
        "Not Feasible": "pill-red",
        "Funding Gap": "pill-red",
        "Review Required": "pill-red",
    }
    return mapping.get(status, "pill-grey")


def priority_pill_class(priority: str) -> str:
    return {"High": "pill-red", "Medium": "pill-amber", "Low": "pill-grey"}.get(
        priority, "pill-grey"
    )


def kpi_card(label, value, sub=""):
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-sub">{sub}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def alert_card(level, title, body):
    cls = {"red": "alert-red", "amber": "alert-amber", "green": "alert-green"}[level]
    st.markdown(
        f"""
        <div class="alert-card {cls}">
            <div class="alert-title">{title}</div>
            <div class="alert-body">{body}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def allocation_donut(allocation: dict, title: str):
    labels = ["Equity", "Debt", "Gold", "Cash"]
    values = [
        allocation.get("equity", 0),
        allocation.get("debt", 0),
        allocation.get("gold", 0),
        allocation.get("cash", 0),
    ]
    colors = [NAVY, "#3B82F6", AMBER, "#CBD5E1"]
    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.62,
                marker=dict(colors=colors, line=dict(color="white", width=2)),
                textinfo="percent",
                textfont=dict(size=11),
            )
        ]
    )
    fig.update_layout(
        title=dict(text=title, font=dict(size=13, color=NAVY)),
        showlegend=True,
        legend=dict(orientation="h", y=-0.15, font=dict(size=10)),
        margin=dict(t=40, b=10, l=10, r=10),
        height=260,
    )
    st.plotly_chart(fig, use_container_width=True)


def scenario_bar(scenarios, title):
    names = [s["scenario"] for s in scenarios]
    sips = [s["required_monthly_sip"] for s in scenarios]
    colors = [NAVY if n == "Base" else "#CBD5E1" for n in names]
    fig = go.Figure(
        data=[
            go.Bar(
                x=names,
                y=sips,
                marker_color=colors,
                text=[f"₹{v:,.0f}" for v in sips],
                textposition="outside",
            )
        ]
    )
    fig.update_layout(
        title=dict(text=title, font=dict(size=13, color=NAVY)),
        margin=dict(t=40, b=10, l=10, r=10),
        height=260,
        yaxis_title=None,
        xaxis_title=None,
    )
    st.plotly_chart(fig, use_container_width=True)


def health_color(score):
    if score >= 70:
        return GREEN
    if score >= 40:
        return AMBER
    return RED


# ----------------------------------------------------------------------------
# HEADER
# ----------------------------------------------------------------------------
h1, h2 = st.columns([4, 1])
with h1:
    st.markdown('<div class="app-title">AI Financial Planner</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="app-subtitle">Personal finance planning powered by deterministic financial analytics</div>',
        unsafe_allow_html=True,
    )
with h2:
    st.markdown(
        '<div style="text-align:right; margin-top:8px;">'
        '<span class="badge-proto">Planning Prototype</span></div>',
        unsafe_allow_html=True,
    )

st.markdown(
    '<div class="privacy-note">Privacy-first prototype • No OpenAI API key required</div>',
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------------
# INPUTS
# ----------------------------------------------------------------------------
st.markdown('<div class="section-title">Financial Profile</div>', unsafe_allow_html=True)

with st.expander("Personal & Cash Flow", expanded=True):
    c1, c2 = st.columns(2)
    with c1:
        age = st.number_input("Age", 18, 100, 28, help="Used to gauge investment horizon and risk capacity")
        monthly_income = st.number_input(
            "Monthly Income (₹)", 0, 10_000_000, 100_000, step=5_000
        )
    with c2:
        monthly_expenses = st.number_input(
            "Monthly Expenses (₹)", 0, 10_000_000, 55_000, step=5_000
        )
        monthly_emi = st.number_input(
            "Monthly EMI (₹)", 0, 10_000_000, 10_000, step=1_000,
            help="Total of all recurring loan/EMI obligations"
        )

with st.expander("Assets", expanded=True):
    a1, a2 = st.columns(2)
    with a1:
        current_savings = st.number_input(
            "Current Savings (₹)", 0, 100_000_000, 300_000, step=10_000,
            help="Liquid savings used for your emergency fund calculation"
        )
    with a2:
        existing_investments = st.number_input(
            "Existing Investments (₹)", 0, 100_000_000, 500_000, step=10_000
        )

with st.expander("Risk Profile", expanded=True):
    r1, r2 = st.columns(2)
    with r1:
        risk_tolerance = st.selectbox(
            "Risk Tolerance", ["low", "moderate", "high"], index=1,
            help="Your self-reported comfort with investment risk"
        )
    with r2:
        investment_experience = st.selectbox(
            "Investment Experience",
            ["beginner", "some experience", "experienced"],
            index=0,
        )

# ----------------------------------------------------------------------------
# GOALS
# ----------------------------------------------------------------------------
GOAL_LIBRARY = {
    "Retirement":      {"icon": "🏦", "target": 5_000_000, "current": 500_000,   "years": 10, "priority": "High"},
    "Home":            {"icon": "🏠", "target": 5_000_000, "current": 1_000_000, "years": 7,  "priority": "High"},
    "Car":             {"icon": "🚗", "target": 1_200_000, "current": 200_000,   "years": 3,  "priority": "Medium"},
    "Education":       {"icon": "🎓", "target": 2_000_000, "current": 0,         "years": 5,  "priority": "Medium"},
    "Travel":          {"icon": "✈️", "target": 300_000,   "current": 50_000,    "years": 1,  "priority": "Medium"},
    "Marriage":        {"icon": "💍", "target": 1_500_000, "current": 200_000,   "years": 4,  "priority": "Medium"},
    "Emergency Fund":  {"icon": "🛟", "target": 300_000,   "current": 100_000,   "years": 1,  "priority": "High"},
    "Wealth Creation": {"icon": "📈", "target": 3_000_000, "current": 200_000,   "years": 8,  "priority": "Medium"},
    "Other":           {"icon": "🎯", "target": 500_000,   "current": 0,         "years": 3,  "priority": "Medium"},
}
PRIORITY_OPTIONS = ["High", "Medium", "Low"]

st.markdown('<div class="section-title">Financial Goals</div>', unsafe_allow_html=True)
st.caption("Select one or more goals you want to plan for.")

selected_goal_types = st.multiselect(
    "What are you planning for?",
    options=list(GOAL_LIBRARY.keys()),
    default=["Retirement", "Car", "Home"],
    key="selected_goal_types",
)

goals = []
goal_errors = []

if not selected_goal_types:
    goal_errors.append("Select at least one goal to continue.")

for goal_type in selected_goal_types:
    defaults = GOAL_LIBRARY[goal_type]

    # Resolve the display name — "Other" needs a custom name from the user.
    if goal_type == "Other":
        other_name = st.text_input(
            "Enter your goal name",
            value="",
            key="goal_other_name",
            placeholder="e.g. Startup, Sabbatical, Gadget Fund",
        )
        display_name = other_name.strip()
        header_label = display_name if display_name else "Other (name required)"
    else:
        display_name = goal_type
        header_label = goal_type

    with st.expander(f"{defaults['icon']} {header_label}", expanded=True):
        g1, g2, g3 = st.columns(3)

        with g1:
            target_amount = st.number_input(
                "Target Amount (₹)", min_value=0, value=defaults["target"], step=50_000,
                key=f"goal_target_{goal_type}"
            )

        with g2:
            current_amount = st.number_input(
                "Current Amount (₹)", min_value=0, value=defaults["current"], step=25_000,
                key=f"goal_current_{goal_type}"
            )
            horizon = st.number_input(
                "Time Horizon (Years)", min_value=1, max_value=50, value=defaults["years"], step=1,
                key=f"goal_years_{goal_type}"
            )

        with g3:
            goal_priority = st.selectbox(
                "Priority", PRIORITY_OPTIONS,
                index=PRIORITY_OPTIONS.index(defaults["priority"]),
                key=f"goal_priority_{goal_type}"
            )

        # ---- validation ----
        if goal_type == "Other" and not display_name:
            goal_errors.append("Enter a goal name for 'Other'.")
        if target_amount <= 0:
            goal_errors.append(f"{header_label}: Target amount must be greater than 0.")
        if current_amount < 0:
            goal_errors.append(f"{header_label}: Current amount cannot be negative.")
        if horizon <= 0:
            goal_errors.append(f"{header_label}: Time horizon must be greater than 0.")

        if display_name:
            goals.append(
                FinancialGoal(
                    name=display_name,
                    target_amount=target_amount,
                    current_amount=current_amount,
                    years=horizon,
                    priority=goal_priority,
                )
            )

if goal_errors:
    for err in goal_errors:
        st.warning(err)

st.markdown('<div class="section-title">Generate Plan</div>', unsafe_allow_html=True)
generate = st.button("Generate Financial Plan", type="primary", disabled=bool(goal_errors))

# ----------------------------------------------------------------------------
# PLAN OUTPUT
# ----------------------------------------------------------------------------
if generate:
    try:
        plan = generate_financial_plan(
            age=age,
            monthly_income=monthly_income,
            monthly_expenses=monthly_expenses,
            monthly_emi=monthly_emi,
            current_savings=current_savings,
            existing_investments=existing_investments,
            risk_tolerance=risk_tolerance,
            investment_experience=investment_experience,
            goals=goals,
        )

        health = plan["financial_health"]
        risk = plan["risk_profile"]
        risk_validation = plan["risk_validation"]
        emergency = plan["emergency_fund"]
        capacity = plan["investment_capacity"]
        analysis = plan["goal_analysis"]
        priority_plan = plan["priority_based_plan"]

        st.success("Financial plan generated successfully.")

        # ---------------- KPI DASHBOARD ----------------
        st.markdown('<div class="section-title">Overview</div>', unsafe_allow_html=True)
        k1, k2, k3, k4, k5, k6 = st.columns(6)
        with k1:
            kpi_card("Financial Health", f"{health['financial_health_score']:.1f}/100")
        with k2:
            kpi_card("Monthly Surplus", f"₹{health['monthly_surplus']:,.0f}")
        with k3:
            kpi_card("Investment Capacity", f"₹{capacity['monthly_investment_capacity']:,.0f}")
        with k4:
            kpi_card("Emergency Fund", f"{emergency['current_months']:.2f} mo", f"target {emergency['target_months']} mo")
        with k5:
            kpi_card("Risk Profile", risk["risk_profile"])
        with k6:
            kpi_card("Funding Status", analysis["overall_status"])

        # ---------------- RISK PROFILE ----------------
        st.markdown('<div class="section-title">Risk Profile</div>', unsafe_allow_html=True)
        rc1, rc2 = st.columns([1, 2])
        with rc1:
            kpi_card("Risk Score", f"{risk['risk_score']}/100")
        with rc2:
            st.markdown(
                f'<span class="pill {pill_class(risk_validation["status"])}">{risk_validation["status"]}</span> '
                f'&nbsp; Stated tolerance: <b>{risk_validation["stated_risk_tolerance"].title()}</b> '
                f'&nbsp;|&nbsp; Calculated profile: <b>{risk_validation["calculated_risk_profile"]}</b>',
                unsafe_allow_html=True,
            )
            if risk_validation["status"] != "Aligned":
                st.markdown(
                    f'<div style="margin-top:8px; font-size:13px; color:{NAVY_SOFT};">'
                    f'Your calculated risk profile is <b>{risk_validation["calculated_risk_profile"]}</b>, '
                    f'while your stated tolerance is <b>{risk_validation["stated_risk_tolerance"]}</b>.</div>',
                    unsafe_allow_html=True,
                )

        # ---------------- EMERGENCY FUND ----------------
        st.markdown('<div class="section-title">Emergency Fund</div>', unsafe_allow_html=True)
        ef_ratio = min(emergency["current_months"] / emergency["target_months"], 1.0) if emergency["target_months"] else 0
        st.progress(ef_ratio)
        ef1, ef2, ef3 = st.columns(3)
        ef1.metric("Current", f"₹{emergency['current_savings']:,.0f}")
        ef2.metric("Target", f"₹{emergency['target_amount']:,.0f}")
        ef3.metric("Gap", f"₹{emergency['gap']:,.0f}")

        # ---------------- GOAL-WISE PLAN ----------------
        st.markdown('<div class="section-title">Goal-wise Plan</div>', unsafe_allow_html=True)
        for goal in analysis["goals"]:
            st.markdown(
                f"""
                <div class="goal-card">
                    <div class="goal-title-row">
                        <div class="goal-name">{goal['goal']}</div>
                        <div>
                            <span class="pill {priority_pill_class(goal['priority'])}">{goal['priority'].upper()} PRIORITY</span>
                            <span class="pill {pill_class(goal['status'])}" style="margin-left:6px;">{goal['status']}</span>
                        </div>
                    </div>
                    <div class="goal-metrics">
                        <div><div class="goal-metric-label">Target</div><div class="goal-metric-value">₹{goal['target_amount']:,.0f}</div></div>
                        <div><div class="goal-metric-label">Current</div><div class="goal-metric-value">₹{goal['current_amount']:,.0f}</div></div>
                        <div><div class="goal-metric-label">Horizon</div><div class="goal-metric-value">{goal['years']} yrs</div></div>
                        <div><div class="goal-metric-label">Required SIP</div><div class="goal-metric-value">₹{goal['required_monthly_sip']:,.2f}</div></div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # ---------------- PRIORITY-BASED FUNDING ----------------
        st.markdown('<div class="section-title">Priority-Based Funding</div>', unsafe_allow_html=True)
        for item in priority_plan["allocations"]:
            pct = (item["allocated_sip"] / item["required_sip"]) if item["required_sip"] else 1.0
            pct = min(pct, 1.0)
            st.markdown(
                f"""
                <div class="priority-row">
                    <div class="priority-head">
                        <span class="priority-name">{item['goal']}</span>
                        <span class="pill {pill_class(item['funding_status'])}">{item['funding_status']}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.progress(pct)
            st.markdown(
                f'<div class="priority-sub">Required ₹{item["required_sip"]:,.2f} &nbsp;|&nbsp; '
                f'Allocated ₹{item["allocated_sip"]:,.2f} &nbsp;|&nbsp; '
                f'Unfunded ₹{item["unfunded_amount"]:,.2f}</div>',
                unsafe_allow_html=True,
            )
            st.write("")

        # ---------------- PORTFOLIO ALLOCATION ----------------
        st.markdown('<div class="section-title">Portfolio Allocation</div>', unsafe_allow_html=True)
        goal_list = analysis["goals"]
        for i in range(0, len(goal_list), 3):
            row = goal_list[i:i + 3]
            cols = st.columns(len(row))
            for col, goal in zip(cols, row):
                with col:
                    allocation_donut(goal["allocation"], goal["goal"])

        # ---------------- SCENARIO ANALYSIS ----------------
        st.markdown('<div class="section-title">Scenario Analysis</div>', unsafe_allow_html=True)
        for i in range(0, len(goal_list), 3):
            row = goal_list[i:i + 3]
            cols = st.columns(len(row))
            for col, goal in zip(cols, row):
                with col:
                    scenario_bar(goal["scenarios"], goal["goal"])

        # ---------------- KEY RISKS ----------------
        st.markdown('<div class="section-title">Key Risks</div>', unsafe_allow_html=True)
        risks_found = False

        if risk_validation["status"] != "Aligned":
            risks_found = True
            level = "red" if risk_validation["status"] == "Review Required" else "amber"
            alert_card(
                level,
                "Risk Profile Mismatch",
                f"Calculated profile is {risk_validation['calculated_risk_profile']} while stated "
                f"tolerance is {risk_validation['stated_risk_tolerance']}.",
            )

        if risk_validation["experience_flag"] != "No major experience conflict":
            risks_found = True
            alert_card("amber", "Experience Mismatch", risk_validation["experience_flag"])

        if emergency["gap"] > 0:
            risks_found = True
            alert_card(
                "amber",
                "Emergency Fund Gap",
                f"₹{emergency['gap']:,.0f} remains to reach the {emergency['target_months']}-month target.",
            )

        if analysis["overall_status"] == "Funding Gap":
            risks_found = True
            alert_card(
                "red",
                "Funding Gap",
                f"Total required SIP (₹{analysis['total_required_sip']:,.2f}) exceeds available "
                f"investment capacity (₹{analysis['investment_capacity']:,.2f}).",
            )

        deferred_goals = [g["goal"] for g in priority_plan["allocations"] if g["funding_status"] == "Deferred"]
        if deferred_goals:
            risks_found = True
            alert_card(
                "red",
                "Deferred Goals",
                f"The following goals currently receive no funding: {', '.join(deferred_goals)}.",
            )

        if not risks_found:
            alert_card("green", "No Major Risks Detected", "Your plan is currently well aligned across risk, funding and emergency fund coverage.")

        # ---------------- RECOMMENDED NEXT ACTIONS ----------------
        st.markdown('<div class="section-title">Recommended Next Actions</div>', unsafe_allow_html=True)
        actions = []
        if emergency["gap"] > 0:
            actions.append(("Complete Emergency Fund", "High"))
        if risk_validation["status"] == "Review Required":
            actions.append(("Review Risk Profile", "High"))
        elif risk_validation["status"] == "Review Recommended":
            actions.append(("Review Risk Profile", "Medium"))
        if deferred_goals:
            actions.append((f"Prioritize {', '.join(deferred_goals)}", "High"))
        elif analysis["overall_status"] == "Funding Gap":
            actions.append(("Reassess Goal Timelines or Increase Capacity", "Medium"))
        if not actions:
            actions.append(("Maintain Current Plan and Review Annually", "Low"))

        for idx, (text, prio) in enumerate(actions, start=1):
            st.markdown(
                f"""
                <div class="action-row">
                    <div class="action-num">{idx:02d}</div>
                    <div class="action-text">{text}</div>
                    <span class="pill {priority_pill_class(prio)}">{prio} Priority</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # ---------------- LOCAL ADVISOR REPORT ----------------
        st.markdown('<div class="section-title">Local Advisor Report</div>', unsafe_allow_html=True)
        report = generate_local_advisor_report(plan)
        with st.expander("View full report", expanded=False):
            st.markdown(report)

        st.download_button(
            "Download Local Report",
            data=report,
            file_name="financial_plan_report.md",
            mime="text/markdown",
        )

        st.markdown(
            '<div class="disclaimer">This tool provides a deterministic, rule-based estimate for '
            'informational purposes only and does not constitute financial advice. Please consult a '
            'certified financial advisor before making investment decisions.</div>',
            unsafe_allow_html=True,
        )

    except Exception as exc:
        st.error(f"Unable to generate the plan: {exc}")
