"""tools.clinical_tools — outils Needle certifiés (domaine clinique/émotionnel).

Cohérent avec le corpus EmoContext (SemEval 2019, dialogues patient-soignant).
Ces outils sont déclarés à Needle : RATIS décide QUAND les appeler (via le
router du bridge), Needle exécute COMMENT (tool-calling structuré + JSON).
"""
from __future__ import annotations

import needle


@needle.tool
def get_patient_status(patient_id: str):
    """Assess a patient's current emotional and physical status.

    Args:
        patient_id: the unique identifier of the patient
    """
    db = {
        "123": {"patient_id": "123", "stress_level": 0.8, "mood": "anxious",
                "status": "needs reassurance"},
        "456": {"patient_id": "456", "stress_level": 0.2, "mood": "calm",
                "status": "stable"},
        "789": {"patient_id": "789", "stress_level": 0.6, "mood": "sad",
                "status": "monitoring"},
    }
    return db.get(patient_id, {"patient_id": patient_id, "stress_level": 0.5,
                               "mood": "unknown", "status": "no data"})


@needle.tool
def check_resource_availability(resource: str):
    """Check if a care resource (room, therapist, bed) is available.

    Args:
        resource: the name of the resource to check (e.g. 'therapy room', 'bed 4')
    """
    return {"resource": resource, "available": True,
            "next_slot": "2026-08-14 15:00", "capacity": 1}


@needle.tool
def log_emotion_observation(patient_id: str, emotion: str, intensity: float):
    """Log an emotional observation for a patient in the care record.

    Args:
        patient_id: the unique identifier of the patient
        emotion: the observed emotion (happy, sad, angry, calm, anxious)
        intensity: the intensity from 0.0 to 1.0
    """
    return {"logged": True, "patient_id": patient_id,
            "emotion": emotion, "intensity": intensity,
            "timestamp": "2026-08-14T21:46:00Z"}


DEFAULT_TOOLS = [get_patient_status, check_resource_availability, log_emotion_observation]
