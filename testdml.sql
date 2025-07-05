USE debt;

INSERT INTO status_domain VALUES
    ('Pending'),
    ('Approved'),
    ('Denied');

INSERT INTO users (name, username, password) VALUES
    ('john', 'jjognnyy', 'password'),
    ('bob', 'bbobbby', 'bobword'),
    ('patrick', 'ppatttyy', 'pattword');

INSERT INTO friends VALUES
    (3, 4),
    (2, 3);

INSERT INTO friend_requests(made_by, made_for, date_created) VALUES
    (3, 5, '2025-06-06 22:37:22');

INSERT INTO friend_requests(made_by, made_for, date_created) VALUES
    (4, 5, NOW());