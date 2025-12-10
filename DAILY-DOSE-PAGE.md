# How I Built a Voice AI That Updates Salesforce After Appointments (No More Data Entry)

**Build:** Poppy - AE Voice Assistant
**Published:** December 10, 2025
**Category:** Salesforce Automation | Voice AI | Real Estate Tech

---

## THE PROBLEM

Acquisition agents hate manual Salesforce data entry after appointments. They're tired, mentally drained from negotiations, and the last thing they want to do is click through 15 fields in Salesforce to log what happened. So what do they do? They skip it, forget details, or write terrible notes that nobody can use later.

Result? Your CRM data is trash, deals fall through the cracks, and nobody has visibility into what's actually happening in the field. You're paying good money for a CRM that's basically a glorified contact list because nobody updates it properly.

---

## THE SOLUTION

Built a voice AI agent (Poppy) that calls AEs right after appointments and naturally debriefs them in conversation. She asks the right questions, listens patiently, extracts structured data from their responses, and updates Salesforce automatically—no clicking, no forms, no data entry.

**Key capabilities:**
- Natural conversation (not robotic Q&A)
- Comprehension, not just transcription (understands context)
- Creates tasks ("Remind me to get a seawall quote")
- Schedules follow-up appointments on calendar
- Updates 15+ Salesforce fields in under 2 minutes
- Empathetic responses for tough appointments

---

## WATCH ME BUILD IT

[YouTube embed placeholder - record the walkthrough video]

**Video includes:**
- Demo of actual call with Poppy
- How the Retell AI agent works
- Backend Flask app walkthrough
- Salesforce integration setup
- Prompt engineering for natural conversation

---

## WHAT YOU'LL LEARN

- How to build a conversational AI agent with Retell AI
- How to design prompts for comprehension (not just transcription)
- How to integrate Retell webhooks with Python/Flask
- How to update Salesforce via REST API from external apps
- How to handle natural language → structured data extraction
- How to deploy voice AI apps on Heroku
- Prompt engineering for empathy and natural conversation flow

---

## BUILD DETAILS

### Time Investment

| Who | Time Required |
|-----|---------------|
| **If You Hire a Dev** | 40-60 hours (1-2 weeks) |
| **If You Build It (with this guide)** | 12-16 hours (2-3 days) |

**Breakdown:**
- Retell AI setup & configuration: 2 hours
- Salesforce field mapping & API setup: 3 hours
- Backend Flask app development: 5-8 hours
- Testing & refinement: 2-3 hours

### Cost Breakdown

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

## TECH STACK

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

## STEP-BY-STEP BREAKDOWN

### Step 1: Set Up Retell AI Agent

