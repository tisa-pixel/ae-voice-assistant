# Live Build Prompt

Use this prompt to recreate the AE Voice Assistant (Poppy) from scratch in a recording session.

---

## The Prompt

```
I need to build a voice AI assistant for real estate acquisition agents using Retell AI and Heroku. Here's what I need:

**Project: Post-Appointment Debrief Assistant**

An AI assistant that Account Executives call after property appointments to debrief. The assistant asks questions, extracts structured data, and updates Salesforce.

**Personality:**
- Name: Poppy
- Tone: Warm, supportive teammate - not robotic
- Style: Short, direct questions. No over-explaining.
- Opening: "Hey, how'd it go at the appointment?"

**Voice Settings (Retell):**
- Voice: 11labs-Cleo
- Speed: 1
- Temperature: 1.02
- Volume: 1.2
- Responsiveness: 0.75
- Interruption Sensitivity: 0.6
- Backchannel: enabled at 0.3 frequency
- Backchannel words: yeah, got it, okay, mm-hmm
- Ambient sound: call-center at 20% volume

**Conversation Flow:**
1. Greet: "Hey, how'd it go at the appointment?"
2. Get property address (required - can't proceed without it)
3. Ask one question at a time:
   - ARV?
   - Rehab?
   - Offer?
   - Lowest they'll take?
   - Why not closeable?
   - Hot, warm, or nurture?
   - Walk me through the layout inside (wait patiently for long answer)
   - Anything for marketing?
   - Major repairs?
4. If they mention a follow-up meeting, ask "What time?" then confirm calendar add
5. Rapid-fire confirmation: "Got it. [address], ARV 600k, rehab 80k, lowest 400k, stage hot. [layout]. Sound right?"
6. Reminder: "Don't forget to upload photos and recording from today"
7. Sign-off: "You're all set. Talk soon."

**Critical Rules:**
- Numbers: Say "600k" not "$600K" - never use dollar signs
- Property walkthrough: Let them talk - don't interrupt long descriptions
- Gender: Use they/them for sellers unless specified
- Acknowledgments: Don't start every response with "Got it"

**Tech Stack:**
- Voice: Retell AI
- Backend: Heroku (Python/Flask)
- CRM: Salesforce REST API

**Backend should:**
1. Receive webhook from Retell with call data
2. Parse transcript for structured data (ARV, rehab, stage, etc.)
3. Look up Opportunity in Salesforce by property address
4. Update the Opportunity with extracted fields
5. Create Tasks/Events if mentioned in call

**Salesforce Fields to Update:**
- StageName (Hot, Warm, Nurture, etc.)
- ARV__c
- Rehab_Cost__c
- Lowest_price_seller_will_accept__c
- Last_Offer_Made__c
- Property_Walk_Thru__c
- AE_Marketing_Notes__c
- AE_Repair_Notes__c
- Why_was_this_not_closable__c
- Obstacle_to_Contract__c

Please help me build this step by step. Start with the Retell agent setup, then the Heroku webhook, then the Salesforce integration.
```

---

## What This Prompt Gets You

When you give Claude this prompt, it will:

1. **Create the Retell Agent** - Set up voice, personality, and conversation settings
2. **Build the Heroku Backend** - Flask app with webhook endpoint for Retell
3. **Wire Up Salesforce** - REST API integration to update Opportunities
4. **Create the LLM Prompt** - The full system prompt for Poppy's personality

## Recording Tips

For a good demo recording:

1. **Start clean** - Create a fresh directory
2. **Show the progression**:
   - First, explain what we're building (30 sec)
   - Create the Retell agent (show the settings)
   - Build the Flask app
   - Deploy to Heroku
   - Test with a call
3. **Good stopping points**:
   - After Retell agent is configured
   - After first successful webhook test
   - After Salesforce integration works

## Expected Output Files

```
ae-voice-assistant/
├── app.py              # Flask webhook handler
├── requirements.txt    # Python dependencies
├── Procfile           # Heroku process file
├── runtime.txt        # Python version
├── prompts/
│   └── poppy_prompt.json
├── AGENT-SPEC.md      # Full specification
└── POPPY-VOICE.md     # Voice/personality guide
```

## Time Estimate

Full build from scratch: 15-25 minutes depending on explanation depth

- Retell setup: 3-5 min
- Flask app: 5-8 min
- Heroku deploy: 3-5 min
- Salesforce integration: 5-8 min
- Testing: 2-3 min
