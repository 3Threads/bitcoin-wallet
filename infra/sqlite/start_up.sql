DROP TABLE IF EXISTS units;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS receipts;
DROP TABLE IF EXISTS products_in_receipts;

CREATE TABLE units
(
    id   UUID PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE products
(
    id      UUID PRIMARY KEY,
    unit_id UUID not null,
    name    text    not null,
    barcode text    not null unique,
    price   float   not null check ( price > 0 ),
    foreign key (unit_id) references units (id)
);

CREATE TABLE receipts
(
    id     UUID PRIMARY KEY,
    status text  not null default 'open'
);

CREATE TABLE products_in_receipts
(
    id         INTEGER PRIMARY KEY autoincrement,
    receipt_id UUID not null,
    product_id UUID not null,
    quantity   integer not null check ( quantity > 0 ),
    foreign key (receipt_id) references receipts (id),
    foreign key (product_id) references products (id)
);



