import pandas as pd 
import numpy as np
import string
import re    
from nltk.corpus import stopwords
import spacy
import tweepy
from tokenizer import tokenizer
from spacy.lang.en import English
#from scipy import sparse
#import warnings
#import regex as re
#from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer, TfidfTransformer
from sklearn.cross_validation import cross_val_predict, cross_val_score


class ProcUnit(object):

    def __init__(self, name_twitter, id_until):
        self.name_twitter = name_twitter
        self.id_until = id_until
        self.APPO_dict = {
"aren't" : "are not",
"can't" : "cannot",
"couldn't" : "could not",
"didn't" : "did not",
"doesn't" : "does not",
"don't" : "do not",
"hadn't" : "had not",
"hasn't" : "has not",
"haven't" : "have not",
"he'd" : "he would",
"he'll" : "he will",
"he's" : "he is",
"i'd" : "I would",
"i'd" : "I had",
"i'll" : "I will",
"i'm" : "I am",
"isn't" : "is not",
"it's" : "it is",
"it'll":"it will",
"i've" : "I have",
"let's" : "let us",
"mightn't" : "might not",
"mustn't" : "must not",
"shan't" : "shall not",
"she'd" : "she would",
"she'll" : "she will",
"she's" : "she is",
"shouldn't" : "should not",
"that's" : "that is",
"there's" : "there is",
"they'd" : "they would",
"they'll" : "they will",
"they're" : "they are",
"they've" : "they have",
"we'd" : "we would",
"we're" : "we are",
"weren't" : "were not",
"we've" : "we have",
"what'll" : "what will",
"what're" : "what are",
"what's" : "what is",
"what've" : "what have",
"where's" : "where is",
"who'd" : "who would",
"who'll" : "who will",
"who're" : "who are",
"who's" : "who is",
"who've" : "who have",
"won't" : "will not",
"wouldn't" : "would not",
"you'd" : "you would",
"you'll" : "you will",
"you're" : "you are",
"you've" : "you have",
"'re": " are",
"wasn't": "was not",
"we'll":" will",
"didn't": "did not",
"tryin'":"trying",
"arent" : "are not",
"cant" : "cannot",
"couldnt" : "could not",
"didnt" : "did not",
"doesnt" : "does not",
"dont" : "do not",
"hadnt" : "had not",
"hasnt" : "has not",
"havent" : "have not",
"isnt" : "is not",
"its" : "it is",
"itll":"it will",
"ive" : "I have",
"lets" : "let us",
"mightnt" : "might not",
"mustnt" : "must not",
"shant" : "shall not",
"shed" : "she would",
"shell" : "she will",
"shes" : "she is",
"shouldnt" : "should not",
"thats" : "that is",
"theres" : "there is",
"theyd" : "they would",
"theyll" : "they will",
"theyre" : "they are",
"theyve" : "they have",
"wed" : "we would",
"were" : "we are",
"werent" : "were not",
"weve" : "we have",
"whatll" : "what will",
"whatre" : "what are",
"whats" : "what is",
"whatve" : "what have",
"wheres" : "where is",
"whod" : "who would",
"wholl" : "who will",
"whore" : "who are",
"whos" : "who is",
"whove" : "who have",
"wont" : "will not",
"wouldnt" : "would not",
"youd" : "you would",
"youll" : "you will",
"youre" : "you are",
"youve" : "you have",
"wasnt": "was not"
}
        self.tfidf_char = TfidfVectorizer(analyzer = "char",   \
                             tokenizer = None,    \
                             preprocessor = None, \
                             stop_words = None,   \
                             max_features = 6000, ngram_range=(2,6)) 
        self.tfidf_word = TfidfVectorizer(analyzer = "word",   \
                             tokenizer = None,    \
                             preprocessor = None, \
                             stop_words = None,   \
                             max_features = 6000, ngram_range=(1,3))
        self.eng_stopwords = set(stopwords.words("english")) 
        self.T = tokenizer.TweetTokenizer(preserve_url=False,
                             regularize=True, preserve_case= False)
        self.parser = English()
        self.parser.vocab["not"].is_stop = False
        self.parser.vocab["cannot"].is_stop = False

        self.train = pd.read_csv("../model_ml/data_ref/train.csv") ### toxic dataset

        self.consumer_key = 'SSqTVGJ5RTb8cfvp14gULqULn'
        self.consumer_secret = 'ZNGNneoRIFKg3j05M1NOabgvLzfHZXknfuARxYJjbIg1iUqotI'
        self.access_token = '946335506475962368-vY2nm6lL3g1YafAH7xRRNUPomCgOn9W'
        self.access_secret = 'J1RiXEo5nb062wCDgMftv9q34rATkvtQR132gTJB42ROZ'

        # create an OAuthHandler instance
        # Twitter requires all requests to use OAuth for authentication
        self.auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
        self.auth.set_access_token(self.access_token, self.access_secret)

        # Construct the API instance
        self.api = tweepy.API(self.auth)  # create an API object
        self.auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)

    def get_all_tweets(self):
        alltweets = []
        new_tweets = self.api.user_timeline(screen_name=self.name_twitter, count=200)
        alltweets.extend(new_tweets)
        oldest = alltweets[-1].id - 1
        while len(new_tweets) > 0:
            new_tweets = self.api.user_timeline(screen_name=self.name_twitter, count=200, max_id=oldest)
            alltweets.extend(new_tweets)
            oldest = alltweets[-1].id - 1
        outtweets = [(tweet.id_str, tweet.text) for tweet in alltweets]
        return outtweets, alltweets[0].id

    def get_new_tweets(self, since_id):
        alltweets = []
        new_tweets = self.api.user_timeline(screen_name=self.name_twitter, count=200, since_id=since_id)
        alltweets.extend(new_tweets)
        if len(alltweets) != 0:
            oldest = alltweets[-1].id - 1
            while len(new_tweets) > 0:
                new_tweets = self.api.user_timeline(screen_name=self.name_twitter, count=200, max_id=oldest, since_id=since_id)
                alltweets.extend(new_tweets)
                oldest = alltweets[-1].id - 1
            outtweets = [(tweet.id_str, tweet.text) for tweet in alltweets] , alltweets[0].id
        else:
            outtweets = [], -1
        return outtweets

    def is_number(self, s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    def replace_number(self, sentence_list, replace = "numeric"):
        return [x  if not self.is_number(x) else replace for x in sentence_list]

    def new_tweets_df(self, prev_tweets, new_tweets):
        def clean(comment):
            comment=re.sub("\\n"," ",comment)
            comment=re.sub("\[\[.*\]","",comment)
            words = self.T.tokenize(comment) 
            words = " ".join([self.APPO_dict[word] if word in self.APPO_dict else word for word in words])
            words = [token.lemma_ for token in self.parser(words) if (not token.is_stop and not token.is_punct and
                                                                      not token.is_space)]
            words = [word for word in words if (word != "s" and word != "=" and word != ">")]
            clean_sent = " ".join(self.replace_number(words))
            return clean_sent
        list_train_pos = [tweet_msg for (tweet_id,tweet_msg) in prev_tweets]
        list_tweet_pred = [tweet_msg for (tweet_id, tweet_msg) in new_tweets]
        new_tweets_df = pd.DataFrame(list_tweet_pred, columns=["comment_text"])
        new_tweets_df["id_tweet"] = [tweet_msg for (tweet_id, tweet_msg) in new_tweets]
        train_pos = pd.DataFrame(list_train_pos, columns=["comment_text"])
        train_neg = self.train.sample(frac = 1)[:4*len(prev_tweets)][["comment_text"]]
        train_pos["label"] = 1
        train_neg["label"] = 0
        train_final = pd.concat((train_pos, train_neg),axis = 0)
        train_final = train_final.sample(frac = 1)
        corpus = train_final.comment_text
        train_data_features = self.tfidf_word.fit_transform(corpus)
        train_data_features_toarray = train_data_features.toarray()
        lg = LogisticRegression()
        lg.fit(train_data_features, train_final["label"])
        new_tweets_df["prediction"] = lg.predict_proba(self.tfidf_word.transform(
            new_tweets_df.comment_text.apply(clean)))[:,1]
        return new_tweets_df

"""proc_test = ProcUnit('ABallNeverLies',957585522049896448)
prev_tweets, new_tweets = proc_test.tweet_scrap()
print(proc_test.new_tweets_df(prev_tweets, new_tweets))"""



