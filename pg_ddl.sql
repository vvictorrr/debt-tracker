
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL
);

-- status domain table
CREATE TABLE status_domain (
    status VARCHAR(50) PRIMARY KEY
);

-- friend_requests table
CREATE TABLE friend_requests (
    request_id SERIAL PRIMARY KEY,
    made_by INT NOT NULL,
    made_for INT NOT NULL,
    date_created TIMESTAMP NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'Pending',
    date_reviewed TIMESTAMP DEFAULT NULL,
    CONSTRAINT freq_ck UNIQUE (made_by, made_for, date_created),
    CONSTRAINT made_by_user_fk FOREIGN KEY (made_by) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT made_for_user_fk FOREIGN KEY (made_for) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT freq_fk FOREIGN KEY (status) REFERENCES status_domain(status) ON DELETE CASCADE
);

-- friends table
CREATE TABLE friends (
    friend1 INT NOT NULL,
    friend2 INT NOT NULL,
    owes FLOAT NOT NULL DEFAULT 0.0,
    PRIMARY KEY (friend1, friend2),
    CONSTRAINT friend1_users_fk FOREIGN KEY (friend1) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT friend2_users_fk FOREIGN KEY (friend2) REFERENCES users(id) ON DELETE CASCADE
);

-- payments table
CREATE TABLE payments (
    payment_id SERIAL PRIMARY KEY,
    paid_by INT NOT NULL,
    date_paid TIMESTAMP NOT NULL,
    total FLOAT NOT NULL,
    description VARCHAR(200) NOT NULL,
    CONSTRAINT paid_by_user_fk FOREIGN KEY (paid_by) REFERENCES users(id) ON DELETE CASCADE
);

-- debts table
CREATE TABLE debts (
    payment INT NOT NULL,
    debtor INT NOT NULL,
    amount_owed FLOAT NOT NULL,
    PRIMARY KEY (payment, debtor),
    CONSTRAINT debts_payments_fk FOREIGN KEY (payment) REFERENCES payments(payment_id) ON DELETE CASCADE,
    CONSTRAINT debts_users_fk FOREIGN KEY (debtor) REFERENCES users(id) ON DELETE CASCADE
);

-- payment_logs table
CREATE TABLE payment_logs (
    log_id SERIAL PRIMARY KEY,
    done_by INT NOT NULL,
    done_to INT NOT NULL,
    amount INT DEFAULT NULL,
    time_occurred TIMESTAMP NOT NULL,
    action_type VARCHAR(50) NOT NULL
);

INSERT INTO status_domain VALUES
    ('Pending'),
    ('Approved'),
    ('Denied');