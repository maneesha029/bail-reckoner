"""
Judge's-discretion indicators: flight risk and witness/evidence-influence risk.

This is intentionally a transparent, rule-based scorer - not a prediction
model. It never outputs a release/deny recommendation; it only surfaces
factors for a judge to weigh, matching how discretion is actually meant
to work under CrPC/BNSS. Every score comes with a reasoning_summary
listing exactly which factors fired, so it can be inspected and disputed
like any other input to a judicial decision.
"""

FLIGHT_RISK_FACTORS = {
    "no_fixed_address": 2,
    "no_local_ties": 1,
    "prior_absconding_history": 3,
    "passport_or_travel_docs_held": 2,
    "no_stable_employment": 1,
    "offense_max_sentence_months_ge_84": 1,  # 7+ years - higher-stakes flight incentive
}

WITNESS_INFLUENCE_FACTORS = {
    "victim_witness_known_to_accused": 2,
    "accused_in_position_of_authority_over_witness": 2,
    "prior_witness_tampering_allegation": 3,
    "case_stage_is_pre_charge_evidence_collection": 1,
    "co_accused_still_at_large": 1,
}


def _score(indicators: dict, weights: dict) -> tuple[int, list[str]]:
    total = 0
    fired = []
    for key, weight in weights.items():
        if indicators.get(key):
            total += weight
            fired.append(key)
    return total, fired


def _band(score: int, max_score: int) -> str:
    ratio = score / max_score if max_score else 0
    if ratio >= 0.5:
        return "high"
    if ratio >= 0.25:
        return "moderate"
    return "low"


def compute_discretion_indicators(case_id: str, indicators: dict) -> dict:
    """
    indicators: dict of boolean flags matching the keys in
    FLIGHT_RISK_FACTORS / WITNESS_INFLUENCE_FACTORS. Missing keys are
    treated as False (factor not present / not yet assessed), never as
    True - absence of information must never inflate a risk score.
    """
    flight_max = sum(FLIGHT_RISK_FACTORS.values())
    witness_max = sum(WITNESS_INFLUENCE_FACTORS.values())

    flight_score, flight_fired = _score(indicators, FLIGHT_RISK_FACTORS)
    witness_score, witness_fired = _score(indicators, WITNESS_INFLUENCE_FACTORS)

    return {
        "case_id": case_id,
        "flight_risk": {
            "band": _band(flight_score, flight_max),
            "score": flight_score,
            "max_score": flight_max,
            "factors_present": flight_fired,
        },
        "witness_influence_risk": {
            "band": _band(witness_score, witness_max),
            "score": witness_score,
            "max_score": witness_max,
            "factors_present": witness_fired,
        },
        "disclaimer": (
            "These are transparent, rule-based indicators for the judge's "
            "consideration under CrPC/BNSS discretion factors. This is not "
            "a recommendation to grant or deny bail, and does not replace "
            "judicial evaluation of the individual case."
        ),
    }
