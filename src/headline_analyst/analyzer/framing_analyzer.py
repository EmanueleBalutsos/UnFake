from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import List, Type

from headline_analyst.data import *
from headline_analyst.utils.schema import resolve_schema

ANALYSIS_PROMPT = """
You are a media framing analyst. You will be given a numbered list of news headlines.
For each headline, produce a structured analysis object according to the schema provided.
Note : be mindful of quotation marks in headlines. Sentences in quotes may not reflect the headline's intents or biases but simply report what a person said.
CRITICAL RULES:
- Output a JSON object with a single key "analyses" containing one object per headline, in order.
- The "id" field must exactly match the headline's number in the input list.
- Base your analysis exclusively on the headline text itself — no external knowledge about the event.
- If a headline is ambiguous, make your best judgment and reflect uncertainty in lower scores.
- All enum fields must be integers matching the IDs defined below.

METRIC DEFINITIONS

1. BIAS  →  "bias": {{ BiasID: score, ... }}
Identify all bias types present in the headline. A headline may exhibit multiple types simultaneously.
For each detected bias, assign a score:
  1 = minor, does not significantly affect neutrality
  2 = noticeable, somewhat influences framing or perception
  3 = dominant, strongly shapes the narrative
If no bias is detected, return an empty object: {{}}

Bias types (use integer ID as key):
  1 POLITICAL: Favors or criticizes a political viewpoint, party, or figure.
    Look for: partisan labels, uneven treatment of political actors, ideological framing.
    e.g. "The radical left continues to sabotage the economy."
  2 GENDER: Reinforces gender stereotypes or applies unequal standards based on gender.
    Look for: unnecessary gender mentions, gendered adjectives, double standards.
    e.g. "Female engineer surprisingly solves complex problem."
  3 CULTURAL: Generalizes or stereotypes ethnic/cultural groups.
    Look for: broad group generalizations, "othering" language, uneven cultural portrayal.
    e.g. "Immigrants flooding labor market."
  4 AGE: Stereotypes or dismisses based on age.
    Look for: generational generalizations, ageist framing.
    e.g. "Older employees struggle with new technology."
  5 RELIGION: Stereotypes or discriminates based on religious identity.
    Look for: religious group generalizations, uneven treatment across faiths.
    e.g. "Muslim neighborhood linked to extremism."
  6 DISABILITY: Portrays disability/mental health in a dehumanizing or stigmatizing way.
    Look for: outdated terminology, defining people by their condition.
    e.g. "Facility for mentally deficient individuals."
  7 STATEMENT: Loaded or partisan word choices that reveal the author's ideological stance.
    Look for: politically coded labels, contested terminology used as neutral fact.
    e.g. "pro-life" vs. "anti-abortion"; "regime" vs. "government."
  8 OMISSION: A perspective or key actor that the headline's framing implies is absent.
    NOTE: Evaluate based on wording and emphasis only — you do not have access to the full article.
    Look for: one-sided actor framing, absence of counter-perspective in the phrasing.
    e.g. Reporting policy outcomes without naming who is affected.
  9 SENSATIONALISM: Exaggerates or dramatizes to provoke emotional reaction.
    Look for: hyperbolic verbs ("bloodbath", "devastate"), catastrophizing language.
    e.g. "Economy in freefall as chaos engulfs markets."
  10 NEGATIVITY: Disproportionately emphasizes negative aspects.
    Look for: negative framing where neutral alternatives exist, consistent pessimistic slant.
    e.g. "Country continues downward spiral under failed leadership."
  11 SUBJECTIVE: Qualifying adjectives that insert the writer's judgment rather than facts.
    Look for: evaluative adjectives that prime reader interpretation ("disturbing", "reckless").
    e.g. "The troubling rise of remote work."
  12 ADHOMINEM: Attacks on a person's character rather than their actions or arguments.
    Look for: personal insults, character-based dismissals unrelated to the topic.
    e.g. "Clueless senator proposes new bill."
  13 OPINION: Presents subjective interpretation as objective fact.
    Look for: declarative assertions that are actually judgments, no qualifying language.
    e.g. "This policy proves the government has failed citizens."

2. AGENCY  →  "agency": [ {{ "name": "...", "role": ID }}, ... ]
Extract all named and unnamed entities (persons, people, main grammatical subjects of the sentence, organizations, nations, groups, populations...).
Assign each a role based on their grammatical and narrative function:
  2  ACTIVE    : Performs the action or drives the event described.
  1  PASSIVE   : Receives the action or is acted upon.
  3  MENTIONED : Present in the headline but not clearly active or passive (context, backdrop).

Granularity rule: treat distinct named actors separately; treat vague collective references
("officials", "residents") as single entities unless the headline differentiates them.

3. FRAMING  →  "framing": ID
Select exactly one frame that best captures the headline's primary angle:
  1  CONFLICT       : Presents opposing actors, forces, or interpretations in tension.
  2  GAME_STRATEGY  : Focuses on actors pursuing goals, gaining advantage, or mobilizing support.
  3  THEMATIC       : Centers on a broader social/political issue or systemic concern.
  4  HUMAN_INTEREST : Foregrounds individuals or human experience affected by an event.
  5  EPISODIC       : Reports a specific event with no explicit connection to broader context.
  6  OTHER          : Does not fit any of the above.

4. FOCUS  →  "focus": [ID] or [ID, ID]
Select at most 2 subject matters that represent the headline's primary evaluative lens:
  1  ECONOMIC      6  POLICY        11  CULTURAL_ID
  2  RESOURCES     7  CRIME         12  PUBLIC_OPINION
  3  MORALITY      8  SECURITY      13  POLITICAL
  4  FAIRNESS      9  HEALTH        14  OTHER
  5  LEGAL         10 QOL

5. GENRE  →  "genre": ID
Identify the editorial intent behind the headline:
  1  INFORMATIVE   : Factual reporting of an event. e.g. "President signs new bill."
  2  INVESTIGATIVE : Exposes hidden truths or systemic issues. e.g. "Leaked files reveal..."
  3  ANALYTIC      : Explains causes, context, or implications. e.g. "Why inflation keeps rising."
  4  EDITORIAL     : Persuasive, opinion-driven. e.g. "Why we must act on climate now."
  5  ENTERTAINMENT : Lifestyle, culture, soft news. e.g. "Met Gala 2026: best looks."
  6  OTHER

6. TONE  →  "tone": 1-5
Rate the intensity and loadedness of the headline's language:
  1 = Clinical/neutral — plain factual language, no evaluative charge
  3 = Moderate — some loaded words or framing but not dominant
  5 = Sensational/catastrophizing — heavy emotional or dramatic language throughout

Indicators of high tone scores:
  - Hyperbolic or dramatic adjectives/adverbs ("devastating", "unprecedented", "shockingly")
  - Morally charged words ("corrupt", "sinister", "heroic", "toxic", "shameful")
  - Extreme-action verbs ("slam", "crush", "decimate", "destroy", "plague")
  - Totalizing language ("always", "never", "everyone", "permanent", "undeniable")
  - Identity labels with loaded connotations ("elites", "thugs", "regime", "extremists", "mob")

HEADLINES TO ANALYZE:
{items}
"""

