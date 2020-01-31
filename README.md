# Alexa / Google Music

* **What is this?** It's an Alexa skill to play music from your Google Music Account.
* **Who is this for?** Anyone with an Alexa device and some music uploaded to Google Music.
* **Can it play any song?** It can only play music you have uploaded, and can only play playlists you have created.
* **How do I set it up?** Just follow the instructions below. It may look a little daunting, but it should be ok.
* **Will it cost me anything?** No, it is entirely free. You have to set up an Amazon AWS account, but you should be entirely covered by the free tier.
* **What do I say to Alexa?** When you have set it up, just say "Alexa, ask Google Music to play Disco Music", or whatever your favourite playlist is called in Google Music.
* **Can it shuffle?** Yes, just say 'shuffle' instead of 'play'.
* **What other commands work?** "Alexa, pause/resume/next/previous" should all work. If you say "Alexa, can you say that again", she should tell you the name of the song. Also, you can say shuffle on/off or loop on/off.
* **It tells me the device ID is invalid?** If you open the Alexa app on your phone, go to the menu, and select Activity, it should show you some possible values for the device ID. Put one of those in as your DEVICE_ID in the environment variables as described below.


### Stage 1: Get a Google App Password
1. Go to https://myaccount.google.com/.
2. Click "Security" on the left.
3. Under "Signing into Google", click "App Passwords".
4. Where it says "Select app", choose "Other (Custom Name)", type "Alexa Google Music", and click "Generate". 
5. Make a note of the 16 character password it gives you, do not share it with anyone.

### Stage 2: Deploy the Lambda Function
1. Go to https://console.aws.amazon.com. You will need to set-up an AWS account (the basic one will do fine) if you don't have one already. Make sure you use the same Amazon account that your Echo device is registered to. **Note - you will need a credit or debit card to set up an AWS account - there is no way around this. There should be no charges from using this skill in a normal way, though I am not resposible if there are.**
2.  Go to the drop down "Location" menu at the top right and ensure you select one of the following. This is important as other regions do not work with Alexa.
  * US East (N. Virginia)
  * US West (Oregon)
  * Asia Pacific (Tokyo)
  * Europe (Ireland)
3. Select Lambda from the AWS Services menu at the top left.
4. Click on the "Create Function" button.
5. Select "Author From Scratch", and name the Lambda Function 'Google-Music'
6. Select the runtime as "Python 3.7".
7. Click "Create Function".
8. On the new window that loads, under "Designer", click "Add trigger", and select "Alexa Skills Kit" (NOTE - if you do not see Alexa Skills Kit as an option then you are in the wrong AWS region). Choose "Disable" under "Skill ID Verification", and click "Add".
9. In the middle of the screen, click on the box that says "Google-Music".
10. Under "Function Code", make sure Runtime says "Python 3.7", and Handler says "lambda_function.lambda_handler".
11. Under "Code Entry Type", select "Upload a .zip file".
12. In a new tab, download this file to your PC - https://github.com/ndg63276/alexa-google-music/raw/master/lambda_function.zip
13. Back in the Lambda tab, click on the "Upload" button. Find and select the lambda_function.zip file you just downloaded.
14. Enter the following into the Environment Variables Section:

|Key           | Value|
|--------------| -----|
|EMAIL         |(Put your gmail email address here)|
|PASSWORD      |(Put the 16 character password you created in stage 1 here)|
|LOCALE        |(Put your [ICU](http://www.localeplanet.com/icu/) locale here, eg en_US, en_GB)|
|DEVICE_ID     |(Put your device ID here. If you don't know it, put 1234567890abcdef, and you should be told a valid value when you try and use the skill)|

15. Scroll down to the section labelled "Basic Settings", and click "Edit". Set the Memory to 512 MB, and the Timeout to 9 seconds. Click "Save".
16. Click "Save" in the top right. This will upload the lambda_function.zip file to Lambda. This may take a few minutes depending on your connection speed.
17. Copy the ARN from the top right to be used later in the Alexa Skill Setup (it's the text after ARN - it won't be in bold and will look a bit like this arn:aws:lambda:eu-west-1:XXXXXXX:function:Google-Music).

### Stage 3: Create the Alexa Skill
1. Go to the Alexa Console (https://developer.amazon.com/alexa/console/ask)
2. If you have not registered as an Amazon Developer then you will need to do so. Fill in your details and ensure you answer "No" for "Do you plan to monetize apps by charging for apps or selling in-app items" and "Do you plan to monetize apps by displaying ads from the Amazon Mobile Ad Network or Mobile Associates?"
3. Once you are logged into your account click "Create Skill" on the right hand side.
4. Give your skill any name, eg "Google Music".
5. **Important** Set the "Default Language" to whatever your Echo device is set to. If you are not sure, go to the Alexa app, go to Settings, Device Settings, then click on your Echo device, and look under Language. If your Echo is set to English (UK), then the skill must be English (UK), other types of English will not work!
6. Choose "Custom" as your model, and "Provision Your Own" as your method, then click "Create Skill" in the top right. On the template page, choose "Start from scratch".
7. On the left hand side, click "JSON Editor".
8. Delete everything in the text box, and copy in the text from https://raw.githubusercontent.com/ndg63276/alexa-google-music/master/Interaction_Model_en.json.
9. Click "Save Model" at the top.
10. Click "Interfaces" in the menu on the left, and enable "Audio Player". Click "Save Interfaces".
11. Click "Endpoint" in the menu on the left, and select "AWS Lambda ARN". Under "Default Region", put your ARN from stage 2 above. Click "Save Endpoints".
13. Click "Invocation" in the menu on the left.
14. If you want to call the skill anything other than "google music", change it here. Click "Save Model" if you change anything.
15. Click "Build Model". This will take a minute, be patient. It should tell you if it succeeded.
16. **Important:** At the top, click "Test". Where it says "Test is disabled for this skill", change the dropdown from "Off" to "Development". 
