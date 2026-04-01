import streamlit as st
import requests
import time
import pandas as pd
import os
from dotenv import load_dotenv

try:
    from streamlit_agraph import agraph, Node, Edge, Config
except ImportError:
    pass

load_dotenv()

API = os.getenv('API_URL', "http://127.0.0.1:8000")

st.set_page_config(page_title="Migration Control", layout="wide")

st.markdown("## 🚀 Cloud Migration Control Center")
st.caption("AI-powered dependency-aware orchestration")

# 🔥 Toast (runs once)
if "toast_shown" not in st.session_state:
    st.toast("🚀 Migration pipeline initialized", icon="🔥")
    st.session_state.toast_shown = True

placeholder = st.empty()

while True:
    try:
        services_res = requests.get(f"{API}/services")
        
        if services_res.status_code == 200:
            data = services_res.json()

            with placeholder.container():

                total = len(data)
                success = sum(1 for s in data.values() if s["status"] == "SUCCESS")
                deploying = sum(1 for s in data.values() if s["status"] == "DEPLOYING")
                failed = sum(1 for s in data.values() if s["status"] == "FAILED")

                # =========================
                # 🔥 METRICS
                # =========================
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Total", total)
                col2.metric("Completed", success)
                col3.metric("Running", deploying)
                col4.metric("Failed", failed)

                st.divider()

                # =========================
                # 🔥 PROGRESS
                # =========================
                progress = success / total if total else 0
                st.progress(progress)
                st.caption(f"{int(progress*100)}% completed")

                st.divider()

                # =========================
                # 🔥 MAIN LAYOUT
                # =========================
                left, right = st.columns([2, 1])

                # =========================
                # LEFT SIDE
                # =========================
                with left:

                    st.markdown("### ⚡ Services")

                    for name, info in data.items():
                        status = info["status"]
                        url = info.get("url")

                        if status == "SUCCESS":
                            if url:
                                st.markdown(f"🟢 **{name}** — {status}  [Open]({url})")
                            else:
                                st.markdown(f"🟢 **{name}** — {status}")
                        elif status == "FAILED":
                            st.markdown(f"🔴 **{name}** — {status}")
                        elif status == "DEPLOYING":
                            st.markdown(f"🔵 **{name}** — {status}")
                        elif status == "RECTIFYING":
                            st.markdown(f"🟡 **{name}** — {status}")
                        else:
                            st.markdown(f"⚪ **{name}** — {status}")

                    st.divider()

                    # 🔥 TIMELINE / STATUS CHART
                    st.markdown("### 📊 Deployment Overview")

                    df = pd.DataFrame({
                        "Status": [info["status"] for info in data.values()]
                    })

                    st.bar_chart(df["Status"].value_counts())

                # =========================
                # RIGHT SIDE
                # =========================
                with right:

                    st.markdown("### 📡 Activity")

                    logs = []

                    for name, info in data.items():
                        status = info["status"]

                        if status == "DEPLOYING":
                            logs.append(f"🚀 Deploying {name}")
                        elif status == "SUCCESS":
                            logs.append(f"✅ {name} completed")
                        elif status == "FAILED":
                            logs.append(f"❌ {name} failed")

                    if logs:
                        for log in logs[-6:]:
                            st.caption(f"• {log}")
                    else:
                        st.caption("Waiting for services...")

        else:
            st.error("Backend not responding")

    except Exception as e:
        st.error(f"⚠️ System initializing... ({str(e)})")

    time.sleep(2)
    st.rerun()
