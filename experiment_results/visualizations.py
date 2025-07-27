import os
import psycopg2
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from decimal import Decimal
from collections import defaultdict
from psycopg2.extras import RealDictCursor
from pathlib import Path
from dotenv import load_dotenv


env_path = Path(__file__).resolve().parent.parent / '.env'  # Goes up 2 folders
print(env_path)
load_dotenv(env_path)

def close_resources(conn, cur):
    if cur:
        cur.close()
    if conn:
        conn.close()


def get_db_connection():
    """Connects to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            host=os.getenv("PG_HOST"),
            database=os.getenv("PG_DB"),
            user=os.getenv("PG_USER"),
            port=os.getenv("PG_PORT")
        )
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def fetch_payments(threshold=0):
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("""SELECT p.payment_id, p.description, p.paid_by, d.debtor, d.amount_owed FROM payments AS p 
                            INNER JOIN debts AS d ON p.payment_id = d.payment
                            WHERE p.payment_id > 20;""")
            all_payments = cur.fetchall()
            print((all_payments))
            close_resources(conn, cur)
            return all_payments
        except psycopg2.Error as err:
            close_resources(conn, cur)
            print(str(err), "danger")
    else:
        print("Database connection failed", "danger")

def fetch_dataframe(query):
    conn = get_db_connection()
    if conn:
        try:
            df = pd.read_sql_query(query, conn)
            close_resources(conn, None)
            return df
        except Exception as e:
            print(f"Error: {e}")
            return pd.DataFrame()

def fetch_value(query):
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute(query)
            value = cur.fetchone()
            close_resources(conn, None)
            return value
        except Exception as e:
            print(f"Error: {e}")
            return pd.DataFrame()


# --- Visualization Functions ---
def plot_payment_categories():
    data = {'Category': ['Food', 'Recreation'], 'Count': [9, 5]}
    df = pd.DataFrame(data)
    total = df['Count'].sum()
    plt.pie(df['Count'], labels=df['Category'], autopct='%1.1f%%', startangle=90)
    plt.title(f"Payments by Category (Total: {total})")
    plt.axis('equal')
    plt.savefig("category_breakdown_pie.png")
    plt.clf()


def plot_total_paid_by_user():
    query = '''SELECT paid_by, SUM(total) AS total_paid 
               FROM payments WHERE payment_id > 20 
               GROUP BY paid_by ORDER BY total_paid DESC;'''
    df = fetch_dataframe(query)
    total = df['total_paid'].sum()
    plt.pie(df['total_paid'], labels=df['paid_by'], autopct='%1.1f%%', startangle=90)
    plt.title(f"Total Paid by Each User (Total Volume: ${total:.2f})")
    plt.axis('equal')
    plt.savefig("total_paid_by_user_pie.png")
    plt.clf()


def plot_debts_simplification():
    initial_transaction = fetch_value("""SELECT COUNT(payment_id) FROM payments AS p 
                            INNER JOIN debts AS d ON p.payment_id = d.payment
                            WHERE p.payment_id > 20;""")
    simplified_transactions = fetch_value("""SELECT COUNT(friend1) FROM friends WHERE owes > 0;""")
    data = {'Stage': ['Before', 'After'], 'Transactions': [30, 3]}
    df = pd.DataFrame(data)
    sns.barplot(data=df, x='Stage', y='Transactions')
    plt.title("Debt Simplification: Transactions Before vs After")
    plt.savefig("debt_simplification.png")
    plt.clf()


def plot_money_saved():
    query = """
            SELECT debtor AS user, 
                   SUM(amount_owed) AS would_have_paid, 
                   ROUND((SUM(amount_owed) * 0.029 + 0.3)::numeric, 2) AS fees_avoided
            FROM debts
            WHERE payment > 20
            GROUP BY debtor;
            """
    df = fetch_dataframe(query)
    sns.barplot(data=df, x='user', y='fees_avoided')
    plt.title("PayPal Payment Fees Avoided by Each User")
    plt.xlabel("User")
    plt.ylabel("Fees Avoided ($)")
    plt.savefig("paypal_fees_avoided.png")
    plt.clf()


def plot_net_received():
    query = """
            SELECT p.paid_by AS user,
                   ROUND((SUM(d.amount_owed) * 0.015)::numeric, 2) AS fees_lost
            FROM payments AS p
            INNER JOIN debts AS d ON p.payment_id = d.payment
            WHERE p.payment_id > 20
            GROUP BY p.paid_by;
            """
    df = fetch_dataframe(query)
    sns.barplot(data=df, x='user', y='fees_lost')
    plt.title("PayPal Withdrawal Loss Avoided by Each User")
    plt.xlabel("User")
    plt.ylabel("Loss Avoided ($)")
    plt.savefig("net_received_and_loss.png")
    plt.clf()


def main():
    #plot_payment_categories()
    plot_total_paid_by_user()
    #plot_debts_simplification()
    #plot_money_saved()
    #plot_net_received()
    print("Visualizations generated and saved.")


if __name__ == "__main__":
    main()