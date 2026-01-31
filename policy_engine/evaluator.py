from policies.violence import evaluate_violence
from policies.nudity import evaluate_nudity
from policies.accidents import evaluate_accidents
from policies.dangerous_activity import evaluate_dangerous_activity
from policies.self_harm import evaluate_self_harm
from policies.safe_overrides import apply_safe_overrides


def evaluate_policies(signals):
    """
    Evaluate all policies against signals.
    Action model has been removed - using BLIP-1 instead.
    """
    risks = {}

    for name, fn in [
        ("violence", evaluate_violence),
        ("nudity", evaluate_nudity),
        ("self_harm", evaluate_self_harm),
        ("accidents", evaluate_accidents),
        ("dangerous_activity", evaluate_dangerous_activity),
    ]:
        score, reasons = fn(signals)
        score, reasons = apply_safe_overrides(score, reasons, signals)
        risks[name] = {"score": score, "reasons": reasons}

    return risks
