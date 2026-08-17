
from dataclasses import dataclass, field
from typing import List

@dataclass
class FinancialGoal:
    name: str
    target_amount: float
    current_amount: float
    years: float
    priority: str

@dataclass
class UserFinancialProfile:
    age: int
    monthly_income: float
    monthly_expenses: float
    dependents: int
    current_savings: float
    existing_investments: float
    monthly_emi: float
    risk_tolerance: str
    investment_experience: str
    goals: List[FinancialGoal] = field(default_factory=list)
    preferred_assets: List[str] = field(default_factory=list)


def calculate_financial_health(user):
    monthly_surplus = (
        user.monthly_income
        - user.monthly_expenses
        - user.monthly_emi
    )

    if user.monthly_income > 0:
        savings_rate = (monthly_surplus / user.monthly_income) * 100
        debt_to_income = (user.monthly_emi / user.monthly_income) * 100
    else:
        savings_rate = 0
        debt_to_income = 0

    if user.monthly_expenses > 0:
        emergency_months = user.current_savings / user.monthly_expenses
    else:
        emergency_months = 0

    savings_score = min(max(savings_rate / 20 * 30, 0), 30)
    debt_score = min(max((1 - debt_to_income / 50) * 20, 0), 20)
    emergency_score = min((emergency_months / 6) * 25, 25)
    investment_score = min(
        (user.existing_investments / max(user.monthly_income * 12, 1)) * 25,
        25
    )

    financial_health_score = (
        savings_score + debt_score + emergency_score + investment_score
    )

    return {
        "monthly_surplus": round(monthly_surplus, 2),
        "savings_rate": round(savings_rate, 2),
        "debt_to_income": round(debt_to_income, 2),
        "emergency_months": round(emergency_months, 2),
        "financial_health_score": round(min(financial_health_score, 100), 2)
    }


def calculate_risk_profile(
    user,
    investment_horizon_years,
    max_loss_tolerance,
    risk_knowledge
):
    score = 0

    if user.age < 30:
        score += 20
    elif user.age < 40:
        score += 16
    elif user.age < 50:
        score += 12
    elif user.age < 60:
        score += 8
    else:
        score += 4

    if investment_horizon_years >= 15:
        score += 25
    elif investment_horizon_years >= 10:
        score += 20
    elif investment_horizon_years >= 5:
        score += 14
    elif investment_horizon_years >= 3:
        score += 8
    else:
        score += 3

    if max_loss_tolerance >= 30:
        score += 25
    elif max_loss_tolerance >= 20:
        score += 20
    elif max_loss_tolerance >= 10:
        score += 12
    else:
        score += 5

    experience_scores = {
        "beginner": 5,
        "some experience": 10,
        "experienced": 15
    }
    score += experience_scores.get(user.investment_experience.lower(), 5)

    tolerance_scores = {
        "low": 5,
        "moderate": 10,
        "high": 15
    }
    score += tolerance_scores.get(user.risk_tolerance.lower(), 10)

    health = calculate_financial_health(user)

    if health["financial_health_score"] >= 75:
        score += 10
    elif health["financial_health_score"] >= 50:
        score += 5

    score = min(score, 100)

    if score < 30:
        profile = "Conservative"
    elif score < 50:
        profile = "Moderately Conservative"
    elif score < 70:
        profile = "Moderate"
    elif score < 85:
        profile = "Moderately Aggressive"
    else:
        profile = "Aggressive"

    return {
        "risk_score": score,
        "risk_profile": profile,
        "investment_horizon_years": investment_horizon_years,
        "max_loss_tolerance": max_loss_tolerance,
        "risk_knowledge": risk_knowledge
    }


def calculate_required_sip(target_amount, current_amount, years, annual_return):
    months = years * 12
    monthly_rate = annual_return / 12

    future_current_amount = (
        current_amount * (1 + monthly_rate) ** months
    )

    future_gap = target_amount - future_current_amount

    if future_gap <= 0:
        return {
            "target_amount": target_amount,
            "future_value_current_amount": round(future_current_amount, 2),
            "future_gap": 0,
            "required_monthly_sip": 0
        }

    required_sip = (
        future_gap * monthly_rate
        / ((1 + monthly_rate) ** months - 1)
    )

    return {
        "target_amount": target_amount,
        "future_value_current_amount": round(future_current_amount, 2),
        "future_gap": round(future_gap, 2),
        "required_monthly_sip": round(required_sip, 2)
    }


