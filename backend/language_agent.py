def language_agent(question=""):

    question_lower = question.lower()

    tamil_indicators = [
        "தமிழ்",
        "என்ன",
        "எப்படி",
        "கடல்",
        "மீன்",
        "மீன்பிடி",
        "வானிலை",
        "காற்று",
        "அலை",
        "கடல் நிலை"
    ]

    detected_language = "English"

    for word in tamil_indicators:
        if word in question or word in question_lower:
            detected_language = "Tamil"
            break

    return {
        "agent": "Language Agent",
        "status": "SUCCESS",
        "detected_language": detected_language,
        "supported_languages": [
            "English",
            "Tamil"
        ],
        "question": question,
        "message": (
            "ORCA can process marine questions in English and Tamil."
        )
    }