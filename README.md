# Slack Developer Work

This repository is a walk-through on how to develop Slack applications. This is a simple application that will allow an App to read messages it is tagged in, pass the message to the OpenAI API, and post back in the Slack Channel the response from ChatGPT.

#### Create a new Application in the Desired Workspace

- Turn *Activate Incoming Webhook* on
- Navigate to bottom of screen and select *Add New Webhook to Workspace*
- Select the channel the bot should be posting 
- To get the Channel ID, click the dropdown menu on any channel and scroll to the bottom. 



#### Adding Scopes

Navigate to the **OAuth & Permissions** tab to add scopes for your Slack Application. For reading messages you are tagged in and responding to them, you will just need the three following scopes: *app_mentions:read*, *chat:write*, *channels:read*. There are many other scopes that you can add depending on the goal of your application. 
