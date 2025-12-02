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
- stage: One of [New Lead, Contacted, Appointment Set, Attended, Offer Made, Under Contract, Nurture, Closed Won, Closed Lost]
- nurture_reason: Only if stage is Nurture - one of [3-6 Months, 6-9 Months, 9-24 Months, Uncontacted, Cold, Property Currently List, Skiptrace Needed, SOLD, Check Back, Below Mortgage]
- appointment_attended: true/false - did the AE attend the appointment?
- arv: After Repair Value as integer (no $ or commas)
- rehab_cost: Estimated repair costs as integer
- last_offer: Last offer made to seller as integer
- lowest_accept: Lowest price seller will accept as integer
- options_presented: true/false - were purchase options presented?
- option_notes: Notes about option presentation
- obstacle: What's preventing contract signing
- next_step: What happens next
- post_appt_notes: General notes from the appointment
- marketing_notes: Marketing-related observations
- repair_notes: Details about property repairs needed
- not_closeable_reason: If not closeable, why?
- post_om_email_sent: true/false - was post-offer email sent?
- tasks: Array of tasks to create, each with "subject" and optional "due_date" (YYYY-MM-DD)

IMPORTANT:
- Convert dollar amounts to integers (e.g., "320k" = 320000, "$195,000" = 195000)
- Infer stage from context if not explicitly stated (e.g., if they made an offer, stage is likely "Offer Made")
- Extract emotional/motivation details into appropriate notes fields

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
        # Return first match but log that there were multiple
        return results['records'][0]

    # Try with just street number and name
    parts = clean_address.split()
    if len(parts) >= 2:
        partial = f"{parts[0]} {parts[1]}"
        query = f"SELECT Id, Name, StageName FROM Opportunity WHERE Name LIKE '%{partial}%' LIMIT 5"
        results = sf.query(query)
        if results['totalSize'] >= 1:
            return results['records'][0]

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
        'appointment_attended': 'Appointment_Attended__c',
        'arv': 'ARV__c',
        'rehab_cost': 'Estimated_Rehab_Costs__c',
        'last_offer': 'Last_Offer_Made__c',
        'lowest_accept': 'Lowest_price_seller_will_accept__c',
        'options_presented': 'Options_Presented__c',
        'option_notes': 'Option_Presentation_Notes__c',
        'obstacle': 'Obstacle_to_Contract__c',
        'next_step': 'NextStep',
        'post_appt_notes': 'Post_Appointment_Notes__c',
        'marketing_notes': 'AE_Marketing_Notes__c',
        'repair_notes': 'AE_Repair_Notes__c',
        'not_closeable_reason': 'Why_was_this_not_closable__c',
        'post_om_email_sent': 'Post_OM_Email_Sent__c'
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

        # Create any tasks
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
            logger.info(f"Created {len(tasks_created)} tasks")

        return jsonify({
            'status': 'success',
            'opportunity_id': opp['Id'],
            'opportunity_name': opp['Name'],
            'fields_updated': list(extracted.keys()) if extracted else [],
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
