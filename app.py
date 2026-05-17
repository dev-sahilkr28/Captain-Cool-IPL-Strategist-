import os
import streamlit as st
from google import genai
from google.genai import types

# 1. PAGE CONFIGURATION & STYLING
st.set_page_config(page_title="Captain Cool AI", page_icon="🏏", layout="wide")

st.title("🏏 Captain Cool — Multi-Agent IPL Match Strategist")
st.markdown("*Built on Google Gemini Ecosystem & Agent Development Kit Framework*")
st.markdown("---")

# 2. MANDATORY INPUTS (Sidebar Form Layout)
st.sidebar.header("🎯 Live Match State Configurator")
innings = st.sidebar.selectbox("Innings", [1, 2], index=1)
venue = st.sidebar.text_input("Venue / Stadium", "M. Chinnaswamy Stadium, Bengaluru")

col_score, col_wickets = st.sidebar.columns(2)
with col_score:
    score = st.sidebar.number_input("Current Score (Runs)", min_value=0, max_value=400, value=142)
with col_wickets:
    wickets = st.sidebar.number_input("Wickets Down", min_value=0, max_value=10, value=4)

overs = st.sidebar.number_input("Overs Completed (e.g., 14.2)", min_value=0.0, max_value=20.0, value=14.2, step=0.1)
pitch = st.sidebar.selectbox("Pitch Condition", ["Turning / Spin-friendly", "Flat track / Batter's paradise", "Two-paced / Sluggish"])
dew = st.sidebar.checkbox("Is Dew Factor present?", value=True)

target = 0
if innings == 2:
    target = st.sidebar.number_input("Target Score to Chase", min_value=1, max_value=400, value=185)

# Wrap state inside context dictionary
match_state_dict = {
    "innings": innings, "venue": venue, "score": score, "wickets": wickets,
    "overs": overs, "pitch": pitch, "dew": "Yes" if dew else "No", "target": target
}

# 3. NATIVE GEMINI TOOL (Function Calling Requirement)
def calculate_match_metrics(score: int, wickets: int, overs: float, target: int = 0) -> str:
    """Calculates live run rates and a dynamic win probability graph baseline."""
    completed_overs = int(overs)
    balls_in_current_over = int(round((overs % 1) * 10))
    balls_bowled = (completed_overs * 6) + balls_in_current_over
    
    if balls_bowled == 0: return "Match just started. Metrics at baseline equilibrium."
    
    current_rr = (score / balls_bowled) * 6
    metrics_summary = f"Current Run Rate (CRR): {current_rr:.2f}. "
    
    if target > 0:
        runs_needed = target - score
        balls_remaining = 120 - balls_bowled
        required_rr = (runs_needed / balls_remaining) * 6 if balls_remaining > 0 else 99.0
        prob = max(5, min(95, 50 + (current_rr - required_rr) * 4.5 - (wickets * 8.5)))
        metrics_summary += f"Target: {target}. Runs Needed: {runs_needed} off {balls_remaining} balls. Required Run Rate (RRR): {required_rr:.2f}. Win Prob: {prob:.1f}%"
    else:
        metrics_summary += f"Projected Score: {int(current_rr * 20)}"
        
    return metrics_summary

# 4. ORCHESTRATION PIPELINE LOGIC
if st.button("⚡ Run Dugout Strategy Session", type="primary"):
    with st.spinner("🤖 Orchestrating multi-turn reasoning between Gemini Agents..."):
        try:
            # Client picks key automatically from environment configuration
            client = genai.Client()
            model_id = "gemini-2.5-flash"
            state_context = f"Innings: {innings}, Venue: {venue}, Score: {score}/{wickets}, Overs: {overs}, Pitch: {pitch}, Dew: {dew}, Target: {target}"

            # Turn 1: The Performance Analyst (Executes Tool Call)
            response_analyst = client.models.generate_content(
                model=model_id,
                contents=f"Analyze and run metrics tool for: {state_context}",
                config=types.GenerateContentConfig(
                    system_instruction="You are an elite IPL Performance Analyst. You MUST use the calculate_match_metrics tool and provide data-backed tactical recommendations.",
                    tools=[calculate_match_metrics]
                )
            )
            analyst_out = response_analyst.text

            # Turn 2: The Devil's Advocate (Critiques Strategy)
            response_advocate = client.models.generate_content(
                model=model_id,
                contents=f"The Analyst suggested:\n{analyst_out}\n\nFind fatal flaws based on context: {state_context}",
                config=types.GenerateContentConfig(
                    system_instruction="You are a cynical coach serving as Devil's Advocate. Counter the analyst's ideas using field realities like wet ball dew or short boundary dimensions."
                )
            )
            advocate_out = response_advocate.text

            # Turn 3: Captain Cool (Final Executive Synthesis)
            response_captain = client.models.generate_content(
                model="gemini-2.5-pro",
                contents=f"Context: {state_context}\n\nAnalyst: {analyst_out}\n\nDevil's Advocate: {advocate_out}\n\nSettle the dugout debate and command the final move.",
                config=types.GenerateContentConfig(
                    system_instruction="You are 'Captain Cool' (MS Dhoni & Rohit Sharma hybrid). Make the ultimate match decision using authentic, street-smart cricket slang vernacular."
                )
            )
            captain_out = response_captain.text

            # 5. OUTPUT DISPLAY COMPONENT
            st.success("## 🏆 The Captain's Final Call")
            st.markdown(f"{captain_out}")
            
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                st.info("### 📊 Performance Analyst Recommendation")
                st.write(analyst_out)
            with col2:
                st.error("### 🤬 Devil's Advocate Counter-Argument")
                st.write(advocate_out)

        except Exception as e:
            st.error(f"Execution Context Log: {e}")
            st.warning("Ensure your GEMINI_API_KEY environment token is loaded inside Google Antigravity runtime.")
