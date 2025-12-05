# pages/Data_Dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px

from ai_helper import ask_cyber_assistant
from services.datasets_service import DatasetService

dataset_service = DatasetService()


def require_login():
    if "user" not in st.session_state:
        st.error("You must be logged in to view this dashboard. Go to the **Login** page first.")
        st.stop()
    return st.session_state["user"]


def datasets_to_df(rows):
    if not rows:
        return pd.DataFrame(
            columns=["id", "dataset_name", "owner", "source_system", "size_mb", "row_count", "created_at"]
        )

    first = rows[0]
    if hasattr(first, "keys"):
        cols = list(first.keys())
        data = [tuple(r[c] for c in cols) for r in rows]
        return pd.DataFrame(data, columns=cols)

    return pd.DataFrame(
        rows,
        columns=["id", "dataset_name", "owner", "source_system", "size_mb", "row_count", "created_at"],
    )


def load_datasets_df():
    rows = dataset_service.list_datasets()
    return datasets_to_df(rows)


def apply_filters(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    st.subheader("Filters")
    c1, c2, c3 = st.columns([1, 1, 2])

    with c1:
        owners = sorted(df["owner"].dropna().unique())
        owner_sel = st.multiselect("Owner", owners, default=owners)

    with c2:
        sources = sorted(df["source_system"].dropna().unique())
        src_sel = st.multiselect("Source system", sources, default=sources)

    with c3:
        search = st.text_input("Search dataset name")

    mask = pd.Series(True, index=df.index)
    if owner_sel:
        mask &= df["owner"].isin(owner_sel)
    if src_sel:
        mask &= df["source_system"].isin(src_sel)
    if search:
        s = search.lower()
        mask &= df["dataset_name"].str.lower().str.contains(s)

    return df[mask]


def create_dataset_form():
    st.markdown("### Register new dataset")

    with st.form("create_dataset_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            name = st.text_input("Dataset name")
            owner = st.text_input("Owner")
        with col2:
            source = st.text_input("Source system")
            size_mb = st.number_input("Size (MB)", min_value=0.0, step=1.0)
        with col3:
            rows = st.number_input("Row count", min_value=0, step=1000)
            created_at = st.date_input("Created at")

        submitted = st.form_submit_button("Create")
        if submitted:
            if not name:
                st.error("Dataset name is required.")
            else:
                dataset_service.register_dataset(
                    dataset_name=name,
                    owner=owner,
                    source_system=source,
                    size_mb=float(size_mb),
                    row_count=int(rows),
                    created_at=str(created_at),
                )
                st.success(f"Dataset {name} created.")
                st.rerun()


def update_delete_section(df: pd.DataFrame):
    st.markdown("### Update or delete dataset")

    if df.empty:
        st.info("No datasets available yet.")
        return

    names = df["dataset_name"].tolist()

    with st.expander("Change dataset owner", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            ds_name = st.selectbox("Dataset", names, key="ds_update_name")
        with col2:
            new_owner = st.text_input("New owner", key="ds_new_owner")

        if st.button("Update owner"):
            if not new_owner:
                st.error("Please enter a new owner.")
            else:
                dataset_service.change_owner(ds_name, new_owner)
                st.success(f"Owner for {ds_name} updated.")
                st.rerun()

    with st.expander("Delete dataset"):
        del_name = st.selectbox("Dataset to delete", names, key="ds_delete_name")
        if st.button("Delete dataset"):
            dataset_service.remove_dataset(del_name)
            st.warning(f"Dataset {del_name} deleted.")
            st.rerun()


def visualisations(df: pd.DataFrame):
    st.markdown("### Dataset analytics")

    if df.empty:
        st.info("No data available for charts.")
        return

    df_num = df.copy()
    df_num["size_mb"] = pd.to_numeric(df_num["size_mb"], errors="coerce")
    df_num["row_count"] = pd.to_numeric(df_num["row_count"], errors="coerce")

    c1, c2 = st.columns(2)

    with c1:
        by_owner = df_num.groupby("owner")["size_mb"].sum().reset_index()
        fig = px.bar(by_owner, x="owner", y="size_mb", title="Total size by owner (MB)")
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        by_source = df_num.groupby("source_system")["row_count"].sum().reset_index()
        fig2 = px.bar(by_source, x="source_system", y="row_count", title="Total rows by source system")
        st.plotly_chart(fig2, use_container_width=True)

    df_num["created_at"] = pd.to_datetime(df_num["created_at"], errors="coerce")
    df_num = df_num.dropna(subset=["created_at"])
    if not df_num.empty:
        ts = df_num.groupby("created_at")["size_mb"].sum().reset_index()
        ts.columns = ["created_at", "total_size_mb"]
        fig3 = px.line(ts, x="created_at", y="total_size_mb", title="Storage growth over time (MB)")
        st.plotly_chart(fig3, use_container_width=True)

def build_data_context(df: pd.DataFrame) -> str:
    """
    Build a natural-language summary for the Data Dashboard
    from the datasets table.
    """
    if df.empty:
        return "There are currently no datasets in the catalog."

    total = len(df)

    # Ensure numeric columns
    df_num = df.copy()
    df_num["size_mb"] = pd.to_numeric(df_num["size_mb"], errors="coerce")
    df_num["row_count"] = pd.to_numeric(df_num["row_count"], errors="coerce")

    total_rows = int(df_num["row_count"].sum(skipna=True)) if "row_count" in df_num.columns else None
    total_size = float(df_num["size_mb"].sum(skipna=True)) if "size_mb" in df_num.columns else None

    by_owner = df["owner"].value_counts().to_dict() if "owner" in df.columns else {}
    by_source = df["source_system"].value_counts().to_dict() if "source_system" in df.columns else {}

    lines = f"Total datasets: {total}."
    if total_rows is not None:
        lines += f" Total rows across all datasets: {total_rows:,}."
    if total_size is not None:
        lines += f" Total size: {total_size:,.2f} MB."

    if by_owner:
        owner_parts = ", ".join(f"{k}: {v}" for k, v in by_owner.items())
        lines += f" By owner: {owner_parts}."
    if by_source:
        src_parts = ", ".join(f"{k}: {v}" for k, v in by_source.items())
        lines += f" By source system: {src_parts}."

    return lines



def dashboard():
    user = require_login()

    st.title("📚 Data Assets Dashboard")
    st.caption(f"Welcome, {user['username']}.")

    df = load_datasets_df()
    df_f = apply_filters(df)

    st.markdown("### Summary")
    total_ds = len(df_f)
    total_size = float(pd.to_numeric(df_f["size_mb"], errors="coerce").sum()) if not df_f.empty else 0.0
    avg_rows = float(pd.to_numeric(df_f["row_count"], errors="coerce").mean()) if not df_f.empty else 0.0

    c1, c2, c3 = st.columns(3)
    c1.metric("Datasets (filtered)", total_ds)
    c2.metric("Total size (MB)", f"{total_size:,.1f}")
    c3.metric("Average row count", f"{avg_rows:,.0f}")

    col_left, col_right = st.columns([2, 1])
    with col_left:
        st.markdown("### Dataset table")
        st.dataframe(df_f, use_container_width=True, height=380)
        st.caption(f"Showing {len(df_f)} of {len(df)} datasets (after filters).")
    with col_right:
        create_dataset_form()

    update_delete_section(df_f)
    visualisations(df_f)

   # --- AI Assistant section ---
    st.markdown("### 🔎 AI Data Assistant")

    with st.expander("Ask questions about the datasets (ChatGPT-powered)", expanded=False):
        st.caption(
            "Example questions: "
            "`Which dataset is most important?`, "
            "`What categories dominate our catalog?`, "
            "`Are we storing too much large-sized data?`"
        )
        user_q = st.text_area("Your question", key="ai_data_question", height=100)

        if st.button("Ask AI (Data)", key="ai_data_button"):
            if not user_q.strip():
                st.warning("Please enter a question first.")
            else:
                # Use the filtered dataframe from this page
                context = build_data_context(df_f)
                with st.spinner("Contacting AI assistant..."):
                    answer = ask_cyber_assistant(user_q, context)
                st.markdown("**Assistant response:**")
                st.write(answer)

if __name__ == "__main__":
    dashboard()
