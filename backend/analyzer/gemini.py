import json
import logging
import time

from google import genai

from backend.config import load_config

logger = logging.getLogger(__name__)

ANALYSIS_PROMPT = """Analyze this LinkedIn post. Return ONLY valid JSON with these fields:
{
  "sentiment_score": <float -1.0 to 1.0, negative=negative, positive=positive>,
  "is_political": <boolean, true if the post is political in nature>,
  "political_score": <float 0.0 to 1.0, how political is this post? 0.0 = not political at all, 1.0 = extremely political>,
  "political_topics": [<list of detected political topics as strings, empty if not political>],
  "is_ai_slop": <boolean, true if the post appears to be AI-generated slop>,
  "ai_slop_score": <float 0.0 to 1.0, how likely is this AI slop? 0.0 = clearly human-written, 1.0 = almost certainly AI-generated>
}

IMPORTANT: "political_score" is NOT a confidence score. It measures HOW political the content is:
- 0.0 = completely non-political (tech announcements, job posts, company news)
- 0.3 = mildly political (mentions policy in passing)
- 0.6 = moderately political (advocates for political positions)
- 1.0 = overtly political (partisan advocacy, culture war, election content)

Set "is_political" to true when political_score >= 0.4.

"Political" means: expresses political opinions, endorses candidates/parties, discusses government policy, culture war topics, immigration, gun control, abortion, election content, partisan attacks, or divisive social issues.

"AI slop" means: generic AI-generated motivational/engagement content with no original insight — typically uses excessive emojis, numbered lists of platitudes, "agree?" engagement bait, or suspiciously polished generic advice.

Post text:
\"\"\"
{post_content}
\"\"\""""


class RateLimiter:
    """Simple token bucket rate limiter."""

    def __init__(self, max_per_minute: int = 15):
        self.max_per_minute = max_per_minute
        self.timestamps: list[float] = []

    def acquire(self):
        now = time.time()
        self.timestamps = [t for t in self.timestamps if now - t < 60]

        if len(self.timestamps) >= self.max_per_minute:
            wait = 60 - (now - self.timestamps[0])
            if wait > 0:
                logger.info("Rate limit reached, waiting %.1fs...", wait)
                time.sleep(wait)

        self.timestamps.append(time.time())


class GeminiAnalyzer:
    def __init__(self):
        config = load_config()
        self.client = genai.Client(api_key=config["gemini_api_key"])
        self.model = "gemini-2.5-flash"
        self.rate_limiter = RateLimiter(max_per_minute=15)

    def analyze_post(self, content: str) -> dict | None:
        """Analyze a single post. Returns parsed JSON dict or None on failure."""
        prompt = ANALYSIS_PROMPT.replace("{post_content}", content)

        for attempt in range(2):
            self.rate_limiter.acquire()
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                )
                text = response.text.strip()

                # Strip markdown code fences if present
                if text.startswith("```"):
                    text = text.split("\n", 1)[1] if "\n" in text else text[3:]
                if text.endswith("```"):
                    text = text[:-3]
                if text.startswith("json"):
                    text = text[4:]
                text = text.strip()

                result = json.loads(text)
                required = {"sentiment_score", "is_political", "political_score", "is_ai_slop"}
                if not required.issubset(result.keys()):
                    logger.warning("Missing keys in response: %s", required - result.keys())
                    if attempt == 0:
                        continue
                return result

            except json.JSONDecodeError as e:
                logger.warning("JSON parse error (attempt %d): %s", attempt + 1, e)
                if attempt == 0:
                    continue
                return {"raw_response": text if text else "", "parse_error": str(e)}

            except Exception as e:
                logger.error("Gemini API error: %s", e)
                if "429" in str(e):
                    wait = 5 * (2**attempt)
                    logger.info("Rate limited by API, backing off %ds...", wait)
                    time.sleep(wait)
                    continue
                return None

        return None
