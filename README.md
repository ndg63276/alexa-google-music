# alexa-google-music

### Stage 1: Get a Google App Password
1. Go to https://myaccount.google.com/.
2. Click "Security" on the left.
3. Under "Signing into Google", click "App Passwords".
4. Where it says "Select app", choose "Other (Custom Name)", type "Alexa Google Music", and click "Generate". 
5. Make a note of the 16 character password it gives you, do not share it with anyone.

### Stage 2: Deploy the Lambda Function

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
