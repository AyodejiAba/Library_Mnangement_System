"""
Library Management System — Streamlit front end for a MySQL database.

Tables expected in MySQL (see liane_library_setup.sql):
  author(author_id, first_name, last_name, email, nationality)
  publishers(publisher_id, publisher_name, country)
  books(isbn, title, publication_year, language, publisher_id, author_id)
  book_copies(copy_id, isbn, status)
  members(member_id, first_name, last_name, email, phone, address, join_date)
  book_loans(loan_id, isbn, member_id, borrowed_date, due_date, returned_date)

Setup:
  1. Run liane_library_setup.sql against your MySQL server to create the
     schema and load the seed data.
  2. Set the DB_* values below (or environment variables of the same name)
     to match your MySQL server.
  3. pip install streamlit pandas sqlalchemy pymysql
  4. streamlit run app.py
"""

import os
import datetime as dt
import traceback
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

st.set_page_config(page_title="Library Management System", page_icon="📚", layout="wide")

# --------------------------------------------------------------------------------------
# Database connection
# --------------------------------------------------------------------------------------
# Values can be overridden with environment variables so you don't have to hardcode
# a password in this file: DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_SCHEMA.
DB_SCHEMA = os.environ.get("DB_SCHEMA", "liane_library")
DB_HOST = os.environ.get("DB_HOST", "127.0.0.1")
DB_PORT = int(os.environ.get("DB_PORT", "3306"))
DB_USER = os.environ.get("DB_USER", "root")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "Ayodeji007!")

connection_string = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_SCHEMA}"
)


@st.cache_resource
def get_engine():
    return create_engine(connection_string, pool_pre_ping=True)


def run_query(sql, params=None):
    """SELECT queries -> returns a DataFrame."""
    try:
        with get_engine().connect() as conn:
            return pd.read_sql(text(sql), conn, params=params or {})
    
    except Exception as e:
        st.code(traceback.format_exc())
        raise e


def run_action(sql, params=None):
    """INSERT / UPDATE / DELETE queries -> commits, returns success bool + error message."""
    try:
        with get_engine().begin() as conn:
            conn.execute(text(sql), params or {})
        return True, None
    except SQLAlchemyError as e:
        return False, str(e.orig) if hasattr(e, "orig") else str(e)


def test_connection():
    try:
        with get_engine().connect() as conn:
            conn.execute(text("SELECT 1"))
        return True, None
    except SQLAlchemyError as e:
        return False, str(e.orig) if hasattr(e, "orig") else str(e)


# --------------------------------------------------------------------------------------
# Sidebar navigation + connection status
# --------------------------------------------------------------------------------------
st.sidebar.title("📚 Library System")

ok, err = test_connection()
if ok:
    st.sidebar.success(f"Connected to `{DB_SCHEMA}` @ {DB_HOST}:{DB_PORT}")
else:
    st.sidebar.error("Database connection failed")
    st.sidebar.caption(str(err))

page = st.sidebar.radio(
    "Go to",
    ["Dashboard", "Books", "Authors", "Publishers", "Members", "Loans"],
    disabled=not ok,
)

if not ok:
    st.title("📚 Library Management System")
    st.error(
        "Could not connect to the database. Check `DB_HOST`, `DB_PORT`, `DB_USER`, "
        "`DB_PASSWORD`, and `DB_SCHEMA` (env vars, or the defaults at the top of app.py), "
        "and make sure MySQL is running and `liane_library_setup.sql` has been run."
    )
    st.code(str(err))
    st.stop()

