# pages/Login.py
import streamlit as st
import bcrypt

from services.users_service import UserService

user_service = UserService()


def login_page():
    st.title("🔐 Login")

    # Already logged in
    if "user" in st.session_state:
        user = st.session_state["user"]
        st.success(f"You are logged in as `{user['username']}` (`{user['role']}`).")

        cols = st.columns([1, 1, 2])
        with cols[0]:
            if st.button("Go to Cyber Dashboard"):
                st.rerun()
        with cols[1]:
            if st.button("Log out", type="secondary"):
                st.session_state.pop("user")
                st.success("Logged out successfully.")
                st.rerun()
        return

    # Centered login form
    left, center, right = st.columns([1, 2, 1])
    with center:
        st.markdown("### Welcome back")
        st.caption("Use the credentials from the Week 7 system.")

        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")

        if submitted:
            if not username or not password:
                st.error("Please enter both a username and a password.")
                return

            user_row = user_service.find_user(username)
            if user_row is None:
                st.error("Invalid username or password.")
                return

            stored_hash = user_row["password_hash"]
            if isinstance(stored_hash, bytes):
                stored_hash_bytes = stored_hash
            else:
                stored_hash_bytes = stored_hash.encode("utf-8")

            if bcrypt.checkpw(password.encode("utf-8"), stored_hash_bytes):
                st.session_state["user"] = {
                    "id": user_row["id"],
                    "username": user_row["username"],
                    "role": user_row["role"],
                }
                st.success("Login successful.")
                st.rerun()
            else:
                st.error("Invalid username or password.")


if __name__ == "__main__":
    login_page()
