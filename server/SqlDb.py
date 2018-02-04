import sqlite3 as lite
import datetime
import pickle


class SqlDb(object):
    """
    Class to manage SQLITE db
    """
    db_handler = None
    nb_rows = 0
    seen_idx = 0

    def __init__(self, db_table, db_empty_table):
        """ Constructor """
        self.db_handler = lite.connect(db_table, check_same_thread=False)
        self.create_table(db_empty_table)

    def create_table(self, db_schema_table):
        """ Create Table or Open it if exists"""

        with self.db_handler:
            # Open and read the file as a single buffer
            fd = open(db_schema_table, 'r')
            sqlFile = fd.read()
            fd.close()

            # all SQL commands (split on ';')
            sqlCommands = sqlFile.split(';')

            # Execute every command from the input file
            for command in sqlCommands:
                try:
                    self.db_handler.execute(command)
                except ValueError as msg:
                    return False

            # Initialize nb_rows
            count_cmd = "SELECT COUNT(*) FROM users;"
            (nb_count,) = self.execute_cmd(count_cmd)
            self.nb_rows = nb_count

        return True

    def get_next_user(self):
        """ Get next entry of table """
        if self.nb_rows != 0:
            sel_cmd = "SELECT Name_Twitter, Email, Id_Last_Tweet FROM users WHERE ID = %d" % self.seen_idx
            print("id :"+str(self.seen_idx))
            print("nb_rows : "+str(self.nb_rows))
            data = self.execute_cmd(sel_cmd)
            print(data)
            content = []
            if data[2] != 0:
                try:
                    with open('db/'+str(self.seen_idx)+'.txt', 'rb') as fp:
                        content = pickle.loads(fp.read())
                finally:
                    fp.close()

            if self.nb_rows == 0:
                return -1
            return data, content
        return -1

    def update_id_twitter(self, id_twitter):
        """ Update ID Twitter """
        upd_cmd = "UPDATE users SET Id_Last_Tweet = %d WHERE ID = %d;" % (id_twitter, self.seen_idx)
        data = self.execute_cmd(upd_cmd)
        # TODO : check if error
        return True

    def update_list_tweet(self, list_tweet):
        """ Update ID Twitter """
        #upd_cmd = "UPDATE users SET Tweet_List = \"%s\" WHERE ID = %d;" % (str(list_tweet), self.seen_idx)
        #print(upd_cmd)
        #data = self.execute_cmd(upd_cmd)
        try:
            with open('db/'+str(self.seen_idx)+'.txt', 'wb+') as fp:
                fp.write(pickle.dumps(list_tweet))
        finally:
            fp.close()

        # TODO : check if error
        return True

    def update_idx(self):
        """ Update index to look at the next row """
        if self.seen_idx == self.nb_rows - 1:
            self.seen_idx = 0
        else:
            self.seen_idx += 1

        return True

    def is_in_table(self, name_twitter):
        """
        Check if this ID is already registered
        :param id_twitter:
        :return:
        """
        count_cmd = "SELECT COUNT(*) FROM users WHERE Name_Twitter = '%s';" % name_twitter
        (nb_count,) = self.execute_cmd(count_cmd)
        if nb_count != 0:
            return True

        return False

    def insert_in_table(self, name_twitter, email, avatar):
        """
        Check if this ID is already registered
        :param name_twitter:f
        :param email:
        :param avatar:
        :return:
        """
        ins_cmd = "INSERT INTO users VALUES (%d, '%s', '%s', '%s', 0, '%s', 1, '');" \
                  % (self.nb_rows, name_twitter, avatar, email, datetime.datetime.now())
        print(ins_cmd)
        value = self.execute_cmd(ins_cmd)
        self.nb_rows += 1
        if value != 0:
            return True

        return False

    def execute_cmd(self, cmd):
        """ Execute command and get return value """
        try:

            cur = self.db_handler.cursor()
            cur.execute(cmd)
            data = cur.fetchone()
            self.db_handler.commit()
            ret_val = data

        except lite.Error as e:
            print("Error %s:" % e.args[0])
            ret_val = -1

        return ret_val

    def close_table(self):
        """ close handler """
        self.db_handler.close()
