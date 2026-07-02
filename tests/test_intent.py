import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.intent import detect_intent


queries = [

    "Hiring Java developer 4 years",

    "Looking for Python engineer with 5 years experience",

    "Need AWS architect",

    "Need React developer",

    "Need DevOps engineer",

    "Actually I need QA manager",

    "Compare analyst and designer",

    "Java vs Python",

    "Need Machine Learning scientist",

    "Need Kubernetes administrator"

]


for q in queries:

    result = detect_intent(q)

    print()

    print("Query:", q)

    print(

        result

    )