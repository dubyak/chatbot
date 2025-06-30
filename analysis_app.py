import streamlit as st
import pandas as pd
import altair as alt

st.title("📊 LCM Messaging Impact Analysis")

st.write(
    "Upload a list of LCM messages and conversation logs to explore how marketing\n"
    "campaigns affect user interactions with the AI loan officer/biz coach agent.\n"
)

messages_file = st.file_uploader("LCM messages CSV", type="csv")
logs_file = st.file_uploader("Conversation logs CSV", type="csv")

if messages_file and logs_file:
    messages = pd.read_csv(messages_file, parse_dates=["timestamp"])
    logs = pd.read_csv(logs_file, parse_dates=["timestamp"])

    required_message_cols = {"user_id", "timestamp"}
    required_log_cols = {"user_id", "timestamp"}

    if not required_message_cols.issubset(messages.columns):
        st.error(f"Messages CSV must contain columns: {', '.join(required_message_cols)}")
    elif not required_log_cols.issubset(logs.columns):
        st.error(f"Logs CSV must contain columns: {', '.join(required_log_cols)}")
    else:
        messages = messages.sort_values("timestamp")
        logs = logs.sort_values("timestamp")

        counts = []
        for _, msg in messages.iterrows():
            after = logs[(logs["user_id"] == msg["user_id"]) & (logs["timestamp"] >= msg["timestamp"])]
            counts.append(len(after))
        messages["post_interactions"] = counts

        st.subheader("Message Impact Table")
        st.dataframe(messages)

        chart = alt.Chart(messages).mark_bar().encode(
            x=alt.X("timestamp:T", title="Message Time"),
            y=alt.Y("post_interactions:Q", title="Post-message Interactions")
        )
        st.altair_chart(chart, use_container_width=True)
else:
    st.info("Please upload both CSV files to begin analysis.")