def calculate_goal_allocation(risk_profile, goal_years):
    risk_equity = {
        "Conservative": 25,
        "Moderately Conservative": 40,
        "Moderate": 55,
        "Moderately Aggressive": 65,
        "Aggressive": 75
    }

    max_equity = risk_equity.get(risk_profile, 55)

    if goal_years < 1:
        allocation = {"equity": 0, "debt": 70, "gold": 5, "cash": 25}
    elif goal_years < 3:
        allocation = {
            "equity": min(max_equity, 15),
            "debt": 65, "gold": 10, "cash": 10
        }
    elif goal_years < 5:
        allocation = {
            "equity": min(max_equity, 30),
            "debt": 50, "gold": 10, "cash": 10
        }
    elif goal_years < 10:
        allocation = {
            "equity": min(max_equity, 50),
            "debt": 35, "gold": 10, "cash": 5
        }
    else:
        equity = max_equity
        debt = 15
        gold = 5
        cash = 100 - equity - debt - gold
        allocation = {
            "equity": equity, "debt": debt,
            "gold": gold, "cash": cash
        }

    return allocation


def check_goal_feasibility(required_monthly_sip, available_monthly_surplus):
    if required_monthly_sip <= available_monthly_surplus:
        status = "Feasible"
    else:
        status = "Not Feasible"

    surplus_after_goal = available_monthly_surplus - required_monthly_sip

    if available_monthly_surplus > 0:
        utilization = (
            required_monthly_sip / available_monthly_surplus
        ) * 100
    else:
        utilization = 100 if required_monthly_sip > 0 else 0

    return {
        "status": status,
        "surplus_after_goal": round(surplus_after_goal, 2),
        "surplus_utilization": round(utilization, 2)
    }


def analyze_goal_scenarios(
    target_amount,
    current_amount,
    years,
    scenarios=None
):
    if scenarios is None:
        scenarios = {
            "Conservative": 0.07,
            "Base": 0.10,
            "Optimistic": 0.12
        }

    results = []

    for name, annual_return in scenarios.items():
        result = calculate_required_sip(
            target_amount=target_amount,
            current_amount=current_amount,
            years=years,
            annual_return=annual_return
        )

        results.append({
            "scenario": name,
            "annual_return": annual_return * 100,
            "required_monthly_sip": result["required_monthly_sip"]
        })

    return results


def evaluate_goal(
    user,
    goal,
    risk_profile,
    investment_capacity,
    scenarios=None
):
    base_result = calculate_required_sip(
        target_amount=goal.target_amount,
        current_amount=goal.current_amount,
        years=goal.years,
        annual_return=0.10
    )

    required_sip = base_result["required_monthly_sip"]

    feasibility = check_goal_feasibility(
        required_monthly_sip=required_sip,
        available_monthly_surplus=investment_capacity
    )

    allocation = calculate_goal_allocation(
        risk_profile=risk_profile,
        goal_years=goal.years
    )

    scenario_results = analyze_goal_scenarios(
        target_amount=goal.target_amount,
        current_amount=goal.current_amount,
        years=goal.years,
        scenarios=scenarios
    )

    return {
        "goal": goal.name,
        "priority": goal.priority,
        "target_amount": goal.target_amount,
        "current_amount": goal.current_amount,
        "years": goal.years,
        "required_monthly_sip": required_sip,
        "investment_capacity": investment_capacity,
        "surplus_after_goal": feasibility["surplus_after_goal"],
        "surplus_utilization": feasibility["surplus_utilization"],
        "status": feasibility["status"],
        "allocation": allocation,
        "scenarios": scenario_results
    }


def validate_risk_profile(
    stated_risk_tolerance,
    calculated_risk_profile,
    risk_score
):
    tolerance_map = {"low": 1, "moderate": 2, "high": 3}
    profile_map = {
        "Conservative": 1,
        "Moderately Conservative": 1,
        "Moderate": 2,
        "Moderately Aggressive": 3,
        "Aggressive": 3
    }

    stated_level = tolerance_map.get(stated_risk_tolerance.lower(), 2)
    calculated_level = profile_map.get(calculated_risk_profile, 2)

    difference = abs(stated_level - calculated_level)

    if difference == 0:
        status = "Aligned"
    elif difference == 1:
        status = "Review Recommended"
    else:
        status = "Review Required"

    if (
        calculated_risk_profile in ["Aggressive", "Moderately Aggressive"]
        and risk_score >= 80
    ):
        experience_flag = "High-risk profile with limited experience"
    else:
        experience_flag = "No major experience conflict"

    return {
        "stated_risk_tolerance": stated_risk_tolerance,
        "calculated_risk_profile": calculated_risk_profile,
        "risk_score": risk_score,
        "status": status,
        "experience_flag": experience_flag
    }


