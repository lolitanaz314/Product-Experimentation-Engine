def make_decision(
    ab_results,
    srm_results,
    guardrail_results,
    segmentation_df,
    alpha=0.05
):
    """
    Produces a launch recommendation.
    """

    if not srm_results["srm_passed"]:
        return {
            "decision": "hold",
            "reason": "Sample ratio mismatch detected. Randomization integrity may be broken."
        }

    if ab_results["p_value"] > alpha:
        return {
            "decision": "extend_test",
            "reason": "Primary metric is not statistically significant yet."
        }

    if ab_results["lift"] <= 0:
        return {
            "decision": "do_not_ship",
            "reason": "Primary metric did not improve."
        }

    guardrail_bad = False
    bad_guardrails = []

    for metric_name, result in guardrail_results.items():
        if result["status"] == "worse":
            guardrail_bad = True
            bad_guardrails.append(metric_name)

    negative_segments = segmentation_df[segmentation_df["lift"] < 0]

    if guardrail_bad and len(negative_segments) > 0:
        return {
            "decision": "iterate",
            "reason": (
                f"Primary metric improved, but guardrails worsened ({', '.join(bad_guardrails)}) "
                f"and some segments underperformed."
            )
        }

    if len(negative_segments) > 0:
        return {
            "decision": "partial_rollout",
            "reason": "Overall result is positive, but some user segments show negative lift."
        }

    if guardrail_bad:
        return {
            "decision": "iterate",
            "reason": f"Primary metric improved, but guardrails worsened ({', '.join(bad_guardrails)})."
        }

    return {
        "decision": "ship",
        "reason": "Primary metric improved significantly and no major guardrail/segment issues were detected."
    }
