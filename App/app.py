from flask import Flask, request, redirect, url_for, session, g, flash, \
     render_template
from flask_oauth import OAuth
import sys
#sys.path.append('C:\\Users\\david\\CloudStation\\ITC\\IsMyTweet\\')

import sys
sys.path.insert(0, "../")
import config as cfg
import socket
import pickle
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from twython import Twython

# configuration
SECRET_KEY = 'development key'
DEBUG = False
CONSUMER_KEY = "pwxVM2wIn5p2XvM4gsaZJMSJA"
CONSUMER_SECRET = "j1Azi1x7w76u0fMZoM8OTja67bbTbMG7ApTimJvmcTCrIgjfbZ"

# setup flask
app = Flask(__name__)
app.debug = DEBUG
app.secret_key = SECRET_KEY
oauth = OAuth()
 
# Use Twitter as example remote application
twitter = oauth.remote_app('twitter',
    # unless absolute urls are used to make requests, this will be added
    # before all URLs.  This is also true for request_token_url and others.
    base_url='https://api.twitter.com/oauth2/token',
    # where flask should look for new request tokens
    request_token_url='https://api.twitter.com/oauth/request_token',
    # where flask should exchange the token with the remote application
    access_token_url='https://api.twitter.com/oauth/access_token',
    # twitter knows two authorizatiom URLs.  /authorize and /authenticate.
    # they mostly work the same, but for sign on /authenticate is
    # expected because this will give the user a slightly different
    # user interface on the twitter side.
    authorize_url='https://api.twitter.com/oauth/authorize',
    # the consumer keys from the twitter application registry.
    consumer_key= CONSUMER_KEY,
    consumer_secret= CONSUMER_SECRET
)
 
 
@twitter.tokengetter
def get_twitter_token(token=None):
    return session.get('twitter_oauth_tokens')
 
@app.route('/')
def index():
    access_token = session.get('access_token')
    if access_token is None:
        return render_template('login.html')
 
    access_token = access_token[0]
 
    return render_template('login.html')
    
@app.route('/login')
def login():
    return twitter.authorize(callback=url_for('oauth_authorized',
        next=request.args.get('next') or request.referrer or None))
 
 
@app.route('/logout')
def logout():
    session.pop('screen_name', None)
    flash('You were signed out')
    return redirect(request.referrer or url_for('index'))
 
@app.route('/validation')
def validation():
    twyton = Twython(app_key=CONSUMER_KEY,
                      app_secret=CONSUMER_SECRET,
                      oauth_token=session['twitter_token'][0],
                      oauth_token_secret=session['twitter_token'][1])

    obj = twyton.verify_credentials(include_email="true", 
        skip_status=1,
        include_entities=0)
    user_dic = {'screen_name': obj['screen_name'],
                'email': obj['email'],
                'profile_image': obj['profile_image_url_https']}

    try:
        my_socket = socket.socket()
        my_socket.connect(cfg.SOCKET_SERVER)
        data_sent = pickle.dumps(user_dic)
        my_socket.send(data_sent)
        data = my_socket.recv(255)
        print('The server sent : ' + data.decode())
    except socket.error as err:
        print('Server not found.')
    finally:
        my_socket.close()

    return render_template('validation.html', 
        screen_name=user_dic['screen_name'], 
        email=user_dic['email'],
        profile_image=user_dic['profile_image'].replace("_normal", ""))


@app.route('/oauth-authorized')
@twitter.authorized_handler
def oauth_authorized(resp):
    next_url = request.args.get('next') or url_for('index')
    if resp is None:
        flash(u'You denied the request to sign in.')
        return redirect(next_url)
 
    access_token = resp['oauth_token']
    session['access_token'] = access_token
    session['screen_name'] = resp['screen_name']
 
    session['twitter_token'] = (
        resp['oauth_token'],
        resp['oauth_token_secret']
    )
 
 
    return redirect(url_for('validation'))
 
 
if __name__ == '__main__':
    app.run()