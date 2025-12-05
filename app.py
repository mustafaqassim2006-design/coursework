# app.py
import streamlit as st

st.set_page_config(
    page_title="Multi-Domain Intelligence Platform",
    page_icon="📊",
    layout="wide",
)

def main():
    st.title("📊 Multi-Domain Intelligence Platform")

    st.markdown(
        """
        This prototype platform brings together three domains:

        - **Cybersecurity** – incident tracking and analytics  
        - **Data Assets** – dataset catalogue and ownership (Week 10)  
        - **IT Operations** – ticket overview and KPIs (Week 10)  

        Use the **left sidebar** to:
        - log in on the **Login** page  
        - explore the **Cyber Dashboard** once authenticated
        """
    )

    if "user" in st.session_state:
        user = st.session_state["user"]
        st.success(f"Logged in as `{user['username']}` · role: `{user['role']}`")
    else:
        st.info("You are not logged in yet. Open the **Login** page from the sidebar.")

if __name__ == "__main__":
    main()
