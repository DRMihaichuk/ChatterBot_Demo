# ChatterBot_Demo
**Overview**

This is a demo to show of the basic capabilities of ChatterBot in an informal environment (that being the console) 
so we may later evaluate if this chatbot is a good idea before going forward with the UI/UX design for the chatbot


**How to Run**

1. Make sure you are navigated to the first ChatterBot folder directly in the repo.
2. Enter one of the commands below to indicate how you want to run the chatbot.

        To run chatbot on new training data and test it:
            python ./dopomoha.py
        To only run the chatbot on new training data:
            python ./dopomoha.py --mode train
        To only run the chatbot to test:
            python ./dopomoha.py --mode talk
3. If you are testing the chatbot, enter any prompts you would like it to answer after it fully loads (may take a bit depending on if you are also training it on new data as well)


**Training**

For ease of access, I have it set up so it is trained from a Google Sheet which is located here:

https://docs.google.com/spreadsheets/d/1QMV6EBLcvzgh_vQPs7wRQo6kwOwqc5UBZW6izwp33aU/edit?gid=1726193122#gid=1726193122

It should allow editting privilages to anyone with a link, but let me know if that is not the case.

In the spreadsheet, there are 5 columns that being the Prompt (what the user enters), the Response (what the chatbot responds with), the Subject (categorization of the information requested), the Language (what language the prompt and response are written in), and Verified (which is for verifying that the questions are correctly translated for that given language). I am open to add more columns for organization and sorting purposes if you recommend any, but refrain from adding them for now or it may break the conversion.

Once new data is trained for the Chatbot, I have it set up to store the trained data in MongoDB which can be seen by connecting to this cluster on MongoDB Compass:

mongodb+srv://togekip00:BKOErjhmcKwUVNxF@chatterbotdb.f5fwu81.mongodb.net/Dopomoha

It is possible to set up a seperate database to house this information, I just chose MongoDB because it is the database I am most familiar with.

The Chatbot is currently set to not learn from whoever is typing (so it will not learn from users at all) for safety purposes, but it can be set to learn from users if you so choose. The training with the Google Doc and MongoDB cluster is very open giving full control to the user, but there are some warning that I want to make with that

**Warnings**
- Once data has been entered into the spreadsheet and someone runs the command to train the chatbot, that training information will stay with the chatbot even if it is removed from the spreadsheet. If you wish to remove data you don't want it to be trained on, you will have to delete it out directly from MongoDB. This is to make sure the data is in multiple places to allow for backups to occur if MongoDB gets taken down or the file is somehow corrupted.
- In order for a row to be considered valid training data, it must include a Prompt, a Response, and a Language. If no validate is givin, the program will automatically assume that the date is unvalidated. This means you can have prompts that you want to consider before you answer them by simply only having the Prompt column filled but not the Response and the program will automatically skip over the row.
- Inline with the previous two warnings, If someone runs to train the chatbot on the data in the spreadsheet, it will automatically train on whatever is available at the time even if someone else is currently halfway through a response so make sure to coordinate before training on the given spreadsheet
- If a Prompt is entered twice or has already been saved in MongoDB, it will skip the row meaning no data can be updated unless you delete either that entry in MongoDB you want to update or (if you want to update it so it is entirely just the current spreadsheet) you delete all entries in the database.