def user_to_dict(user):
    return {
        "age": user.age,
        "monthly_income": user.monthly_income,
        "monthly_expenses": user.monthly_expenses,
        "dependents": user.dependents,
        "current_savings": user.current_savings,
        "existing_investments": user.existing_investments,
        "monthly_emi": user.monthly_emi,
        "risk_tolerance": user.risk_tolerance,
        "investment_experience": user.investment_experience,
        "investment_horizon_years": 15,
        "max_loss_tolerance": 20,
        "risk_knowledge": "basic"
    }


def build_financial_plan(user, goals):
    user_dict = user_to_dict(user)

    monthly_surplus = (
        user.monthly_income
        - user.monthly_expenses
        - user.monthly_emi
    )

    savings_rate = (
        monthly_surplus / user.monthly_income * 100
        if user.monthly_income > 0 else 0
    )

    debt_to_income = (
        user.monthly_emi / user.monthly_income * 100
        if user.monthly_income > 0 else 0
    )

    emergency_target_months = 6
    emergency_target_amount = (
        user.monthly_expenses * emergency_target_months
    )

    current_emergency_months = (
        user.current_savings / user.monthly_expenses
        if user.monthly_expenses > 0 else 0
    )

    emergency_gap = max(
        0,
        emergency_target_amount - user.current_savings
    )

    emergency_monthly_contribution = min(2500, emergency_gap)

    investment_capacity = max(
        0,
        monthly_surplus - emergency_monthly_contribution
    )

    risk_result = calculate_risk_profile(
        user,
        user_dict["investment_horizon_years"],
        user_dict["max_loss_tolerance"],
        user_dict["risk_knowledge"]
    )

    risk_validation = validate_risk_profile(
        stated_risk_tolerance=user.risk_tolerance,
        calculated_risk_profile=risk_result["risk_profile"],
        risk_score=risk_result["risk_score"]
    )

    analyzed_goals = []

    for goal_data in goals:
        goal = goal_data if isinstance(goal_data, FinancialGoal) else FinancialGoal(
            name=goal_data["name"],
            target_amount=goal_data["target_amount"],
            current_amount=goal_data["current_amount"],
            years=goal_data["years"],
            priority=goal_data["priority"]
        )

        evaluation = evaluate_goal(
            user=user,
            goal=goal,
            risk_profile=risk_result["risk_profile"],
            investment_capacity=investment_capacity
        )
        analyzed_goals.append(evaluation)

    total_required_sip = sum(
        goal["required_monthly_sip"] for goal in analyzed_goals
    )

    overall_gap = investment_capacity - total_required_sip
    overall_status = (
        "Fully Funded"
        if total_required_sip <= investment_capacity
        else "Funding Gap"
    )

    priority_order = {"High": 1, "Medium": 2, "Low": 3}

    sorted_goals = sorted(
        analyzed_goals,
        key=lambda x: priority_order.get(x["priority"], 3)
    )

    remaining_capacity = investment_capacity
    priority_allocations = []

    for goal in sorted_goals:
        required = goal["required_monthly_sip"]
        allocated = min(required, remaining_capacity)
        unfunded = max(0, required - allocated)

        if allocated >= required:
            funding_status = "Fully Funded"
        elif allocated > 0:
            funding_status = "Partially Funded"
        else:
            funding_status = "Deferred"

        priority_allocations.append({
            "goal": goal["goal"],
            "priority": goal["priority"],
            "required_sip": required,
            "allocated_sip": allocated,
            "unfunded_amount": unfunded,
            "funding_status": funding_status
        })

        remaining_capacity -= allocated

    return {
        "user_profile": user_dict,
        "financial_health": calculate_financial_health(user),
        "risk_profile": risk_result,
        "risk_validation": risk_validation,
        "emergency_fund": {
            "target_months": emergency_target_months,
            "current_months": current_emergency_months,
            "target_amount": emergency_target_amount,
            "current_savings": user.current_savings,
            "gap": emergency_gap,
            "status": "Fully Funded" if emergency_gap == 0 else "Partially Funded"
        },
        "investment_capacity": {
            "monthly_surplus": monthly_surplus,
            "emergency_monthly_contribution": emergency_monthly_contribution,
            "monthly_investment_capacity": investment_capacity
        },
        "goal_analysis": {
            "goals": analyzed_goals,
            "total_required_sip": round(total_required_sip, 2),
            "investment_capacity": round(investment_capacity, 2),
            "overall_gap": round(overall_gap, 2),
            "overall_status": overall_status
        },
        "priority_based_plan": {
            "allocations": priority_allocations,
            "remaining_capacity": round(remaining_capacity, 2)
        }
    }


