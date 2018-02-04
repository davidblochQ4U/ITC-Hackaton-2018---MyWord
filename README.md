# ITC Hackathon - IsMyTweet



*Authors : Alexis AMSELLEM, David BLOCH, David Jacob COHEN, David COHEN*

This repository is the App we created during a Hackathon hosted by Israel Tech Challenge 2018 cohort. For information about Israel Tech Challenge please go to <https://www.israeltechallenge.com/>  
IsMyTweet is an app that allows influencer twitter to be folow and detect whether the content of new message tweeted comply to the usual style of the influencer. 
InIsMytTweet asks for a twitter account and then applies an "intelligent" algorithm that uses Machine Learning and Natural Language Processing to detect the  suspicous tweets. If a suspicious tweet is detected an email is sent to the email of the twitter account.
For now the app isn't deployed, but you can test it locally  by running the Flask app.
 

### Usage and Installation  

 See [requirements](requirements.txt) for the list of  the required packages.  
Creating a virtual environment is recommanded, then you can install all the requirements by : 
```
pip install git+https://github.com/erikavaris/tokenizer.git  
pip install -r requirements.txt
```  
Then you can run the flask APP : 
```
export FLASK_APP=app.py
flask run
```  