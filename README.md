# 📚 Library Management System

A relational database project built with **MySQL**, **Python**, **SQLAlchemy**, and **Jupyter Notebook** to manage a library's daily operations. The project demonstrates database design, SQL querying, CRUD operations, and Python database integration.
![SQL](https://img.shields.io/badge/SQL-336791?style=for-the-badge&logo=postgresql&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
![Git](https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white)
![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)

---

## 📖 Project Overview

This project simulates the backend database of a library management system. It allows librarians to manage:

- Authors
- Publishers
- Books
- Book Copies
- Members
- Book Loans

The project was developed to demonstrate practical SQL skills, database normalization, and Python integration with relational databases.

---

## 🚀 Features

- Design and implementation of a normalized relational database
- Primary and Foreign Key relationships
- CRUD (Create, Read, Update, Delete) operations using Python
- SQLAlchemy database connection
- Parameterized SQL queries
- Data retrieval using Pandas DataFrames
- Transaction management
- Error handling for database operations

---

## 🛠 Technologies Used

- Python
- MySQL
- SQLAlchemy
- PyMySQL
- Pandas
- Jupyter Notebook
- Git
- GitHub

---

## 🗂 Database Schema

The project contains the following tables:

### Authors

Stores information about book authors.

| Column | Description |
|---------|-------------|
| author_id | Primary Key |
| first_name | Author first name |
| last_name | Author last name |
| email | Email address |
| nationality | Country of origin |

---

### Publishers

Stores publisher information.

| Column | Description |
|---------|-------------|
| publisher_id | Primary Key |
| publisher_name | Publisher name |
| country | Country |

---

### Books

Stores book details.

| Column | Description |
|---------|-------------|
| isbn | Primary Key |
| title | Book title |
| publication_year | Publication year |
| language | Language |
| publisher_id | Foreign Key |
| author_id | Foreign Key |

---

### Book Copies

Tracks individual physical copies of books.

| Column | Description |
|---------|-------------|
| copy_id | Primary Key |
| isbn | Foreign Key |
| status | Available / Borrowed |

---

### Members

Stores registered library members.

| Column | Description |
|---------|-------------|
| member_id | Primary Key |
| first_name | First name |
| last_name | Last name |
| email | Email |
| phone | Phone number |
| membership_date | Registration date |

---

### Book Loans

Tracks borrowing history.

| Column | Description |
|---------|-------------|
| loan_id | Primary Key |
| isbn | Foreign Key |
| member_id | Foreign Key |
| borrowed_date | Borrow date |
| due_date | Due date |
| returned_date | Return date |

---

## 📊 Entity Relationship

```

Authors
│
│
└────── Books ────── Publishers
│
│
Book Copies

│

Book Loans

│

Members


## ⚙ Installation

Clone the repository.

```bash
git clone https://github.com/yourusername/library-management-system.git

cd library-management-system
```

Install the required packages.

```bash
pip install -r requirements.txt
```

---

## 🔌 Database Connection

```python
from sqlalchemy import create_engine

engine = create_engine(
    "mysql+pymysql://username:password@localhost:3306/liane_library"
)
```

---

## 💻 Example CRUD Operations

### Create

```python
create_author(
    "John",
    "Doe",
    "john@email.com",
    "USA"
)
```

### Read

```python
get_authors()
```

### Update

```python
update_author(
    1,
    "Johnny",
    "Doe",
    "john@email.com",
    "USA"
)
```

### Delete

```python
delete_author(1)
```

---

## 📈 Skills Demonstrated

- Relational Database Design
- SQL Joins
- Foreign Keys
- Data Modeling
- CRUD Operations
- Python Programming
- SQLAlchemy
- Pandas
- Data Management
- Git Version Control
- Database Integration

---

## 🎯 Learning Outcomes

This project demonstrates the ability to:

- Design normalized relational databases
- Connect Python applications to MySQL
- Implement reusable CRUD functions
- Write parameterized SQL queries
- Load and retrieve data efficiently using Pandas
- Manage database transactions with SQLAlchemy

---

## 🔮 Future Improvements

- Build a Flask web interface
- Add user authentication
- Implement book reservations
- Add overdue fine calculations
- Develop an interactive dashboard using Power BI
- Deploy the application using Docker

---

## 👤 Author

**Ayodeji Abajingin**

Aspiring Data Analyst | BI Analyst | Data Engineer

**Skills**

- SQL
- Python
- MySQL
- SQLAlchemy
- Pandas
- Git
- GitHub

---

## ⭐ If you found this project helpful

Feel free to ⭐ star the repository and connect with me on LinkedIn.
