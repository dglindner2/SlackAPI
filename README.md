# Slack Developer Work

This repository is a walk-through on how to develop Slack applications. This is a simple application that will allow an App to read messages it is tagged in, pass the message to the OpenAI API, and post back in the Slack Channel the response from ChatGPT.


### Creating a Slack Application

Start by navigating to the [Slack API Webpage](https://api.slack.com/apps?new_app=1). Make sure that you are logged into Slack and then click the "Create New App" button. You will be given the option to create an app from scratch or from an app manifest. This walk-through will help you create an application from scratch.

![Create from Scratch](/images/create_app.jpg)

You will then be asked to name your application and to choose your desired workspace. For this project, we have named the application "SlackGPT" and chosen the "Dev Testing" workspace. 

![Choose Workspace](/images/create_app2.jpg)

### Adding Features and Functionality

There are six different pages where you can add features and functionalities for your Slack Application. We will use four of them for SlackGPT. 

- Incoming Webhooks
- Event Subscriptions
- Bots
- Permissions

![Features and Functionality](/images/features_functionality.jpg)


#### Incoming Webhooks

This feature of the API allows your application to post messages from external sources into a Slack Channel. You can use this feature to integrate other tools and services with your Slack workspace, such as alerting systems, monitoring tools, or chatbots. Messages sent to the webhook URL can include text, attachments, and other formatting options. 

Turn Incoming Webhooks on by clicking the slider in the top right hand side of the screen.

![Incoming Webhooks](/images/webhooks.jpg)

#### Event Subscriptions

Enabling Events will require a few steps. We start by turning the **Enable Events** slider to 'on'. We are then asked for a Request URL where the Slack Events API will send a POST request when events occur. In order to verify your Request URL, the API will send a request with a **challenge** parameter. Your endpoint needs to respond to this with the challenge token that was originally sent to you. 

![Event Subscriptions](/images/events.jpg)

If you're developing locally like I am, you can use the service **ngrok** to create a publicly accessible endpoint that forwards requests to your local server. **ngrok** is a tool that creates a secure tunnel between a public endpoint and a locally running web server. It allows you to expose your local web server to the internet and receive requests from external sources.

If you have Homebrew installed, you can simply install ngrok by entering 

`brew install ngrok`

in the terminal. You can also visit [the ngrok website](https://ngrok.com/download) where you can download a ZIP file. 

Sign up for a free ngrok account and grab your authtoken provided on the site under **Getting Started** and **Your Authtoken** in the left-hand side navigation panel. 

Enter your token in your terminal to authenticate your ngrok agent.

`$ ngrok config add-authtoken <YOUR-AUTHTOKEN-HERE>`

To run ngrok, enter the following line of code into your terminal with your desired port number:

`ngrok http <PORT-NUMBER>`

You will use the Forwarding URL that is returned in your terminal as the Request URL. The Web Interface provided in the output will allow you to see any requests. 

![ngrok Forwarding URL](/images/ngrok.jpg)

In a separate terminal, you need to run the following script:

```
from flask import Flask, request, make_response

app = Flask(__name__)

@app.route('/slack/events', methods=['POST'])
def slack_events():
    if request.headers.get('Content-Type') == 'application/json':
        data = request.json
        
        # Complete the URL Verification Challenge
        if data['type'] == 'url_verification':
            return make_response(data['challenge'], 200, {'Content-Type': 'text/plain'})

    return make_response('', 404)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

It is important to note that the port provided in the last line of the code matches the port specified in the ngrok terminal command. 

The Request URL for the Slack API from this example would now be "https://3cd5-2620-1f7-8ff-c4c-ac2c-72b7-c1b6-1da5.ngrok-free.app/slack/events". This is the Forwarding URL followed by `/slack/events` as specified in our Python script. 

You should now get a *Verified* checkmark next to your Request URL on the Slack API webpage. 


#### Bots



#### Permissions


#### Create a new Application in the Desired Workspace

- Turn *Activate Incoming Webhook* on
- Navigate to bottom of screen and select *Add New Webhook to Workspace*
- Select the channel the bot should be posting 
- To get the Channel ID, click the dropdown menu on any channel and scroll to the bottom. 



#### Adding Scopes

Navigate to the **OAuth & Permissions** tab to add scopes for your Slack Application. For reading messages you are tagged in and responding to them, you will just need the three following scopes: *app_mentions:read*, *chat:write*, *channels:read*. There are many other scopes that you can add depending on the goal of your application. 
