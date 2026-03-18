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
    /* 1. GLOBAL APP & TEXT COLORS */
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    h1, h2, h3, h4, h5, h6 { color: #FFFFFF !important; }
    
    /* 2. FIX INVISIBLE LABELS (Add Book Form etc.) */
    label, .stWidgetLabel, [data-testid="stWidgetLabel"] p {
        color: #FFFFFF !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
    }

    /* 3. GLASSMORPHISM CARDS */
    div[data-testid="column"], [data-testid="stVerticalBlock"] > div[style*="border"] {
        background: rgba(255, 255, 255, 0.05); 
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 20px;
    }

    /* 4. EMERALD BUTTONS WITH BLACK TEXT */
    .stButton>button { 
        background-color: #50C878 !important; 
        color: #000000 !important; /* FORCED BLACK TEXT */
        font-weight: 800 !important; /* EXTRA BOLD FOR READABILITY */
        border: none; 
        border-radius: 10px;
        transition: 0.3s; 
        width: 100%;
        text-transform: uppercase; /* OPTIONAL: Makes it look like a pro UI */
        letter-spacing: 1px;
    }

    /* Button Hover Effect */
    .stButton>button:hover {
        background-color: #FFFFFF !important; /* TURNS WHITE ON HOVER */
        color: #000000 !important; /* TEXT STAYS BLACK */
        box-shadow: 0px 0px 20px rgba(80, 200, 120, 0.6);
        transform: scale(1.02); /* SUBTLE POP EFFECT */
    }

    /* 5. SIDEBAR & NAVIGATION FIX (Kills the white box) */
    [data-testid="stSidebar"] {
        background-color: #050505 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* This targets the dropdown list itself */
    div[data-baseweb="popover"], div[data-baseweb="menu"] {
        background-color: #1A1C23 !important;
    }

    /* This targets the items inside the dropdown */
    div[data-baseweb="popover"] li {
        background-color: #1A1C23 !important;
        color: white !important;
    }

    /* Hover effect for dropdown items */
    div[data-baseweb="popover"] li:hover {
        background-color: #50C878 !important;
        color: #0E1117 !important;
    }

    /* Fix sidebar selectbox background */
    div[data-testid="stSidebar"] .stSelectbox > div > div {
        background-color: #1A1C23 !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
    }

    /* 6. INPUT FIELDS */
    .stTextInput>div>div>input, .stSelectbox>div>div>div, .stNumberInput>div>div>input {
        background-color: #1A1C23 !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
    }

    /* FIX: Navigation Dropdown (The white box) Text */
    div[data-baseweb="popover"] ul, 
    div[data-baseweb="menu"] {
        background-color: #FFFFFF !important; /* Keeps the box white */
    }

    /* Target the actual text inside the list items */
    div[data-baseweb="popover"] li, 
    div[data-baseweb="popover"] span,
    div[role="listbox"] div {
        color: #000000 !important; /* FORCES TEXT TO BLACK */
        font-weight: 500 !important;
    }

    /* Add a nice hover effect so you know which one you are picking */
    div[data-baseweb="popover"] li:hover {
        background-color: #50C878 !important; /* Emerald green highlight */
        color: #000000 !important;
    }
            
    /* 7. CAPTIONS & METRICS */
    .stCaption, p { color: #E0E0E0 !important; }
    [data-testid="stMetricValue"] { color: #50C878 !important; }
    
            
     /* FINAL NAVIGATION FIX: Black text on white/light dropdown items */
    div[data-baseweb="popover"] li, 
    div[data-baseweb="popover"] span,
    div[role="listbox"] div,
    [data-testid="stVirtualDropdown"] div {
        color: #000000 !important; /* Forces black text */
        background-color: transparent !important;
        font-weight: 600 !important;
    }

    /* Keep the dropdown container white or very light for contrast */
    div[data-baseweb="popover"] ul, 
    div[data-baseweb="menu"] {
        background-color: #FFFFFF !important; 
        border: 1px solid #50C878 !important; /* Emerald border for style */
    }

    /* Hover state for dropdown items */
    div[data-baseweb="popover"] li:hover {
        background-color: #50C878 !important; /* Emerald highlight */
        color: #000000 !important;
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
        menu = ["Home", "Dashboard", "Add Book", "View All Books", "Review Suggestions"]
    else:
        menu = ["Home", "View All Books", "Borrow Book", "Return Book", "Recommendation"]

    # --- 4.5 SAFE MENU SELECTION ---
    if "menu_choice" not in st.session_state:
        st.session_state.menu_choice = "Home"

    # CRITICAL: Check if the saved choice exists in the current role's menu
    # This prevents the ValueError when switching roles
    if st.session_state.menu_choice not in menu:
        st.session_state.menu_choice = "Home"

    # Now we can safely find the index
    choice_index = menu.index(st.session_state.menu_choice)
    
    choice = st.sidebar.selectbox("Menu", menu, index=choice_index)
    
    # Update the session state for the next rerun
    st.session_state.menu_choice = choice
    # --- 5. PAGE ROUTING ---
    
    # HOME PAGE (Quick Actions)
    # HOME PAGE (Quick Actions)
    if choice == "Home":
        st.title(f"👋 Welcome back, {username}!")
        st.markdown(f"### 🏛️ The Reading Nook | **{user_role.upper()} PORTAL**")
        
        st.subheader("Quick Actions")
        
        # --- ADMIN HOME PAGE ---
        if user_role == "admin":
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("### 📊 Analytics")
                st.write("Check library stats and fines.")
                if st.button("Open Dashboard", use_container_width=True):
                    st.session_state.menu_choice = "Dashboard"
                    st.rerun()
            
            with col2:
                st.markdown("### ➕ Inventory")
                st.write("Add new books to the catalog.")
                if st.button("Add New Book", use_container_width=True):
                    st.session_state.menu_choice = "Add Book"
                    st.rerun()
                    
            with col3:
                st.markdown("### 📩 Requests")
                st.write("Review student book suggestions.")
                if st.button("View Suggestions", use_container_width=True):
                    st.session_state.menu_choice = "Review Suggestions"
                    st.rerun()

        # --- STUDENT/USER HOME PAGE ---
        else:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("### 📖 Catalog")
                st.write("Browse and search books.")
                if st.button("Open Catalog", use_container_width=True):
                    st.session_state.menu_choice = "View All Books"
                    st.rerun()
            
            with col2:
                st.markdown("### 📤 Borrow")
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
    # BORROW BOOK
    elif choice == "Borrow Book":
        st.subheader("📖 Issue a Book")
        
        # 1. Pull the selected book from Catalog if it exists
        selected_title = st.session_state.get('selected_book_title', "")
        
        with st.form("borrow_form"):
            book_title = st.text_input("Book Title", value=selected_title)
            student_name = st.text_input("Borrower Name", value=username)
            borrow_date = st.date_input("Borrow Date", value=date.today())
            submit_borrow = st.form_submit_button("Confirm Issue")
            
            if submit_borrow:
                if not book_title or not student_name:
                    st.error("Please fill in all details.")
                else:
                    conn = get_db_connection()
                    if conn:
                        cursor = conn.cursor()
                        # Check if book exists and has copies
                        cursor.execute("SELECT copies FROM books WHERE title=%s", (book_title,))
                        result = cursor.fetchone()
                        
                        if result and result[0] > 0:
                            # Update: Reduce copies and mark as borrowed if last copy
                            new_status = 'borrowed' if result[0] == 1 else 'available'
                            cursor.execute("""
                                UPDATE books 
                                SET copies = copies - 1, status = %s 
                                WHERE title = %s
                            """, (new_status, book_title))
                            
                            conn.commit()
                            st.success(f"✅ {book_title} has been issued to {student_name}!")
                            st.balloons()
                            # Clear the selection so it doesn't stay stuck
                            st.session_state.selected_book_title = ""
                        else:
                            st.error("Sorry, this book is currently Out of Stock.")
                        conn.close()

    
    
    
    elif choice == "Return Book":
        st.subheader("🔄 Return & Fine Management")
        
        selected_title = st.session_state.get('selected_book_title', "")
        book_to_return = st.text_input("Title to Return", value=selected_title)
        
        col1, col2 = st.columns(2)
        with col1:
            due_date = st.date_input("Due Date (See your slip)")
        with col2:
            return_date = st.date_input("Return Date", value=date.today())

        fine = 0
        if return_date > due_date:
            days_late = (return_date - due_date).days
            fine = days_late * 20
            st.warning(f"⚠️ Overdue: ₹{fine} fine.")

        if st.button("Complete Return Process"):
            conn = get_db_connection()
            if conn: # All DB logic MUST stay inside this block
                cursor = conn.cursor()
                try:
                    # Update status AND increment copies so the Borrow button enables
                    cursor.execute("""
                        UPDATE books 
                        SET status = 'available', 
                            copies = copies + 1, 
                            fine = fine + %s 
                        WHERE title = %s
                    """, (fine, book_to_return))
                    
                    conn.commit()
                    st.success(f"✅ {book_to_return} returned!")
                    st.session_state.selected_book_title = ""
                    st.rerun()
                except Exception as e:
                    st.error(f"DB Update Failed: {e}")
                finally:
                    conn.close()

    
    # VIEW ALL BOOKS
    elif choice == "View All Books":
        st.subheader("📚 Library Catalog")
        search = st.text_input("🔍 Search...")
        conn = get_db_connection()
        if conn:
            df = pd.read_sql("SELECT * FROM books", conn) # Add WHERE filters if needed
            for index, row in df.iterrows():
                book_id = row.get('id') or row.get('ID')
                with st.container():
                    col_info, col_btn1, col_btn2 = st.columns([4, 1, 1])
                    with col_info:
                        st.write(f"**{row['title']}** | {row['author']}")
                        st.caption(f"Copies: {row.get('copies', 0)} | Status: {row['status']}")

                    if user_role == "user":
                        # BORROW BUTTON
                        if col_btn1.button("Borrow", key=f"br_{book_id}", disabled=(row.get('copies', 0) <= 0)):
                            st.session_state.selected_book_title = row['title']
                            st.session_state.menu_choice = "Borrow Book"
                            st.rerun()
                        
                        # RETURN BUTTON
                        if col_btn2.button("Return", key=f"ret_{book_id}"):
                            st.session_state.selected_book_title = row['title']
                            st.session_state.menu_choice = "Return Book"
                            st.rerun()
                
                    elif user_role == "admin":
                        if col_btn2.button("🗑️ Delete", key=f"del_{book_id}"):
                            cursor = conn.cursor()
                            cursor.execute("DELETE FROM books WHERE id = %s", (book_id,))
                            conn.commit()
                            st.toast(f"Deleted {row['title']}")
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
    # DASHBOARD (Admin Only)
    elif choice == "Dashboard":
        st.subheader("📊 Analytics Overview")
        conn = get_db_connection()
        if conn:
            # Fetch all books to calculate stats
            df = pd.read_sql("SELECT * FROM books", conn)
            
            if not df.empty:
                # Calculate metrics
                total_titles = len(df)
                on_loan = len(df[df['status'] == 'borrowed'])
                
                # Ensure 'fine' column exists and treat it as a number
                # This sums up all values in the fine column
                total_fines = df['fine'].sum() if 'fine' in df.columns else 0
                
                m1, m2, m3 = st.columns(3)
                m1.metric("Total Titles", total_titles)
                m2.metric("On Loan", on_loan)
                m3.metric("Total Fines Collected (₹)", f"₹{total_fines}")
                
                st.divider()
                
                # Visualizing inventory by genre
                # Change this line in your Dashboard logic
                fig = px.bar(df, x='genre', color='status', 
                        template="plotly_dark", # <--- Add this!
                        title="Inventory by Category",
                        color_discrete_map={'available': '#50C878', 'borrowed': '#FF4B4B'})
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No data available yet. Add some books to see stats!")
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