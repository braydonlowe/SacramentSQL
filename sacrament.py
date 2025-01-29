import sqlite3
from openai import OpenAI
import json
import os
from datetime import date

with open("config.json", "r") as config_file:
    full_configuration = json.load(config_file)


#Delete db:
fdir = os.path.dirname(__file__)
def getPath(fname):
    return os.path.join(fdir, fname)

db_path = getPath("ward_members.db")

if os.path.exists(db_path):
    os.remove(db_path)

#Open AI
opeenAIClient = OpenAI(api_key = full_configuration["GPT_KEY"])

#Throw an error if config not working
if not opeenAIClient:
     print("Error: API configuration is incorrect.")

def query_database(sql):
    try:
        with sqlite3.connect("ward_members.db") as conn:
            cursor = conn.cursor()
            cursor.execute(sql)
            result = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]
            return {"columns": column_names, "data": result}
    except Exception as e:
        return {"error": str(e)}
    

def generate_sql(user_input):
    prompt = f"""
You are an expert SQL assistant. The database schema is as follows:

Table: QuoremMembers
- MemberID (INTEGER): Primary Key
- Name (VARCHAR): Member's name
- Email (VARCHAR): Member's email
- TimesPassed (INTEGER): Times the member has passed
- LastPassedDate (DATE): Last date the member passed
- LatestResponse (TEXT): The latest response of the member.

Table: Week
- WeekID (INTEGER): Primary Key
- SundayDate (DATE): The date of the week
- Role (TEXT): 'Blesser' or 'Passer'
- MemberID (INTEGER): Foreign Key referencing QuoremMembers(MemberID)

User's question: "{user_input}"

Generate an SQL query to answer the user's question.
"""
    stream = opeenAIClient.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        stream=True,
    )
    responseList = []
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            responseList.append(chunk.choices[0].delta.content)

    result = "".join(responseList)
    return result

def format_response(user_input, sql_result):
    prompt = f"""
You are an expert in converting database query results into plain language. 

User's question: "{user_input}"
SQL result: {sql_result}

Answer the user's question in plain language based on the SQL result.
"""
    stream = opeenAIClient.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        stream=True,
    )
    responseList = []
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            responseList.append(chunk.choices[0].delta.content)

    result = "".join(responseList)
    return result


def sanitizeForJustSql(value):
    gptStartSqlMarker = "```sql"
    gptEndSqlMarker = "```"
    if gptStartSqlMarker in value:
        value = value.split(gptStartSqlMarker)[1]
    if gptEndSqlMarker in value:
        value = value.split(gptEndSqlMarker)[0]

    return value


conn = sqlite3.connect("ward_members.db")
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS QuoremMembers (
    MemberID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name VARCHAR(50) NOT NULL,
    Email VARCHAR(200),
    TimesPassed INTEGER,
    LastPassedDate DATE,
    LatestResponse TEXT

)
''')


cursor.execute('''
CREATE TABLE IF NOT EXISTS Week (
    WeekID INTEGER PRIMARY KEY AUTOINCREMENT,
    SundayDate DATE NOT NULL,
    Role TEXT CHECK (Role IN ('Blesser', 'Passer')),
    MemberID integer,
    FOREIGN KEY (MemberID) REFERENCES QuoremMembers (MemberID)
)
''')


#Data in DB
members = [
    ('John Doe', 'john.doe@example.com', 5, '2025-01-05', 'Available'),
    ('Doug Smith', 'doug.smith@example.com', 3, '2025-01-05', 'Unavailable'),
    ('Mark Lee', 'mark.lee@example.com', 2, '2025-01-26', 'Available'),
    ('Ben Davis', 'ben.davis@example.com', 7, '2025-01-26', 'Available'),
    ('Don Marks', 'donmarks17@example.com', 18, '2025-01-26' ,'Available'),
    ('Matt Howels', 'howlsmatt@hotmail.com', 6, '2025-01-26', 'If you want me to be available.'),
    ('Unavailable Ken', 'passmenot@example.com', 0, None, 'Unavailable')
]

#Who are the people who are scheduled to pass that haven't passed yet?
schedule = [
    ('2025-01-05', 'Blesser', 1),
    ('2025-01-05', 'Blesser', 2),
    ('2025-01-26', 'Passer', 3),
    ('2025-01-26', 'Passer', 4),
    ('2025-01-26', 'Passer', 5),
    ('2025-01-26', 'Passer', 6),
    ('2025-02-02', 'Blesser', 2),
    ('2025-02-02', 'Blesser', 3),
    ('2025-02-02', 'Passer', 1),
    ('2025-02-02', 'Passer', 4),
    ('2025-02-02', 'Passer', 5),
    ('2025-02-02', 'Passer', 6)
]



#Insert into DB
cursor.executemany('''
INSERT INTO Week (SundayDate, Role, MemberID)
VALUES (?,?,?)
''', schedule)

cursor.executemany('''
INSERT INTO QuoremMembers (Name, Email, TimesPassed, LastPassedDate, LatestResponse)
VALUES (?,?,?,?,?)
''', members)



conn.commit()
conn.close()

print("Updated database")



def main():
    print("Welcome to the Automated Sacrament Coordinator!")
    print("Ask a question about the Sacrament DB.")
    print("Type 'exit' to quit.")


    while True:
        user_input = input("Question: ")
        if user_input.lower() == 'exit':
                print("Goodbye!")
                break
        
        sql_query = generate_sql(user_input)
        print(f"Generated SQL: {sql_query}")

        if "error" in sql_query.lower():
             print("Failed to generate SQL. Please try repharasing your question.")
             continue
        
        sql_only  = sanitizeForJustSql(sql_query)
        sql_result = query_database(sql_only)

        print()
        print("SQL ONLY:")
        print(sql_only)
        print()
        
    
        readable_response = format_response(user_input, sql_result)
        print(f"\nAnswer: {readable_response}")





if __name__ == "__main__":
     main()
            

        