# --------------------------------------------------------------------------------------
# Dashboard
# --------------------------------------------------------------------------------------
if page == "Dashboard":
    st.title("Dashboard")

    try:
        n_books = run_query("SELECT COUNT(*) AS n FROM books")["n"][0]
        n_copies = run_query("SELECT COUNT(*) AS n FROM book_copies")["n"][0]
        n_available = run_query(
            "SELECT COUNT(*) AS n FROM book_copies WHERE status = 'Available'"
        )["n"][0]
        n_members = run_query("SELECT COUNT(*) AS n FROM members")["n"][0]
        n_active_loans = run_query(
            "SELECT COUNT(*) AS n FROM book_loans WHERE returned_date IS NULL"
        )["n"][0]
        n_overdue = run_query(
            "SELECT COUNT(*) AS n FROM book_loans "
            "WHERE returned_date IS NULL AND due_date < CURDATE()"
        )["n"][0]

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Total Books", n_books)
        c2.metric("Total Copies", n_copies)
        c3.metric("Available Copies", n_available)
        c4.metric("Members", n_members)
        c5.metric("Active Loans", n_active_loans, delta=f"{n_overdue} overdue", delta_color="inverse")

        st.subheader("Overdue Loans")
        overdue = run_query(
            """
            SELECT bl.loan_id, b.title, m.first_name, m.last_name, bl.due_date
            FROM book_loans bl
            JOIN books b ON b.isbn = bl.isbn
            JOIN members m ON m.member_id = bl.member_id
            WHERE bl.returned_date IS NULL AND bl.due_date < CURDATE()
            ORDER BY bl.due_date
            """
        )
        if not overdue.empty:
           st.dataframe(overdue, use_container_width=True)
        else:
           st.info("No overdue loans 🎉")
        
    except Exception:
        st.exception(traceback.format_exc())

