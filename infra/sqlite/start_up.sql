DROP TABLE IF EXISTS USERS;
DROP TABLE IF EXISTS WALLETS;
DROP TABLE IF EXISTS TRANSACTIONS;

CREATE TABLE USERS
(
    ID      UUID PRIMARY KEY,
    EMAIL   TEXT UNIQUE NOT NULL,
    API_KEY TEXT UNIQUE NOT NULL
);

CREATE TABLE WALLETS
(
    ADDRESS UUID PRIMARY KEY  NOT NULL,
    USER_ID UUID              NOT NULL,
    BALANCE FLOAT DEFAULT 1.0 NOT NULL,
    FOREIGN KEY (USER_ID) REFERENCES USERS (ID) ON DELETE CASCADE
);

CREATE TABLE TRANSACTIONS
(
    ID           INTEGER PRIMARY KEY AUTOINCREMENT,
    FROM_ADDRESS TEXT NOT NULL,
    TO_ADDRESS   TEXT NOT NULL,
    AMOUNT       FLOAT       NOT NULL,
    FEE          FLOAT       NOT NULL,
    FOREIGN KEY (FROM_ADDRESS) REFERENCES WALLETS (ADDRESS) ON DELETE CASCADE,
    FOREIGN KEY (TO_ADDRESS) REFERENCES WALLETS (ADDRESS) ON DELETE CASCADE
);

