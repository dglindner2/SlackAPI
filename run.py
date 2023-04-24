from flask import Flask, request, make_response, Response
from env_variables import SLACK_BOT_TOKEN, CHANNEL_ID, OPENAI_API_KEY, BOT_ID
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import openai
import chat
import json

# Initialize Slack API client
client = chat.init_client(SLACK_BOT_TOKEN)

# Set API Key
openai.api_key = OPENAI_API_KEY

# Initialize set to store processed event IDs
processed_event_ids = set()

app = Flask(__name__)
@app.route('/slack/events', methods=['POST'])
def slack_events():
    if request.headers.get('Content-Type') == 'application/json':
        data = request.json
        
        # Complete the URL Verification Challenge
        if data['type'] == 'url_verification':
            return make_response(data['challenge'], 200, {'Content-Type': 'text/plain'})
        
        elif data['type'] == 'event_callback':
            # Respond to @ mentions
            if data['event']['type'] == 'app_mention':
                event_id = data['event']['client_msg_id']
                event_ts = data['event']['ts']

                # Ignore any events with the same ID that have already been processed
                if event_id in processed_event_ids:
                    print(f"Ignoring duplicate event with ID {event_id}")
                    return Response(status=200)
                else:
                    processed_event_ids.add(event_id)

                try:
                # Call the chat_postMessage method to send response in message thread
                    message = data['event']['text']
                    response = chat.call_gpt(message)
                    client.chat_postMessage(channel=CHANNEL_ID, text=response, thread_ts=event_ts)
                    return make_response('', 200)
                except SlackApiError as e:
                    print("Error sending message: ", e)
            
            # Respond to subsequent posts in a thread
            elif data['event']['type'] == 'message' and 'thread_ts' in data['event'] and 'client_msg_id' in data['event']:
                event_id = data['event']['client_msg_id']
                event_ts = data['event']['ts']
                thread_ts = data['event']['thread_ts']
                
                # Ignore any events with the same ID that have already been processed
                if event_id in processed_event_ids:
                    print(f"Ignoring duplicate event with ID {event_id}")
                    return Response(status=200)
                else:
                    processed_event_ids.add(event_id)
                
                # Check if bot was mentioned in original message
                original_message = client.conversations_history(
                    channel=data['event']['channel'],
                    latest=thread_ts,
                    limit=1
                )['messages'][0]
                
                if f"<@{BOT_ID}>" in original_message['text']:
                    # Obtain the thread history to pass to ChatGPT for memory in conversations
                    thread_history = chat.get_thread_history(client, CHANNEL_ID, thread_ts)
                    
                    # Reduce thread history if too long to reduce API call costs
                    chat.reduce_input_token_len(thread_history)
                    thread_history = json.dumps(thread_history)[1:-1]
                    try:
                        # Pass Thread History to ChatGPT
                        response = chat.call_gpt(thread_history)
                        response = json.loads(response).get("content")                
                        
                        # Return the response in Slack Thread
                        client.chat_postMessage(
                            channel=data['event']['channel'],
                            text=response,
                            thread_ts=thread_ts)
                        
                        return make_response('', 200)
                    except SlackApiError as e:
                        
                        client.chat_postMessage(
                            channel=data['event']['channel'],
                            text="Slack API Error: Retry Sending your message.",
                            thread_ts=thread_ts
                        )
                        print("Error sending message: ", e)
                else:
                    return make_response('', 404)
    return make_response('', 404)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
