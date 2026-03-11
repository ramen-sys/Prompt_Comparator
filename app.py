import streamlit as st
from google import genai
import time
import re
from google.genai import types
import os

st.set_page_config(
    page_title="Prompt Strategy Lab",
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

    .strategy-name {
        font-size: 1.1rem;
        font-weight: 600;
        color: #f1f5f9;
    }

    .token-box {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 10px;
        padding: 0.8rem 1rem;
        margin-bottom: 1rem;
        display: flex;
        gap: 1.5rem;
        flex-wrap: wrap;
    }

    .token-item {
        display: flex;
        flex-direction: column;
        align-items: center;
    }

    .token-value {
        font-size: 1.4rem;
        font-weight: 700;
        color: #f8fafc;
    }

    .token-label {
        font-size: 0.7rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

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


def estimate_tokens(text:str):
    return max(1,len(text)//4)
def count_words(text:str):
    return(len(text.split())) if text else 0
def build_prompts(user_input:str,task_type:str):

    examples_map={
        "Summarize":{
            "few":(
                "Example 1:\nInput: The cat sat on the mat and looked out the window all day.\n"
                "Output: A cat spent the day sitting on a mat, gazing outside.\n\n"
                "Example 2:\nInput: Scientists discovered a new species of frog in the Amazon rainforest last Tuesday.\n"
                "Output: Researchers found a previously unknown frog species in the Amazon.\n\n"
            )
        },
        "Explain (ELI5)": {
            "few": (
                "Example 1:\nInput: What is gravity?\n"
                "Output: Imagine you have a big trampoline. When you put a bowling ball on it, it makes a dip. "
                "Now roll a marble near the bowling ball — it curves toward it. That's kind of like gravity!\n\n"
                "Example 2:\nInput: What is electricity?\n"
                "Output: Think of electricity like tiny invisible balls called electrons running through wires, "
                "like water through a pipe. When they flow, they power your lights and toys!\n\n"
            )
        },
        "Classify Sentiment": {
            "few": (
                "Example 1:\nInput: I absolutely love this product! Best purchase ever.\nOutput: POSITIVE\n\n"
                "Example 2:\nInput: It was okay, nothing special.\nOutput: NEUTRAL\n\n"
                "Example 3:\nInput: Terrible quality, broke after one day.\nOutput: NEGATIVE\n\n"
            )
        },
        "Write Code": {
            "few": (
                "Example 1:\nInput: Reverse a string in Python\n"
                "Output:\n```python\ndef reverse_string(s):\n    return s[::-1]\n```\n\n"
                "Example 2:\nInput: Check if a number is even\n"
                "Output:\n```python\ndef is_even(n):\n    return n % 2 == 0\n```\n\n"
            )
        },
        "Answer Question": {
            "few": (
                "Example 1:\nQ: What is the capital of France?\nA: Paris is the capital of France.\n\n"
                "Example 2:\nQ: How many days are in a leap year?\nA: A leap year has 366 days.\n\n"
            )
        },
    }

    task_instruction = {
        "Summarize": "Summarize the following text concisely",
        "Explain (ELI5)": "Explain the following as if I'm 5 years old",
        "Classify Sentiment": "Classify the sentiment of the following text as POSITIVE, NEUTRAL, or NEGATIVE",
        "Write Code": "Write Python code for the following task",
        "Answer Question": "Answer the following question accurately",
    }[task_type]

    few_ex=examples_map[task_type]["few"]

    return {
        "zero_shot": {
            "label": "Zero-Shot",
            "color": "#a78bfa",
            "badge": "badge-zero",
            "icon": "⚡",
            "description": "No examples — just a direct instruction.",
            "prompt": f"{task_instruction}:\n\n{user_input}"
        },
        "few_shot": {
            "label": "Few-Shot",
            "color": "#60a5fa",
            "badge": "badge-few",
            "icon": "📚",
            "description": "Learns from 2–3 examples before answering.",
            "prompt": f"{task_instruction}.\n\nHere are some examples:\n\n{few_ex}Now do the same for:\nInput: {user_input}\nOutput:"
        },
        "chain_of_thought": {
            "label": "Chain-of-Thought",
            "color": "#34d399",
            "badge": "badge-cot",
            "icon": "🔗",
            "description": "Thinks step-by-step before answering.",
            "prompt": (
                f"{task_instruction}. Think through this step by step, showing your reasoning clearly "
                f"before giving your final answer.\n\n"
                f"Input: {user_input}\n\n"
                f"Let's work through this step by step:"
            )
        },
    }
def call_gemini(prompt:str,model,client,temperature:float):
    t0=time.time()
    try:
        response=client.models.generate_content(model=model,contents=prompt,config=types.GenerateContentConfig(temperature=temperature,max_output_tokens=1024))
        latency=time.time()-t0
        text=response.text

        try:
            in_tokens=response.usage_metadata.prompt_token_count
            out_tokens=response.usage_metadata.candidates_token_count
        except Exception:
            in_tokens=estimate_tokens(prompt)
            out_tokens=estimate_tokens(text)
        
        return {"text": text,
            "latency": latency,
            "in_tokens": in_tokens,
            "out_tokens": out_tokens,
            "total_tokens": in_tokens + out_tokens,
            "words": count_words(text),
            "error": None,
        }
    except Exception as e:
        return {
            "text": "",
            "latency": time.time() - t0,
            "in_tokens": 0,
            "out_tokens": 0,
            "total_tokens": 0,
            "words": 0,
            "error": str(e),
        }


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

    task_type=st.selectbox(
        "Task type",
        ["Summarize", "Explain (ELI5)", "Classify Sentiment", "Write Code", "Answer Question"],
        index=0

    )
    st.markdown("----")
    st.markdown("###STrategy guide")

    st.markdown("""
                <div style='font-size:0.82rem; color:#94a3b8; line-height:1.6;'>
<b style='color:#a78bfa'>⚡ Zero-Shot</b><br>
No examples. The model relies entirely on its training. Fast & concise.<br><br>
<b style='color:#60a5fa'>📚 Few-Shot</b><br>
2–3 examples teach the model the format. More consistent output.<br><br>
<b style='color:#34d399'>🔗 Chain-of-Thought</b><br>
"Think step by step" unlocks reasoning. Best for complex tasks.
</div>
""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
<div style='font-size:0.78rem; color:#475569; text-align:center;'>
Built with Streamlit + Gemini API<br>
🧠 Prompt Strategy Lab
</div>
""", unsafe_allow_html=True)
    
st.markdown('<h1 class="main-title">Prompt strategy lab</h1>',unsafe_allow_html=True)

st.markdown(
    '<p class="subtitle">Compare Zero_Shot. Few Shot.Chain_of_thought</p>',unsafe_allow_html=True
)

user_input=st.text_area(
    "Your Input",
    placeholder="Type anything here-a question, a paragraph",
    height=120,
    label_visibility="visible",
)
col_btn,col_space=st.columns([1,3])
with col_btn:
    run=st.button("Run comparison",use_container_width=True)

if run:
    if not api_key:
        st.error("Please enter your Gemini api key to Start")
        st.stop()
    if not user_input.strip():
        st.warning("Please enter some input first")
        st.stop()
    os.environ["GOOGLE_API_KEY"]=api_key
    client=genai.Client(api_key=os.environ["GOOGLE_API_KEY"])
    prompts=build_prompts(user_input.strip(),task_type)
    results={}

    with st.spinner("Calling Gemini for all three strategies..."):
        for key,pdata in prompts.items():
            results[key]== {**pdata, **call_gemini(pdata["prompt"], model_choice,client, temperature)}

    cols=st.columns(3)
    keys=["zero_shot","few_shot","chain_of_thought"]      
    max_latency = max(results[k]["latency"] for k in keys) or 1

    for col, key in zip(cols, keys):
        r = results[key]
        with col:
            bar_pct = int((r["latency"] / max_latency) * 100)
            bar_color = r["color"] 
            st.markdown(f"""
<div class="card">
  <div class="card-header">
    <span class="badge {r['badge']}">{r['icon']} {r['label']}</span>
  </div>
  <div style="color:#94a3b8; font-size:0.8rem; margin-bottom:1rem;">{r['description']}</div>

  <div class="token-box">
    <div class="token-item">
      <span class="token-value">{r['in_tokens']}</span>
      <span class="token-label">In Tokens</span>
    </div>
    <div class="token-item">
      <span class="token-value">{r['out_tokens']}</span>
      <span class="token-label">Out Tokens</span>
    </div>
    <div class="token-item">
      <span class="token-value">{r['total_tokens']}</span>
      <span class="token-label">Total</span>
    </div>
    <div class="token-item">
      <span class="token-value">{r['words']}</span>
      <span class="token-label">Words</span>
    </div>
  </div>

  <div class="latency-bar-container">
    <div class="latency-label">⏱ Latency: {r['latency']:.2f}s</div>
    <div style="background:rgba(255,255,255,0.08);border-radius:3px;height:6px;">
      <div class="latency-bar" style="width:{bar_pct}%;background:{bar_color};"></div>
    </div>
  </div>

  <hr style="border:none;border-top:1px solid rgba(255,255,255,0.07);margin:1rem 0;">

  <div class="response-text">{r['text'] if not r['error'] else '❌ Error: ' + r['error']}</div>
</div>
""", unsafe_allow_html=True)

    # ── Summary comparison ─────────────────────────────────────────────────
    fastest_key = min(keys, key=lambda k: results[k]["latency"])
    most_words_key = max(keys, key=lambda k: results[k]["words"])
    cheapest_key = min(keys, key=lambda k: results[k]["total_tokens"])

    st.markdown(f"""
<div class="comparison-summary">
  <div style="font-size:1rem;font-weight:600;color:#f1f5f9;margin-bottom:0.8rem;">📊 Run Summary</div>
  <div style="display:flex;gap:2rem;flex-wrap:wrap;font-size:0.88rem;color:#94a3b8;">
    <div>⚡ Fastest: <span class="winner-chip">{results[fastest_key]['label']} ({results[fastest_key]['latency']:.2f}s)</span></div>
    <div>📝 Most Verbose: <span class="winner-chip">{results[most_words_key]['label']} ({results[most_words_key]['words']} words)</span></div>
    <div>💰 Fewest Tokens: <span class="winner-chip">{results[cheapest_key]['label']} ({results[cheapest_key]['total_tokens']} tokens)</span></div>
    <div>🌡 Temperature: <span class="winner-chip">{temperature}</span></div>
    <div>🤖 Model: <span class="winner-chip">{model_choice}</span></div>
  </div>
</div>
""", unsafe_allow_html=True)

    # ── Prompt inspector (expander) ────────────────────────────────────────
    with st.expander("🔍 View Raw Prompts Sent to Gemini"):
        for key in keys:
            r = results[key]
            st.markdown(f"**{r['icon']} {r['label']}**")
            st.code(r["prompt"], language="text")

else:
    # ── Empty state ────────────────────────────────────────────────────────
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
