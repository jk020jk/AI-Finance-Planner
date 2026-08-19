import streamlit as st

from reportlab.lib.pagesizes import A4

from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from reportlab.lib.enums import TA_LEFT

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

from reportlab.lib.units import mm

def markdown_to_pdf(markdown_text):
    pdf_path = "financial_plan_report.pdf"

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleCustom",
        parent=styles["Title"],
        fontSize=18,
        leading=22,
        spaceAfter=12,
    )

    heading_style = ParagraphStyle(
        "HeadingCustom",
        parent=styles["Heading2"],
        fontSize=13,
        leading=16,
        spaceBefore=10,
        spaceAfter=6,
    )

    body_style = ParagraphStyle(
        "BodyCustom",
        parent=styles["BodyText"],
        fontSize=9.5,
        leading=14,
        spaceAfter=5,
    )

    story = []

    for line in markdown_text.splitlines():

        line = line.strip()

        if not line:
            story.append(Spacer(1, 5))
            continue

        if line.startswith("# "):
            text = line[2:].strip()
            story.append(Paragraph(text, title_style))

        elif line.startswith("## "):
            text = line[3:].strip()
            story.append(Paragraph(text, heading_style))

        elif line.startswith("### "):
            text = line[4:].strip()
            story.append(Paragraph(text, heading_style))

        elif line.startswith("- "):
            text = "• " + line[2:].strip()
            story.append(Paragraph(text, body_style))

        else:
            story.append(Paragraph(line, body_style))

    doc.build(story)

    with open(pdf_path, "rb") as pdf_file:
        return pdf_file.read()
from financial_engine import (
    FinancialGoal,
    generate_financial_plan,
    generate_local_advisor_report,
)

st.set_page_config(
    page_title="AI Financial Planner",
        layout="wide"
)

st.title("AI Financial Planner")
st.header("1. Financial Profile")

c1, c2 = st.columns(2)

with c1:
    age = st.number_input("Age", 18, 100, 28)
    monthly_income = st.number_input(
        "Monthly Income (₹)", 0, 10_000_000, 100_000, step=5_000
    )
    monthly_expenses = st.number_input(
        "Monthly Expenses (₹)", 0, 10_000_000, 55_000, step=5_000
    )
    monthly_emi = st.number_input(
        "Monthly EMI (₹)", 0, 10_000_000, 10_000, step=1_000
    )

with c2:
    current_savings = st.number_input(
        "Current Savings (₹)", 0, 100_000_000, 300_000, step=10_000
    )
    existing_investments = st.number_input(
        "Existing Investments (₹)", 0, 100_000_000, 500_000, step=10_000
    )
    risk_tolerance = st.selectbox(
        "Risk Tolerance", ["low", "moderate", "high"], index=1
    )
    investment_experience = st.selectbox(
        "Investment Experience",
        ["beginner", "some experience", "experienced"],
        index=0
    )

st.header("2. Financial Goals")

st.caption("Select one or more goals you want to plan for.")

# -------------------------------------------------------------------------
# GOAL OPTIONS
# -------------------------------------------------------------------------
GOAL_LIBRARY = {
    "Retirement": {
        "target": 5_000_000,
        "current": 500_000,
        "years": 10,
        "priority": "High",
    },
    "Home": {
        "target": 5_000_000,
        "current": 1_000_000,
        "years": 7,
        "priority": "High",
    },
    "Car": {
        "target": 1_200_000,
        "current": 200_000,
        "years": 3,
        "priority": "Medium",
    },
    "Education": {
        "target": 2_000_000,
        "current": 0,
        "years": 5,
        "priority": "Medium",
    },
    "Travel": {
        "target": 1_000_000,
        "current": 0,
        "years": 3,
        "priority": "Low",
    },
    "Marriage": {
        "target": 1_500_000,
        "current": 200_000,
        "years": 4,
        "priority": "Medium",
    },
    "Emergency Fund": {
        "target": 300_000,
        "current": 100_000,
        "years": 1,
        "priority": "High",
    },
    "Wealth Creation": {
        "target": 3_000_000,
        "current": 200_000,
        "years": 8,
        "priority": "Medium",
    },
    "Other": {
        "target": 500_000,
        "current": 0,
        "years": 3,
        "priority": "Medium",
    },
}

PRIORITY_OPTIONS = ["High", "Medium", "Low"]

# -------------------------------------------------------------------------
# MULTI-SELECT GOALS
# -------------------------------------------------------------------------
selected_goal_types = st.multiselect(
    "What are you planning for?",
    options=list(GOAL_LIBRARY.keys()),
    default=[],
    key="selected_goal_types",
)

goals = []