# --------------------------------------------------------------------------------------
# Books
# --------------------------------------------------------------------------------------
elif page == "Books":
    st.title("Books")

    tab_view, tab_add, tab_edit, tab_delete = st.tabs(["View", "Add", "Edit", "Delete"])

    with tab_view:
        search = st.text_input("Search by title or ISBN")
        query = """
            SELECT b.isbn, b.title, b.publication_year, b.language,
                   p.publisher_name, CONCAT(a.first_name, ' ', a.last_name) AS authors
            FROM books b
            LEFT JOIN publishers p ON p.publisher_id = b.publisher_id
            LEFT JOIN authors a ON a.author_id = b.author_id
        """
        if search:
            query += " WHERE b.title LIKE :s OR b.isbn LIKE :s"
            df = run_query(query, {"s": f"%{search}%"})
        else:
            df = run_query(query)
        st.dataframe(df, use_container_width=True)

    with tab_add:
        publishers = run_query("SELECT publisher_id, publisher_name FROM publishers")
        authors = run_query("SELECT author_id, first_name, last_name FROM authors")

        with st.form("add_book"):
            isbn = st.text_input("ISBN")
            title = st.text_input("Title")
            publication_year = st.number_input("Publication year", min_value=1000, max_value=dt.date.today().year, step=1)
            language = st.text_input("Language", value="English")
            publishers = st.selectbox(
                "Publisher", publishers["publisher_id"],
                format_func=lambda x: publishers.set_index("publisher_id").loc[x, "publisher_name"],
            ) if not publishers.empty else None
            authors = st.selectbox(
                "Author", authors["author_id"],
                format_func=lambda x: f"{authors.set_index('author_id').loc[x, 'first_name']} "
                                       f"{authors.set_index('author_id').loc[x, 'last_name']}",
            ) if not authors.empty else None
            submitted = st.form_submit_button("Add Book")

        if submitted:
            if not isbn or not title:
                st.warning("ISBN and title are required.")
            else:
                ok, err = run_action(
                    """
                    INSERT INTO books (isbn, title, publication_year, language, publisher_id, author_id)
                    VALUES (:isbn, :title, :publication_year, :language, :publishers, :authors)
                    """,
                    {"isbn": isbn, "title": title, "publication_year": publication_year, "language": language,
                     "publishers": publishers, "authors": authors},
                )
                st.success("Book added.") if ok else st.error(f"Failed: {err}")

    with tab_edit:
        books = run_query("SELECT isbn, title FROM books")
        if books.empty:
            st.info("No books yet.")
        else:
            isbn_choice = st.selectbox(
                "Select a book to edit", books["isbn"],
                format_func=lambda x: f"{x} — {books.set_index('isbn').loc[x, 'title']}",
            )
            current = run_query("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn_choice}).iloc[0]

            with st.form("edit_book"):
                title = st.text_input("Title", value=current["title"])
                year = st.number_input(
                    "Publication year", min_value=1000, max_value=dt.date.today().year,
                    value=int(current["publication_year"]), step=1,
                )
                language = st.text_input("Language", value=current["language"])
                submitted = st.form_submit_button("Save changes")

            if submitted:
                ok, err = run_action(
                    "UPDATE books SET title=:title, publication_year=:year, language=:language WHERE isbn=:isbn",
                    {"title": title, "year": publication_year, "language": language, "isbn": isbn_choice},
                )
                st.success("Book updated.") if ok else st.error(f"Failed: {err}")

    with tab_delete:
        books = run_query("SELECT isbn, title FROM books")
        if books.empty:
            st.info("No books yet.")
        else:
            isbn_choice = st.selectbox(
                "Select a book to delete", books["isbn"],
                format_func=lambda x: f"{x} — {books.set_index('isbn').loc[x, 'title']}",
                key="delete_book_select",
            )
            if st.button("Delete book", type="primary"):
                ok, err = run_action("DELETE FROM books WHERE isbn = :isbn", {"isbn": isbn_choice})
                st.success("Book deleted.") if ok else st.error(
                    f"Failed: {err}. It may have copies or loans referencing it."
                )

# --------------------------------------------------------------------------------------
# Authors
# --------------------------------------------------------------------------------------
elif page == "Authors":
    st.title("Authors")

    tab_view, tab_add, tab_delete = st.tabs(["View", "Add", "Delete"])

    with tab_view:
        st.dataframe(run_query("SELECT * FROM authors"), use_container_width=True)

    with tab_add:
        with st.form("add_author"):
            first_name = st.text_input("First name")
            last_name = st.text_input("Last name")
            email = st.text_input("Email")
            nationality = st.text_input("Nationality")
            submitted = st.form_submit_button("Add Author")

        if submitted:
            if not first_name or not last_name:
                st.warning("First and last name are required.")
            else:
                ok, err = run_action(
                    """
                    INSERT INTO author (first_name, last_name, email, nationality)
                    VALUES (:fn, :ln, :email, :nat)
                    """,
                    {"fn": first_name, "ln": last_name, "email": email, "nat": nationality},
                )
                st.success("Author added.") if ok else st.error(f"Failed: {err}")

    with tab_delete:
        authors = run_query("SELECT author_id, first_name, last_name FROM authors")
        if authors.empty:
            st.info("No authors yet.")
        else:
            author_choice = st.selectbox(
                "Select an author to delete", authors["author_id"],
                format_func=lambda x: f"{authors.set_index('author_id').loc[x, 'first_name']} "
                                       f"{authors.set_index('author_id').loc[x, 'last_name']}",
            )
            if st.button("Delete author", type="primary"):
                ok, err = run_action(
                    "DELETE FROM authors WHERE author_id = :id", {"id": author_choice}
                )
                st.success("Author deleted.") if ok else st.error(
                    f"Failed: {err}. They may still have books linked to them."
                )

# --------------------------------------------------------------------------------------
# Publishers
# --------------------------------------------------------------------------------------
elif page == "Publishers":
    st.title("Publishers")

    tab_view, tab_add, tab_delete = st.tabs(["View", "Add", "Delete"])

    with tab_view:
        st.dataframe(run_query("SELECT * FROM publishers"), use_container_width=True)

    with tab_add:
        with st.form("add_publisher"):
            publisher_name = st.text_input("Publisher name")
            country = st.text_input("Country")
            submitted = st.form_submit_button("Add Publisher")

        if submitted:
            if not publisher_name:
                st.warning("Publisher name is required.")
            else:
                ok, err = run_action(
                    "INSERT INTO publishers (publisher_name, country) VALUES (:name, :country)",
                    {"name": publisher_name, "country": country},
                )
                st.success("Publisher added.") if ok else st.error(f"Failed: {err}")

    with tab_delete:
        publishers = run_query("SELECT publisher_id, publisher_name FROM publishers")
        if publishers.empty:
            st.info("No publishers yet.")
        else:
            pub_choice = st.selectbox(
                "Select a publisher to delete", publishers["publisher_id"],
                format_func=lambda x: publishers.set_index("publisher_id").loc[x, "publisher_name"],
            )
            if st.button("Delete publisher", type="primary"):
                ok, err = run_action(
                    "DELETE FROM publishers WHERE publisher_id = :id", {"id": pub_choice}
                )
                st.success("Publisher deleted.") if ok else st.error(
                    f"Failed: {err}. They may still have books linked to them."
                )

# --------------------------------------------------------------------------------------
# Members
# --------------------------------------------------------------------------------------
elif page == "Members":
    st.title("Members")

    tab_view, tab_add, tab_edit, tab_delete = st.tabs(["View", "Add", "Edit", "Delete"])

    with tab_view:
        search = st.text_input("Search by name or email")
        query = "SELECT * FROM members"
        if search:
            query += " WHERE first_name LIKE :s OR last_name LIKE :s OR email LIKE :s"
            df = run_query(query, {"s": f"%{search}%"})
        else:
            df = run_query(query)
        st.dataframe(df, use_container_width=True)

    with tab_add:
        with st.form("add_member"):
            first_name = st.text_input("First name")
            last_name = st.text_input("Last name")
            email = st.text_input("Email")
            phone = st.text_input("Phone")
            address = st.text_input("Address")
            join_date = st.date_input("Join date", value=dt.date.today())
            submitted = st.form_submit_button("Add Member")

        if submitted:
            if not first_name or not last_name:
                st.warning("First and last name are required.")
            else:
                ok, err = run_action(
                    """
                    INSERT INTO members (first_name, last_name, email, phone, address, join_date)
                    VALUES (:fn, :ln, :email, :phone, :address, :join_date)
                    """,
                    {"fn": first_name, "ln": last_name, "email": email,
                     "phone": phone, "address": address, "join_date": join_date},
                )
                st.success("Member added.") if ok else st.error(f"Failed: {err}")

    with tab_edit:
        members = run_query("SELECT member_id, first_name, last_name FROM members")
        if members.empty:
            st.info("No members yet.")
        else:
            member_choice = st.selectbox(
                "Select a member to edit", members["member_id"],
                format_func=lambda x: f"{members.set_index('member_id').loc[x, 'first_name']} "
                                       f"{members.set_index('member_id').loc[x, 'last_name']}",
            )
            current = run_query(
                "SELECT * FROM members WHERE member_id = :id", {"id": member_choice}
            ).iloc[0]

            with st.form("edit_member"):
                email = st.text_input("Email", value=current["email"] or "")
                phone = st.text_input("Phone", value=current["phone"] or "")
                address = st.text_input("Address", value=current["address"] or "")
                submitted = st.form_submit_button("Save changes")

            if submitted:
                ok, err = run_action(
                    "UPDATE members SET email=:email, phone=:phone, address=:address WHERE member_id=:id",
                    {"email": email, "phone": phone, "address": address, "id": member_choice},
                )
                st.success("Member updated.") if ok else st.error(f"Failed: {err}")

    with tab_delete:
        members = run_query("SELECT member_id, first_name, last_name FROM members")
        if members.empty:
            st.info("No members yet.")
        else:
            member_choice = st.selectbox(
                "Select a member to delete", members["member_id"],
                format_func=lambda x: f"{members.set_index('member_id').loc[x, 'first_name']} "
                                       f"{members.set_index('member_id').loc[x, 'last_name']}",
                key="delete_member_select",
            )
            if st.button("Delete member", type="primary"):
                ok, err = run_action(
                    "DELETE FROM members WHERE member_id = :id", {"id": member_choice}
                )
                st.success("Member deleted.") if ok else st.error(
                    f"Failed: {err}. They may still have loans linked to them."
                )

# --------------------------------------------------------------------------------------
# Loans
# --------------------------------------------------------------------------------------
elif page == "Loans":
    st.title("Loans")

    tab_view, tab_checkout, tab_return = st.tabs(["View", "Check Out", "Return"])

    with tab_view:
        status_filter = st.radio("Filter", ["All", "Active", "Returned", "Overdue"], horizontal=True)
        query = """
            SELECT bl.loan_id, b.title, bl.isbn, CONCAT(m.first_name, ' ', m.last_name) AS member,
                   bl.borrowed_date, bl.due_date, bl.returned_date
            FROM book_loans bl
            JOIN books b ON b.isbn = bl.isbn
            JOIN members m ON m.member_id = bl.member_id
        """
        if status_filter == "Active":
            query += " WHERE bl.returned_date IS NULL"
        elif status_filter == "Returned":
            query += " WHERE bl.returned_date IS NOT NULL"
        elif status_filter == "Overdue":
            query += " WHERE bl.returned_date IS NULL AND bl.due_date < CURDATE()"
        query += " ORDER BY bl.borrowed_date DESC"
        st.dataframe(run_query(query), use_container_width=True)

    with tab_checkout:
        available_copies = run_query(
            """
            SELECT bc.copy_id, bc.isbn, b.title
            FROM book_copies bc
            JOIN books b ON b.isbn = bc.isbn
            WHERE bc.status = 'Available'
            """
        )
        members = run_query("SELECT member_id, first_name, last_name FROM members")

        if available_copies.empty:
            st.info("No available copies to loan out.")
        else:
            with st.form("checkout_form"):
                copy_choice = st.selectbox(
                    "Copy to loan out", available_copies["copy_id"],
                    format_func=lambda x: f"Copy #{x} — "
                    f"{available_copies.set_index('copy_id').loc[x, 'title']} "
                    f"({available_copies.set_index('copy_id').loc[x, 'isbn']})",
                )
                member_choice = st.selectbox(
                    "Member", members["member_id"],
                    format_func=lambda x: f"{members.set_index('member_id').loc[x, 'first_name']} "
                                           f"{members.set_index('member_id').loc[x, 'last_name']}",
                )
                borrowed_date = st.date_input("Borrowed date", value=dt.date.today())
                due_date = st.date_input("Due date", value=dt.date.today() + dt.timedelta(days=21))
                submitted = st.form_submit_button("Check out")

            if submitted:
                isbn = available_copies.set_index("copy_id").loc[copy_choice, "isbn"]
                ok1, err1 = run_action(
                    """
                    INSERT INTO book_loans (isbn, member_id, borrowed_date, due_date, returned_date)
                    VALUES (:isbn, :member_id, :borrowed_date, :due_date, NULL)
                    """,
                    {"isbn": isbn, "member_id": member_choice,
                     "borrowed_date": borrowed_date, "due_date": due_date},
                )
                ok2, err2 = run_action(
                    "UPDATE book_copies SET status = 'On Loan' WHERE copy_id = :copy_id",
                    {"copy_id": copy_choice},
                )
                if ok1 and ok2:
                    st.success("Book checked out.")
                else:
                    st.error(f"Failed: {err1 or err2}")

    with tab_return:
        active_loans = run_query(
            """
            SELECT bl.loan_id, b.title, bl.isbn, CONCAT(m.first_name, ' ', m.last_name) AS member
            FROM book_loans bl
            JOIN books b ON b.isbn = bl.isbn
            JOIN members m ON m.member_id = bl.member_id
            WHERE bl.returned_date IS NULL
            """
        )
        if active_loans.empty:
            st.info("No active loans.")
        else:
            loan_choice = st.selectbox(
                "Loan to mark as returned", active_loans["loan_id"],
                format_func=lambda x: f"{active_loans.set_index('loan_id').loc[x, 'title']} — "
                                       f"{active_loans.set_index('loan_id').loc[x, 'member']}",
            )
            return_date = st.date_input("Return date", value=dt.date.today())
            if st.button("Mark returned"):
                isbn = active_loans.set_index("loan_id").loc[loan_choice, "isbn"]
                ok1, err1 = run_action(
                    "UPDATE book_loans SET returned_date = :d WHERE loan_id = :id",
                    {"d": return_date, "id": loan_choice},
                )
                ok2, err2 = run_action(
                    """
                    UPDATE book_copies SET status = 'Available'
                    WHERE isbn = :isbn ORDER BY copy_id LIMIT 1
                    """,
                    {"isbn": isbn},
                )
                if ok1 and ok2:
                    st.success("Loan marked as returned.")
                else:
                    st.error(f"Failed: {err1 or err2}")