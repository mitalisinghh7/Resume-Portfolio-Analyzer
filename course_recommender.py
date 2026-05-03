def get_course_recommendations(missing_skills, role):
    """Return courses for each missing skill"""

    SKILL_COURSES = {
        "Python": [
            {
                "title": "Scientific Computing with Python",
                "platform": "freeCodeCamp",
                "link": "https://www.freecodecamp.org/learn/"
            }
        ],
        "Java": [
            {
                "title": "Java Programming",
                "platform": "Coursera",
                "link": "https://www.coursera.org/"
            }
        ],
        "SQL": [
            {
                "title": "Relational Database Certification",
                "platform": "freeCodeCamp",
                "link": "https://www.freecodecamp.org/learn/"
            }
        ],
        "Django": [
            {
                "title": "Django Web Development",
                "platform": "freeCodeCamp",
                "link": "https://www.freecodecamp.org/learn/"
            }
        ],
        "Flask": [
            {
                "title": "Flask Tutorial",
                "platform": "YouTube",
                "link": "https://www.youtube.com/"
            }
        ],
        "Machine Learning": [
            {
                "title": "Machine Learning with Python",
                "platform": "freeCodeCamp",
                "link": "https://www.freecodecamp.org/learn/"
            }
        ],
        "JavaScript": [
            {
                "title": "JavaScript Certification",
                "platform": "freeCodeCamp",
                "link": "https://www.freecodecamp.org/learn/"
            }
        ],
        "React": [
            {
                "title": "React Course",
                "platform": "freeCodeCamp",
                "link": "https://www.freecodecamp.org/learn/"
            }
        ],
        "Node.js": [
            {
                "title": "Node.js Course",
                "platform": "freeCodeCamp",
                "link": "https://www.freecodecamp.org/learn/"
            }
        ],
        "MongoDB": [
            {
                "title": "MongoDB Basics",
                "platform": "MongoDB",
                "link": "https://www.mongodb.com/"
            }
        ],
        "HTML": [
            {
                "title": "HTML Course",
                "platform": "freeCodeCamp",
                "link": "https://www.freecodecamp.org/learn/"
            }
        ],
        "CSS": [
            {
                "title": "CSS Course",
                "platform": "freeCodeCamp",
                "link": "https://www.freecodecamp.org/learn/"
            }
        ],
        "Excel": [
            {
                "title": "Excel Tutorial",
                "platform": "YouTube",
                "link": "https://www.youtube.com/"
            }
        ]
    }

    recommendations = {}

    for skill in missing_skills:
        if skill in SKILL_COURSES:
            recommendations[skill] = SKILL_COURSES[skill]
        else:
            # ✅ SMART FALLBACK (skill + role based search)
            search_query = f"{skill} {role} course".replace(" ", "+")

            recommendations[skill] = [
                {
                    "title": f"Learn {skill} for {role}",
                    "platform": "YouTube",
                    "link": f"https://www.youtube.com/results?search_query={search_query}"
                },
                {
                    "title": f"{skill} Full Course Resources",
                    "platform": "Google",
                    "link": f"https://www.google.com/search?q={search_query}"
                }
            ]

    return recommendations


def get_role_course(role):
    """Return one complete course for the selected role"""

    ROLE_COURSES = {
        "Backend Developer": {
            "title": "Backend Development Full Course",
            "link": "https://www.youtube.com/"
        },
        "Full Stack Developer": {
            "title": "Full Stack Web Development",
            "link": "https://www.freecodecamp.org/learn/"
        },
        "Data Scientist": {
            "title": "Data Science Full Course",
            "link": "https://www.freecodecamp.org/learn/"
        },
        "Machine Learning Engineer": {
            "title": "Machine Learning Full Course",
            "link": "https://www.freecodecamp.org/learn/"
        }
    }

    return ROLE_COURSES.get(role, None)