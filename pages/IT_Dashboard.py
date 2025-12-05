# pages/IT_Dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px

from ai_helper import ask_cyber_assistant
from services.tickets_service import TicketService

ticket_service = TicketService()


def require_login():
    if "user" not in st.session_state:
        st.error("You must be logged in to view this dashboard. Go to the **Login** page first.")
        st.stop()
    return st.session_state["user"]


def tickets_to_df(rows):
    if not rows:
        return pd.DataFrame(
            columns=[
                "id",
                "ticket_id",
                "category",
                "priority",
                "status",
                "opened_at",
                "closed_at",
                "assigned_to",
            ]
        )

    first = rows[0]
    if hasattr(first, "keys"):
        cols = list(first.keys())
        data = [tuple(r[c] for c in cols) for r in rows]
        return pd.DataFrame(data, columns=cols)

    return pd.DataFrame(
        rows,
        columns=[
            "id",
            "ticket_id",
            "category",
            "priority",
            "status",
            "opened_at",
            "closed_at",
            "assigned_to",
        ],
    )


def load_tickets_df():
    rows = ticket_service.list_tickets()
    return tickets_to_df(rows)


def add_resolution_days(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["opened_at"] = pd.to_datetime(df["opened_at"], errors="coerce")
    df["closed_at"] = pd.to_datetime(df["closed_at"], errors="coerce")
    df["resolution_days"] = (df["closed_at"] - df["opened_at"]).dt.days
    return df


def apply_filters(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    st.subheader("Filters")
    c1, c2, c3 = st.columns([1, 1, 2])

    with c1:
        prios = sorted(df["priority"].dropna().unique())
        p_sel = st.multiselect("Priority", prios, default=prios)

    with c2:
        statuses = sorted(df["status"].dropna().unique())
        s_sel = st.multiselect("Status", statuses, default=statuses)

    with c3:
        assignees = sorted(df["assigned_to"].dropna().unique())
        a_sel = st.multiselect("Assigned to", assignees, default=assignees)

    mask = pd.Series(True, index=df.index)
    if p_sel:
        mask &= df["priority"].isin(p_sel)
    if s_sel:
        mask &= df["status"].isin(s_sel)
    if a_sel:
        mask &= df["assigned_to"].isin(a_sel)

    return df[mask]


def create_ticket_form():
    st.markdown("### Create new ticket")

    with st.form("create_ticket_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            ticket_id = st.text_input("Ticket ID")
            category = st.text_input("Category")
        with col2:
            priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"])
            status = st.selectbox("Status", ["Open", "In Progress", "Resolved", "Closed"])
        with col3:
            opened_at = st.date_input("Opened at")
            closed_at = st.date_input("Closed at (optional)")
            assigned_to = st.text_input("Assigned to")

        submitted = st.form_submit_button("Create")
        if submitted:
            if not ticket_id:
                st.error("Ticket ID is required.")
            else:
                # If user leaves closed_at equal to opened_at and wants it "empty",
                # they can later edit via status updates; we still store a date or None.
                closed_val = str(closed_at) if closed_at else None
                ticket_service.create_ticket(
                    ticket_id=ticket_id,
                    category=category,
                    priority=priority,
                    status=status,
                    opened_at=str(opened_at),
                    closed_at=closed_val,
                    assigned_to=assigned_to,
                )
                st.success(f"Ticket {ticket_id} created.")
                st.rerun()


def update_delete_section(df: pd.DataFrame):
    st.markdown("### Update or delete ticket")

    if df.empty:
        st.info("No tickets available yet.")
        return

    ids = df["ticket_id"].tolist()

    with st.expander("Update ticket status", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            t_id = st.selectbox("Ticket ID", ids, key="tt_update_id")
        with col2:
            new_status = st.selectbox(
                "New status",
                ["Open", "In Progress", "Resolved", "Closed"],
                key="tt_new_status",
            )

        if st.button("Apply status update"):
            ticket_service.change_status(t_id, new_status)
            st.success(f"Status for {t_id} updated to {new_status}.")
            st.rerun()

    with st.expander("Delete ticket"):
        del_id = st.selectbox("Ticket ID to delete", ids, key="tt_delete_id")
        if st.button("Delete ticket"):
            ticket_service.remove_ticket(del_id)
            st.warning(f"Ticket {del_id} deleted.")
            st.rerun()


def visualisations(df: pd.DataFrame):
    st.markdown("### Ticket analytics")

    if df.empty:
        st.info("No data available for charts.")
        return

    df = add_resolution_days(df)

    c1, c2 = st.columns(2)

    with c1:
        by_prio = df["priority"].value_counts().reset_index()
        by_prio.columns = ["priority", "count"]
        fig = px.bar(by_prio, x="priority", y="count", title="Tickets by priority")
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        by_status = df["status"].value_counts().reset_index()
        by_status.columns = ["status", "count"]
        fig2 = px.bar(by_status, x="status", y="count", title="Tickets by status")
        st.plotly_chart(fig2, use_container_width=True)

    by_assignee = df.groupby("assigned_to")["resolution_days"].mean().reset_index()
    by_assignee["resolution_days"] = by_assignee["resolution_days"].round(1)
    fig3 = px.bar(
        by_assignee,
        x="assigned_to",
        y="resolution_days",
        title="Average resolution time by assignee (days)",
    )
    st.plotly_chart(fig3, use_container_width=True)

def build_it_context(df: pd.DataFrame) -> str:
    """
    Build a natural-language summary for the IT Dashboard
    from it_tickets.
    """
    if df.empty:
        return "There are currently no IT tickets."

    total = len(df)

    by_priority = (
        df["priority"].value_counts().to_dict()
        if "priority" in df.columns
        else {}
    )
    by_status = (
        df["status"].value_counts().to_dict()
        if "status" in df.columns
        else {}
    )
    by_category = (
        df["category"].value_counts().to_dict()
        if "category" in df.columns
        else {}
    )

    lines = f"Total IT tickets: {total}."
    if by_priority:
        pr_parts = ", ".join(f"{k}: {v}" for k, v in by_priority.items())
        lines += f" By priority: {pr_parts}."
    if by_status:
        st_parts = ", ".join(f"{k}: {v}" for k, v in by_status.items())
        lines += f" By status: {st_parts}."
    if by_category:
        cat_parts = ", ".join(f"{k}: {v}" for k, v in by_category.items())
        lines += f" By category: {cat_parts}."

    return lines


def dashboard():
    user = require_login()

    st.title("🛠️ IT Service Desk Dashboard")
    st.caption(f"Welcome, {user['username']}.")

    df = load_tickets_df()
    df_f = apply_filters(df)
    df_f = add_resolution_days(df_f)

    st.markdown("### Summary")
    total = len(df_f)
    open_count = int((df_f["status"] == "Open").sum()) if not df_f.empty else 0
    avg_res = float(df_f["resolution_days"].mean()) if not df_f.empty else 0.0

    c1, c2, c3 = st.columns(3)
    c1.metric("Tickets (filtered)", total)
    c2.metric("Open tickets", open_count)
    c3.metric("Avg resolution time (days)", f"{avg_res:,.1f}")

    col_left, col_right = st.columns([2, 1])
    with col_left:
        st.markdown("### Ticket table")
        st.dataframe(df_f, use_container_width=True, height=380)
        st.caption(f"Showing {len(df_f)} of {len(df)} tickets (after filters).")
    with col_right:
        create_ticket_form()

    update_delete_section(df_f)
    visualisations(df_f)

    # --- AI Assistant section ---
    st.markdown("### 🔎 AI IT Support Assistant")

    with st.expander("Ask questions about the IT tickets (ChatGPT-powered)", expanded=False):
        st.caption(
            "Example questions: "
            "`Which priority level should be resolved first?`, "
            "`Why are Open tickets increasing?`, "
            "`How are issues distributed by category?`"
        )
        user_q = st.text_area("Your question", key="ai_it_question", height=100)

        if st.button("Ask AI (IT)", key="ai_it_button"):
            if not user_q.strip():
                st.warning("Please enter a question first.")
            else:
                context = build_it_context(df_f)
                with st.spinner("Contacting AI assistant..."):
                    answer = ask_cyber_assistant(user_q, context)
                st.markdown("**Assistant response:**")
                st.write(answer)


if __name__ == "__main__":
    dashboard()
