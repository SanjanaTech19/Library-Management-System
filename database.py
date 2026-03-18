import mysql.connector
import os
import streamlit as st
from dotenv import load_dotenv

# Load variables from your .env file
load_dotenv()

def get_db_connection():
    
    try:
        # If connection exists, check if it's still alive
        if 'conn' in st.session_state and st.session_state.conn.is_connected():
            st.session_state.conn.ping(reconnect=True, attempts=3, delay=5)
            return st.session_state.conn
        
        # Otherwise, create a new one
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            port=int(os.getenv("DB_PORT", 18525))
        )
        st.session_state.conn = conn
        return conn
    except mysql.connector.Error as err:
        st.error(f"Error: {err}")
        return None