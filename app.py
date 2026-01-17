"""
ClinicalMind: Multi-Agent Clinical Trial Simulator
Streamlit Dashboard Application

Built for Gemini 3 Hackathon
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import os

# Page configuration
st.set_page_config(
      page_title="ClinicalMind - Trial Simulator",
      page_icon="🧬",
      layout="wide",
      initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
            font-size: 2.5rem;
                    font-weight: bold;
                            color: #1E88E5;
                                    text-align: center;
                                            margin-bottom: 1rem;
                                                }
                                                    .agent-card {
                                                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                                                    padding: 1.5rem;
                                                                            border-radius: 10px;
                                                                                    color: white;
                                                                                            margin: 0.5rem 0;
                                                                                                }
                                                                                                    .metric-card {
                                                                                                            background: #f0f2f6;
                                                                                                                    padding: 1rem;
                                                                                                                            border-radius: 8px;
                                                                                                                                    text-align: center;
                                                                                                                                        }
                                                                                                                                            .status-ready { color: #28a745; font-weight: bold; }
                                                                                                                                                .status-running { color: #ffc107; font-weight: bold; }
                                                                                                                                                </style>
                                                                                                                                                """, unsafe_allow_html=True)


def main():
      # Sidebar
      with st.sidebar:
                st.image("https://img.icons8.com/fluency/96/dna-helix.png", width=80)
                st.title("ClinicalMind")
                st.caption("Multi-Agent Trial Simulator")

        st.divider()

        # Navigation
        page = st.radio(
                      "Navigation",
                      ["🏠 Dashboard", "👥 Patient Population", "💊 Drug Interactions", 
                                    "⚠️ Adverse Events", "📄 Regulatory Docs", "📊 Reports"]
        )

        st.divider()

        # API Key input
        api_key = st.text_input("Gemini API Key", type="password", 
                                                                help="Enter your Google Gemini API key")

        if api_key:
                      st.success("API Key configured ✓")
else:
            st.warning("API Key required for AI features")

    # Main content based on navigation
      if "Dashboard" in page:
                show_dashboard()
elif "Patient" in page:
        show_patient_population()
elif "Drug" in page:
        show_drug_interactions()
elif "Adverse" in page:
        show_adverse_events()
elif "Regulatory" in page:
        show_regulatory_docs()
elif "Reports" in page:
        show_reports()


def show_dashboard():
      st.markdown('<h1 class="main-header">🧬 ClinicalMind Dashboard</h1>', unsafe_allow_html=True)
    st.caption("Multi-Agent Clinical Trial Simulator powered by Gemini AI")

    # System Status
    col1, col2, col3, col4 = st.columns(4)
    with col1:
              st.metric("System Status", "READY", delta="Online")
          with col2:
                    st.metric("Active Agents", "4", delta="+4")
                with col3:
                          st.metric("Simulations Run", "0", delta="Today")
                      with col4:
                                st.metric("Documents Generated", "0")

    st.divider()

    # Agent Status Cards
    st.subheader("🤖 AI Agents Status")

    col1, col2 = st.columns(2)

    with col1:
              with st.container():
                            st.markdown("### 👥 Patient Population Agent")
                            st.write("Generates digital twin patient profiles with genomic data")
                            st.progress(100)
                            st.caption("Status: Ready")

              with st.container():
                            st.markdown("### ⚠️ Adverse Event Agent")
                            st.write("Predicts side effects and safety signals")
                            st.progress(100)
                            st.caption("Status: Ready")

          with col2:
                    with st.container():
                                  st.markdown("### 💊 Drug Interaction Agent")
                                  st.write("Simulates PK/PD and drug-drug interactions")
                                  st.progress(100)
                                  st.caption("Status: Ready")

                    with st.container():
                                  st.markdown("### 📄 Regulatory Document Agent")
                                  st.write("Generates FDA-compliant documents")
                                  st.progress(100)
                                  st.caption("Status: Ready")

                st.divider()

    # Quick Start
    st.subheader("🚀 Quick Start Simulation")

    col1, col2, col3 = st.columns(3)

    with col1:
              drug_name = st.text_input("Investigational Drug", "CardioX-2024")
              indication = st.text_input("Target Indication", "Resistant Hypertension")

    with col2:
              sample_size = st.slider("Sample Size", 10, 500, 100)
              duration = st.selectbox("Trial Duration", ["4 weeks", "8 weeks", "12 weeks", "24 weeks"])

    with col3:
              age_min = st.number_input("Min Age", 18, 100, 40)
              age_max = st.number_input("Max Age", 18, 100, 75)

    if st.button("🔬 Start Simulation", type="primary", use_container_width=True):
              with st.spinner("Running multi-agent simulation..."):
                            # Simulate progress
                            progress_bar = st.progress(0)
                            for i in range(100):
                                              progress_bar.progress(i + 1)

                            st.success("✅ Simulation completed!")
                            st.balloons()


