from flask import Flask, request, make_response, Response
from env_variables import SLACK_BOT_TOKEN, CHANNEL_ID
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import openai
from env_variables import OPENAI_API_KEY


# Initialize Slack API client
client = WebClient(token=SLACK_BOT_TOKEN)
openai.api_key = OPENAI_API_KEY
app = Flask(__name__)

# Initialize set to store processed event IDs
processed_event_ids = set()

@app.route('/slack/events', methods=['POST'])
def slack_events():
    if request.headers.get('Content-Type') == 'application/json':
        data = request.json
        
        # Complete the URL Verification Challenge
        if data['type'] == 'url_verification':
            return make_response(data['challenge'], 200, {'Content-Type': 'text/plain'})
        
        # Respond to @ mentions
        elif data['type'] == 'event_callback':
            if data['event']['type'] == 'app_mention':
                
                event_id = data['event']['client_msg_id']
                # Ignore any events with the same ID that have already been processed
                if event_id in processed_event_ids:
                    print(f"Ignoring duplicate event with ID {event_id}")
                    return Response(status=200)
                else:
                    processed_event_ids.add(event_id)

                try:
                # Call the chat_postMessage method to send the message
                    message = data['event']['text']

                    question = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[
                        {"role":"user",
                        "content":message}],
                        temperature=0,
                        max_tokens=200,
                        top_p=1,
                        frequency_penalty=0.0,
                        presence_penalty=0.0)
                    
                    response = question['choices'][0]['message']['content']
                    status = client.chat_postMessage(channel=CHANNEL_ID, text=response)
                    return make_response('', 200)
                except SlackApiError as e:
                    print("Error sending message: ", e)
    return make_response('', 404)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
