"""
Simple summaries of the codeHive 2026 curriculum.
Used only when the user turns on "Base interview on codeHive curriculum".
"""

CURRICULUM_TRACKS = {
    "frontend": {
        "name": "Frontend Development",
        "topics": (
            "How the web works, HTML, CSS, JavaScript basics, responsive design, "
            "accessibility, React and Next.js, TypeScript, JSX, state and hooks, "
            "data fetching, forms, testing, deployment, and using Firebase/Genkit for AI UIs."
        ),
    },
    "backend": {
        "name": "Backend Development",
        "topics": (
            "Python basics, Linux, OOP, files and dates, FastAPI, REST APIs, "
            "Pydantic validation, PostgreSQL, SQLAlchemy, auth (JWT, hashing), "
            "testing, layered architecture (services, repositories, routers), "
            "AI integration with Gemini/OpenAI, agents, Docker, CI/CD, and cloud basics."
        ),
    },
    "data_ml": {
        "name": "Data & Machine Learning",
        "topics": (
            "Problem solving, algorithms and data structures, SQL and data modeling, "
            "Pandas/NumPy, EDA, supervised vs unsupervised learning, classic ML models, "
            "metrics, AI agents, RAG, vector stores, and basic data engineering."
        ),
    },
    "iot": {
        "name": "Internet of Things (IoT)",
        "topics": (
            "Electronics basics, Arduino, sensors and actuators, ESP32, WiFi, MQTT, "
            "cloud integration, cameras, cellular, LoRa, GPS/geofencing, 3D design, "
            "and RTOS/OTA concepts."
        ),
    },
    "mobile": {
        "name": "Mobile Development",
        "topics": (
            "Dart basics, Flutter widgets and layouts, state management, navigation, "
            "forms, networking, local storage, device features (camera, GPS, biometrics), "
            "testing, Gemini in Flutter, and app publishing."
        ),
    },
    "product_management": {
        "name": "Product Management",
        "topics": (
            "Product roles and lifecycle, user needs, personas, user stories, Agile, "
            "prioritization, roadmapping, competitor analysis, AI products, metrics, "
            "compliance, and interview/job readiness for PMs."
        ),
    },
    "qa": {
        "name": "Quality Assurance (QA)",
        "topics": (
            "QA foundations, manual testing, test plans and cases, bug reports, "
            "Agile QA, risk-based testing, Playwright automation, API testing, "
            "CI/CD awareness, testing AI systems, and using AI to help with QA work."
        ),
    },
    "cyber_security": {
        "name": "Cyber Security",
        "topics": (
            "Secure software development, OWASP Top 10, web and mobile security, "
            "API exploits (BOLA, BFLA), cloud security, IAM, DevSecOps, SAST/DAST/SCA, "
            "and secure coding practices."
        ),
    },
    "product_design": {
        "name": "Product Design",
        "topics": (
            "Design and visual literacy, branding, UI design in Figma, packaging, "
            "web design best practices, micro-interactions, portfolio work, "
            "dashboards, and designing with/for AI."
        ),
    },
    "ux_research": {
        "name": "UX Research",
        "topics": (
            "UX research foundations, human-centered design, research methods, "
            "planning and ethics, interviews and surveys, analysis and synthesis, "
            "AI in UX research (with human validation), and communicating insights."
        ),
    },
}


def get_curriculum_context(track_key: str) -> str:
    """Return a short text block for the AI, or empty if track is unknown."""
    track = CURRICULUM_TRACKS.get(track_key)
    if not track:
        return ""
    return (
        f"codeHive track: {track['name']}\n"
        f"Main topics the student is learning: {track['topics']}\n"
        "Base your questions on these topics when the role fits. "
        "Stay practical and clear."
    )
