"""
Pre-configured dummy business case for testing the Quorum multi-agent boardroom swarm.
Labelled explicitly as a testing fixture.
"""

from .business_case import BusinessCase

DUMMY_BUSINESS_CASE = BusinessCase(
    title="[TEST CASE] AeroCharge Mobility: Fleet Charging Hubs vs Enterprise SaaS Expansion",
    problem=(
        "AeroCharge Mobility is experiencing slowing growth in its legacy commercial charging hardware sales "
        "(declined 12% YoY). The company has $15M in available capital and must choose between two distinct "
        "strategic expansion vectors to achieve sustainable profitability within 18 months, while competition "
        "is intensifying from well-funded incumbent energy providers."
    ),
    objective=(
        "Select and commit to one primary growth vector for the next 18 months that maximizes return on capital, "
        "reaches positive operating cash flow within 12 months, and establishes a defensible competitive moat."
    ),
    context=(
        "AeroCharge is a Series B mobility infrastructure firm with 120 employees. The executive board is split "
        "between two strategic paths: \n"
        "1. Strategy Alpha (Asset-Heavy): Construct proprietary Ultra-Fast Charging Hubs in 8 Tier-1 urban logistics "
        "corridors for last-mile delivery fleets (Amazon, FedEx, DHL).\n"
        "2. Strategy Beta (Asset-Light SaaS): Pivot to an Enterprise Charging Management Software platform (SaaS) "
        "licensing AI-driven dynamic load balancing and billing software to existing third-party fleet operators."
    ),
    constraints=[
        "Total capital expenditure budget capped strictly at $15M for Phase 1.",
        "Must reach EBITDA break-even within 14 months.",
        "Engineering team is currently 35 engineers with strong IoT/firmware skills but limited B2B enterprise software sales talent.",
        "Regulatory grid connection lead time for physical charging hubs currently averages 6-9 months."
    ],
    available_data={
        "financial_metrics": {
            "current_cash_reserves": "$15.0M",
            "monthly_cash_burn": "$450K",
            "hardware_gross_margin": "18%",
            "projected_saas_gross_margin": "78%",
            "projected_hub_gross_margin": "42%"
        },
        "strategy_alpha_hub_projections": {
            "capex_per_hub": "$1.4M (8 hubs = $11.2M total CapEx)",
            "ramp_up_time": "9-12 months per hub",
            "projected_year1_revenue": "$6.8M",
            "projected_year2_revenue": "$18.5M",
            "key_risk": "Grid delay and high upfront capital lock-in"
        },
        "strategy_beta_saas_projections": {
            "rd_and_sales_investment": "$4.5M",
            "target_annual_contract_value": "$120K / enterprise client",
            "sales_cycle": "6-9 months",
            "projected_year1_revenue": "$3.2M",
            "projected_year2_revenue": "$12.0M",
            "key_risk": "Intense software competition from ChargePoint and Siemens, low existing software sales pipeline"
        },
        "customer_discovery": {
            "interviews_conducted": "24 fleet managers",
            "hub_demand_sentiment": "85% urgent demand for dedicated overnight depot hubs",
            "software_demand_sentiment": "60% already using legacy software or unwilling to switch without bundled hardware"
        }
    },
    assumptions=[
        "Electricity grid connection approvals in target Tier-1 cities will not exceed 9 months.",
        "Fleet EV transition rate in target zones will increase by at least 25% over the next 18 months.",
        "Enterprise SaaS customer acquisition cost (CAC) will remain under $35K per customer.",
        "AeroCharge can cross-sell SaaS to at least 30% of its existing hardware client base."
    ]
)
