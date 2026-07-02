import re


ROLE_KEYWORDS = [

    "developer",
    "engineer",
    "manager",
    "analyst",
    "designer",
    "architect",
    "scientist",
    "consultant",
    "administrator",
    "specialist",
    "lead",
    "director",
    "tester"

]


SKILLS = [

    "java",
    "python",
    "javascript",
    "typescript",

    "react",
    "angular",
    "vue",

    "node",

    "spring",

    "django",

    "flask",

    "aws",
    "azure",
    "gcp",

    "docker",

    "kubernetes",

    "terraform",

    "ansible",

    "devops",

    "qa",

    "selenium",

    "cypress",

    "sql",

    "postgresql",

    "mysql",

    "mongodb",

    "redis",

    "kafka",

    "spark",

    "hadoop",

    "machine learning",

    "ai",

    "data science"

    "golang"

    "rust"

    "c++"

    "c#"

    "scala"

    "spark"

    "hadoop"

    "airflow"

    "snowflake"

    "pytorch"

    "tensorflow"

    "llm"

    "langchain"

    "genai"

    "redis"

    "elasticsearch"

    "graphql"

    "fastapi"

    "springboot"

    "docker"

    "terraform"
]
DISPLAY_NAMES = {
    "aws": "AWS",
    "gcp": "GCP",
    "qa": "QA",
    "devops": "DevOps",
    "sql": "SQL",
    "postgresql": "PostgreSQL",
    "mysql": "MySQL",
    "kubernetes": "Kubernetes",
    "javascript": "JavaScript",
    "typescript": "TypeScript",
    "react": "React",
    "node": "Node.js",
}
patterns = [

r'(\d+)\s*\+\s*years?',

r'(\d+)\s*years?',

r'(\d+)\s*yrs?',

r'(\d+)\s*y\b'

]
SENIORITY = [

"intern",

"junior",

"mid",

"senior",

"lead",

"principal",

"staff"

]


def extract_experience(text):
    text = text.lower()

    # Seniority keywords mapped to representative years
    keywords = {
        "graduate": 1,
        "intern": 1,
        "entry-level": 1,
        "entry": 1,
        "junior": 2,
        "mid-level": 4,
        "mid": 4,
        "senior": 8,
        "lead": 10
    }

    # 1. Check exact keywords first
    for k, v in keywords.items():
        if re.search(r'\b' + re.escape(k) + r'\b', text):
            return v

    # 2. Check for numeric patterns like "2+", "5 years", "3 yrs", etc.
    m = re.search(r'(\d+)\s*(?:\+|years?|yrs?|y\b)?', text)
    if m:
        return int(m.group(1))

    return None


def extract_skills(text):

    text = text.lower()

    skills = []

    for skill in SKILLS:

        if skill in text:

            skills.append(skill.title())

    return skills


def extract_role(text):

    text = text.lower()

    for skill in SKILLS:

        for role in ROLE_KEYWORDS:

            phrase = f"{skill} {role}"

            if phrase in text:

                return phrase.title()

    for role in ROLE_KEYWORDS:

        if role in text:

            return role.title()

    return None


def parse_query(text):

    return {

        "role":

            extract_role(text),

        "skills":

            extract_skills(text),

        "experience":

            extract_experience(text)

    }