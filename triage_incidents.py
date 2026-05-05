import os
import json
from pathlib import Path
from dotenv import load_dotenv
from google import genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("Missing GEMINI_API_KEY. Check your .env file.")

client = genai.Client(api_key=GEMINI_API_KEY)


def load_mock_incidents():
    file_path = Path("mock_incidents.json")

    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def triage_incident(incident):
    prompt = f"""
You are an IT service desk triage assistant.

Analyze this incident and return ONLY valid JSON.

Incident:
ID: {incident.get("id")}
Number: {incident.get("number")}
Name: {incident.get("name")}
Description: {incident.get("description_no_html")}
Current Priority: {incident.get("priority")}
State: {incident.get("state")}

Return JSON with exactly these fields:
{{
  "summary": "one sentence summary",
  "category": "best category such as Network, Hardware, Software, Access, Server, Account, Request, Security, Other",
  "suggested_priority": "Low, Medium, High, or Critical",
  "reasoning": "brief reason for the priority/category",
  "suggested_next_action": "specific next step for a technician"
}}
"""

    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=prompt
    )

    text = response.text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {
            "summary": "Gemini returned non-JSON output.",
            "raw_response": text
        }


def main():
    incidents = load_mock_incidents()

    for incident in incidents:
        triage = triage_incident(incident)

        print("=" * 80)
        print(f"Incident #{incident['number']}: {incident['name']}")
        print(json.dumps(triage, indent=2))


if __name__ == "__main__":
    main()