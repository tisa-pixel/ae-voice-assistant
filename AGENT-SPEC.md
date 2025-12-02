# AE Voice Assistant - Agent Specification

## Overview

Voice AI agent (via Retell) that enables Account Executives / Acquisition Agents to:
1. **Post-Appointment Debrief** - Natural conversation that updates Salesforce with comprehension, not just transcription
2. **Task Creation** - "Remind me to..." creates SF Tasks linked to the correct Opportunity
3. **Quick Updates** - Direct field updates without full debrief

## Technology Stack

- **Voice**: Retell AI
- **Backend**: Heroku (Python/Flask)
- **CRM**: Salesforce REST API
- **Org**: tisa289@agentforce.com

---

## Conversation Flow (Hybrid)

### Opening
```
AGENT: "Hey, what property are we updating?"
```

### Natural Debrief
AE talks freely about the appointment. Agent listens and extracts structured data.

### Confirmation
Agent reads back all extracted fields before saving:
```
AGENT: "Let me confirm what I'm updating:
- Stage: [value]
- ARV: [value]
- [etc...]

Anything I missed or got wrong?"
```

### Reminders (End of Every Debrief)
```
AGENT: "Quick reminders:
- Upload photos and video
- Upload appointment recording

Anything else?"
```

### Task Creation
```
AE: "Create a task to send a follow-up email"
AGENT: "Created task: 'Send follow-up email' for [address], due [next business day]. All set?"
```

---

## Salesforce Field Mapping

### Opportunity Fields - MANDATORY (Agent must ask if not mentioned)

| Field | SF API Name | Type | Notes |
|-------|-------------|------|-------|
| Stage | `StageName` | Picklist | New Lead → Contacted → Appointment Set → Attended → Offer Made → Under Contract → Nurture → Closed Won/Lost |
| Nurture Reason | `Nurture_Reason__c` | Picklist | Only required if Stage = Nurture |
| Next Step | `NextStep` | Text | |
| ARV (Post Appt) | `ARV__c` | Currency | |
| Rehab Cost | `Estimated_Rehab_Costs__c` | Currency | |
| Lowest Offer Seller will accept | `Lowest_price_seller_will_accept__c` | Currency | |
| Last Offer Made | `Last_Offer_Made__c` | Currency | |
| Were Options Presented? | `Options_Presented__c` | Checkbox | **NEW FIELD** |
| Option Presentation Notes | `Option_Presentation_Notes__c` | Long Textarea | **NEW FIELD** |
| Obstacle to Contract Signed | `Obstacle_to_Contract__c` | Long Textarea | **NEW FIELD** |
| Post OM Email Sent | `Post_OM_Email_Sent__c` | Checkbox | **NEW FIELD** |
| AE Marketing Notes | `AE_Marketing_Notes__c` | Textarea | |
| AE Repair Notes | `AE_Repair_Notes__c` | Textarea | |
| Why was this not closeable? | `Why_was_this_not_closable__c` | Text | |
| Property Walk Thru | `Property_Walk_Thru__c` | Long Textarea | **NEW FIELD** |
| Appointment Status | `Appointment_Status__c` | Picklist | Scheduled, Attended, No-Show, Cancelled, Rescheduled **NEW FIELD** |
| Post Appt Notes | `Post_Appointment_Notes__c` | Textarea | |

### Stage Values (Updated)

| Stage | Description |
|-------|-------------|
| New Lead | Fresh lead, not yet contacted |
| Contacted | Initial contact made |
| Appointment Set | Appointment scheduled |
| Attended | Appointment completed |
| Offer Made | Offer presented to seller |
| Under Contract | Signed contract |
| Nurture | Long-term follow-up (requires Nurture Reason) |
| Closed Won | Deal closed successfully |
| Closed Lost | Deal lost |

### Task Fields

