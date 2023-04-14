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


#### Create a new Application in the Desired Workspace

- Turn *Activate Incoming Webhook* on
- Navigate to bottom of screen and select *Add New Webhook to Workspace*
- Select the channel the bot should be posting 
- To get the Channel ID, click the dropdown menu on any channel and scroll to the bottom. 



#### Adding Scopes

Navigate to the **OAuth & Permissions** tab to add scopes for your Slack Application. For reading messages you are tagged in and responding to them, you will just need the three following scopes: *app_mentions:read*, *chat:write*, *channels:read*. There are many other scopes that you can add depending on the goal of your application. 
