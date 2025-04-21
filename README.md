# ChatterBot_Demo
**Overview**

This is a demo to show of the basic capabilities of ChatterBot with a basic training interface.
If this chatbot is deemed to be good functionality wise, further improvements to the UI/UX can be made.


**How to Run**

1. You can find a deployed version of the chatbot for testing at this link [here](https://chatterbot-demo.onrender.com/) (Please note that the server spins down when it is not active
so it may take a while for it to load when opening it for the first time in a while).
2. Type prompts into the textbox and hit send (the enter key will not work)
3. Wait for a response. If no response comes, try reloading the page or retrying the link.

I have encountered issues of a 400 (bad request) error from time to time. If you get this error, close out of the tab and try the link again to see if that resolves it.

**Training**

Training can be done in numerous ways including through Google Sheets which connects through the Render deployment, CSV upload to the Google Sheets, or direct training through the generation of a JSON file.

***1. Directly through Google Sheets***

For ease of access, I have it set up so it is trained from a Google Sheet which is located here:

https://docs.google.com/spreadsheets/d/1QMV6EBLcvzgh_vQPs7wRQo6kwOwqc5UBZW6izwp33aU/edit?gid=1726193122#gid=1726193122

It should allow viewing privilages to anyone with a link. To gain editting privilages, please feel free to send a request through the Google Sheet.

In the spreadsheet, there are 2 sheets that being Data and Training Log. Data has 6 columns that being the Prompt (what the user enters), the Response (what the chatbot responds with), the Subject (categorization of the information requested), the Language (what language the prompt and response are written in), Verified Translation (which is for verifying that the questions are correctly translated for that given language), and Status (what the current statud of the training data is including not ready to train, ready to train, trained, untrain, removed, and scraped which I will go into later). I am open to add more columns for organization and sorting purposes if you recommend any, but refrain from adding them for now or it may break the training scripts set in place right now. There is also the Training Log sheet which consists of 4 columns that being Command (what action or script was run), User (who ran the command), Data (how many rows were impacted by the command), and Time (a timestamp of when the command was run).

All functionality for the Google Sheet is under the Chatbot Functions tab.

*1. Train Chatbot*

This function will automatically train all data that has the Status 'Ready'. Once all of the data has been trained, all data that has the Status 'Ready' will be changed to 'Trained' instead. 

It is advised that while someone is training the Chatbot through Google Sheets that everyone else working on the spreadsheet does not change any Statuses to or from 'Ready' or some data may get false flagged as being trained on while other data may be false flagged as not being trained. For this reason, it is recommended that you coordinate when training to make sure these issues do not arise. Using Ctrl-Z or undo also does not reverse the effect of the function as the data is saved onto a separate database, but it does delete the Training Log saying the action was taken. In order to reverse Trained data, use the Untrain feature and vise versa. Please refrain from training data that has already been trained or untraining data the chatbot never knew as it will cause extra data to be used and errors to be raised for each respectively.

As mentioned before, Render will spindown inactive deployments so training for the first time the deployment has been active in a while will result in it taking a much longer time. To avoid this, you can use the link I posted above for chatting with the chatbot to wake the server before use with it running in the background. 

It should also be noted that when training data, the chatbot will be able to pull from that new data instantly meaning that if you are testing on the new link, you do not have to refresh the page.

*2. Untrain Chatbot*

This function will automatically untrain or remove all data that has the Status 'Untrain' from the Chatbot's database. Once all of the data has been removed, all data that has the Status 'Untrain' will be changed to 'Removed' instead.

All of the statements made from the Train Chatbot functionality is also true here so be aware of all of the warnings listed there.

*3. Delete Removed Data*

This function will automatically delete all rows of data that have the Status 'Removed'. This action can be undone using Ctrl-Z or Undo to add the data back in and delete the action from the Training Log.

This action is not subject to multithreading issues or server issues as it is run completely on Google Sheets.

*4. Scrape Page*

This function will automatically scrape / crawl a webpage to extract out relavant information and synthesize it into a question answer format. This method will automatically give the Prompt, Response, and Language of the data. It will also automatically set Subject to blank, Verified Translation to No, and the Status to Scraped signalling that the data must still be reviewed before approving and training the chatbot on it.

There are some details that are important to note about this function however. For starters, due to restrictions with Render data rates and how much data can be processed in one fetch, restrictions are in place to make sure only 10 - 18 rows of data are added for each function call. If you want to scrape a page with a lot of information, it is recommended you use a different scraping method instead which will be outlined later. Another thing to keep in mind is that scraped data needs to be approved first before the chatbot is trained on it meaning scraped data is not automatically trained.

This can also be undone using Ctrl-Z or Undo if necessary, but keep in mind that AI credits are used with every successful run of this function so try to use the data that is received wherever possible.

*5. Approve Scraped Data*

This method will make it so all rows with the Status 'Scraped' will be set instead to 'Ready' signalling it is ready for training.

This function should be coordinated with the rest of the team to make sure unverified scraped data does not get approved. Approving and setting each one to 'Ready' may be a better way to train off of scraped data, but this function can help with quickly readying scraped data if you are confident in all of the data being correct.

*6. Import CSV*

This function allows users to directly import CSV data and append it directly into the 'Data' sheet in the spreadsheet.

You can do this with any CSV file as long as it has 6 different columns of information. This does allow for people to scrape a page and save it as a CSV file as well allowing for a more thorough data set that is not restricted by Render. The way to scrape data like this will be mentioned later.








Once new data is trained for the Chatbot, I have it set up to store the trained data in MongoDB which can be seen by connecting to this cluster on MongoDB Compass:

mongodb+srv://togekip00:BKOErjhmcKwUVNxF@chatterbotdb.f5fwu81.mongodb.net/Dopomoha

It is possible to set up a seperate database to house this information, I just chose MongoDB because it is the database I am most familiar with.

The Chatbot is currently set to not learn from whoever is typing (so it will not learn from users at all) for safety purposes, but it can be set to learn from users if you so choose. The training with the Google Doc and MongoDB cluster is very open giving full control to the user, but there are some warning that I want to make with that

**Warnings**
- Once data has been entered into the spreadsheet and someone runs the command to train the chatbot, that training information will stay with the chatbot even if it is removed from the spreadsheet. If you wish to remove data you don't want it to be trained on, you will have to delete it out directly from MongoDB. This is to make sure the data is in multiple places to allow for backups to occur if MongoDB gets taken down or the file is somehow corrupted.
- In order for a row to be considered valid training data, it must include a Prompt, a Response, and a Language. If no validate is givin, the program will automatically assume that the date is unvalidated. This means you can have prompts that you want to consider before you answer them by simply only having the Prompt column filled but not the Response and the program will automatically skip over the row.
- Inline with the previous two warnings, If someone runs to train the chatbot on the data in the spreadsheet, it will automatically train on whatever is available at the time even if someone else is currently halfway through a response so make sure to coordinate before training on the given spreadsheet
- If a Prompt is entered twice or has already been saved in MongoDB, it will skip the row meaning no data can be updated unless you delete either that entry in MongoDB you want to update or (if you want to update it so it is entirely just the current spreadsheet) you delete all entries in the database.
