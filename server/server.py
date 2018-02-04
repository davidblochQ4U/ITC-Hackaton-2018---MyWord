import SqlDb as db
import sys
sys.path.append('C:\\Users\\david\\CloudStation\\ITC\\IsMyTweet\\')
import config as cfg
import socket
import pickle
import time
sys.path.append('C:\\Users\\david\\CloudStation\\ITC\\IsMyTweet\\model_ml')
sys.path.append('C:\\Users\\david\\CloudStation\\ITC\\IsMyTweet\\notification')
from notification.email_sending import notification as ntf
from model_ml import ProcUnit as pu
from threading import Thread, Lock
import json

LAST_TWEET_ID = 0
ID_MSG = 0
mutex = Lock()


def looking_for_update(sql_db):
    """
    Thread target
    Look for update each DELTA_TIME sec for each user of the DB
    1) get mutex for each read in DB
    2) look in DB for next user
    3) run model on current user
    4) send notification when needed
    """
    while True:  # No delta time for now
        mutex.acquire()
        try:
            # look in DB for next user
            next_row = sql_db.get_next_user()
            if next_row != -1:
                (name_twitter, email, last_id_twitter), last_tweets = next_row
                print("nb tweets : " + str(len(last_tweets)))
                # use ML model for this user
                pu_obj = pu.ProcUnit(name_twitter, last_id_twitter)
                predict = []
                # if no tweet, get all tweet
                if last_id_twitter == 0:
                    list_tweets, update_id = pu_obj.get_all_tweets()
                    if len(list_tweets) == 0:
                        update_id = -1
                else:
                    prev_tweets = last_tweets
                    new_tweets, update_id = pu_obj.get_new_tweets(last_id_twitter)
                    if len(new_tweets) != 0:
                        predict = pu_obj.new_tweets_df(prev_tweets, new_tweets)
                        list_tweets = prev_tweets + new_tweets
                        print("predict")
                        print(predict)
                    else:
                        update_id = -1

                # update id_twitter for next run
                if update_id != -1:
                    sql_db.update_list_tweet(list_tweets)
                    sql_db.update_id_twitter(update_id)
                    # Send notification
                    if len(predict) != 0:
                        to_notify = predict[predict.prediction < cfg.THRESHOLD]
                        for i in range(len(to_notify)):
                            print("mail sent")
                            print(to_notify.iloc[i].comment_text, to_notify.iloc[i].prediction)

                            notif = ntf()
                            notif.send_email(email, to_notify.iloc[i].comment_text)

                sql_db.update_idx()
        finally:
            mutex.release()
            time.sleep(cfg.DELTA_TIME)
    return


def add_user(sql_db, dict_user):
    """ Add user in DB """
    mutex.acquire()

    try:
        name_twitter = dict_user['screen_name']
        email = dict_user['email']
        avatar = dict_user['profile_image']
        #name_twitter = 'ABallNeverLies'
        #email = 'toto@toto.com'
        #avatar = 'test'

        #name_twitter = 'T0toTaTa'
        #email = 'totoRREEE@toto.com'
        #avatar = 'testRREE'
        if not sql_db.is_in_table(name_twitter):
            print("is not in table so add it")
            if not sql_db.insert_in_table(name_twitter, email, avatar):
                exit(-1)
    finally:
        mutex.release()

    return True


def main():
    """ Server of IsMyTweet << Should be running on the same host than the server """
    """ 1) Wait for user input to update database << Open socket for Flask app 
        2) Check for each user if change in nb of twitter 
        3) If change, run checker twitter << use deep learning / nlp fct on message scrapped 
        TODO : 
            - message scrapped saved in DB ?
    """
    try:

        notif = ntf()

        # Open DB File
        sql_db = db.SqlDb(cfg.DB_FILE_NAME, cfg.DB_SCHEMA_TABLE)
        if not sql_db:
            print("Impossible to open db file")

        # Open thread
        t = Thread(target=looking_for_update, args=(sql_db,))
        t.start()
        
        # Open socket
        server_socket = socket.socket()
        server_socket.bind(cfg.SOCKET_SERVER)
        server_socket.listen(cfg.NB_SIMUL_CONNECTION)

        # Wait for command from App Web to update database
        exit_cmd = False
        while not exit_cmd:
            (client_socket, client_address) = server_socket.accept()

            client_cmd = client_socket.recv(cfg.DATA_SIZE_MAX)
            data_loaded = pickle.loads(client_cmd)
            print("Data received : ")
            print(data_loaded)
            id_user = add_user(sql_db, data_loaded)
            client_socket.send(str(id_user).encode())

    except socket.error as err:
        print('Socket : impossible to open. ErrorCode : ' + err)

    finally:
        client_socket.close()
        server_socket.close()

        if sql_db:
            sql_db.close_table()


if __name__ == "__main__":
    main()