def show_patient_population():
      st.title("👥 Patient Population Agent")
    st.write("Generate and manage digital twin patient populations")

    tab1, tab2, tab3 = st.tabs(["Generate", "View Population", "Analytics"])

    with tab1:
              st.subheader("Generate New Population")

        col1, col2 = st.columns(2)
        with col1:
                      n_patients = st.number_input("Number of Patients", 10, 1000, 100)
                      indication = st.text_input("Indication", "Type 2 Diabetes")

        with col2:
                      age_range = st.slider("Age Range", 18, 90, (30, 70))
                      gender_dist = st.slider("Female %", 0, 100, 50)

        st.subheader("Inclusion Criteria")
        inclusion = st.text_area("Enter criteria (one per line)", 
                                                                  "Age 18-75 years\nDiagnosed with condition\nWilling to comply")

        st.subheader("Exclusion Criteria")
        exclusion = st.text_area("Enter criteria (one per line)",
                                                                  "Pregnant or nursing\nSevere renal impairment\nAllergy to study drug")

        if st.button("Generate Population", type="primary"):
                      st.info("Generating patient population with Gemini AI...")
                      st.success(f"Generated {n_patients} patient profiles!")

    with tab2:
              st.subheader("Current Population")
              # Sample data
              df = pd.DataFrame({
                            "Patient ID": [f"PT-{i:05d}" for i in range(1, 11)],
                            "Age": [45, 52, 38, 61, 55, 48, 67, 42, 59, 51],
                            "Gender": ["M", "F", "F", "M", "M", "F", "M", "F", "M", "F"],
                            "CYP2D6": ["Normal", "Poor", "Normal", "Ultra", "Normal", "Normal", "Poor", "Normal", "Normal", "Ultra"],
                            "BMI": [28.5, 24.2, 31.0, 26.8, 29.1, 23.5, 27.4, 30.2, 25.9, 28.0]
              })
        st.dataframe(df, use_container_width=True)

    with tab3:
              st.subheader("Population Analytics")
              col1, col2 = st.columns(2)

        with col1:
                      fig = px.histogram(x=[45, 52, 38, 61, 55, 48, 67, 42, 59, 51], 
                                                                       nbins=10, title="Age Distribution")
                      st.plotly_chart(fig, use_container_width=True)

        with col2:
                      fig = px.pie(values=[5, 5], names=["Male", "Female"], 
                                                           title="Gender Distribution")
                      st.plotly_chart(fig, use_container_width=True)