# -------------------------------------------------------------------------
# GOAL DETAILS
# -------------------------------------------------------------------------
for goal_type in selected_goal_types:

    defaults = GOAL_LIBRARY[goal_type]

    # Custom name for "Other"
    if goal_type == "Other":
        goal_name = st.text_input(
            "Goal Name",
            value="",
            placeholder="e.g. Startup, Sabbatical, Gadget Fund",
            key="goal_name_other",
        )
    else:
        goal_name = goal_type

    with st.expander(f"{goal_type}", expanded=True):

        g1, g2, g3 = st.columns(3)

        with g1:
            target_amount = st.number_input(
                "Target Amount (₹)",
                min_value=0,
                value=defaults["target"],
                step=100_000,
                key=f"goal_target_{goal_type}",
            )

        with g2:
            current_amount = st.number_input(
                "Current Amount (₹)",
                min_value=0,
                value=defaults["current"],
                step=50_000,
                key=f"goal_current_{goal_type}",
            )

        with g3:
            horizon = st.number_input(
                "Time Horizon (Years)",
                min_value=1,
                max_value=50,
                value=defaults["years"],
                step=1,
                key=f"goal_years_{goal_type}",
            )

        goal_priority = st.selectbox(
            "Priority",
            PRIORITY_OPTIONS,
            index=PRIORITY_OPTIONS.index(defaults["priority"]),
            key=f"goal_priority_{goal_type}",
        )

        # Validation
        if goal_type == "Other" and not goal_name.strip():
            st.warning("Please enter a name for your custom goal.")

        if goal_name.strip() and target_amount > 0:
            goals.append(
                FinancialGoal(
                    name=goal_name.strip(),
                    target_amount=target_amount,
                    current_amount=current_amount,
                    years=horizon,
                    priority=goal_priority,
                )
            )

if st.button("Generate Financial Plan", type="primary"):
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

        st.success("Financial plan generated successfully.")

        health = plan["financial_health"]
        risk = plan["risk_profile"]
        emergency = plan["emergency_fund"]
        capacity = plan["investment_capacity"]
        analysis = plan["goal_analysis"]

        st.header("Financial Health")
        a, b, c, d = st.columns(4)
        a.metric("Monthly Surplus", f"₹{health['monthly_surplus']:,.0f}")
        b.metric("Savings Rate", f"{health['savings_rate']:.1f}%")
        c.metric("Debt-to-Income", f"{health['debt_to_income']:.1f}%")
        d.metric("Health Score", f"{health['financial_health_score']:.2f}/100")

        st.header("Risk Profile")
        a, b, c = st.columns(3)
        a.metric("Profile", risk["risk_profile"])
        b.metric("Risk Score", risk["risk_score"])
        c.metric("Horizon", f"{risk['investment_horizon_years']} years")

        if plan["risk_validation"]["status"] != "Aligned":
            st.warning(
                f"Risk review recommended: stated tolerance is "
                f"{plan['risk_validation']['stated_risk_tolerance']}, "
                f"calculated profile is "
                f"{plan['risk_validation']['calculated_risk_profile']}."
            )

        st.header("Emergency Fund")
        a, b, c = st.columns(3)
        a.metric("Current Coverage", f"{emergency['current_months']:.2f} months")
        b.metric("Target", f"{emergency['target_months']} months")
        c.metric("Gap", f"₹{emergency['gap']:,.0f}")

        st.header("Investment Capacity")
        st.metric(
            "Monthly Investment Capacity",
            f"₹{capacity['monthly_investment_capacity']:,.0f}"
        )

        st.header("Goal-wise Plan")
        for goal in analysis["goals"]:
            with st.expander(
                f"{goal['goal']} • {goal['priority']} • {goal['status']}"
            ):
                a, b, c = st.columns(3)
                a.metric("Target", f"₹{goal['target_amount']:,.0f}")
                b.metric("Required SIP", f"₹{goal['required_monthly_sip']:,.2f}")
                c.metric("Horizon", f"{goal['years']} years")

                st.write(
                    f"Allocation — Equity {goal['allocation']['equity']}% | "
                    f"Debt {goal['allocation']['debt']}% | "
                    f"Gold {goal['allocation']['gold']}% | "
                    f"Cash {goal['allocation']['cash']}%"
                )

                st.write("Scenario SIPs:")
                for scenario in goal["scenarios"]:
                    st.write(
                        f"- {scenario['scenario']}: "
                        f"{scenario['annual_return']:.0f}% assumption → "
                        f"₹{scenario['required_monthly_sip']:,.2f}/month"
                    )

        st.header("Priority-Based Funding")
        for item in plan["priority_based_plan"]["allocations"]:
            st.write(
                f"**{item['goal']} — {item['funding_status']}**  \n"
                f"Required: ₹{item['required_sip']:,.2f} | "
                f"Allocated: ₹{item['allocated_sip']:,.2f} | "
                f"Unfunded: ₹{item['unfunded_amount']:,.2f}"
            )

        st.header("Overall Plan")
        a, b, c = st.columns(3)
        a.metric("Total Required SIP", f"₹{analysis['total_required_sip']:,.2f}")
        b.metric("Available Capacity", f"₹{analysis['investment_capacity']:,.2f}")
        c.metric("Gap", f"₹{analysis['overall_gap']:,.2f}")

        if analysis["overall_status"] == "Funding Gap":
            st.error(f"Overall status: {analysis['overall_status']}")
        else:
            st.success(f"Overall status: {analysis['overall_status']}")

        st.header("Local Advisor Report")
        report = generate_local_advisor_report(plan)
        st.markdown(report)

       pdf_data = markdown_to_pdf(report)

st.download_button(
    "Download Financial Plan (PDF)",
    data=pdf_data,
    file_name="financial_plan_report.pdf",
    mime="application/pdf",
)

    except Exception as exc:
        st.error(f"Unable to generate the plan: {exc}")
