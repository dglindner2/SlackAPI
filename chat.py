import openai
import tiktoken
import re
from env_variables import OPENAI_API_KEY,SLACK_BOT_TOKEN, BOT_ID
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

openai.api_key = OPENAI_API_KEY

def init_client(SLACK_BOT_TOKEN):
    return WebClient(token=SLACK_BOT_TOKEN)

def get_thread_history(CLIENT,
                       CHANNEL: str, 
                       MESSAGE_TS: str):
    # Initialize list for holding conversation history
    history = []
    # Call the conversations.history method to get the conversation history
    try:
        result = CLIENT.conversations_replies(
            channel=CHANNEL,
            ts=MESSAGE_TS,
            inclusive=True,
            limit=100
        )
        messages = result['messages']
        # Loop through thread and create user/assistant conversation
        for message in messages:
            if 'thread_ts' in message and message['thread_ts'] == MESSAGE_TS:
                if message['user'] != BOT_ID:
                    update_message_history(message['text'], 'user', history)
                else:
                    update_message_history(message['text'], 'assistant', history)
            else:
                continue
        return history
    
    except SlackApiError as e:
        return "Error"

def remove_ai_language_model_sentence(text):
    pattern = r'As an AI language model[^.]*\.'
    result = re.sub(pattern, '', text)
    return result

def format_message(
        prompt: str,
        role: str
) -> dict:
    return [{"role":role,
            "content":prompt}]

def update_message_history(
        prompt: str, 
        role: str,
        message_history: list
        ) -> list:
    """
    Update the history of the Slack Thread for back-and-forth conversations with OpenAI's ChatGPT.
    """

    message_history.append(format_message(prompt, role)[0])
    
    return message_history

def reduce_input_token_len(
        message_history: list,
        max_tokens: int = 1024,
        max_output_token: int = 200,
        model: str = 'gpt-3.5-turbo'
    ) -> int:
    """
    Takes conversation history and limits the number of tokens OpenAI API will output based on the input
    """

    # Reserve tokens for the response from API Call
    # Max Input Tokens allowed should be Max Tokens less the maximum length of a response
    max_input_tokens = max_tokens - max_output_token

    # Format length of input message and get number of tokens
    #prompt = format_message(input, role="user")
    #prompt_length = get_token_len(prompt, model)
    token_length = get_token_len(message_history, model) #+ prompt_length

    # If the token_length is larger than we want to pass to the model, reduce the history
    while token_length > max_input_tokens:
        message_history.pop(0)
        token_length = get_token_len(message_history, model) #+ prompt_length

    return 1

def get_token_len(
    messages: list[dict[str, str]], 
    model: str = "gpt-3.5-turbo"
) -> int:
    """
    Returns the number of tokens used by a list of messages.
    Args:
        messages (list): A list of messages, each of which is a dictionary
            containing the role and content of the message.
        model (str): The name of the model to use for tokenization.
            Defaults to "gpt-3.5-turbo-0301".
    Returns:
        int: The number of tokens used by the list of messages.
    """
    try:
        encoder = tiktoken.encoding_for_model(model)
    except KeyError:
        encoder = tiktoken.get_encoding("cl100k_base")
    if model == "gpt-3.5-turbo":
        # !Note: gpt-3.5-turbo may change over time.
        # Returning num tokens assuming gpt-3.5-turbo-0301.")
        return get_token_len(messages, model="gpt-3.5-turbo-0301")
    elif model == "gpt-4":
        # !Note: gpt-4 may change over time. Returning num tokens assuming gpt-4-0314.")
        return get_token_len(messages, model="gpt-4-0314")
    elif model == "gpt-3.5-turbo-0301":
        tokens_per_message = (
            4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
        )
        tokens_per_name = -1  # if there's a name, the role is omitted
    elif model == "gpt-4-0314":
        tokens_per_message = 3
        tokens_per_name = 1
    else:
        raise NotImplementedError(
            f"num_tokens_from_messages() is not implemented for model {model}.\n"
            " See https://github.com/openai/openai-python/blob/main/chatml.md for"
            " information on how messages are converted to tokens."
        )
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoder.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens

def call_gpt(
            message,
            model: str = "gpt-3.5-turbo",
            max_tokens: int = 1024,
            temperature: float = 0.9
            ) -> str:
    try:
        response = openai.ChatCompletion.create(
                        model=model,
                        messages=[
                            {"role":"user",
                            "content":message}],
                        temperature=temperature,
                        max_tokens=max_tokens,
                        top_p=1,
                        frequency_penalty=0.0,
                        presence_penalty=0.0)
    
        response = response['choices'][0]['message']['content']
        return remove_ai_language_model_sentence(response)
    except openai.error.RateLimitError as e:
        response = "The ChatGPT API is overloaded. Please try again momentarily"
        return response