# ai_engine.py
# D:\DietLens2026\ai_engine.py

import os
import base64
import httpx
from groq import Groq
from dotenv import load_dotenv
from verdict_checker import check_verdict

load_dotenv()

GROQ_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"


# ─────────────────────────────────────────────────────────────
# MAIN FUNCTION
# ─────────────────────────────────────────────────────────────

def analyze_food_label(image_path, user_conditions):
    """
    1. AI extracts ingredients & analysis
    2. Python checks conditions using verdict_checker
    3. AI verdict is removed completely
    4. Python verdict is appended at the bottom
    """

    # ── Get API key ──────────────────────────────────────────
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return (
            "❌ API Key not found!\n\n"
            "Please add GROQ_API_KEY to your .env file."
        )

    # ── Read and encode image ───────────────────────────────
    try:
        with open(image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")
    except Exception as e:
        return f"❌ Could not read image:\n{str(e)}"

    # ── Connect to Groq ─────────────────────────────────────
    http_client = httpx.Client(timeout=60.0)
    client = Groq(api_key=api_key, http_client=http_client)

    try:
        print(f"\n📤 Sending image to Groq: {GROQ_MODEL}")

        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_data}"
                            }
                        },
                        {
                            "type": "text",
                            "text": build_prompt()
                        }
                    ]
                }
            ],
            max_tokens=1500,
            temperature=0.0  # deterministic extraction
        )

        # ✅ Raw AI analysis text
        ai_text = response.choices[0].message.content

        # ✅ REMOVE any AI verdict completely
        ai_text_no_verdict = remove_ai_verdict(ai_text)

        # ✅ Run Python verdict checker
        verdict_result = check_verdict(
            ai_response_text=ai_text,
            user_conditions=user_conditions
        )

        # ✅ Clean & format AI analysis
        formatted_analysis = clean_response(
            ai_text_no_verdict,
            user_conditions
        )

        # ✅ Append Python verdict ONLY
        final_output = (
            formatted_analysis
            + "\n\n"
            + verdict_result["verdict_text"]
        )

        return final_output

    except Exception as e:
        return f"❌ Error: {str(e)}"

    finally:
        http_client.close()


# ─────────────────────────────────────────────────────────────
# REMOVE AI VERDICT COMPLETELY
# ─────────────────────────────────────────────────────────────

def remove_ai_verdict(ai_text):
    """
    Completely removes everything from the first occurrence
    of the word 'VERDICT' until the end of AI response.
    This guarantees AI verdict never appears.
    """

    lower_text = ai_text.lower()
    verdict_index = lower_text.find("verdict")

    if verdict_index != -1:
        return ai_text[:verdict_index]

    return ai_text


# ─────────────────────────────────────────────────────────────
# BUILD PROMPT
# ─────────────────────────────────────────────────────────────

def build_prompt():
    """
    AI extracts ingredients and analysis only.
    AI is NOT allowed to write a verdict.
    """

    return (
        "You are a food safety expert and FDA compliance specialist.\n"
        "Carefully read EVERY word on this food ingredient label image.\n\n"

        "Respond using these EXACT sections:\n\n"

        "INGREDIENTS FOUND:\n"
        "List EVERY ingredient exactly as written on label.\n"
        "Write each on a new line starting with -\n"
        "Do NOT summarize.\n"
        "If no ingredients visible write: NO INGREDIENTS FOUND\n\n"

        "ALLERGEN CHECK:\n"
        "Check for FDA major allergens:\n"
        "Milk, Eggs, Fish, Shellfish, Tree Nuts, Peanuts, Wheat, Soy, Sesame\n"
        "List detected allergens.\n\n"

        "FATS AND OILS:\n"
        "List fats and oils and classify Healthy/Unhealthy.\n\n"

        "FOOD ADDITIVES:\n"
        "List additives and classify Safe/Caution/Harmful.\n\n"

        "HARMFUL PRESERVATIVES:\n"
        "List any harmful preservatives.\n\n"

        "ARTIFICIAL COLOURS:\n"
        "List artificial colors.\n\n"

        "WARNINGS:\n"
        "List harmful ingredients with short reason.\n\n"

        "FDA COMPLIANCE:\n"
        "Compare nutrition values with FDA daily limits if available.\n\n"

        "STOP HERE.\n"
        "Do NOT write a VERDICT.\n"
        "Do NOT write SAFE or NOT SAFE.\n"
    )


# ─────────────────────────────────────────────────────────────
# CLEAN RESPONSE
# ─────────────────────────────────────────────────────────────

def clean_response(raw_text, user_conditions):
    """
    Formats AI response nicely for UI.
    """

    lines = raw_text.split("\n")
    new_lines = []

    for line in lines:

        if line.strip().startswith("##"):
            line = line.strip().replace("##", "").strip()
        elif line.strip().startswith("#"):
            line = line.strip().replace("#", "").strip()

        if line.strip().startswith("* "):
            line = "- " + line.strip()[2:]

        while "**" in line:
            line = line.replace("**", "", 2)

        new_lines.append(line)

    cleaned = "\n".join(new_lines)

    while "\n\n\n" in cleaned:
        cleaned = cleaned.replace("\n\n\n", "\n\n")

    section_headers = [
        "INGREDIENTS FOUND:",
        "ALLERGEN CHECK:",
        "FATS AND OILS:",
        "FOOD ADDITIVES:",
        "HARMFUL PRESERVATIVES:",
        "ARTIFICIAL COLOURS:",
        "WARNINGS:",
        "FDA COMPLIANCE:"
    ]

    for header in section_headers:
        if header in cleaned:
            cleaned = cleaned.replace(
                header,
                f"\n{'─' * 40}\n  {header}\n{'─' * 40}"
            )

    conditions_text = (
        ", ".join(user_conditions)
        if user_conditions else "None selected"
    )

    header = (
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "       🔍 DIETLENS ANALYSIS REPORT\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"  Conditions : {conditions_text}\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    )

    return header + cleaned.strip()