import sqlite3
import os
from openai import OpenAI

from db.initt_db import db_path
from pipelines.simulation import simulate_threshold_change


# initialise openAI key......

client = OpenAI(api_key=os.getenv("OpenAI_API_KEY"))

# get database schema......


def get_schema():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("Select name from sqlite_master where type='table';")
    tables = cursor.fetchall()

    schema=""

    for table in tables:
        table_name = tables[0]
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        schema += f"\nTable: {table_name}\n"
        for col in columns:
            schema += f" - {col[1]} ({col[2]})\n"

    conn.close()
    return schema


# -------------------------------
# 2. Generate SQL from Question
# -------------------------------
def generate_sql(question):
    schema = get_schema()

    prompt = f"""
You are a fintech data analyst AI.

Convert the following natural language question into a valid SQLite SQL query.

Rules:
- Only use the tables and columns provided
- Do not hallucinate columns
- Use JOINs where needed
- Output ONLY SQL (no explanation)

Database Schema:
{schema}

Question:
{question}
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "You generate SQL queries."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    return response.choices[0].message.content.strip()


# -------------------------------
# 3. SQL Safety Validation
# -------------------------------
def validate_sql(sql_query):
    forbidden = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER"]

    for word in forbidden:
        if word in sql_query.upper():
            raise ValueError("Unsafe query detected!")

    return True


# -------------------------------
# 4. Execute SQL
# -------------------------------
def execute_sql(sql_query):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(sql_query)
    rows = cursor.fetchall()

    columns = [desc[0] for desc in cursor.description]

    conn.close()

    return columns, rows


# -------------------------------
# 5. Generate Business Insight
# -------------------------------
def generate_insight(question, sql_query, columns, rows):
    preview = rows[:5]

    prompt = f"""
You are a fintech analyst.

Explain the result of this SQL query in simple business terms.

Question:
{question}

SQL Query:
{sql_query}

Columns:
{columns}

Sample Data:
{preview}

Give a concise business insight.
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "You explain data insights."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )

    return response.choices[0].message.content.strip()


# -------------------------------
# 6. Detect Simulation Queries
# -------------------------------
def is_simulation_query(question):
    keywords = ["simulate", "threshold", "what happens", "impact"]

    return any(word in question.lower() for word in keywords)


# -------------------------------
# 7. Main Agent Function
# -------------------------------
def ask_agent(question):

    print("\n[User Question]")
    print(question)

    # -------------------------------
    # Simulation Mode
    # -------------------------------
    if is_simulation_query(question):
        print("\n[Simulation Mode Activated]")

        # Default threshold (we'll upgrade this later)
        new_threshold = 0.45

        result = simulate_threshold_change(new_threshold)

        print(result)
        return result

    # -------------------------------
    # SQL Mode
    # -------------------------------
    sql_query = generate_sql(question)

    print("\n[Generated SQL]")
    print(sql_query)

    validate_sql(sql_query)

    columns, rows = execute_sql(sql_query)

    print("\n[Query Result - First 5 Rows]")
    for row in rows[:5]:
        print(row)

    insight = generate_insight(question, sql_query, columns, rows)

    print("\n[Business Insight]")
    print(insight)

    return {
        "sql": sql_query,
        "columns": columns,
        "rows": rows,
        "insight": insight
    }