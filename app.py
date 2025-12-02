"""
Poppy - AE Voice Assistant Backend
Handles Retell webhooks and updates Salesforce
"""
import os
import json
import re
import logging
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from simple_salesforce import Salesforce
import anthropic

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Salesforce connection
def get_sf_connection():
    return Salesforce(
        username=os.environ.get('SF_USERNAME'),
        password=os.environ.get('SF_PASSWORD'),
        security_token=os.environ.get('SF_SECURITY_TOKEN'),
        domain=os.environ.get('SF_DOMAIN', 'login')
    )

# Anthropic client for extraction
claude_client = anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))

def get_next_business_day():
    """Get the next business day (skip weekends)"""
    today = datetime.now()
    days_ahead = 1
    next_day = today + timedelta(days=days_ahead)
    # Skip Saturday (5) and Sunday (6)
    while next_day.weekday() >= 5:
        days_ahead += 1
        next_day = today + timedelta(days=days_ahead)
    return next_day.strftime('%Y-%m-%d')

def extract_data_from_transcript(transcript: str, property_address: str) -> dict:
    """Use GPT to extract structured data from conversation transcript"""

    extraction_prompt = f"""
Extract structured data from this sales call transcript. The AE is debriefing about an appointment at {property_address}.

TRANSCRIPT:
{transcript}

Extract the following fields (return null if not mentioned):
- stage: One of [Appointment Attended, Warm, Hot, Nurture, Contract Signed, Closed Won, Closed Lost]
  * Warm = interested but not urgent, needs follow-up
  * Hot = very interested, likely to close soon
  * Nurture = long-term follow-up needed
  * Contract Signed = got the contract signed
- nurture_reason: Only if stage is Nurture - one of [3-6 Months, 6-9 Months, 9-24 Months, Uncontacted, Cold, Property Currently List, Skiptrace Needed, SOLD, Check Back, Below Mortgage]
- appt_status: One of [Scheduled, Attended, No-Show, Cancelled, Rescheduled] - status of the appointment
- appointment_attended: true/false - did the AE attend the appointment? (usually true for debrief calls)
- ae_in_attendance: Name of the AE who attended (if mentioned)
- arv: After Repair Value as integer (no $ or commas)
- rehab_cost: Estimated repair costs as integer
- last_offer: Last offer made to seller as integer
- lowest_accept: Lowest price seller will accept as integer
- options_presented: true/false - were purchase options presented to the seller?
- option_notes: Notes about option presentation - what options were discussed
- obstacle: What's preventing contract signing right now
- property_walk_thru: Notes from the property walkthrough - condition, observations, etc.
- seller_declined_offer: One of [Yes, No, Counter Offered, Considering, No Response] - did the seller decline the offer price?
- next_step: What happens next
- post_appt_notes: General notes from the appointment
- marketing_notes: Marketing-related observations
- repair_notes: Details about property repairs needed
- not_closeable_reason: Why did the AE leave without a signed contract? (e.g., price gap, seller needs time, competing offers, title issues, etc.) - ALWAYS populate this if no contract was signed
- tasks: Array of tasks to create, each with "subject" and optional "due_date" (YYYY-MM-DD)

IMPORTANT:
- Convert dollar amounts to integers (e.g., "320k" = 320000, "$195,000" = 195000)
- For stage: ONLY extract if the AE explicitly states the stage (e.g., "this is a hot lead", "put them in nurture", "mark it warm"). Do NOT guess or infer the stage - return null if not explicitly mentioned.
- Extract emotional/motivation details into appropriate notes fields
- If no contract was signed at the appointment, ALWAYS extract not_closeable_reason - what prevented the close?

Return valid JSON only, no markdown formatting.
"""

    response = claude_client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system="You extract structured data from sales call transcripts. Return only valid JSON, no markdown formatting or code blocks.",
        messages=[
            {"role": "user", "content": extraction_prompt}
        ]
    )

    try:
        content = response.content[0].text
        # Strip any markdown code blocks if present
        content = re.sub(r'^```json\s*', '', content)
        content = re.sub(r'^```\s*', '', content)
        content = re.sub(r'\s*```$', '', content)
        return json.loads(content)
    except json.JSONDecodeError:
        # Try to extract JSON from response
        match = re.search(r'\{.*\}', content, re.DOTALL)
        if match:
            return json.loads(match.group())
        return {}

