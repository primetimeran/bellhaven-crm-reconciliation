from pathlib import Path

import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Bellhaven CRM Intelligence",
    page_icon="🏥",
    layout="wide"
)

st.title("Bellhaven CRM Intelligence")
st.caption("Facility Discovery | CRM Matching | Approval Workflow")

tab1, tab2, tab3 = st.tabs([
    "Facility Discovery",
    "CRM Matching",
    "Approval Queue"
])

with tab1:
    st.header("Bellhaven Facility Discovery")

    df = pd.read_csv("facilities.csv").fillna("")

    c1, c2, c3 = st.columns(3)
    c1.metric("Facilities Discovered", len(df))
    c2.metric("Missing Addresses", (df["address"] == "").sum())
    c3.metric("Missing Care Offerings", (df["care_offerings"] == "").sum())

    st.dataframe(df, use_container_width=True, hide_index=True)

    st.download_button(
        "Download Facility Data",
        data=df.to_csv(index=False),
        file_name="bellhaven_facilities.csv",
        mime="text/csv"
    )

with tab2:
    st.header("CRM Matching Results")
    matches = pd.read_csv("crm_matches.csv").fillna("")

    c1, c2, c3 = st.columns(3)
    c1.metric("Facilities Compared", len(matches))
    c2.metric("Manual Review", (matches["recommendation"] == "Manual review").sum())
    c3.metric("Potentially Missing", (matches["recommendation"] == "Potential missing account").sum())

    search = st.text_input("Search facilities or CRM accounts")

    if search:
        matches = matches[
            matches["facility"].str.contains(search, case=False, na=False)
            | matches["crm_account"].str.contains(search, case=False, na=False)
        ]

    st.dataframe(matches, width="stretch", hide_index=True)

    st.download_button(
        "Download CRM Matching Results",
        data=matches.to_csv(index=False),
        file_name="bellhaven_crm_matches.csv",
        mime="text/csv"
    )

with tab3:
    st.header("CRM Change Approval Queue")
    st.caption("Review proposed matches before any CRM changes.")

    queue = pd.read_csv("crm_matches.csv").fillna("")
    queue = queue[queue["recommendation"] != "Likely match - verify"].copy()

    st.metric("Items Requiring Review", len(queue))

    decisions_file = Path("approval_decisions.csv")

    if decisions_file.exists():
        decisions = pd.read_csv(decisions_file).fillna("")
    else:
        decisions = pd.DataFrame(columns=[
            "facility", "crm_account_id", "decision", "review_note"
        ])

    for _, item in queue.iterrows():
        with st.expander(
            f'{item["facility"]} — {item["recommendation"]}'
        ):
            st.write("Website address:", item["facility_address"])
            st.write("CRM candidate:", item["crm_account"])
            st.write("CRM address:", item["crm_address"])
            st.write("Match score:", item["confidence"])

            saved = decisions[decisions["facility"] == item["facility"]]
            saved_decision = saved.iloc[-1]["decision"] if not saved.empty else "Pending"
            saved_note = saved.iloc[-1]["review_note"] if not saved.empty else ""

            options = ["Pending", "Approve for further processing", "Reject"]
            if saved_decision not in options:
                saved_decision = "Pending"

            decision = st.selectbox(
                "Decision",
                options,
                index=options.index(saved_decision),
                key=f'decision_{item["facility"]}'
            )

            note = st.text_input(
                "Review notes",
                value=str(saved_note) if pd.notna(saved_note) else "",
                key=f'note_{item["facility"]}'
            )

            if st.button(
                "Save Decision",
                key=f'save_{item["facility"]}'
            ):
                decisions = decisions[
                    decisions["facility"] != item["facility"]
                ]

                new_row = pd.DataFrame([{
                    "facility": item["facility"],
                    "crm_account_id": item["crm_account_id"],
                    "decision": decision,
                    "review_note": note
                }])

                decisions = pd.concat(
                    [decisions, new_row],
                    ignore_index=True
                )

                decisions.to_csv(decisions_file, index=False)
                st.success("Decision saved locally. CRM unchanged.")

    if decisions_file.exists():
        st.download_button(
            "Download Approval Decisions",
            data=decisions_file.read_text(),
            file_name="approval_decisions.csv",
            mime="text/csv"
        )


st.divider()
st.subheader("Financial Risk Review")

audit_path = Path("crm_financial_audit.csv")

if audit_path.exists():
    audit = pd.read_csv(audit_path).fillna("")
    flagged = audit[
        audit["requires_financial_review"].astype(str).str.lower()
        == "true"
    ]

    st.warning(
        f"{len(flagged)} CRM accounts require financial review. "
        "Do not merge, delete, or transfer billing history without approval."
    )

    st.dataframe(
        flagged,
        width="stretch",
        hide_index=True
    )
else:
    st.info("Run audit_crm.py to generate financial risk data.")
