DROP TABLE IF EXISTS units;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS receipts;
DROP TABLE IF EXISTS products_in_receipts;
DROP TABLE IF EXISTS USERS;
DROP TABLE IF EXISTS WALLETS;
DROP TABLE IF EXISTS TRANSACTIONS;

CREATE TABLE units
(
    id   UUID PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE products
(
    id      UUID PRIMARY KEY,
    unit_id UUID  not null,
    name    text  not null,
    barcode text  not null unique,
    price   float not null check ( price > 0 ),
    foreign key (unit_id) references units (id)
);

CREATE TABLE receipts
(
    id     UUID PRIMARY KEY,
    status text not null default 'open'
);

CREATE TABLE products_in_receipts
(
    id         INTEGER PRIMARY KEY autoincrement,
    receipt_id UUID    not null,
    product_id UUID    not null,
    quantity   integer not null check ( quantity > 0 ),
    foreign key (receipt_id) references receipts (id),
    foreign key (product_id) references products (id)
);

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
    ID           UUID PRIMARY KEY,
    API_KEY      TEXT UNIQUE NOT NULL,
    FROM_ADDRESS TEXT UNIQUE NOT NULL,
    TO_ADDRESS   TEXT UNIQUE NOT NULL,
    AMOUNT       FLOAT       NOT NULL,
    FEE          FLOAT       NOT NULL,
    FOREIGN KEY (API_KEY) REFERENCES USERS (API_KEY) ON DELETE CASCADE,
    FOREIGN KEY (FROM_ADDRESS) REFERENCES WALLETS (ADDRESS) ON DELETE CASCADE,
    FOREIGN KEY (TO_ADDRESS) REFERENCES WALLETS (ADDRESS) ON DELETE CASCADE
);

