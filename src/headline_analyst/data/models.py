from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Dict
from pydantic import BaseModel, Field

# ---------------- ENUMS -------------------------- #

# Possible bias types found in the framing of a headline
class Bias(Enum):
    POLITICAL = 1
    GENDER = 2
    CULTURAL = 3
    AGE = 4
    RELIGION = 5
    DISABILITY = 6
    STATEMENT = 7
    OMISSION = 8
    SENSATIONALISM = 9
    NEGATIVITY = 10
    SUBJECTIVE = 11
    ADHOMINEM = 12
    OPINION = 13

# For NER -> detect if an entity is the active subject of an action, passive, or just mentionned
class Agency(Enum):
    PASSIVE = 1
    ACTIVE = 2
    MENTIONNED = 3

# Generic Frames of the headline
# based on the research paper "The Power of Framing: How News Headlines Guide Search Behavior"
# + additional categories
class GenericFraming(Enum):
    CONFLICT = 1 # Conflic between actors, issues or interpretations
    GAME_STRATEGY = 2 # focuses on efforts of actors to achieve specific goals
    THEMATIC = 3 # centers on the substantive content of public concerns and issues
    HUMAN_INTEREST = 4 # narrates event from perspective of individuals affected by the issues
    EPISODIC = 5 # presents events without extensive context or connection to broader themes
    OTHER = 6


# Evaluative Focus : the perspective through which the topic is presented
class Focus(Enum):
    ECONOMIC = 1
    RESOURCES = 2
    MORALITY = 3
    FAIRNESS = 4
    LEGAL = 5
    POLICY = 6
    CRIME = 7
    SECURITY = 8
    HEALTH = 9
    QOL = 10
    CULTURAL_ID = 11
    PUBLIC_OPINION = 12
    POLITICAL = 13
    OTHER = 14

# Intent behind the headline 
class Genre(Enum):
    INFORMATIVE = 1
    INVESTIGATIVE = 2
    ANALYTIC = 3
    EDITORIAL = 4
    ENTERTAINMENT = 5
    OTHER = 6

# From the GoEmotions dataset : 28 emotion categories + neutral
class EmotionsEnum(Enum):
    ADMIRATION = 1
    AMUSEMENT = 2
    ANGER = 3
    ANNOYANCE = 4
    APPROVAL = 5
    CARING = 6
    CONFUSION = 7
    CURIOSITY = 8
    DESIRE = 9
    DISAPPOINTMENT= 10
    DISAPPROVAL = 11
    DISGUST = 12
    EMBARASSMENT = 13
    EXCITMENT = 14
    FEAR = 15
    GRATITUDE = 16
    GRIEF = 17
    JOY = 18
    LOVE = 19
    NERVOUSNESS = 20
    OPTIMISM = 21
    PRIDE = 22
    REALIZATION = 23
    RELIEF = 24
    REMORSE = 25
    SADNESS = 26
    SURPRISE = 27
    NEUTRAL = 28


# ---------------- DATA CLASSES -------------------- #

@dataclass(frozen=True) # make it immutable after creation
class Article:
    title: str
    source: str
    query_origin: str # which query retrieved this
    published_at: datetime | None = None
    url: str = ""
    description: str | None = None
    content: str | None = None

    def __str__(self):
        return f"{self.title}, source='{self.source}', query_origin='{self.query_origin}' - URL : {self.url}"
    
    def __repr__(self):
        return self.__str__()


@dataclass(frozen=True)
class Entity:
    name: str
    role: Agency

    def __str__(self):
        return f"{self.name}, role='{self.role.name}'"
    
    def __repr__(self):
        return self.__str__()


@dataclass(frozen=True)
class Emotion:
    label: EmotionsEnum
    score: float

    def __str__(self):
        return f"{self.label.name} (score : {self.score:.2f})"

    def __repr__(self):
        return self.__str__()


@dataclass
class Analysis:
    headline_index: int
    biases: Dict[Bias, int]  # Maps Enum to the 1-3 score
    agencies: List[Entity]
    frame: GenericFraming
    focus: List[Focus]
    genre: Genre
    tone_intensity: int # 1 - 5 score
    main_emotion: Emotion | None = None

    @classmethod
    def from_json(cls, data: dict):
        """Parses the Schema JSON format into an Analysis object."""

        return cls(
            headline_index=data['id'],
            
            biases = {Bias(int(k)): v for k, v in data['bias'].items()},
            agencies = [
                Entity(name=a['name'], role=Agency(a['role'])) 
                for a in data['agency']
            ],
            frame = GenericFraming(data['framing']),
            focus = [Focus(int(k)) for k in data['focus']],
            genre = Genre(data['genre']),
            tone_intensity=data['tone'],
            main_emotion=None
        )

# ------------------- CLASSES FOR THE FORMATTING OF JSON OUTPUTS FOR GEMINI ------------------------- #
# Using Pydantic, guarantee that the data types returned match the defined expectations, 
# converting data to the correct type where necessary.

class AgencyModel(BaseModel):
    name: str = Field(description="Name of the entity detected")
    role: int = Field(description="Agency Enum ID (1: Passive, 2: Active, 3: Mentioned)")

class AnalysisItem(BaseModel):
    id: int = Field(description="The index of the headline")
    # Dict[str, int] handles the Bias Enum ID as key and 1-5 score as value
    bias: Dict[str, int] = Field(description="Map of Bias Enum IDs (1-13) to intensity 1-3. Empty {} if none.")
    agency: List[AgencyModel]
    framing: int = Field(description="GenericFraming Enum ID (1-6)")
    # Focus as a list of dicts with at most 2 items
    focus: List[int] = Field(description="List of max 2 objects mapping Focus ID (1-14)", max_length=2)
    genre: int = Field(description="Genre Enum ID (1-6)")
    tone: int = Field(description="Tone intensity score 1-5")

class AnalysisResponse(BaseModel):
    analyses: List[AnalysisItem]


# Test
if __name__ == "__main__":
    print(AnalysisResponse.model_json_schema())