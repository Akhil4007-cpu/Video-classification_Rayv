def final_decision(intent_score,
                   fast_suspicious,
                   has_safe_context=False,
                   low=0.3,
                   high=0.6):

    explanation = {
        "intent_score": float(intent_score),
        "fast_stage_flag": fast_suspicious
    }

    # 🚨 Strong UNSAFE
    if intent_score >= high:
        explanation["reason"] = "High sustained violent intent"
        return "UNSAFE", explanation

    # 🟢 STAGE 5 — CONTEXT OVERRIDE
    if intent_score < 0.1 and has_safe_context:
        explanation["reason"] = "Clear safe context (cooking / daily life)"
        return "SAFE", explanation

    # ⚠️ Ambiguous
    if intent_score >= low or fast_suspicious:
        explanation["reason"] = "Ambiguous or suspicious signals"
        return "REVIEW", explanation

    # ✅ Safe
    explanation["reason"] = "No sustained risk detected"
    return "SAFE", explanation
