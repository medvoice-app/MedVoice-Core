# JSON schema for medical transcription output
MEDICAL_TRANSCRIPTION_SCHEMA = """
{
    "type": "object",
    "properties": {
        "patient_name": {
            "type": "string"
        },
        "patient_dob": {
            "type": "string",
            "pattern": "^\\\\d{2}/\\\\d{2}/\\\\d{2}$"
        },
        "patient_gender": {
            "type": "string"
        },
        "Demographics_of_patient": {
            "type": "object",
            "properties": {
                "Marital_status": { "type": "string" },
                "Ethnicity": { "type": "string" },
                "Occupation": { "type": "string" }
            }
        },
        "Past_medical_history": {
            "type": "object", 
            "properties": {
                "Medical_history": { "type": "string" },
                "Surgical_history": { "type": "string" }
            }
        },
        "Current_medications_and_drug_allergies": {
            "type": "object",
            "properties": {
                "Drug_allergy": { "type": "string" },
                "Prescribed_medications": { "type": "string" },
                "Recently_prescribed_medications": { "type": "string" }
            }
        },
        "Mental_state_examination": {
            "type": "object",
            "properties": {
                "Appearance_and_behavior": { "type": "string" },
                "Speech_and_thoughts": { "type": "string" },
                "Mood": { "type": "string" },
                "Thoughts": { "type": "string" }
            }
        },
        "Physical_examination": {
            "type": "object",
            "properties": {
                "Blood_pressure": { "type": "string" },
                "Pulse_rate": { "type": "string" },
                "Temperature": { "type": "string" }
            }
        },
        "note": { "type": "string" }
    },
    "required": [
        "patient_name",
        "patient_gender",
        "Demographics_of_patient",
        "Past_medical_history", 
        "Current_medications_and_drug_allergies",
        "Mental_state_examination",
        "Physical_examination",
        "note"
    ]
}
"""

MEDICAL_OUTPUT_EXAMPLE = """{
    "patient_name": "Tony Stark",
    "patient_dob": "15/04/1985",
    "patient_gender": "Male",
    "Demographics_of_patient": {
        "Marital_status": "Married",
        "Ethnicity": "Vietnamese",
        "Occupation": "Software Engineer"
    },
    "Past_medical_history": {
        "Medical_history": "Hypertension since 2020",
        "Surgical_history": "Appendectomy 2015"
    },
    "Current_medications_and_drug_allergies": {
        "Drug_allergy": "None",
        "Prescribed_medications": "Lisinopril 10mg daily",
        "Recently_prescribed_medications": "None"
    },
    "Mental_state_examination": {
        "Appearance_and_behavior": "Alert and oriented",
        "Speech_and_thoughts": "Clear and coherent",
        "Mood": "Stable",
        "Thoughts": "No abnormalities"
    },
    "Physical_examination": {
        "Blood_pressure": "120/80",
        "Pulse_rate": "72",
        "Temperature": "36.8C"
    },
    "note": "Dr. Jane Foster noted patient is responding well to treatment. Follow-up in 3 months."
}"""

SYSTEM_PROMPT_TEMPLATE = """
You are an AI assisstant that summarizes medical transcript into a structured JSON format. 
Analyze the medical transcript provided. If multiple speakers are present, focus on summarizing patient-related information only from the speaker discussing patient details.

Schema Format:
{schema}

Example Output:
{output_schema}

You must use {patient_name} as the value of "patient_name" field in the JSON schema.

If the medical transcript is in a language other than English, provide all JSON values and only the values in that same language. You must not modify the JSON field names in English.

If no patient-related information is present, use empty strings ("") for any missing information adhering to the JSON schema. 
Ensuring the use of explicit information and recognized medical terminology. 
Follow the JSON schema strictly without making assumptions about unspecified details.
Format your response exactly like this example, maintaining all fields.
You must only return the JSON schema. Do not include any additional information."""