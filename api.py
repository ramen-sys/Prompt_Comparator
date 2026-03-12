import os
from google import genai
from google.genai import types
import streamlit as st
import time


import json

os.environ["GOOGLE_API_KEY"]="AIzaSyD3TJjXQu1nW-kOSrDcAb3U_-6f0HSW-nI"

client=genai.Client(api_key=os.environ["GOOGLE_API_KEY"])

st.set_page_config(
    page_title="Test Chat bot",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        min-height: 100vh;
    }

    .main-title {
        text-align: center;
        font-size: 2.8rem;
        font-weight: 700;
        background: linear-gradient(90deg, #a78bfa, #60a5fa, #34d399);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }

    .subtitle {
        text-align: center;
        color: #94a3b8;
        font-size: 1.05rem;
        margin-bottom: 2rem;
    }

    .card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 1.5rem;
        height: 100%;
    }

    .card-header {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        margin-bottom: 1rem;
    }

    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }

    .badge-zero { background: rgba(167,139,250,0.2); color: #a78bfa; border: 1px solid #a78bfa44; }
    .badge-few  { background: rgba(96,165,250,0.2);  color: #60a5fa; border: 1px solid #60a5fa44; }
    .badge-cot  { background: rgba(52,211,153,0.2);  color: #34d399; border: 1px solid #34d39944; }

    

    

    

    .response-text {
        color: #cbd5e1;
        font-size: 0.92rem;
        line-height: 1.7;
        white-space: pre-wrap;
        max-height: 420px;
        overflow-y: auto;
        padding-right: 0.3rem;
    }

    .response-text::-webkit-scrollbar { width: 4px; }
    .response-text::-webkit-scrollbar-track { background: transparent; }
    .response-text::-webkit-scrollbar-thumb { background: #475569; border-radius: 4px; }

    .latency-bar-container {
        margin-top: 0.8rem;
    }

    .latency-label {
        font-size: 0.75rem;
        color: #64748b;
        margin-bottom: 0.3rem;
    }

    .latency-bar {
        height: 6px;
        border-radius: 3px;
        transition: width 0.5s ease;
    }

    .tip-box {
        background: rgba(167,139,250,0.08);
        border-left: 3px solid #a78bfa;
        border-radius: 0 8px 8px 0;
        padding: 0.8rem 1rem;
        margin-top: 0.8rem;
        font-size: 0.83rem;
        color: #94a3b8;
    }

    div[data-testid="stTextArea"] textarea {
        background: rgba(255,255,255,0.06) !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
        border-radius: 12px !important;
        color: #f1f5f9 !important;
        font-size: 1rem !important;
    }

    div[data-testid="stTextInput"] input {
        background: rgba(255,255,255,0.06) !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
        border-radius: 12px !important;
        color: #f1f5f9 !important;
    }

    .stButton button {
        background: linear-gradient(135deg, #7c3aed, #2563eb) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.6rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        width: 100% !important;
        transition: all 0.2s ease !important;
    }

    .stButton button:hover {
        opacity: 0.88 !important;
        transform: translateY(-1px) !important;
    }

    .stSelectbox div[data-baseweb="select"] {
        background: rgba(255,255,255,0.06) !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
        border-radius: 10px !important;
    }

    .comparison-summary {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        margin-top: 1.5rem;
    }

    .winner-chip {
        display: inline-block;
        background: linear-gradient(135deg, #7c3aed44, #2563eb44);
        border: 1px solid #7c3aed88;
        border-radius: 999px;
        padding: 0.2rem 0.8rem;
        font-size: 0.8rem;
        font-weight: 600;
        color: #c4b5fd;
    }
</style>
""", unsafe_allow_html=True)
def call_gemini(prompt,model,client,temperature):

    history=[]
    t0=time.time()
    if os.path.exists("history.json"):
        with open("history.json") as f:
            content=f.read().strip()
            if content:
                data=json.loads(content)
                history=[types.Content(role=m["role"],parts=[types.Part(text=m["text"])]) for m in data]
            response=client.models.generate_content(model="gemini-2.5-flash",contents=history+[types.Content(role="user", parts=[types.Part(text=prompt)])],config= types.GenerateContentConfig(system_instruction="Always Keep the answer concise",temperature=0.7,max_output_tokens=1024))
            latency=time.time()-t0
            text=response.text
            print(response.text)
            history.append(types.Content(role="user",parts=[types.Part(text=prompt)]))
            history.append(types.Content(role="model",parts=[types.Part(text=response.text)]))
            with open ("history.json",'w') as f:
                data=[{"role":m.role,"text":m.parts[0].text}for m in history]
                json.dump(data,f)
        return text
with st.sidebar:
    st.markdown("## Configuration")
    st.markdown("---")

    api_key=st.text_input(
    "gemini Api key",
    type="password",
    placeholder="AIZ...",
    
    )

    model_choice=st.selectbox(
        "Model",
        ["gemini-2.5-flash","gemini-2.5-pro"],
        index=0
    )
    temperature=st.sidebar.slider(
        "temperature",
        min_value=0.0,max_value=1.0,value=0.7,step=0.05,
    )

user_input=st.text_area(
    "Your Input",
    placeholder="Type anything here-a question, a paragraph",
    height=120,
    label_visibility="visible",
)
col_btn,col_space=st.columns([1,3])
with col_btn:
    run=st.button("Run ",use_container_width=True)

if run:
    if not api_key:
        st.error("Please enter your Gemini api key to Start")
        st.stop()
    if not user_input.strip():
        st.warning("Please enter some input first")
        st.stop()
    os.environ["GOOGLE_API_KEY"]=api_key
    client=genai.Client(api_key=os.environ["GOOGLE_API_KEY"])
    prompt=user_input.strip()
    results={}

    with st.spinner("Calling Gemini for all three strategies..."):
        results= call_gemini(prompt, model_choice,client, temperature)
    st.text(
        body=results
    )

        

st.markdown("""
<div style="text-align:center;padding:4rem 2rem;color:#475569;">
  <div style="font-size:4rem;margin-bottom:1rem;">🧪</div>
  <div style="font-size:1.2rem;font-weight:600;color:#64748b;margin-bottom:0.5rem;">
    Ready to compare prompting strategies
  </div>
  <div style="font-size:0.9rem;">
    Enter your API key in the sidebar, type something above, and hit <b>Run Comparison</b>
  </div>
</div>
""", unsafe_allow_html=True)