| Field | SF API Name | Type | Default |
|-------|-------------|------|---------|
| Subject | `Subject` | Text | From AE request |
| Due Date | `ActivityDate` | Date | Next business day |
| Related To | `WhatId` | Reference | Opportunity ID |
| Assigned To | `OwnerId` | Reference | Calling AE |
| Status | `Status` | Picklist | Not Started |
| Priority | `Priority` | Picklist | Normal |

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
- Estimated Rehab Costs: $40,000
- AE Repair Notes: "Roof replacement needed, kitchen damaged"

### Example 3: Negotiation Status
**AE says**: "Offered 195, she wants 220, told her I'd check with my partner"
**Agent extracts**:
- Last Offer Made: $195,000
- Lowest price seller will accept: $220,000
- Stage: Offer Made (or Negotiation if already past that)
- Next Step: "Follow up after checking with partner"

### Example 4: Obstacles
**AE says**: "Main thing is she's lived there 20 years, hard to let go"
**Agent extracts**:
- Obstacle to Contract Signed: "Emotional attachment - lived in property 20 years"

---

## Identification Logic

### AE Identification
- Phone number → SF User lookup
- Or prompt: "Who am I speaking with?"

### Opportunity Identification
- AE states address: "Just left 1847 Elm Street"
- Agent queries SF: `SELECT Id, Name FROM Opportunity WHERE Name LIKE '%1847 Elm%'`
- If multiple matches: "I found a few properties with that address. Did you mean [options]?"
- If no match: "I couldn't find that address. Want me to create a task to update it manually?"

---

## Error Handling

| Scenario | Response |
|----------|----------|
| Can't find Opportunity | "I couldn't find that address in Salesforce. Can you double-check? Or I can create a task to update it manually." |
| Missing required field | "I didn't catch the [field]. What's the [field]?" |
| Ambiguous data | "Just to clarify - when you said [X], did you mean [interpretation]?" |
| SF API error | "I'm having trouble connecting to Salesforce. Want me to try again, or create a task for manual update?" |

---

## Reminders

At the end of every appointment debrief (not for task-only calls):

```
AGENT: "Quick reminders:
- Upload photos and video
- Upload appointment recording

Anything else?"
```

---

## Sample Conversations

### Full Debrief Flow
```
AE: *calls in*

AGENT: "Hey, what property are we updating?"

AE: "Just finished at 1847 Elm Street"

AGENT: "Got it, 1847 Elm. Tell me how it went."

AE: "Good meeting. Seller is motivated, going through a divorce, wants to close in 30 days. House needs work - roof and kitchen mainly, I'd say 40k. ARV around 320. I offered 195, she countered at 220. Presented all the options, she's leaning cash but wants to think about it. Main obstacle is emotional - she's lived there 20 years."

AGENT: "Got it. Here's what I'm updating:
- Stage: Offer Made
- ARV: $320,000
- Estimated Rehab: $40,000
- Last Offer Made: $195,000
- Lowest she'll accept: $220,000
- Options Presented: Yes
- Obstacle: Emotional attachment - lived there 20 years
- Next Step: Follow up - seller considering options
- Appointment Status: Attended

Anything I missed or got wrong?"

AE: "Add to the notes that her ex might need to sign too, could complicate things"

AGENT: "Added to post-appointment notes.

Quick reminders:
- Upload photos and video
- Upload appointment recording

Anything else?"

AE: "Yeah, task me to follow up with her Thursday"

AGENT: "Created task: 'Follow up with seller' for 1847 Elm, due Thursday. All set?"

AE: "That's it, thanks"

AGENT: "Done. Talk soon."
```

### Task-Only Call
```
AE: *calls in*

AGENT: "Hey, what property are we updating?"

AE: "No debrief, just need a task. Remind me to send a proposal to the seller at 555 Oak Ave"

AGENT: "Got it. Task: 'Send proposal to seller' for 555 Oak Ave, due tomorrow. Anything else?"

AE: "Nope"

AGENT: "Done."
```

---

## Next Steps

1. [ ] Deploy SF field metadata to org
2. [ ] Build Heroku backend with SF integration
3. [ ] Create Retell agent with this prompt/logic
4. [ ] Test with sample calls
5. [ ] Iterate based on real AE feedback
