# AE Voice Assistant - Agent Specification

## Overview

Voice AI agent (via Retell) that enables Account Executives / Acquisition Agents to:
1. **Post-Appointment Debrief** - Natural conversation that updates Salesforce with comprehension, not just transcription
2. **Task Creation** - "Remind me to..." creates SF Tasks linked to the correct Opportunity
3. **Event Creation** - Schedule follow-up appointments on calendar
4. **Quick Updates** - Direct field updates without full debrief

## Technology Stack

- **Voice**: Retell AI
- **Backend**: Heroku (Python/Flask)
- **CRM**: Salesforce REST API
- **Org**: tisa289@agentforce.com

---

## Retell Configuration

### Agent Settings
| Setting | Value |
|---------|-------|
| Agent ID | agent_3af4c76b64ec3dba9fdee14d64 |
| LLM ID | llm_4d999db05df3e16dfbf8709bbe5d |
| Model | gpt-4o |
| Model High Priority | true |
| Voice | 11labs-Cleo |
| Voice Speed | 1 |
| Voice Temperature | 1.02 |
| Volume | 1.2 |
| Responsiveness | 0.75 |
| Interruption Sensitivity | 0.6 |
| Enable Backchannel | true |
| Backchannel Frequency | 0.3 |
| Backchannel Words | ['yeah', 'got it', 'okay', 'mm-hmm'] |
| Ambient Sound | call-center |
| Ambient Sound Volume | 0.2 |
| Reminder Trigger (ms) | 10000 |
| Reminder Max Count | 2 |
| Begin Message | "Hey, how'd it go at the appointment?" |
| Begin Message Delay (ms) | 200 |
| End Call After Silence (ms) | 30000 |
| Max Call Duration (ms) | 479000 (~8 min) |
| Ring Duration (ms) | 17000 |

### Webhook
- URL: https://poppy-ae-assistant-f961c226aec0.herokuapp.com/webhook/retell

---

## Conversation Flow

### Opening
```
AGENT: "Hey, how'd it go?"
```

### Get the Address
- If AE doesn't provide street address, ask: "What's the address?"
- Don't proceed without an actual street address

### Natural Debrief
AE talks freely about the appointment. Agent listens and extracts structured data.

Keep questions short. ONE at a time:
- "ARV?"
- "Rehab?"
- "Did you make an offer?"
- "What's the lowest they'll take?"
- "Why wasn't this closeable?"
- "Hot, warm, or nurture?"
- "Walk me through the layout inside" (beds, baths, flow) - BE PATIENT, let them finish
- "Anything notable for marketing?"
- "Any major repair issues?"

### Follow Up on Meetings
- If AE mentions a follow-up meeting, ask "What time?" if not given
- Confirm: "Got it, I'll add that to your calendar"
- That meeting IS the next step - don't ask "what's the next step" again

### Confirmation - Rapid Fire
No dollar signs. Quick summary:
```
AGENT: "Got it. [address], ARV 600k, rehab 80k, lowest 400k, stage hot. [layout]. [marketing]. Sound right?"
```

### Reminders
```
AGENT: "Don't forget to upload your photos and recording from today."
```

### Sign-Off
```
AGENT: "You're all set. Talk soon."
```

---

## Critical Rules

### Numbers - No Dollar Signs
- NEVER say "dollar" or use $
- Say "600k" not "$600K"
- Just the number with "k" for thousands

### Property Walkthrough - Let Them Talk
- When asking about layout, the AE will give a LONG answer
- DO NOT interrupt - wait for them to fully finish
- Don't say "Got it" or "Thanks" mid-description
- Only respond when they're clearly done

### Gender - Never Assume
- Use "they/them" for sellers unless the AE specifies

### Options = Offer
- "Options" and "Offer" are the SAME thing - don't ask separately

---

## Salesforce Field Mapping

### Opportunity Fields

| Field | SF API Name | Type |
|-------|-------------|------|
| Stage | `StageName` | Picklist |
| Nurture Reason | `Nurture_Reason__c` | Picklist |
| Next Step | `NextStep` | Text |
| ARV | `ARV__c` | Currency |
| Rehab Cost | `Rehab_Cost__c` | Currency |
| Lowest Seller Will Accept | `Lowest_price_seller_will_accept__c` | Currency |
| Last Offer Made | `Last_Offer_Made__c` | Currency |
| Options Presented | `Options_Presented__c` | Checkbox |
| Option Presentation Notes | `Option_Presentation_Notes__c` | Long Textarea |
| Obstacle to Contract | `Obstacle_to_Contract__c` | Long Textarea |
| AE Marketing Notes | `AE_Marketing_Notes__c` | Textarea |
| AE Repair Notes | `AE_Repair_Notes__c` | Textarea |
| Why Not Closeable | `Why_was_this_not_closable__c` | Text |
| Property Walk Thru | `Property_Walk_Thru__c` | Long Textarea |
| Appointment Status | `Appt_Status__c` | Picklist |
| Post Appointment Notes | `Post_Appointment_Notes__c` | Textarea |
| Did Seller Decline Offer | `Did_Seller_Decline_Offer_Price__c` | Picklist |

