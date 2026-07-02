from dataclasses import dataclass, field

from app.parser import (

    extract_role,

    extract_skills,

    extract_experience

)


@dataclass
class IntentResult:

    intent: str

    role: str | None = None

    skills: list[str] = field(

        default_factory=list

    )

    experience: int | None = None


COMPARE_WORDS = [

    "difference",

    "compare",

    "comparison",

    "versus",

    "vs",

    "better than"

]


REFINE_WORDS = [

    "actually",

    "instead",

    "also",

    "add",

    "include",

    "change",

    "update"

]


OFFTOPIC_WORDS = [

    "weather",

    "movie",

    "sports",

    "cricket",

    "football",

    "politics"

]


def is_offtopic(text):

    return any(

        word in text

        for word in OFFTOPIC_WORDS

    )


def is_vague(text):

    return len(

        text.split()

    ) < 3


def detect_intent(query):

    text = query.lower()

    if any(

        word in text

        for word in COMPARE_WORDS

    ):

        intent = "compare"

    elif any(

        word in text

        for word in REFINE_WORDS

    ):

        intent = "refine"

    elif is_offtopic(text):

        intent = "refuse"

    elif is_vague(text):

        intent = "clarify"

    else:

        intent = "recommend"

    return IntentResult(

        intent=intent,

        role=extract_role(

            query

        ),

        skills=extract_skills(

            query

        ),

        experience=extract_experience(

            query

        )

    )