def normalize_address(address: str) -> str:
    """Normalize address for better matching"""
    addr = address.lower().strip()
    # Standardize common abbreviations
    replacements = {
        ' street': ' st', ' st.': ' st',
        ' avenue': ' ave', ' ave.': ' ave',
        ' drive': ' dr', ' dr.': ' dr',
        ' road': ' rd', ' rd.': ' rd',
        ' boulevard': ' blvd', ' blvd.': ' blvd',
        ' lane': ' ln', ' ln.': ' ln',
        ' court': ' ct', ' ct.': ' ct',
        ' place': ' pl', ' pl.': ' pl',
        ' circle': ' cir', ' cir.': ' cir',
        ' west': ' w', ' w.': ' w',
        ' east': ' e', ' e.': ' e',
        ' north': ' n', ' n.': ' n',
        ' south': ' s', ' s.': ' s',
        ',': '', ' - ': ' ', '-': ' ',
    }
    for old, new in replacements.items():
        addr = addr.replace(old, new)
    return addr

def find_opportunity_by_address(sf, address: str) -> dict:
    """Find an Opportunity by address (Name field)"""
    # Clean up address for search
    clean_address = address.strip().replace("'", "\\'")

    # Try exact match first
    query = f"SELECT Id, Name, StageName FROM Opportunity WHERE Name LIKE '%{clean_address}%' LIMIT 5"
    results = sf.query(query)

    if results['totalSize'] == 1:
        return results['records'][0]
    elif results['totalSize'] > 1:
        return results['records'][0]

    # Try with just street number and street name (first 2-3 words)
    parts = clean_address.split()
    if len(parts) >= 2:
        # Try "4116 W Iowa" style (number + direction + street)
        partial = f"{parts[0]} {parts[1]}"
        query = f"SELECT Id, Name, StageName FROM Opportunity WHERE Name LIKE '%{partial}%' LIMIT 5"
        results = sf.query(query)
        if results['totalSize'] >= 1:
            return results['records'][0]

    # Try normalized matching - normalize both input and search by street number
    if len(parts) >= 1 and parts[0].isdigit():
        street_num = parts[0]
        # Search by street number and check normalized versions
        query = f"SELECT Id, Name, StageName FROM Opportunity WHERE Name LIKE '{street_num}%' LIMIT 20"
        results = sf.query(query)

        if results['totalSize'] >= 1:
            normalized_input = normalize_address(address)
            for record in results['records']:
                normalized_name = normalize_address(record['Name'])
                # Check if key parts match
                if normalized_input.split()[0] in normalized_name:
                    # Same street number, check street name
                    input_words = set(normalized_input.split())
                    name_words = set(normalized_name.split())
                    # If they share the street number and at least one other word
                    if len(input_words & name_words) >= 2:
                        return record

    return None

def find_user_by_phone(sf, phone: str) -> dict:
    """Find a Salesforce User by phone number"""
    clean_phone = re.sub(r'\D', '', phone)[-10:]  # Last 10 digits

    query = f"SELECT Id, Name FROM User WHERE Phone LIKE '%{clean_phone}%' OR MobilePhone LIKE '%{clean_phone}%' LIMIT 1"
    results = sf.query(query)

    if results['totalSize'] >= 1:
        return results['records'][0]
    return None

def update_opportunity(sf, opp_id: str, data: dict) -> bool:
    """Update Opportunity with extracted data"""
    update_fields = {}

    # Map extracted data keys to SF field API names
    field_mapping = {
        'stage': 'StageName',
        'nurture_reason': 'Nurture_Reason__c',
        'appt_status': 'Appt_Status__c',
        'appointment_attended': 'Appointment_Attended__c',
        'ae_in_attendance': 'AE_in_Attendance__c',
        'arv': 'ARV__c',
        'rehab_cost': 'Rehab_Cost__c',
        'last_offer': 'Last_Offer_Made__c',
        'lowest_accept': 'Lowest_price_seller_will_accept__c',
        'options_presented': 'Options_Presented__c',
        'option_notes': 'Option_Presentation_Notes__c',
        'obstacle': 'Obstacle_to_Contract__c',
        'property_walk_thru': 'Property_Walk_Thru__c',
        'seller_declined_offer': 'Did_Seller_Decline_Offer_Price__c',
        'next_step': 'Next_Step__c',
        'post_appt_notes': 'Post_Appointment_Notes__c',
        'marketing_notes': 'AE_Marketing_Notes__c',
        'repair_notes': 'AE_Repair_Notes__c',
        'not_closeable_reason': 'Why_was_this_not_closable__c',
    }

    for key, sf_field in field_mapping.items():
        if key in data and data[key] is not None:
            update_fields[sf_field] = data[key]

    if update_fields:
        sf.Opportunity.update(opp_id, update_fields)
        return True
    return False

