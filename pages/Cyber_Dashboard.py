# pages/Cyber_Dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px

from ai_helper import ask_cyber_assistant
from services.incidents_service import IncidentService

incident_service = IncidentService()


def require_login():
    if "user" not in st.session_state:
        st.error("You must be logged in to view this dashboard. Go to the **Login** page first.")
        st.stop()
    return st.session_state["user"]


def incidents_to_df(rows):
    if not rows:
        return pd.DataFrame(
            columns=[
                "id",
                "incident_id",
                "incident_type",
                "severity",
                "status",
                "reported_at",
                "resolved_at",
                "assigned_to",
                "description",
            ]
        )

    first = rows[0]
    if hasattr(first, "keys"):
        cols = list(first.keys())
        data = [tuple(r[c] for c in cols) for r in rows]
        return pd.DataFrame(data, columns=cols)

    # fallback if no row_factory
    return pd.DataFrame(
        rows,
        columns=[
            "id",
            "incident_id",
            "incident_type",
            "severity",
            "status",
            "reported_at",
            "resolved_at",
            "assigned_to",
            "description",
        ],
    )


def load_incidents_df():
    rows = incident_service.list_incidents()
    return incidents_to_df(rows)


def apply_filters(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    st.subheader("Filters")

    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        severities = sorted(df["severity"].dropna().unique())
        selected_sev = st.multiselect(
            "Severity",
            severities,
            default=severities,
        )

    with col2:
        statuses = sorted(df["status"].dropna().unique())
        selected_status = st.multiselect(
            "Status",
            statuses,
            default=statuses,
        )

    with col3:
        search_text = st.text_input("Search ID / description")

    mask = pd.Series(True, index=df.index)
    if selected_sev:
        mask &= df["severity"].isin(selected_sev)
    if selected_status:
        mask &= df["status"].isin(selected_status)
    if search_text:
        s = search_text.lower()
        mask &= (
            df["incident_id"].str.lower().str.contains(s)
            | df["description"].fillna("").str.lower().str.contains(s)
        )

    return df[mask]


def create_incident_form():
    st.markdown("### Create new incident")

    with st.form("create_incident_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            incident_id = st.text_input("Incident ID")
            incident_type = st.text_input("Incident type")
        with col2:
            severity = st.selectbox("Severity", ["Low", "Medium", "High", "Critical"])
            status = st.selectbox("Status", ["Open", "In Progress", "Resolved", "Closed"])
        with col3:
            reported_at = st.date_input("Reported at")
            assigned_to = st.text_input("Assigned to")

        description = st.text_area("Description")

        submitted = st.form_submit_button("Create")
        if submitted:
            if not incident_id:
                st.error("Incident ID is required.")
            else:
                incident_service.create_incident(
                    incident_id=incident_id,
                    incident_type=incident_type,
                    severity=severity,
                    status=status,
                    reported_at=str(reported_at),
                    resolved_at=None,
                    assigned_to=assigned_to,
                    description=description,
                )
                st.success(f"Incident {incident_id} created.")
                st.rerun()


def update_delete_section(df: pd.DataFrame):
    st.markdown("### Update or delete incident")

    if df.empty:
        st.info("No incidents available yet.")
        return

    ids = df["incident_id"].tolist()

    with st.expander("Update incident status", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            target_id = st.selectbox("Incident ID", ids, key="update_id")
        with col2:
            new_status = st.selectbox(
                "New status",
                ["Open", "In Progress", "Resolved", "Closed"],
                key="new_status",
            )

        if st.button("Apply status update"):
            incident_service.change_status(target_id, new_status)
            st.success(f"Status for {target_id} updated to {new_status}.")
            st.rerun()

    with st.expander("Delete incident"):
        delete_id = st.selectbox("Incident ID to delete", ids, key="delete_id")
        if st.button("Delete selected incident"):
            incident_service.remove_incident(delete_id)
            st.warning(f"Incident {delete_id} deleted.")
            st.rerun()


def visualisations(df: pd.DataFrame):
    st.markdown("### Incident analytics")

    if df.empty:
        st.info("No data available for charts.")
        return

    col1, col2 = st.columns(2)

    with col1:
        by_sev = df["severity"].value_counts().reset_index()
        by_sev.columns = ["severity", "count"]
        fig = px.bar(by_sev, x="severity", y="count", title="Incidents by severity")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        by_status = df["status"].value_counts().reset_index()
        by_status.columns = ["status", "count"]
        fig2 = px.bar(by_status, x="status", y="count", title="Incidents by status")
        st.plotly_chart(fig2, use_container_width=True)

    if "reported_at" in df.columns:
        df_ts = df.copy()
        df_ts["reported_at"] = pd.to_datetime(df_ts["reported_at"], errors="coerce")
        df_ts = df_ts.dropna(subset=["reported_at"])
        if not df_ts.empty:
            ts = df_ts.groupby("reported_at")["id"].count().reset_index()
            ts.columns = ["reported_at", "incident_count"]
            fig3 = px.line(ts, x="reported_at", y="incident_count", title="Incidents over time")
            st.plotly_chart(fig3, use_container_width=True)


def build_incident_context(df: pd.DataFrame) -> str:
    if df.empty:
        return "There are currently no incidents."

    total = len(df)
    by_sev = df["severity"].value_counts().to_dict()
    by_status = df["status"].value_counts().to_dict()

    lines = f"Total incidents: {total}."
    if by_sev:
        sev_parts = ", ".join(f"{k}: {v}" for k, v in by_sev.items())
        lines += f" By severity: {sev_parts}."
    if by_status:
        st_parts = ", ".join(f"{k}: {v}" for k, v in by_status.items())
        lines += f" By status: {st_parts}."

    return lines


def dashboard():
    user = require_login()

    st.title("🛡️ Cybersecurity Dashboard")
    st.caption(f"Welcome, {user['username']}.")

    df = load_incidents_df()
    df_filtered = apply_filters(df)

    # Summary metrics
    st.markdown("### Summary")
    total = len(df_filtered)
    open_count = int((df_filtered["status"] == "Open").sum()) if not df_filtered.empty else 0
    high_count = int((df_filtered["severity"] == "High").sum()) if not df_filtered.empty else 0
    critical_count = int((df_filtered["severity"] == "Critical").sum()) if not df_filtered.empty else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total incidents (filtered)", total)
    c2.metric("Open incidents", open_count)
    c3.metric("High severity incidents", high_count)
    c4.metric("Critical incidents", critical_count)

    # Layout: table + create form side by side
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.markdown("### Incident table")
        st.dataframe(df_filtered, use_container_width=True, height=380)
        st.caption(f"Showing {len(df_filtered)} of {len(df)} incidents (after filters).")

    with col_right:
        create_incident_form()

    update_delete_section(df_filtered)
    visualisations(df_filtered)

    # --- AI Assistant section ---
    st.markdown("### 🔎 AI Security Assistant")

    with st.expander("Ask questions about the incidents (ChatGPT-powered)", expanded=False):
        st.caption(
            "Example questions: "
            "`Why might my High incidents be increasing?`, "
            "`Which severity should we prioritise first?`"
        )
        user_q = st.text_area("Your question", key="ai_question", height=100)

        if st.button("Ask AI", key="ai_button"):
            if not user_q.strip():
                st.warning("Please enter a question first.")
            else:
                context = build_incident_context(df_filtered)
                with st.spinner("Contacting AI assistant..."):
                    answer = ask_cyber_assistant(user_q, context)
                st.markdown("**Assistant response:**")
                st.write(answer)


if __name__ == "__main__":
    dashboard()
