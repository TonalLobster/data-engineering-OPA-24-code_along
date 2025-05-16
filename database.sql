CREATE DATABASE DEMO_DB;


SHOW DATABASES;

CREATE SCHEMA DEMO_DB.STAGING;


CREATE TABLE customer(
    customer_id integer PRIMARY KEY,
    age integer,
    email varchar(50)
    )