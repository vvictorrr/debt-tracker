USE debt;

CREATE TABLE users (
    id INT AUTO_INCREMENT NOT NULL,
    name VARCHAR(50) NOT NULL,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(100) NOT NULL,
    CONSTRAINT users_ck UNIQUE (username),
    CONSTRAINT users_pk PRIMARY KEY (id)
);

CREATE TABLE status_domain (
    status VARCHAR(50) NOT NULL,
    CONSTRAINT status_domain_pk PRIMARY KEY (status)
);

CREATE TABLE friend_requests (
    request_id INT AUTO_INCREMENT NOT NULL,
    made_by INT NOT NULL,
    made_for INT NOT NULL,
    date_created DATETIME NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'Pending',
    date_reviewed DATETIME DEFAULT NULL,
    CONSTRAINT made_by_user_fk FOREIGN KEY (made_by) REFERENCES users(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT made_for_user_fk FOREIGN KEY (made_for) REFERENCES users(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT freq_fk FOREIGN KEY (status) REFERENCES status_domain(status)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT freq_ck UNIQUE (made_by, made_for, date_created),
    CONSTRAINT freq_pk PRIMARY KEY (request_id)
);

CREATE TABLE friends (
    friend1 INT NOT NULL,
    friend2 INT NOT NULL,
    owes FLOAT NOT NULL DEFAULT 0.0,
    CONSTRAINT friend1_users_fk FOREIGN KEY (friend1) REFERENCES users(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT friend2_users_fk FOREIGN KEY (friend2) REFERENCES users(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT friends_pk PRIMARY KEY (friend1, friend2)
);

CREATE TABLE payments (
    payment_id INT AUTO_INCREMENT NOT NULL,
    paid_by INT NOT NULL,
    date_paid DATETIME NOT NULL,
    total FLOAT NOT NULL,
    description VARCHAR(200) NOT NULL,
    CONSTRAINT paid_by_user_fk FOREIGN KEY (paid_by) REFERENCES users(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT payment_pk PRIMARY KEY (payment_id)
);

CREATE TABLE debts (
    payment INT NOT NULL,
    debtor INT NOT NULL,
    amount_owed FLOAT NOT NULL,
    CONSTRAINT debts_payments_fk FOREIGN KEY (payment) REFERENCES payments(payment_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT debts_users_fk FOREIGN KEY (debtor) REFERENCES users(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT debts_pk PRIMARY KEY (payment, debtor)
);

CREATE TABLE payment_logs (
    log_id INT AUTO_INCREMENT NOT NULL,
    done_by INT NOT NULL,
    done_to INT NOT NULL,
    amount INT DEFAULT NULL,
    time_occurred DATETIME NOT NULL,
    action_type VARCHAR(50) NOT NULL,
    CONSTRAINT logs_pk PRIMARY KEY (log_id)
);