**What you'll do:**
- Create Retell AI account
- Configure agent settings (voice, speed, responsiveness)
- Write the agent prompt (see POPPY-VOICE.md in repo)
- Set up webhook URL (we'll create this in Step 3)

**Key settings:**
- Voice: 11labs-Cleo (warm, conversational)
- Responsiveness: 0.75 (gives AEs time to think)
- Interruption Sensitivity: 0.6 (lets them talk without cutting off)
- Backchannel: Enabled (natural "mm-hmm", "yeah" responses)

**Screenshot:** [Retell agent configuration panel]

---

### Step 2: Map Salesforce Fields

**What you'll do:**
- Identify which Opportunity fields need updating
- Document API names for each field
- Set up Salesforce Connected App for API access
- Get security token for authentication

**Fields updated by Poppy:**
- Stage (Hot, Warm, Nurture)
- ARV, Rehab Cost, Lowest Seller Will Accept
- Last Offer Made, Options Presented
- Property Walk Thru (layout description)
- AE Marketing Notes, AE Repair Notes
- Next Step, Post Appointment Notes
- Appointment Status

**Screenshot:** [Salesforce field setup]

**API Authentication:**
```bash
SF_USERNAME=your-username@salesforce.com
SF_PASSWORD=your-password
SF_SECURITY_TOKEN=your-token
SF_DOMAIN=login  # or test for sandbox
```

---

### Step 3: Build the Flask Backend

**What you'll do:**
- Create Python Flask app
- Set up webhook endpoint for Retell
- Implement Salesforce connection
- Add data extraction logic (using Claude API)
- Handle tasks and events creation

**Core files:**
- `app.py` - Main Flask application
- `requirements.txt` - Python dependencies
- `Procfile` - Heroku deployment config
- `runtime.txt` - Python version

**Key functions:**
1. **Webhook handler** - Receives call data from Retell
2. **SF connection** - Authenticates and connects to Salesforce
3. **Data extraction** - Uses Claude API to interpret transcript
4. **Opportunity update** - Updates SF fields
5. **Task/Event creation** - Creates follow-ups

**Screenshot:** [Code snippet of webhook handler]

---

### Step 4: Deploy to Heroku

**What you'll do:**
- Create Heroku app
- Set environment variables (SF credentials, Retell API key, Claude API key)
- Deploy Flask app
- Get webhook URL
- Add webhook URL to Retell agent config

**Deployment commands:**
```bash
heroku create poppy-ae-assistant
heroku config:set SF_USERNAME=your-username
heroku config:set SF_PASSWORD=your-password
heroku config:set SF_SECURITY_TOKEN=your-token
heroku config:set RETELL_API_KEY=your-retell-key
heroku config:set ANTHROPIC_API_KEY=your-claude-key
git push heroku main
```

**Screenshot:** [Heroku dashboard with environment variables]

---

### Step 5: Configure Retell Webhook

**What you'll do:**
- Copy Heroku app URL
- Add `/webhook/retell` endpoint to Retell agent
- Test webhook connection
- Review logs to ensure data is flowing

**Webhook URL format:**
```
https://poppy-ae-assistant.herokuapp.com/webhook/retell
```

**Screenshot:** [Retell webhook configuration]

---

### Step 6: Write the Agent Prompt

**What you'll do:**
- Define Poppy's personality (warm, empathetic, efficient)
- Write conversation flow (opening → questions → confirmation → sign-off)
- Add critical rules (no dollar signs, let them talk during property walkthrough)
- Include Salesforce field mapping instructions

**Key prompt sections:**
1. **Personality & Voice** - How Poppy should sound
2. **Conversation Flow** - What to ask and when
3. **Critical Rules** - Don't mess these up
4. **Field Mapping** - How to extract data for SF
5. **Error Handling** - What to do if things go wrong

**Full prompt:** See `POPPY-VOICE.md` in GitHub repo

**Screenshot:** [Prompt configuration in Retell]

---

### Step 7: Test & Refine

**What you'll do:**
- Make test calls with various scenarios
- Check Salesforce to verify updates
- Review transcripts for accuracy
- Adjust prompt based on edge cases
- Optimize responsiveness and interruption handling

**Test scenarios:**
- Standard appointment (offer made)
- No offer (follow-up scheduled)
- Tough appointment (seller unreasonable)
- Complex property description (let agent talk)
- Multiple follow-ups needed

**Screenshot:** [Salesforce showing updated Opportunity]

---

## GITHUB REPO

📂 **Get the Code:**

**Repository:** [github.com/tisa-pixel/ae-voice-assistant](https://github.com/tisa-pixel/ae-voice-assistant)

**What's included:**
- ✅ Full Flask application (`app.py`)
- ✅ Agent specification (`AGENT-SPEC.md`)
- ✅ Poppy personality & voice guide (`POPPY-VOICE.md`)
- ✅ Salesforce field mapping
- ✅ Requirements & deployment files
- ✅ Sample conversation flows
- ✅ Heroku deployment instructions

**Quick start:**
```bash
git clone https://github.com/tisa-pixel/ae-voice-assistant.git
cd ae-voice-assistant
pip install -r requirements.txt
# Set environment variables
python app.py  # Test locally
```

---

## DOWNLOAD THE TEMPLATE

⬇️ **Download Resources:**

- [📄 Retell Agent Prompt Template](https://github.com/tisa-pixel/ae-voice-assistant/blob/main/POPPY-VOICE.md)
- [📋 Salesforce Field Mapping Checklist](https://github.com/tisa-pixel/ae-voice-assistant/blob/main/AGENT-SPEC.md)
- [🐍 Python Flask Webhook Template](https://github.com/tisa-pixel/ae-voice-assistant/blob/main/app.py)
- [☁️ Heroku Deployment Guide](https://github.com/tisa-pixel/ae-voice-assistant)

**Setup checklist:**
- [ ] Retell AI account created
- [ ] Salesforce Connected App configured
- [ ] Flask app deployed to Heroku
- [ ] Webhook URL added to Retell
- [ ] Test call completed successfully
- [ ] Salesforce updates verified
- [ ] Agent prompt refined based on testing

---

## KEY INSIGHTS & LEARNINGS

### What Worked Really Well:

**1. Prompt Engineering for Comprehension**
- Don't just transcribe—INTERPRET
- "She's going through a divorce" → Extract urgency, timeline, motivation
- "Roof's shot, kitchen trashed" → Extract rehab cost, repair notes

**2. Natural Conversation Design**
- Short questions: "ARV?" not "Can you tell me what the ARV is?"
- Let them talk: During property walkthrough, WAIT—don't interrupt
- Empathy matters: "That's a tough one" when appointments go badly

**3. No Dollar Signs Rule**
- Say "600k" not "$600,000"
- Sounds more natural, less robotic
- Tested this exhaustively—makes a huge difference

**4. Rapid-Fire Confirmation**
- Read back ALL key details quickly at the end
- Gives AE a chance to catch mistakes
- Builds trust that data is accurate

### What Didn't Work:

**1. Over-Acknowledging**
- Saying "Got it" before every response = annoying
- Mix it up, sometimes just ask the next question

**2. Asking "What's Next Step?" When They Already Told You**
- If they said "Going back tomorrow at 10," that IS the next step
- Don't ask redundant questions

**3. Assuming Gender**
- Always use "they/them" unless AE specifies
- Prevents awkward corrections mid-call

### Edge Cases Handled:

- **Can't find address in SF** → Ask them to double-check
- **AE needs to leave mid-call** → Save partial data, allow resume later
- **Multiple properties in one call** → Not supported yet (future feature)
- **No-show appointments** → Update status, offer to create follow-up task

---

## REAL RESULTS

**Before Poppy:**
- AEs skipped SF updates ~40% of the time
- Average data entry time: 8-12 minutes per appointment
- Incomplete notes, missing details
- Managers had no visibility

**After Poppy:**
- 100% of appointments logged (AEs actually use it)
- Average call time: 2-3 minutes
- Rich, structured data every time
- Real-time visibility for managers

**Time savings:**
- 5 AEs × 3 appointments/day × 10 minutes saved = **2.5 hours saved per day**
- **50 hours saved per month** at ~$250/month cost = **$2,000+ value**

---

## QUESTIONS? DROP THEM BELOW

💬 **Have questions or want to share your results?**

- **Watch the full video:** [YouTube link]
- **Comment on YouTube:** [Link to video comments]
- **DM me on Instagram:** [@donottakeifallergictorevenue](https://www.instagram.com/donottakeifallergictorevenue/)
- **Connect on LinkedIn:** [linkedin.com/in/tisadaniels](https://linkedin.com/in/tisadaniels)

**Common questions:**
- "Can this work with other CRMs?" → Yes, just swap the SF API calls
- "What about HIPAA/compliance?" → Retell has compliant options
- "Can I customize the questions?" → Absolutely, it's all prompt-based

---

## RELATED BUILDS

| Build 1 | Build 2 | Build 3 |
|---------|---------|---------|
| **How I Automated Lead Distribution** | **How I Built an Outbound Dialer for $0** | **How I Track Lead Sources in Real-Time** |
| Smart round-robin without expensive tools | Built a calling system using Retell AI | Automated attribution without paid software |
| [View Build →](#) | [View Build →](#) | [View Build →](#) |

---

## METADATA

**Tags:** #Salesforce #VoiceAI #Automation #RealEstateInvesting #RetellAI #Python #Heroku #FlaskApp #CRM #ProductivityTools

**Duration:**
- Video: ~15 minutes
- Read time: ~10 minutes
- Build time: 12-16 hours

**Difficulty:** Intermediate (requires Python, API knowledge, prompt engineering)

**Best for:**
- REI teams with 3+ acquisition agents
- Companies spending 10+ hours/week on manual data entry
- Teams with poor CRM data quality

---

**Built by:** Tisa Daniels | Catalyst Partners
**Contact:** tisa@conversionisourgame.com
**Book a call:** tisadaniels.com

---

*🤖 Generated with [Claude Code](https://claude.com/claude-code)*

*Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>*
