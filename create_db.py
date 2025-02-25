import sqlite3
from transformers import pipeline

def create_database():
    conn = sqlite3.connect("recruitment.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT,
            Date TEXT,
            Email TEXT,
            Phone_Number TEXT,
            CV TEXT,
            Current_Status TEXT,
            Assignee TEXT,
            Status_Due_Date TEXT,
            Notified TEXT,
            Location TEXT,
            First_Priority TEXT,
            Second_Priority TEXT,
            Fail_Stage TEXT,
            Fail_Reason TEXT,
            University TEXT,
            Notes TEXT
        )
    """)
    
    sample_data = [
        ("John Doe", "2025-02-20", "johndoe@example.com", "1234567890", "CV_John.pdf", "Pending", "HR", "2025-03-01", "Yes", "New York", "Tech", "Finance", "NA", "NA", "Harvard", "Strong candidate"),
        ("Alice Smith", "2025-02-18", "alice@example.com", "2345678901", "CV_Alice.pdf", "Interviewed", "Recruiter", "2025-03-05", "No", "San Francisco", "Marketing", "Sales", "NA", "NA", "Stanford", "Good experience"),
        ("Bob Johnson", "2025-02-15", "bob@example.com", "3456789012", "CV_Bob.pdf", "Rejected", "Manager", "2025-02-25", "Yes", "Chicago", "Engineering", "Tech", "Technical", "Failed test", "MIT", "Needs more skills"),
        ("Emma Brown", "2025-02-22", "emma@example.com", "4567890123", "CV_Emma.pdf", "Pending", "HR", "2025-03-02", "No", "Los Angeles", "Design", "Marketing", "NA", "NA", "Yale", "Creative skills"),
        ("David Wilson", "2025-02-19", "david@example.com", "5678901234", "CV_David.pdf", "Shortlisted", "HR", "2025-03-10", "Yes", "Boston", "Finance", "Banking", "NA", "NA", "Princeton", "Analytical thinker"),
        ("Sophia Turner", "2025-02-21", "sophia@example.com", "6789012345", "CV_Sophia.pdf", "Pending", "Recruiter", "2025-03-06", "Yes", "Seattle", "Marketing", "Design", "NA", "NA", "Columbia", "Strong portfolio"),
        ("Liam Harris", "2025-02-17", "liam@example.com", "7890123456", "CV_Liam.pdf", "Rejected", "Manager", "2025-02-28", "No", "Austin", "Tech", "Engineering", "Experience", "Insufficient", "Carnegie Mellon", "Needs more experience"),
        ("Olivia Martinez", "2025-02-16", "olivia@example.com", "8901234567", "CV_Olivia.pdf", "Interviewed", "HR", "2025-03-07", "Yes", "Denver", "Sales", "Marketing", "NA", "NA", "UPenn", "Excellent communicator"),
        ("Noah Wright", "2025-02-14", "noah@example.com", "9012345678", "CV_Noah.pdf", "Pending", "Recruiter", "2025-03-04", "No", "Portland", "Tech", "Data Science", "NA", "NA", "Berkeley", "Strong data skills"),
        ("Emma Clark", "2025-02-13", "emma.clark@example.com", "0123456789", "CV_EmmaC.pdf", "Shortlisted", "HR", "2025-03-12", "Yes", "Miami", "Finance", "Economics", "NA", "NA", "Cornell", "Detail-oriented"),
        ("Lucas Hall", "2025-02-12", "lucas@example.com", "1123456789", "CV_Lucas.pdf", "Rejected", "Recruiter", "2025-02-27", "No", "Dallas", "Banking", "Finance", "Technical", "Failed test", "Duke", "Needs more preparation"),
        ("Ava Robinson", "2025-02-11", "ava@example.com", "2123456789", "CV_Ava.pdf", "Pending", "HR", "2025-03-08", "Yes", "Atlanta", "Marketing", "Sales", "NA", "NA", "Northwestern", "Creative marketer"),
        ("William King", "2025-02-10", "william@example.com", "3123456789", "CV_William.pdf", "Interviewed", "Manager", "2025-03-09", "No", "Houston", "Tech", "AI", "NA", "NA", "Georgia Tech", "Passionate about AI"),
        ("Charlotte Adams", "2025-02-09", "charlotte@example.com", "4123456789", "CV_Charlotte.pdf", "Rejected", "HR", "2025-03-03", "Yes", "Phoenix", "Design", "UX", "Experience", "Insufficient", "RISD", "Needs more project work"),
        ("James Scott", "2025-02-08", "james@example.com", "5123456789", "CV_James.pdf", "Pending", "Recruiter", "2025-03-11", "No", "Philadelphia", "Engineering", "Robotics", "NA", "NA", "UCLA", "Innovative thinker"),
        ("Isabella White", "2025-02-07", "isabella@example.com", "6123456789", "CV_Isabella.pdf", "Shortlisted", "HR", "2025-03-14", "Yes", "San Diego", "Finance", "Banking", "NA", "NA", "Michigan", "Great analytical skills")
    ]
    
    cursor.executemany("""
        INSERT INTO candidates (Name, Date, Email, Phone_Number, CV, Current_Status, Assignee, Status_Due_Date, Notified, Location, First_Priority, Second_Priority, Fail_Stage, Fail_Reason, University, Notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, sample_data)
    
    conn.commit()
    conn.close()
    print("Database created and populated with sample data.")

create_database()