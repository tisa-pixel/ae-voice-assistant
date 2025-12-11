# Daily Dose - Build Post: Poppy AE Voice Assistant
**For conversionisourgame.com**
**Created:** December 10, 2025

---

## 1. BUILD TITLE
How I Built a Voice AI That Updates Salesforce After Appointments (No More Data Entry)

---

## 2. THE PROBLEM

Acquisition agents hate manual Salesforce data entry after appointments. They're tired, mentally drained from negotiations, and the last thing they want to do is click through 15 fields in Salesforce to log what happened. So what do they do? They skip it, forget details, or write terrible notes that nobody can use later.

Result? Your CRM data is trash, deals fall through the cracks, and nobody has visibility into what's actually happening in the field. You're paying good money for a CRM that's basically a glorified contact list because nobody updates it properly.

---

## 3. THE SOLUTION

Built a voice AI agent (Poppy) that calls AEs right after appointments and naturally debriefs them in conversation. She asks the right questions, listens patiently, extracts structured data from their responses, and updates Salesforce automatically—no clicking, no forms, no data entry.

**Key capabilities:**
- Natural conversation (not robotic Q&A)
- Comprehension, not just transcription (understands context)
- Creates tasks ("Remind me to get a seawall quote")
- Schedules follow-up appointments on calendar
- Updates 15+ Salesforce fields in under 2 minutes
- Empathetic responses for tough appointments

---

## 4. WATCH ME BUILD IT

[YouTube embed placeholder - record the walkthrough video]

**Video includes:**
- Demo of actual call with Poppy
- How the Retell AI agent works
- Backend Flask app walkthrough
- Salesforce integration setup
- Prompt engineering for natural conversation

---

## 5. WHAT YOU'LL LEARN

- How to build a conversational AI agent with Retell AI
- How to design prompts for comprehension (not just transcription)
- How to integrate Retell webhooks with Python/Flask
- How to update Salesforce via REST API from external apps
- How to handle natural language → structured data extraction
- How to deploy voice AI apps on Heroku
- Prompt engineering for empathy and natural conversation flow

---

## 6. BUILD DETAILS

### 6.1 Time Investment

| Who | Time Required |
|-----|---------------|
| **If You Hire a Dev** | 40-60 hours (1-2 weeks) |
| **If You Build It (with this guide)** | 12-16 hours (2-3 days) |

**Breakdown:**
- Retell AI setup & configuration: 2 hours
- Salesforce field mapping & API setup: 3 hours
- Backend Flask app development: 5-8 hours
- Testing & refinement: 2-3 hours

### 6.2 Cost Breakdown

| Approach | Cost |
|----------|------|
| **Developer Rate** | $100-150/hour |
| **Estimated Dev Cost** | $4,000-$9,000 |
| **DIY Cost (Your Time)** | 12-16 hours + $250/month tools |
| **ROI** | 2-3 hours saved per AE per week = 100+ hours/month saved |

**Monthly Tool Costs:**
- Retell AI: ~$150/month (based on usage)
- Heroku: $25-50/month (Hobby or Standard dyno)
- Claude API: ~$50/month (for data extraction)
- Salesforce: (existing - no additional cost)

**Total Monthly Cost:** ~$250/month to save 100+ hours of manual data entry

---

## 7. TECH STACK

🔧 **Tools Used:**

| Tool | Purpose |
|------|---------|
| **Retell AI** | Voice AI platform (handles calls, TTS, STT) |
| **Python/Flask** | Backend webhook handler |
| **Heroku** | App hosting |
| **Salesforce REST API** | CRM updates |
| **Claude API** | Natural language → structured data extraction |
| **11Labs (Cleo voice)** | Voice synthesis (via Retell) |

---

## 8. STEP-BY-STEP BREAKDOWN

### 1. **Set Up Retell AI Agent**

Create a Retell AI account and configure your agent's voice and behavior settings. The key decisions here are voice selection (we use 11labs-Cleo for warmth), responsiveness level, and interruption sensitivity.

Setting responsiveness to 0.75 gives AEs time to think without feeling rushed. Interruption sensitivity at 0.6 lets them finish their thoughts. Enable backchannel for natural "mm-hmm" and "yeah" responses that make the conversation feel human.

---

### 2. **Map Salesforce Fields**

Document which Opportunity fields Poppy will update and their API names. You'll need to set up a Salesforce Connected App to enable API access from external applications.

Poppy updates fields like Stage, ARV, Rehab Cost, Lowest Seller Will Accept, Last Offer Made, Property Walk Thru description, AE Notes, Next Step, and Appointment Status. Create a spreadsheet mapping conversation topics to field API names for your backend to reference.

---

### 3. **Build the Flask Backend**

Create a Python Flask application with a webhook endpoint that Retell will call after each conversation ends. The backend receives the call transcript, authenticates to Salesforce, extracts structured data, and updates the appropriate Opportunity.

The app needs five core functions: webhook handler to receive Retell data, Salesforce connection for authentication, data extraction using Claude API to interpret natural language, Opportunity update to write to SF, and Task/Event creation for follow-ups. See the GitHub repo for the complete implementation.

---

