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

    patterns = [

        r'(\d+)\s*years?',

        r'(\d+)\s*yrs?',

        r'(\d+)\s*y\b'

    ]

    for pattern in patterns:

        match = re.search(pattern, text)

        if match:

            return int(match.group(1))

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