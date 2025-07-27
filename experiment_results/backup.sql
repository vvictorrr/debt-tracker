--
-- PostgreSQL database dump
--

-- Dumped from database version 16.9 (Debian 16.9-1.pgdg120+1)
-- Dumped by pg_dump version 16.9 (Homebrew)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: public; Type: SCHEMA; Schema: -; Owner: debt_tracking_user
--

-- *not* creating schema, since initdb creates it


ALTER SCHEMA public OWNER TO victorli;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: debts; Type: TABLE; Schema: public; Owner: debt_tracking_user
--

CREATE TABLE public.debts (
    payment integer NOT NULL,
    debtor integer NOT NULL,
    amount_owed double precision NOT NULL
);


ALTER TABLE public.debts OWNER TO victorli;

--
-- Name: friend_requests; Type: TABLE; Schema: public; Owner: debt_tracking_user
--

CREATE TABLE public.friend_requests (
    request_id integer NOT NULL,
    made_by integer NOT NULL,
    made_for integer NOT NULL,
    date_created timestamp without time zone NOT NULL,
    status character varying(50) DEFAULT 'Pending'::character varying NOT NULL,
    date_reviewed timestamp without time zone
);


ALTER TABLE public.friend_requests OWNER TO victorli;

--
-- Name: friend_requests_request_id_seq; Type: SEQUENCE; Schema: public; Owner: debt_tracking_user
--

CREATE SEQUENCE public.friend_requests_request_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.friend_requests_request_id_seq OWNER TO victorli;

--
-- Name: friend_requests_request_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: debt_tracking_user
--

ALTER SEQUENCE public.friend_requests_request_id_seq OWNED BY public.friend_requests.request_id;


--
-- Name: friends; Type: TABLE; Schema: public; Owner: debt_tracking_user
--

CREATE TABLE public.friends (
    friend1 integer NOT NULL,
    friend2 integer NOT NULL,
    owes double precision DEFAULT 0.0 NOT NULL
);


ALTER TABLE public.friends OWNER TO victorli;

--
-- Name: payment_logs; Type: TABLE; Schema: public; Owner: debt_tracking_user
--

CREATE TABLE public.payment_logs (
    log_id integer NOT NULL,
    done_by integer NOT NULL,
    done_to integer NOT NULL,
    amount integer,
    time_occurred timestamp without time zone NOT NULL,
    action_type character varying(50) NOT NULL
);


ALTER TABLE public.payment_logs OWNER TO victorli;

--
-- Name: payment_logs_log_id_seq; Type: SEQUENCE; Schema: public; Owner: debt_tracking_user
--

CREATE SEQUENCE public.payment_logs_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.payment_logs_log_id_seq OWNER TO victorli;

--
-- Name: payment_logs_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: debt_tracking_user
--

ALTER SEQUENCE public.payment_logs_log_id_seq OWNED BY public.payment_logs.log_id;


--
-- Name: payments; Type: TABLE; Schema: public; Owner: debt_tracking_user
--

CREATE TABLE public.payments (
    payment_id integer NOT NULL,
    paid_by integer NOT NULL,
    date_paid timestamp without time zone NOT NULL,
    total double precision NOT NULL,
    description character varying(200) NOT NULL
);


ALTER TABLE public.payments OWNER TO victorli;

--
-- Name: payments_payment_id_seq; Type: SEQUENCE; Schema: public; Owner: debt_tracking_user
--

CREATE SEQUENCE public.payments_payment_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.payments_payment_id_seq OWNER TO victorli;

--
-- Name: payments_payment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: debt_tracking_user
--

ALTER SEQUENCE public.payments_payment_id_seq OWNED BY public.payments.payment_id;


--
-- Name: status_domain; Type: TABLE; Schema: public; Owner: debt_tracking_user
--

CREATE TABLE public.status_domain (
    status character varying(50) NOT NULL
);


ALTER TABLE public.status_domain OWNER TO victorli;

--
-- Name: users; Type: TABLE; Schema: public; Owner: debt_tracking_user
--

CREATE TABLE public.users (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    username character varying(50) NOT NULL,
    password character varying(100) NOT NULL
);