def create_task(sf, opp_id: str, owner_id: str, subject: str, due_date: str = None) -> str:
    """Create a Task linked to an Opportunity"""
    if not due_date:
        due_date = get_next_business_day()

    task_data = {
        'Subject': subject,
        'WhatId': opp_id,
        'OwnerId': owner_id,
        'ActivityDate': due_date,
        'Status': 'Not Started',
        'Priority': 'Normal'
    }

    result = sf.Task.create(task_data)
    return result['id']

def log_call_activity(sf, opp_id: str, owner_id: str, call_data: dict, transcript: str) -> str:
    """Log the Poppy debrief call as a completed Task activity"""
    call_id = call_data.get('call_id', 'unknown')
    recording_url = call_data.get('recording_url', '')
    call_duration = call_data.get('call_length', 0)  # in seconds

    # Format duration as minutes:seconds
    minutes = int(call_duration // 60)
    seconds = int(call_duration % 60)
    duration_str = f"{minutes}:{seconds:02d}"

    # Build description with links and transcript
    description_parts = [
        f"Poppy AE Debrief Call",
        f"Duration: {duration_str}",
        f"Call ID: {call_id}",
    ]

    if recording_url:
        description_parts.append(f"\nRecording: {recording_url}")

    # Add transcript (truncate if too long - SF has 32k limit)
    if transcript:
        max_transcript_len = 30000  # Leave room for other content
        if len(transcript) > max_transcript_len:
            transcript = transcript[:max_transcript_len] + "\n\n[Transcript truncated]"
        description_parts.append(f"\n\n--- TRANSCRIPT ---\n{transcript}")

    description = "\n".join(description_parts)

    task_data = {
        'Subject': 'Poppy Debrief Call',
        'WhatId': opp_id,
        'OwnerId': owner_id,
        'ActivityDate': datetime.now().strftime('%Y-%m-%d'),
        'Status': 'Completed',
        'Priority': 'Normal',
        'Description': description,
        'CallDurationInSeconds': int(call_duration) if call_duration else None
    }

    # Remove None values
    task_data = {k: v for k, v in task_data.items() if v is not None}

    result = sf.Task.create(task_data)
    return result['id']

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'agent': 'Poppy'})

@app.route('/webhook/retell', methods=['POST'])
def retell_webhook():
    """Handle Retell webhook for call events"""
    data = request.json
    event_type = data.get('event')
    logger.info(f"Webhook received: event_type={event_type}, keys={list(data.keys())}")

    if event_type == 'call_ended':
        return handle_call_ended(data)
    elif event_type == 'call_analyzed':
        return handle_call_analyzed(data)

    return jsonify({'status': 'ok'})

def extract_address_from_transcript(transcript: str) -> str:
    """Use Claude to extract the property address from transcript"""
    response = claude_client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=100,
        system="Extract the property address from this call transcript. Return ONLY the address (like '2922 N 12th St' or '123 Main Street'), nothing else. If no address found, return 'NONE'.",
        messages=[
            {"role": "user", "content": transcript}
        ]
    )
    address = response.content[0].text.strip()
    return None if address == 'NONE' else address

