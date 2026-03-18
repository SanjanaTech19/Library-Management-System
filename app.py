import streamlit as st
import mysql.connector
import pandas as pd
import plotly.express as px
import os
from datetime import datetime, date

# --- 1. DATABASE CONNECTION ---

def get_db_connection():
    try:
        return mysql.connector.connect(
            host=st.secrets["DB_HOST"],
            user=st.secrets["DB_USER"],
            password=st.secrets["DB_PASSWORD"],
            port=int(st.secrets["DB_PORT"]),
            database=st.secrets["DB_NAME"]
        )
    except Exception as e:
        st.error(f"⚠️ Database Connection Error: {e}")
        return None

# --- 2. PAGE CONFIG & STYLING ---
st.set_page_config(page_title="The Reading Nook", page_icon="📚", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #b9d8e4; }
    h1, h2, h3 { color: #483D8B; }
    .stButton>button { 
        background-color: #f6cab7; 
        color: #2E8B57; 
        font-weight: bold; 
        border: 1px solid #2E8B57;
        border-radius: 10px;
    }
    .stSuccess { background-color: #C1E1C1; color: #006400; }
    [data-testid="stMetricValue"] { color: #483D8B; }
    div[data-testid="column"] {
        padding: 15px;
        border-radius: 15px;
        background-color: rgba(255, 255, 255, 0.4);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. AUTHENTICATION ---
def login_page():
    st.title("🔐 Library Management System")
    if 'signup_mode' not in st.session_state:
        st.session_state.signup_mode = False

    if not st.session_state.signup_mode:
        st.subheader("Login")
        user = st.text_input("Username", key="login_user")
        pw = st.text_input("Password", type="password", key="login_pass")
        
        if st.button("Login", use_container_width=True):
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("SELECT username, role FROM users WHERE username=%s AND password=%s", (user, pw))
                user_data = cursor.fetchone()
                if user_data:
                    st.session_state.logged_in = True
                    st.session_state.username = user_data[0]
                    st.session_state.user_role = user_data[1]
                    st.rerun()
                else:
                    st.error("Invalid credentials.")
                conn.close()
        
        if st.button("Don't have an account? Sign Up"):
            st.session_state.signup_mode = True
            st.rerun()
    else:
        st.subheader("Create a New Account")
        new_user = st.text_input("Choose Username", key="reg_user")
        new_pass = st.text_input("Choose Password", type="password", key="reg_pass")
        
        if st.button("Register", use_container_width=True):
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                try:
                    cursor.execute("SELECT COUNT(*) FROM users")
                    role = "admin" if cursor.fetchone()[0] == 0 else "user"
                    cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)", (new_user, new_pass, role))
                    conn.commit()
                    st.success(f"Account created as {role.upper()}!")
                    st.session_state.signup_mode = False
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
                finally:
                    conn.close()
        
        if st.button("Back to Login"):
            st.session_state.signup_mode = False
            st.rerun()

# --- 4. MAIN LIBRARY SYSTEM ---
def library_system():
    user_role = st.session_state.get("user_role", "user")
    username = st.session_state.get("username", "User")

    # --- Sidebar Navigation ---
    st.sidebar.title(f"🚀 {username}'s Portal")
    if st.sidebar.button("Logout", key="sidebar_logout_btn"):
        st.session_state.logged_in = False
        st.rerun()

    st.sidebar.divider()
    
    if user_role == "admin":
        menu = ["Home", "Dashboard", "Add Book", "Borrow Book", "Return Book", "View All Books", "Review Suggestions"]
    else:
        menu = ["Home", "View All Books", "Borrow Book", "Return Book", "Recommendation"]

    if "menu_choice" not in st.session_state:
        st.session_state.menu_choice = "Home"

    # Selectbox driven by session state
    choice = st.sidebar.selectbox("Menu", menu, index=menu.index(st.session_state.menu_choice))
    st.session_state.menu_choice = choice

    # --- 5. PAGE ROUTING ---
    
    # HOME PAGE (Quick Actions)
    if choice == "Home":
        st.title(f"👋 Welcome back, {username}!")
        st.markdown(f"### 🏛️ The Reading Nook | **{user_role.upper()} PORTAL**")
        
        st.subheader("Quick Actions")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### 📖 Catalog")
            st.write("Browse and search books.")
            if st.button("Open Catalog", use_container_width=True):
                st.session_state.menu_choice = "View All Books"
                st.rerun()
        
        with col2:
            st.markdown("### 📤 Issue")
            st.write("Process a book loan.")
            if st.button("Borrow Now", use_container_width=True):
                st.session_state.menu_choice = "Borrow Book"
                st.rerun()
                
        with col3:
            st.markdown("### 📥 Return")
            st.write("Return books and check fines.")
            if st.button("Process Return", use_container_width=True):
                st.session_state.menu_choice = "Return Book"
                st.rerun()

        if user_role == "admin":
            st.divider()
            st.markdown("#### 🛡️ Administrative Controls")
            a1, a2 = st.columns(2)
            with a1:
                if st.button("📊 View Stats Dashboard", use_container_width=True):
                    st.session_state.menu_choice = "Dashboard"
                    st.rerun()
            with a2:
                if st.button("➕ Add New Inventory", use_container_width=True):
                    st.session_state.menu_choice = "Add Book"
                    st.rerun()

    # ADD BOOK (Admin)
    elif choice == "Add Book":
        st.subheader("📖 Add a New Book")
        with st.form("add_form"):
            title = st.text_input("Title")
            author = st.text_input("Author")
            isbn = st.text_input("ISBN")
            genre = st.selectbox("Genre", ["Fiction", "Non-Fiction", "Sci-Fi", "Tech", "History"])
            copies = st.number_input("Copies", min_value=1)
            submitted = st.form_submit_button("Add Book to Database")
            
            if submitted:
                conn = get_db_connection()
                if conn:
                    cursor = conn.cursor()
                    try:
                        cursor.execute("INSERT INTO books (title, author, isbn, genre, copies, status) VALUES (%s, %s, %s, %s, %s, 'available')", 
                                       (title, author, isbn, genre, copies))
                        conn.commit()
                        st.success(f"Success! {title} added.")
                    except Exception as e:
                        st.error(f"Error: {e}")
                    finally:
                        conn.close()

    # BORROW BOOK
    elif choice == "Borrow Book":
        st.subheader("📖 Borrow a Book")
        book_title = st.text_input("Search Title to Borrow")
        student_name = st.text_input("Borrower Name", value=username)
        
        if st.button("Confirm Borrow"):
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE books SET status='borrowed' WHERE title=%s AND status='available'", (book_title,))
                if cursor.rowcount > 0:
                    conn.commit()
                    st.success(f"Confirmed: {book_title} issued to {student_name}.")
                else:
                    st.error("Book not available or title mismatch.")
                conn.close()

    # RETURN BOOK
    elif choice == "Return Book":
        st.subheader("🔄 Return & Fine Calculation")
        book_to_return = st.text_input("Title to Return")
        due_date = st.date_input("Due Date")
        return_date = st.date_input("Return Date", value=date.today())

        if st.button("Complete Return"):
            fine = 0
            if return_date > due_date:
                days_late = (return_date - due_date).days
                fine = days_late * 20
                st.warning(f"Late Return detected. Fine: ₹{fine}")

            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE books SET status='available', fine=%s WHERE title=%s", (fine, book_to_return))
                conn.commit()
                st.success(f"'{book_to_return}' returned successfully!")
                conn.close()

    # VIEW ALL BOOKS
    elif choice == "View All Books":
        st.subheader("📚 Library Catalog")
        search = st.text_input("🔍 Search books...")
        
        conn = get_db_connection()
        if conn:
            query = "SELECT * FROM books"
            if search:
                query += f" WHERE title LIKE '%{search}%' OR author LIKE '%{search}%'"
            
            df = pd.read_sql(query, conn)
            for index, row in df.iterrows():
                book_id = row.get('id') or row.get('ID') or row.get('book_id')
    
                with st.container():
                    c1, c2 = st.columns([5, 1])
                    c1.write(f"**{row['title']}** | {row['author']} ({row['genre']})")
                    c1.caption(f"Status: {row['status']} | ISBN: {row['isbn']}")
        
                    if row['status'] == 'available':
                        if c2.button("Select", key=f"sel_{book_id}"):
                            st.session_state.menu_choice = "Borrow Book"
                            st.rerun()
            st.divider()
            conn.close()

    # RECOMMENDATION
    elif choice == "Recommendation":
        st.subheader("⭐ Suggest a Purchase")
        rec = st.text_input("Which book should we add next?")
        if st.button("Submit Suggestion"):
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO recommendations (student_name, book_title) VALUES (%s, %s)", (username, rec))
                conn.commit()
                st.toast("Suggestion sent to admin!", icon="📩")
                conn.close()

    # DASHBOARD (Admin Only)
    # DASHBOARD (Admin Only)
    elif choice == "Dashboard":
        st.subheader("📊 Analytics Overview")
        conn = get_db_connection()
        if conn:
            # We fetch all books to calculate stats
            df = pd.read_sql("SELECT * FROM books", conn)
            
            if not df.empty:
                # Calculate metrics
                total_titles = len(df)
                on_loan = len(df[df['status'] == 'borrowed'])
                
                # IMPORTANT: Ensure 'fine' column is treated as a number
                # We use .sum() to get the total collected/pending fines
                total_fines = df['fine'].sum() if 'fine' in df.columns else 0
                
                m1, m2, m3 = st.columns(3)
                m1.metric("Total Titles", total_titles)
                m2.metric("On Loan", on_loan)
                m3.metric("Total Fines (₹)", f"₹{total_fines}")
                
                # Visualizing the data
                st.divider()
                fig = px.bar(df, x='genre', color='status', 
                             title="Inventory by Category",
                             labels={'genre': 'Book Genre', 'status': 'Availability'})
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No data available to display yet. Add some books first!")
            conn.close()

    # REVIEW SUGGESTIONS (Admin Only)
    elif choice == "Review Suggestions":
        st.subheader("📩 Student Requests")
        conn = get_db_connection()
        if conn:
            df = pd.read_sql("SELECT * FROM recommendations", conn)
            st.table(df)
            conn.close()

# --- 6. EXECUTION ---
if __name__ == "__main__":
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    if not st.session_state.logged_in:
        login_page()
    else:
        library_system()