class FramingAnalyzer(ABC):
    """
    Abstract class to implement LLM models for headline framing analysis.
    Concrete implementations must inherit from this class.
    """
    def __init__(self, output_model: Type[BaseModel]):
        self.output_model = output_model
        # Automatically generate the JSON Schema once upon creation
        self.schema = resolve_schema(self.output_model.model_json_schema())

    @abstractmethod
    async def annotate_headline(self, articles: list[Article]) -> List[Analysis]:
        """Specific LLM client logic goes here."""
        pass

    def _build_prompt(self, articles: list[Article]) -> str:
        """
        Format the inputs in the prompt sent to the LLM model as such :
        id:i. Headline
        """
        items = "\n".join(f"id:{id}. {a.title}" for id, a in enumerate(articles))
        return ANALYSIS_PROMPT.format(items=items)

    
    def _parse_response(self, raw_json: str, expected_length: int) -> List[Analysis]:
        """Generalized validation logic for any LLM response."""
        try:
            # Use Pydantic to validate the raw JSON string
            validated = self.output_model.model_validate_json(raw_json)
            # Map back to your internal Analysis objects
            outputs = [Analysis.from_json(item.model_dump()) for item in validated.analyses]
        except Exception as e:
            raise ValueError(f"Schema validation failed: {e}")
        
        # Check if analysis returned the correct amount of outputs (1 for each article)
        if len(outputs) != expected_length:
            raise ValueError(f"LLM analysis returned {len(outputs)} outputs, expected {expected_length}.")
        return outputs