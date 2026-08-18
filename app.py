
import streamlit as st
from financial_engine import (
    FinancialGoal,
    generate_financial_plan,
    generate_local_advisor_report,
)

st.set_page_config(
    page_title="AI Financial Planner",
    page_icon="📊",
    layout="wide"
)

st.title("📊 AI Financial Planner")
st.caption("Private local prototype • Deterministic financial planning engine")

st.info(
    "Privacy mode: this prototype runs the financial calculations locally. "
    "No OpenAI API key is required."
)

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

goal_count = st.number_input(
    "Number of Goals", min_value=1, max_value=5, value=3, step=1
)

default_goals = [
    ("Retirement", 5_000_000, 500_000, 10, "High"),
    ("Car", 1_200_000, 200_000, 3, "Medium"),
    ("House", 5_000_000, 1_000_000, 7, "High"),
    ("Education", 2_000_000, 0, 5, "Medium"),
    ("Travel", 1_000_000, 0, 3, "Low"),
]

goals = []

for i in range(int(goal_count)):
    name, target, current, years, priority = default_goals[i]

    with st.expander(f"Goal {i + 1}: {name}", expanded=True):
        g1, g2, g3 = st.columns(3)

        with g1:
            goal_name = st.text_input(
                "Goal Name", value=name, key=f"goal_name_{i}"
            )
            target_amount = st.number_input(
                "Target Amount (₹)",
                min_value=0,
                value=target,
                step=100_000,
                key=f"goal_target_{i}"
            )

        with g2:
            current_amount = st.number_input(
                "Current Amount (₹)",
                min_value=0,
                value=current,
                step=50_000,
                key=f"goal_current_{i}"
            )
            horizon = st.number_input(
                "Time Horizon (Years)",
                min_value=1,
                max_value=50,
                value=years,
                step=1,
                key=f"goal_years_{i}"
            )

        with g3:
            goal_priority = st.selectbox(
                "Priority",
                ["High", "Medium", "Low"],
                index=["High", "Medium", "Low"].index(priority),
                key=f"goal_priority_{i}"
            )

        goals.append(
            FinancialGoal(
                name=goal_name,
                target_amount=target_amount,
                current_amount=current_amount,
                years=horizon,
                priority=goal_priority,
            )
        )

st.header("3. Generate Plan")

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

        st.download_button(
            "Download Local Report",
            data=report,
            file_name="financial_plan_report.md",
            mime="text/markdown",
        )

    except Exception as exc:
        st.error(f"Unable to generate the plan: {exc}")