ALTER TABLE public.users OWNER TO victorli;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: debt_tracking_user
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO victorli;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: debt_tracking_user
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: friend_requests request_id; Type: DEFAULT; Schema: public; Owner: debt_tracking_user
--

ALTER TABLE ONLY public.friend_requests ALTER COLUMN request_id SET DEFAULT nextval('public.friend_requests_request_id_seq'::regclass);


--
-- Name: payment_logs log_id; Type: DEFAULT; Schema: public; Owner: debt_tracking_user
--

ALTER TABLE ONLY public.payment_logs ALTER COLUMN log_id SET DEFAULT nextval('public.payment_logs_log_id_seq'::regclass);


--
-- Name: payments payment_id; Type: DEFAULT; Schema: public; Owner: debt_tracking_user
--

ALTER TABLE ONLY public.payments ALTER COLUMN payment_id SET DEFAULT nextval('public.payments_payment_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: debt_tracking_user
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: debts; Type: TABLE DATA; Schema: public; Owner: debt_tracking_user
--

COPY public.debts (payment, debtor, amount_owed) FROM stdin;
5	2	10
6	1	10
7	1	12.5
8	1	8
9	1	12.5
10	1	10
11	1	5
12	1	10
13	1	8
14	3	29.5
15	1	12.39
15	6	12.39
16	1	12.39
16	6	12.39
17	7	10
17	1	10
18	2	15
18	1	15
19	2	20
20	1	25
21	3	9
22	1	12.39
22	6	12.39
23	3	4.25
23	1	5.95
24	6	8.75
24	5	8.75
24	3	8.75
25	5	3.8
25	6	3.8
25	3	3.8
26	5	2.57
26	3	2.57
26	1	2.57
27	5	6.4
28	5	47.8
28	6	44.55
28	3	44.55
29	1	9.5
29	6	9.5
29	3	9.5
30	5	7.5
31	6	25
32	5	21.57
32	3	19.57
32	1	19.57
33	6	3.33
33	3	3.33
33	1	3.33
34	3	7.59
\.


--
-- Data for Name: friend_requests; Type: TABLE DATA; Schema: public; Owner: debt_tracking_user
--

COPY public.friend_requests (request_id, made_by, made_for, date_created, status, date_reviewed) FROM stdin;
1	2	1	2025-07-11 23:02:26.449506	Approved	2025-07-11 23:02:37.805845
2	3	1	2025-07-20 01:56:27.786611	Approved	2025-07-20 01:56:43.524114
5	5	6	2025-07-20 21:09:03.102502	Approved	2025-07-20 21:09:05.647136
3	5	1	2025-07-20 21:08:34.814977	Approved	2025-07-20 21:09:12.042805
6	6	1	2025-07-20 21:09:03.179669	Approved	2025-07-20 21:09:12.9082
4	5	3	2025-07-20 21:08:46.235493	Approved	2025-07-20 21:09:30.625489
7	6	3	2025-07-20 21:09:21.033135	Approved	2025-07-20 21:09:31.638329
8	2	7	2025-07-20 22:26:11.574687	Approved	2025-07-20 22:26:31.293038
9	7	1	2025-07-20 22:27:00.890762	Approved	2025-07-20 22:27:10.714636
\.


--
-- Data for Name: friends; Type: TABLE DATA; Schema: public; Owner: debt_tracking_user
--

COPY public.friends (friend1, friend2, owes) FROM stdin;
6	5	0
3	5	0.07999999999999652
1	5	0
5	1	0
2	1	0
3	1	105.33
3	6	0
6	1	24.91
1	3	0
1	6	0
6	3	0
7	1	0
7	2	0
2	7	0
1	2	0
1	7	0
5	3	0
5	6	0
\.


--
-- Data for Name: payment_logs; Type: TABLE DATA; Schema: public; Owner: debt_tracking_user
--

COPY public.payment_logs (log_id, done_by, done_to, amount, time_occurred, action_type) FROM stdin;
1	2	1	15	2025-07-20 02:25:41.043333	forgive
2	2	1	5	2025-07-20 22:41:35.375332	forgive
3	7	1	20	2025-07-20 22:41:46.960226	forgive
4	2	1	5	2025-07-20 22:43:19.873225	forgive
5	1	5	16	2025-07-20 22:48:16.100257	pay_off
6	1	7	20	2025-07-20 22:48:17.014147	pay_off
7	5	6	25	2025-07-20 22:48:51.241314	forgive
8	5	3	9	2025-07-20 22:49:47.68413	forgive
\.


--
-- Data for Name: payments; Type: TABLE DATA; Schema: public; Owner: debt_tracking_user
--

COPY public.payments (payment_id, paid_by, date_paid, total, description) FROM stdin;
1	1	2025-07-11 23:02:49.88763	20	burgers
2	1	2025-07-11 23:09:37.479929	20	burgers
3	1	2025-07-11 23:12:56.880617	20	burgers
5	1	2025-07-11 23:23:56.701826	20	burgers
6	2	2025-07-11 23:24:23.853804	20	burgers
7	3	2025-07-20 01:57:46.713253	61	alcohol
8	3	2025-07-20 01:58:08.180277	16.05	wawawawawa
9	3	2025-07-20 02:00:04.17379	61	t
10	2	2025-07-20 02:17:00.418159	20	burgers
11	2	2025-07-20 02:17:08.19013	15	fries
12	2	2025-07-20 02:21:22.824055	20	burgers
13	3	2025-07-20 02:26:34.163805	16.05	wawaaaaa
14	1	2025-07-20 02:27:02.904409	61	iron hill dinner
15	5	2025-07-20 21:14:27.943842	37.17	canes
16	5	2025-07-20 21:15:04.139806	37.17	.
17	2	2025-07-20 22:27:48.335482	30	burgers
18	7	2025-07-20 22:41:15.74495	40	burgers
19	7	2025-07-20 22:42:48.042867	30	fries
20	2	2025-07-20 22:43:15.784295	40	burgers
21	1	2025-07-20 22:48:39.554456	10	fixbug
22	5	2025-07-20 22:49:26.559247	37.17	canes
23	5	2025-07-21 03:12:00.404153	20.48	wingstop
24	1	2025-07-21 04:45:54.188084	35	Superman movie
25	1	2025-07-21 19:12:03.329424	15.5	sukihana
26	6	2025-07-21 20:00:05.568586	10.25	popcorm
27	6	2025-07-21 20:00:38.451889	6.4	large drink at da theatre
28	1	2025-07-22 00:11:52.543054	181.45	Kpot
29	5	2025-07-22 16:34:09.448561	57	soju
30	3	2025-07-22 16:35:31.485147	14.99	sliiimeeee
31	5	2025-07-22 20:13:57.172664	50	arcade
32	6	2025-07-24 17:32:42.301958	80.27	pho
33	5	2025-07-24 17:38:12.117694	38	escape (down payment)
34	6	2025-07-24 21:56:31.746464	15.18	canes
\.


--
-- Data for Name: status_domain; Type: TABLE DATA; Schema: public; Owner: debt_tracking_user
--

COPY public.status_domain (status) FROM stdin;
Pending
Approved
Denied
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: debt_tracking_user
--

COPY public.users (id, name, username, password) FROM stdin;
1	vic	chirp	password
2	testman	tester	testword
3	nart 	natelids	Njnat2008
4	kristie :3	meowmeow	eow
5	cad	caditalism	chaditalism
6	kristie :3	meow	meowmeow2
7	testman2	testbro	testword
\.


--
-- Name: friend_requests_request_id_seq; Type: SEQUENCE SET; Schema: public; Owner: debt_tracking_user
--

SELECT pg_catalog.setval('public.friend_requests_request_id_seq', 9, true);


--
-- Name: payment_logs_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: debt_tracking_user
--

SELECT pg_catalog.setval('public.payment_logs_log_id_seq', 8, true);


--
-- Name: payments_payment_id_seq; Type: SEQUENCE SET; Schema: public; Owner: debt_tracking_user
--

SELECT pg_catalog.setval('public.payments_payment_id_seq', 34, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: debt_tracking_user
--

SELECT pg_catalog.setval('public.users_id_seq', 7, true);


--
-- Name: debts debts_pkey; Type: CONSTRAINT; Schema: public; Owner: debt_tracking_user
--

ALTER TABLE ONLY public.debts
    ADD CONSTRAINT debts_pkey PRIMARY KEY (payment, debtor);


--
-- Name: friend_requests freq_ck; Type: CONSTRAINT; Schema: public; Owner: debt_tracking_user
--

ALTER TABLE ONLY public.friend_requests
    ADD CONSTRAINT freq_ck UNIQUE (made_by, made_for, date_created);


--
-- Name: friend_requests friend_requests_pkey; Type: CONSTRAINT; Schema: public; Owner: debt_tracking_user
--

ALTER TABLE ONLY public.friend_requests
    ADD CONSTRAINT friend_requests_pkey PRIMARY KEY (request_id);


--
-- Name: friends friends_pkey; Type: CONSTRAINT; Schema: public; Owner: debt_tracking_user
--

ALTER TABLE ONLY public.friends
    ADD CONSTRAINT friends_pkey PRIMARY KEY (friend1, friend2);


--
-- Name: payment_logs payment_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: debt_tracking_user
--

ALTER TABLE ONLY public.payment_logs
    ADD CONSTRAINT payment_logs_pkey PRIMARY KEY (log_id);


--
-- Name: payments payments_pkey; Type: CONSTRAINT; Schema: public; Owner: debt_tracking_user
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_pkey PRIMARY KEY (payment_id);


--
-- Name: status_domain status_domain_pkey; Type: CONSTRAINT; Schema: public; Owner: debt_tracking_user
--

ALTER TABLE ONLY public.status_domain
    ADD CONSTRAINT status_domain_pkey PRIMARY KEY (status);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: debt_tracking_user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: debt_tracking_user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: debts debts_payments_fk; Type: FK CONSTRAINT; Schema: public; Owner: debt_tracking_user
--

ALTER TABLE ONLY public.debts
    ADD CONSTRAINT debts_payments_fk FOREIGN KEY (payment) REFERENCES public.payments(payment_id) ON DELETE CASCADE;


--
-- Name: debts debts_users_fk; Type: FK CONSTRAINT; Schema: public; Owner: debt_tracking_user
--

ALTER TABLE ONLY public.debts
    ADD CONSTRAINT debts_users_fk FOREIGN KEY (debtor) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: friend_requests freq_fk; Type: FK CONSTRAINT; Schema: public; Owner: debt_tracking_user
--

ALTER TABLE ONLY public.friend_requests
    ADD CONSTRAINT freq_fk FOREIGN KEY (status) REFERENCES public.status_domain(status) ON DELETE CASCADE;


--
-- Name: friends friend1_users_fk; Type: FK CONSTRAINT; Schema: public; Owner: debt_tracking_user
--

ALTER TABLE ONLY public.friends
    ADD CONSTRAINT friend1_users_fk FOREIGN KEY (friend1) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: friends friend2_users_fk; Type: FK CONSTRAINT; Schema: public; Owner: debt_tracking_user
--

ALTER TABLE ONLY public.friends
    ADD CONSTRAINT friend2_users_fk FOREIGN KEY (friend2) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: friend_requests made_by_user_fk; Type: FK CONSTRAINT; Schema: public; Owner: debt_tracking_user
--

ALTER TABLE ONLY public.friend_requests
    ADD CONSTRAINT made_by_user_fk FOREIGN KEY (made_by) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: friend_requests made_for_user_fk; Type: FK CONSTRAINT; Schema: public; Owner: debt_tracking_user
--

ALTER TABLE ONLY public.friend_requests
    ADD CONSTRAINT made_for_user_fk FOREIGN KEY (made_for) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: payments paid_by_user_fk; Type: FK CONSTRAINT; Schema: public; Owner: debt_tracking_user
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT paid_by_user_fk FOREIGN KEY (paid_by) REFERENCES public.users(id) ON DELETE CASCADE;