def handle_call_ended(data: dict):
    """Process a completed call"""
    # Retell can send call data nested under 'call' or at top level
    call_data = data.get('call', data)
    transcript = call_data.get('transcript', '')
    caller_number = call_data.get('from_number', '')

    logger.info(f"Processing call_ended. Transcript length: {len(transcript)}, from: {caller_number}")
    logger.info(f"Call data keys: {list(call_data.keys())}")

    if not transcript:
        logger.warning("No transcript in call data")
        return jsonify({'status': 'no_transcript'})

    try:
        sf = get_sf_connection()
        logger.info("SF connection established")

        # Find the user (AE) by phone
        user = find_user_by_phone(sf, caller_number)
        owner_id = user['Id'] if user else None
        logger.info(f"User lookup: {user['Name'] if user else 'Not found'}")

        # Extract property address using Claude (much smarter than regex)
        property_address = extract_address_from_transcript(transcript)
        logger.info(f"Extracted address: {property_address}")

        if not property_address:
            logger.warning("Could not extract address from transcript")
            return jsonify({'status': 'no_address_found', 'message': 'Could not identify property address'})

        # Find the Opportunity
        opp = find_opportunity_by_address(sf, property_address)
        if not opp:
            logger.warning(f"Opportunity not found for address: {property_address}")
            return jsonify({'status': 'opportunity_not_found', 'address': property_address})

        logger.info(f"Found opportunity: {opp['Name']} ({opp['Id']})")

        # Extract structured data from transcript
        extracted = extract_data_from_transcript(transcript, property_address)
        logger.info(f"Extracted data keys: {list(extracted.keys()) if extracted else 'None'}")

        # Update the Opportunity
        if extracted:
            update_opportunity(sf, opp['Id'], extracted)
            logger.info(f"Updated opportunity {opp['Id']}")

        # Log the call as an activity
        call_activity_id = None
        if owner_id:
            call_activity_id = log_call_activity(sf, opp['Id'], owner_id, call_data, transcript)
            logger.info(f"Logged call activity: {call_activity_id}")

        # Create any follow-up tasks from extracted data
        tasks_created = []
        if extracted.get('tasks') and owner_id:
            for task in extracted['tasks']:
                task_id = create_task(
                    sf,
                    opp['Id'],
                    owner_id,
                    task.get('subject', 'Follow up'),
                    task.get('due_date')
                )
                tasks_created.append(task_id)
            logger.info(f"Created {len(tasks_created)} follow-up tasks")

        return jsonify({
            'status': 'success',
            'opportunity_id': opp['Id'],
            'opportunity_name': opp['Name'],
            'fields_updated': list(extracted.keys()) if extracted else [],
            'call_activity_id': call_activity_id,
            'tasks_created': tasks_created
        })

    except Exception as e:
        logger.error(f"Error processing call: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

def handle_call_analyzed(data: dict):
    """Handle post-call analysis from Retell"""
    # This can be used for additional processing after Retell's analysis
    return jsonify({'status': 'ok'})

@app.route('/webhook/retell/function', methods=['POST'])
def retell_function_call():
    """Handle real-time function calls from Retell during the call"""
    data = request.json
    function_name = data.get('function_name')
    args = data.get('arguments', {})

    if function_name == 'lookup_property':
        return lookup_property(args.get('address'))
    elif function_name == 'update_opportunity':
        return update_opp_from_call(args)
    elif function_name == 'create_task':
        return create_task_from_call(args)

    return jsonify({'error': 'Unknown function'})

def lookup_property(address: str):
    """Look up a property during the call"""
    try:
        sf = get_sf_connection()
        opp = find_opportunity_by_address(sf, address)

        if opp:
            return jsonify({
                'found': True,
                'opportunity_id': opp['Id'],
                'name': opp['Name'],
                'current_stage': opp.get('StageName')
            })
        else:
            return jsonify({'found': False, 'message': f"No property found matching '{address}'"})
    except Exception as e:
        return jsonify({'found': False, 'error': str(e)})

def update_opp_from_call(args: dict):
    """Update opportunity during the call"""
    try:
        sf = get_sf_connection()
        opp_id = args.get('opportunity_id')

        if not opp_id and args.get('address'):
            opp = find_opportunity_by_address(sf, args['address'])
            if opp:
                opp_id = opp['Id']

        if not opp_id:
            return jsonify({'success': False, 'message': 'Opportunity not found'})

        update_opportunity(sf, opp_id, args)
        return jsonify({'success': True, 'opportunity_id': opp_id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def create_task_from_call(args: dict):
    """Create a task during the call"""
    try:
        sf = get_sf_connection()
        opp_id = args.get('opportunity_id')

        if not opp_id and args.get('address'):
            opp = find_opportunity_by_address(sf, args['address'])
            if opp:
                opp_id = opp['Id']

        if not opp_id:
            return jsonify({'success': False, 'message': 'Opportunity not found'})

        # Default owner - would need to be passed or looked up
        owner_id = args.get('owner_id')

        task_id = create_task(
            sf,
            opp_id,
            owner_id,
            args.get('subject', 'Follow up'),
            args.get('due_date')
        )

        return jsonify({'success': True, 'task_id': task_id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
