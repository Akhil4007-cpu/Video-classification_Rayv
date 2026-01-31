def aggregate_risks(risks):
    """
    Aggregate risk scores from all policies.
    Action model has been removed - using BLIP-1 instead.
    """
    max_risk = 0.0
    category = None
    reasons = []

    for k, v in risks.items():
        if v["score"] > max_risk:
            max_risk = v["score"]
            category = k
            reasons = v["reasons"]

    if max_risk < 0.2:
        return "SAFE", {
            "max_risk": 0.0,
            "category": None,
            "reasons": ["No harmful signals detected"]
        }

    if max_risk < 0.6:
        return "REVIEW", {
            "max_risk": round(max_risk, 2),
            "category": category,
            "reasons": reasons
        }

    return "UNSAFE", {
        "max_risk": round(max_risk, 2),
        "category": category,
        "reasons": reasons
    }
