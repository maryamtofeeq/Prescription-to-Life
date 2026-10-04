import base64
import json
from groq import Groq


# =========================================================
# MODELS
# =========================================================

# Vision model: reads the prescription image
VISION_MODEL = "qwen/qwen3.8-27b"

# Main reasoning model requested by the project
TEXT_MODEL = "openai/gpt-oss-120b"


# =========================================================
# GROQ CLIENT
# =========================================================

def create_client(api_key):
    return Groq(api_key=api_key)


# =========================================================
# IMAGE CONVERSION
# =========================================================

def image_to_data_url(image_bytes, mime_type):

    encoded = base64.b64encode(image_bytes).decode("utf-8")

    return f"data:{mime_type};base64,{encoded}"


# =========================================================
# JSON TEXT AGENT
# =========================================================

def call_text_agent(client, prompt):

    response = client.chat.completions.create(
        model=TEXT_MODEL,

        messages=[
            {
                "role": "system",
                "content": (
                    "You are a careful healthcare information "
                    "assistant. Never guess missing prescription "
                    "information."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0,

        max_completion_tokens=800,

        response_format={
            "type": "json_object"
        }
    )

    text = response.choices[0].message.content

    return json.loads(text)


# =========================================================
# AGENT 1
# PRESCRIPTION VISION AGENT
# =========================================================

def prescription_reader(client, image_data):

    prompt = """
You are the Prescription Reading Agent.

Read the uploaded prescription image.

Extract ONLY information that is clearly visible.

For every medicine identify:

- medicine_name
- dosage
- frequency
- timing
- duration

IMPORTANT:

1. Never guess handwriting.
2. Never invent a medicine name.
3. Never invent dosage.
4. Never invent frequency.
5. Never invent timing.
6. Never correct the doctor's prescription.
7. If something is unclear, write "UNCLEAR".
8. Set readable to false ONLY if the prescription image
is generally unreadable.

If only one field is unclear, keep readable as true
and mark only that specific field as "UNCLEAR".
Return ONLY valid JSON:

{
    "readable": true,
    "medicines": [
        {
            "medicine_name": "",
            "dosage": "",
            "frequency": "",
            "timing": "",
            "duration": ""
        }
    ],
    "unclear_items": []
}
"""

    response = client.chat.completions.create(

        model=VISION_MODEL,

        messages=[
            {
                "role": "user",

                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },

                    {
                        "type": "image_url",

                        "image_url": {
                            "url": image_data
                        }
                    }
                ]
            }
        ],

        temperature=0,

        max_completion_tokens=1500,

        response_format={
            "type": "json_object"
        }
    )

    result = response.choices[0].message.content

    return json.loads(result)


# =========================================================
# AGENT 2
# SAFETY / VERIFICATION AGENT
# =========================================================
    
def verification_agent(client, prescription):
    prompt = f"""
You are the Prescription Safety Verification Agent.

Review ONLY the information extracted from the prescription:

{json.dumps(prescription, indent=2)}

Your job is to decide whether the information is reliable enough
to create a medicine schedule.

IMPORTANT SAFETY RULES:

1. NEVER guess a medicine name.
2. NEVER guess a dosage.
3. NEVER guess a frequency.
4. NEVER change the doctor's instructions.
5. NEVER add a medicine.
6. NEVER remove a medicine.

BLOCK processing ONLY when one of these CORE fields is unclear:

- medicine_name
- dosage
- frequency

Timing and duration are NOT blocking fields.

If timing is unclear:
write "Not specified"

If duration is unclear:
write "Not specified"

If all medicine names, dosages and frequencies are sufficiently
readable, set safe_to_process to true.

If any CORE field contains UNCLEAR, set safe_to_process to false.

Return ONLY valid JSON:

{{
    "safe_to_process": true,
    "warning": "",
    "blocking_issues": [],
    "medicines": []
}}
"""

    return call_text_agent(client, prompt)

# =========================================================
# AGENT 3
# MEDICINE SCHEDULE AGENT
# =========================================================

def schedule_agent(client, verified_data):

    prompt = f"""
You are the Medicine Schedule Agent.

Use ONLY this verified prescription information:

{json.dumps(verified_data, indent=2)}

Create a simple schedule.

Use these columns:

- medicine_name
- dosage
- frequency
- morning
- afternoon
- evening
- night
- duration

IMPORTANT:

Do NOT invent a timing.

If the prescription does not specify a particular
timing, write:

"Not specified"

Do not change the doctor's instructions.

Return ONLY JSON:

{{
    "schedule": [
        {{
            "medicine_name": "",
            "dosage": "",
            "frequency": "",
            "morning": "",
            "afternoon": "",
            "evening": "",
            "night": "",
            "duration": ""
        }}
    ]
}}
"""

    return call_text_agent(
        client,
        prompt
    )


# =========================================================
# AGENT 4
# SIMPLE MEDICINE EXPLANATION AGENT
# =========================================================

def explanation_agent(client, verified_data, language):

    prompt = f"""
You are the Simple Medicine Explanation Agent.

Use ONLY the verified medicine information below:

{json.dumps(verified_data, indent=2)}

Language: {language}

For each medicine, give a short, simple explanation
of its general purpose.

Example style:

"Generally used for stomach-related problems."

IMPORTANT:

1. Do not diagnose the patient.
2. Do not say that the patient has a disease.
3. Do not change dosage.
4. Do not change frequency.
5. Do not add treatment instructions.
6. Do not claim certainty if the purpose cannot be
   reliably determined.
7. If the purpose cannot be safely determined, say:
   "Purpose could not be safely determined."

Return ONLY JSON:

{{
    "explanations": [
        {{
            "medicine_name": "",
            "simple_use": ""
        }}
    ]
}}
"""

    return call_text_agent(
        client,
        prompt
    )


# =========================================================
# AGENT 5
# LANGUAGE AGENT
# =========================================================

def language_agent(
    client,
    schedule,
    explanations,
    language
):

    prompt = f"""
You are the final Language Agent.

Convert the verified information into:

{language}

Schedule:

{json.dumps(schedule, indent=2)}

Medicine explanations:

{json.dumps(explanations, indent=2)}

IMPORTANT:

Do NOT change:

- medicine names
- dosage
- frequency
- timing
- duration

Only translate the wording.

If language is English:
Use simple English.

If language is Urdu:
Use simple Urdu.

Return ONLY JSON:

{{
    "schedule": [],
    "explanations": []
}}
"""

    return call_text_agent(
        client,
        prompt
    )


# =========================================================
# COMPLETE MULTI-AGENT PIPELINE
# =========================================================

def analyze_prescription(
    client,
    image_bytes,
    mime_type,
    language
):

    # Convert image
    image_data = image_to_data_url(
        image_bytes,
        mime_type
    )


    # -----------------------------------------------------
    # AGENT 1
    # -----------------------------------------------------

    prescription = prescription_reader(
        client,
        image_data
    )


    # -----------------------------------------------------
    # AGENT 2
    # -----------------------------------------------------

    verification = verification_agent(
        client,
        prescription
    )


    # -----------------------------------------------------
    # SAFETY STOP
    # -----------------------------------------------------

    if not verification.get(
        "safe_to_process",
        False
    ):

        return {
            "success": False,

            "prescription": prescription,

            "verification": verification
        }


    # -----------------------------------------------------
    # AGENT 3
    # -----------------------------------------------------

    schedule = schedule_agent(
        client,
        verification
    )


    # -----------------------------------------------------
    # AGENT 4
    # -----------------------------------------------------

    explanations = explanation_agent(
        client,
        verification,
        language
    )


    # -----------------------------------------------------
    # AGENT 5
    # -----------------------------------------------------

    final_result = language_agent(
        client,
        schedule,
        explanations,
        language
    )


    return {

        "success": True,

        "prescription": prescription,

        "verification": verification,

        "schedule": schedule,

        "explanations": explanations,

        "final": final_result
}