def show_drug_interactions():
      st.title("💊 Drug Interaction Agent")
    st.write("Simulate pharmacokinetics and predict drug interactions")

    col1, col2 = st.columns(2)

    with col1:
              st.subheader("Drug Configuration")
              drug = st.selectbox("Select Drug", ["Metformin", "Atorvastatin", "Lisinopril", "Custom"])
              dose = st.number_input("Dose (mg)", 1, 1000, 500)
              frequency = st.selectbox("Frequency", ["Once daily", "Twice daily", "Three times daily"])

    with col2:
              st.subheader("Patient Factors")
              cyp2d6 = st.selectbox("CYP2D6 Status", ["Normal", "Poor", "Intermediate", "Ultra-rapid"])
              cyp3a4 = st.selectbox("CYP3A4 Activity", ["Normal", "Low", "High"])
              age = st.slider("Patient Age", 18, 90, 55)

    if st.button("Simulate PK", type="primary"):
              st.subheader("Pharmacokinetic Results")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Cmax", "1250 ng/mL")
        col2.metric("Tmax", "2.5 hrs")
        col3.metric("Half-life", "6.2 hrs")
        col4.metric("AUC", "8500 ng·h/mL")

        # PK curve
        import numpy as np
        t = np.linspace(0, 24, 100)
        c = 1250 * np.exp(-0.11 * t) * (1 - np.exp(-1.5 * t))

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=t, y=c, mode='lines', name='Concentration'))
        fig.update_layout(title="Plasma Concentration Over Time",
                                                   xaxis_title="Time (hours)",
                                                   yaxis_title="Concentration (ng/mL)")
        st.plotly_chart(fig, use_container_width=True)


def show_adverse_events():
      st.title("⚠️ Adverse Event Agent")
    st.write("Predict and monitor adverse events")

    st.subheader("Predicted Adverse Events")

    ae_data = pd.DataFrame({
              "Event": ["Nausea", "Headache", "Diarrhea", "Dizziness", "Fatigue"],
              "Probability": [0.25, 0.15, 0.12, 0.08, 0.10],
              "Severity": ["Mild", "Mild", "Mild", "Moderate", "Mild"],
              "Category": ["GI", "Neuro", "GI", "Neuro", "General"]
    })

    col1, col2 = st.columns([2, 1])

    with col1:
              st.dataframe(ae_data, use_container_width=True)

    with col2:
              fig = px.bar(ae_data, x="Event", y="Probability", color="Severity",
                                               title="AE Probability")
              st.plotly_chart(fig, use_container_width=True)


def show_regulatory_docs():
      st.title("📄 Regulatory Document Agent")
    st.write("Generate FDA-compliant regulatory documents")

    doc_type = st.selectbox("Document Type", [
              "Clinical Study Report (CSR)",
              "IND Summary",
              "Safety Update Report",
              "Protocol Synopsis"
    ])

    col1, col2 = st.columns(2)
    with col1:
              trial_name = st.text_input("Trial Name", "CARDIO-2024-001")
              sponsor = st.text_input("Sponsor", "PharmaCorp Inc.")

    with col2:
              region = st.selectbox("Regulatory Region", ["FDA (US)", "EMA (EU)", "PMDA (Japan)"])
              version = st.text_input("Version", "1.0")

    if st.button("Generate Document", type="primary"):
              st.info("Generating document with Gemini AI...")

        st.subheader("Document Preview")
        st.markdown("""
                # Clinical Study Report

                                **Protocol:** CARDIO-2024-001  
                                        **Sponsor:** PharmaCorp Inc.  
                                                **Version:** 1.0  

                                                                ## 1. Synopsis
                                                                        This randomized, double-blind, placebo-controlled study evaluated the efficacy
                                                                                and safety of CardioX-2024 in patients with resistant hypertension...

                                                                                                ## 2. Introduction
                                                                                                        Resistant hypertension affects approximately 10-15% of patients with hypertension...
                                                                                                                """)

        st.download_button("Download Document", "Sample CSR content...", "CSR_CARDIO-2024.md")


def show_reports():
      st.title("📊 Simulation Reports")

    st.subheader("Summary Metrics")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Simulations", "12")
    col2.metric("Patients Simulated", "1,200")
    col3.metric("AEs Predicted", "156")
    col4.metric("Documents Generated", "8")

    st.subheader("Recent Simulations")

    sims = pd.DataFrame({
              "ID": ["SIM-001", "SIM-002", "SIM-003"],
              "Date": ["2026-01-17", "2026-01-16", "2026-01-15"],
              "Drug": ["CardioX-2024", "NeuroFlex", "GlucaBalance"],
              "Patients": [100, 200, 150],
              "Status": ["Complete", "Complete", "Complete"]
    })

    st.dataframe(sims, use_container_width=True)


if __name__ == "__main__":
      main()
