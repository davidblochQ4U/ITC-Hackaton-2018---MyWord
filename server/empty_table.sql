CREATE TABLE IF NOT EXISTS users (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name_Twitter varchar(255) NOT NULL,
    Avatar text NOT NULL,
    Email varchar(255) NOT NULL UNIQUE,
    Id_Last_Tweet int,
    Creation_Date date,
    Notification_By_Mail int,
    Tweet_List text
);