### 4. **Deploy to Heroku**

Create a Heroku app and configure environment variables for all your credentials - Salesforce username, password, security token, Retell API key, and Claude API key. Push your Flask app to Heroku using Git.

Once deployed, your app gets a public URL that Retell can call. The Procfile tells Heroku how to run your Flask app, and requirements.txt ensures all Python dependencies are installed automatically.

---

### 5. **Configure Retell Webhook**

In the Retell dashboard, add your Heroku app URL with the webhook endpoint path. When calls end, Retell sends the transcript and metadata to this URL, triggering your Salesforce updates.

Test the webhook connection by making a test call and checking your Heroku logs. You should see the incoming request and Salesforce update confirmation. Fix any authentication or field mapping issues before going live.

---

### 6. **Write the Agent Prompt**

Define Poppy's personality (warm, empathetic, efficient) and conversation flow. The prompt is the heart of the system - it determines how natural and effective the calls feel.

Structure the prompt with personality guidelines, conversation flow (opening → questions → confirmation → sign-off), critical rules (no dollar signs, let them talk during property descriptions), and field mapping instructions. The full prompt is in POPPY-VOICE.md in the repo.

---

### 7. **Test & Refine**

Make test calls covering various scenarios: standard appointments, no-offer situations, tough negotiations, complex property descriptions, and multiple follow-up needs. Check Salesforce after each call to verify the right data landed in the right fields.

Review transcripts for extraction accuracy and adjust your prompts based on edge cases. Fine-tune responsiveness and interruption settings based on real conversation flow. Plan for 2-3 hours of refinement before going live.

---

## 9. GITHUB REPO

📂 **Get the Code:**

**Repository:** [github.com/tisa-pixel/ae-voice-assistant](https://github.com/tisa-pixel/ae-voice-assistant)

**What's included:**
- Full Flask application (app.py)
- Agent specification (AGENT-SPEC.md)
- Poppy personality & voice guide (POPPY-VOICE.md)
- Salesforce field mapping
- Requirements & deployment files
- Sample conversation flows
- Heroku deployment instructions

---

## 10. DOWNLOAD THE TEMPLATE

⬇️ **Download Resources:**

- [Retell Agent Prompt Template](https://github.com/tisa-pixel/ae-voice-assistant/blob/main/POPPY-VOICE.md)
- [Salesforce Field Mapping Checklist](https://github.com/tisa-pixel/ae-voice-assistant/blob/main/AGENT-SPEC.md)
- [Python Flask Webhook Template](https://github.com/tisa-pixel/ae-voice-assistant/blob/main/app.py)
- [Heroku Deployment Guide](https://github.com/tisa-pixel/ae-voice-assistant)

**Setup checklist:**
1. Retell AI account created
2. Salesforce Connected App configured
3. Flask app deployed to Heroku
4. Webhook URL added to Retell
5. Test call completed successfully
6. Salesforce updates verified
7. Agent prompt refined based on testing

---

## 11. QUESTIONS? DROP THEM BELOW

💬 **Have questions or want to share your results?**

- Comment on the [YouTube video](#) (TBD)
- DM me on Instagram: [@donottakeifallergictorevenue](https://www.instagram.com/donottakeifallergictorevenue/)
- Open an issue on [GitHub](https://github.com/tisa-pixel/ae-voice-assistant/issues)

**Common questions:**
- "Can this work with other CRMs?" → Yes, just swap the SF API calls
- "What about HIPAA/compliance?" → Retell has compliant options
- "Can I customize the questions?" → Absolutely, it's all prompt-based

---

## 12. RELATED BUILDS

| Build 1 | Build 2 | Build 3 |
|---------|---------|---------|
| **Attempting Contact Cadence** | **Am I Spam? - Phone Reputation Checker** | **REI Lead Qualifier** |
| 17-touch automated follow-up system in Salesforce | Check if your DIDs are flagged before campaigns | AI voice agent that qualifies leads and warm transfers |
| [View Build](https://github.com/tisa-pixel/attempting-contact) | [View Build](https://github.com/tisa-pixel/am-i-spam) | [View Build](https://github.com/tisa-pixel/rei-lead-qualifier) |

---

## Additional Metadata (for SEO / Backend)

**Published:** December 10, 2025
**Author:** Tisa Daniels
**Category:** Salesforce Automation / Voice AI / Real Estate Tech
**Tags:** #Salesforce #VoiceAI #RetellAI #Python #Heroku #Automation #RealEstateInvesting
**Estimated Read Time:** 8 minutes
**Video Duration:** TBD

---

## Design Notes for Wix Implementation

### Layout Style:
- **Dark background** (charcoal #1B1C1D)
- **High contrast text** (white headings, light gray body)
- **Accent colors:** Blue (#2563eb), Green (#16a34a for "completed"), Orange (#f59e0b for "in progress")
- **Clean, modern, mobile-first**

### Call-to-Action Buttons:
- **Primary CTA** (Clone on GitHub): Purple (#7c3aed)
- **Secondary CTA** (Watch on YouTube): Blue (#2563eb)

---

**Template Version:** 1.0
**Created:** December 10, 2025
**Build Time:** 12-16 hours