def generate_financial_plan(
    age,
    monthly_income,
    monthly_expenses,
    monthly_emi,
    current_savings,
    existing_investments,
    risk_tolerance,
    investment_experience,
    goals
):
    user = UserFinancialProfile(
        age=age,
        monthly_income=monthly_income,
        monthly_expenses=monthly_expenses,
        monthly_emi=monthly_emi,
        current_savings=current_savings,
        existing_investments=existing_investments,
        dependents=1,
        risk_tolerance=risk_tolerance,
        investment_experience=investment_experience,
        goals=goals,
        preferred_assets=["SIP", "Mutual Funds", "Equity", "Debt"]
    )

    return build_financial_plan(user=user, goals=goals)


def generate_local_advisor_report(financial_plan):
    health = financial_plan["financial_health"]
    risk = financial_plan["risk_profile"]
    validation = financial_plan["risk_validation"]
    emergency = financial_plan["emergency_fund"]
    capacity = financial_plan["investment_capacity"]
    goals = financial_plan["goal_analysis"]["goals"]
    priority_plan = financial_plan["priority_based_plan"]

    report = []
    report.append("## 1. Financial Health Summary")
    report.append(
        f"Monthly surplus: ₹{health['monthly_surplus']:,.0f} | "
        f"Savings rate: {health['savings_rate']:.1f}% | "
        f"Financial health score: {health['financial_health_score']:.2f}/100"
    )

    report.append("\n## 2. Risk Profile")
    report.append(
        f"Calculated risk profile: {risk['risk_profile']} | "
        f"Risk score: {risk['risk_score']}."
    )
    if validation["status"] != "Aligned":
        report.append(
            f"Risk review recommended: stated tolerance is "
            f"{validation['stated_risk_tolerance']}, while calculated profile is "
            f"{validation['calculated_risk_profile']}."
        )
    report.append(f"Experience flag: {validation['experience_flag']}.")

    report.append("\n## 3. Emergency Fund")
    report.append(
        f"Current coverage: {emergency['current_months']:.2f} months | "
        f"Target: {emergency['target_months']} months | "
        f"Gap: ₹{emergency['gap']:,.0f}"
    )

    report.append("\n## 4. Investment Capacity")
    report.append(
        f"Monthly investment capacity: "
        f"₹{capacity['monthly_investment_capacity']:,.0f}"
    )

    report.append("\n## 5. Goal-wise Plan")
    for goal in goals:
        report.append(
            f"{goal['goal']} ({goal['priority']}): "
            f"SIP ₹{goal['required_monthly_sip']:,.2f} | "
            f"Status: {goal['status']}"
        )

    report.append("\n## 6. Priority-Based Funding")
    for allocation in priority_plan["allocations"]:
        report.append(
            f"{allocation['goal']}: "
            f"Required ₹{allocation['required_sip']:,.2f} | "
            f"Allocated ₹{allocation['allocated_sip']:,.2f} | "
            f"Unfunded ₹{allocation['unfunded_amount']:,.2f} | "
            f"{allocation['funding_status']}"
        )

    report.append("\n## 7. Overall Plan")
    analysis = financial_plan["goal_analysis"]
    report.append(
        f"Total required SIP: ₹{analysis['total_required_sip']:,.2f} | "
        f"Investment capacity: ₹{analysis['investment_capacity']:,.2f} | "
        f"Overall status: {analysis['overall_status']}"
    )

    return "\n".join(report)