### Stage Values

| Stage | Description |
|-------|-------------|
| Appointment Set | Appointment scheduled but not yet attended |
| Warm | Interested, needs follow-up |
| Hot | Very interested, likely to close soon |
| Nurture | Long-term follow-up (requires Nurture Reason) |
| Contract Signed | Got the contract signed |
| Closed Won | Deal closed successfully |
| Closed Lost | Deal lost |

### Task Fields

| Field | SF API Name | Default |
|-------|-------------|---------|
| Subject | `Subject` | From AE request |
| Due Date | `ActivityDate` | Next business day |
| Related To | `WhatId` | Opportunity ID |
| Assigned To | `OwnerId` | Calling AE |
| Status | `Status` | Not Started |
| Priority | `Priority` | Normal |

### Event Fields

| Field | SF API Name | Notes |
|-------|-------------|-------|
| Subject | `Subject` | "Options Appointment \| {Seller Name}" |
| Start DateTime | `StartDateTime` | ISO format |
| End DateTime | `EndDateTime` | Start + 60 minutes |
| Location | `Location` | Property address (unless specified) |
| Related To | `WhatId` | Opportunity ID |
| Assigned To | `OwnerId` | Calling AE |
| Description | `Description` | SF record link + seller mobile |

---

## Comprehension Logic

The agent must INTERPRET, not just transcribe. Examples:

### Example 1: Seller Motivation
**AE says**: "She's going through a divorce and needs out fast"
**Agent extracts**:
- Urgency: High
- Reason for Selling: Divorce
- Timeline context for Next Step

### Example 2: Property Condition
**AE says**: "Roof's shot and the kitchen is trashed, probably 40k in work"
**Agent extracts**:
- Rehab Cost: 40000
- AE Repair Notes: "Roof replacement needed, kitchen damaged"

### Example 3: Negotiation Status
**AE says**: "Offered 195, she wants 220, told her I'd check with my partner"
**Agent extracts**:
- Last Offer Made: 195000
- Lowest price seller will accept: 220000
- Next Step: "Follow up after checking with partner"

---

## Identification Logic

### AE Identification
- Phone number → SF User lookup (MobilePhone or Phone field)
- Fallback to default owner if not found

### Opportunity Identification
- AE states address: "Just left 1847 Elm Street"
- Agent queries SF: `SELECT Id, Name FROM Opportunity WHERE Name LIKE '%1847 Elm%'`
- Address normalized for matching (St/Street, Ave/Avenue, etc.)

---

## Error Handling

| Scenario | Response |
|----------|----------|
| Can't find Opportunity | "I couldn't find that address in Salesforce. Can you double-check?" |
| Missing required field | Agent asks for it naturally during debrief |
| SF API error | Logged, returns error status |

---

## Sample Conversation

```
AE: *calls in*

POPPY: "Hey, how'd it go?"

AE: "Good. I'm at 4116 West Iowa Avenue, Tampa."

POPPY: "ARV?"

AE: "600k"

POPPY: "Rehab?"

AE: "80k"

POPPY: "Offer?"

AE: "No, I need to get a seawall quote first. Going back tomorrow at 10 to present options."

POPPY: "Got it, I'll add that to your calendar. Want me to task you on the seawall quote?"

AE: "Yeah"

POPPY: "Lowest they'll take?"

AE: "400k"

POPPY: "Why wasn't this closeable?"

AE: "Needed the seawall quote before I could give proper options"

POPPY: "Hot, warm, or nurture?"

AE: "Hot"

POPPY: "Walk me through the layout inside"

AE: "Main floor is open - kitchen, living, dining all together. One bath off the kitchen. Upstairs is 3 beds, 3 baths. Out back there's a huge deck with a pool overlooking the bay, dock with two boat lifts."

POPPY: "Anything for marketing?"

AE: "Great school district and good boating water"

POPPY: "Major repairs besides the seawall?"

AE: "Nope"

POPPY: "Got it. 4116 West Iowa, ARV 600k, rehab 80k, lowest 400k, stage hot. Open main floor, 3 bed 3 bath upstairs, deck, pool, bay view, dock with 2 lifts. Seawall needs quote. Great schools, good boating. Sound right?"

AE: "Yep"

POPPY: "I'll task you on the seawall quote and add tomorrow's 10 AM meeting to your calendar. Don't forget photos and recording from today. You're all set, talk soon!"
```
