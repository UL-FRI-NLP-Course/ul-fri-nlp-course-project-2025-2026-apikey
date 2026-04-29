import streamlit as st
from src.rag import FitnessRAG, build_prompt
from src.llm import ask_ollama
from src.config import OLLAMA_MODEL

st.set_page_config(
    page_title="Fitness RAG Assistant",
    page_icon="🏋️",
    layout="centered",
)

st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.4rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
    }
    .subtitle {
        color: #CBD5E1;
        margin-bottom: 2rem;
    }
    .info-box {
        background-color: #1E293B;
        padding: 1rem;
        border-radius: 0.8rem;
        border: 1px solid #334155;
        margin-bottom: 1.2rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

@st.cache_resource
def load_rag():
    return FitnessRAG()

rag = load_rag()

st.markdown('<div class="main-title">🏋️ Fitness RAG Assistant</div>', unsafe_allow_html=True)
st.markdown(
    f'<div class="subtitle">Local fitness chatbot using <b>{OLLAMA_MODEL}</b>, Qdrant, and the MegaGym dataset.</div>',
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Project Info")
    st.write(f"**Model:** {OLLAMA_MODEL}")
    st.write("**Vector DB:** Qdrant")
    st.write("**Dataset:** MegaGym Exercise Dataset")
    st.write("**Method:** Retrieval-Augmented Generation")

    if st.button("Clear chat"):
        st.session_state.messages = []
        st.rerun()

st.markdown(
    """
    <div class="info-box">
    Ask questions about exercises, muscle groups, equipment, or workout recommendations.
    </div>
    """,
    unsafe_allow_html=True,
)

example_questions = [
    "What exercises can I do for chest with dumbbells?",
    "Which triceps exercises use a cable machine?",
    "Give me beginner leg exercises using bodyweight.",
    "What exercises target rear delts without machines?",
    "Which back exercises can I do with a pull-up bar?",
]

selected_example = st.selectbox("Try an example question:", [""] + example_questions)

if "messages" not in st.session_state:
    st.session_state.messages = []

if selected_example and st.button("Ask example"):
    st.session_state.pending_question = selected_example

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

typed_question = st.chat_input("Ask a fitness question...")

question = typed_question or st.session_state.pop("pending_question", None)

if question:
    st.session_state.messages.append({"role": "user", "content": question})

    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        context = ""
        try:
            with st.spinner("Retrieving relevant exercises..."):
                context = rag.retrieve_context(question)
                prompt = build_prompt(question, context)
                answer = ask_ollama(prompt)

            st.write(answer)

            with st.expander("Retrieved context"):
                st.text(context)
        except Exception as exc:
            answer = (
                "Sorry, I ran into a problem while retrieving relevant exercises or "
                "generating a response. Please try again."
            )
            st.error(f"{answer} Error details: {exc}")
            st.write(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})