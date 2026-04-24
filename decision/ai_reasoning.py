def generate_explanation(patient, fire_zones):
    explanation = {
        "patient_id": patient["id"],
        "reasoning": [],
        "priority_level": "medium"
    }

    # Risk reasoning
    if patient["risk"] > 20:
        explanation["reasoning"].append("High fire risk proximity")

    # Mobility reasoning
    if patient["type"] == "ICU":
        explanation["reasoning"].append("Immobile (ICU patient)")

    # Final label
    if patient["priority_score"] > 40:
        explanation["priority_level"] = "critical"
    elif patient["priority_score"] > 30:
        explanation["priority_level"] = "high"

    return explanation