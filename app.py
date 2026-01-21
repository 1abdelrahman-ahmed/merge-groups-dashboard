import streamlit as st
import pandas as pd
import helper

st.set_page_config(page_title="Merge Groups", layout="wide")
st.title("🔁 Merge Groups Dashboard")

# -----------------------
# Load data (cached)
# -----------------------
@st.cache_data(ttl=60)
def get_df():
    return helper.load_data()

# Refresh
if st.sidebar.button("🔄 Refresh"):
    st.cache_data.clear()

df = get_df()

# -----------------------
# Sidebar controls
# -----------------------
st.sidebar.header("Settings")

# keys options from the dataframe (استبعد الأعمدة اللي مش منطقية للتجميع)
excluded = {"Timestamp"}  # أنت أصلاً بتشيل Timestamp في helper
key_options = [c for c in df.columns if c not in excluded]

default_keys = [k for k in ["Day", "Time", "Level"] if k in key_options]

keys = st.sidebar.multiselect(
    "Keys (Group by)",
    options=key_options,
    default=default_keys
)

threshold = st.sidebar.number_input(
    "Student threshold (keep rows with students < threshold)",
    min_value=0, max_value=1000, value=5, step=1
)

show_only_merged = st.sidebar.checkbox("Show only merged groups", value=False)

# Validation
if not keys:
    st.info("👈 Choose at least one key")
    st.stop()

# -----------------------
# Raw data
# -----------------------
st.subheader("📄 Raw Data")
st.dataframe(df, use_container_width=True, height=320)

# -----------------------
# Aggregated result
# -----------------------
st.subheader("✅ Merged Groups Result")

result = helper.build_view(df, keys, threshold)

if show_only_merged:
    result_view = helper.merged_only(result)
else:
    result_view = result

# small metrics
c1, c2, c3 = st.columns(3)
c1.metric("Rows (raw)", len(df))
c2.metric("Keys after grouping", len(result))
c3.metric("Merged keys", int((result["groups_count"] > 1).sum()))

st.dataframe(result_view, use_container_width=True, height=480)

# -----------------------
# Download
# -----------------------
st.subheader("⬇️ Download")
st.download_button(
    "Download current result (CSV)",
    data=result_view.to_csv(index=False).encode("utf-8"),
    file_name="merged_groups.csv",
    mime="text/csv",
    use_container_width=True
)
