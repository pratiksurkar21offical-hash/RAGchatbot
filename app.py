import streamlit as st

from src.chain import build_chain

st.set_page_config(page_title="NovaCell Support", page_icon="📱")

SAMPLE_QUESTIONS = [
    "What's your cheapest unlimited plan?",
    "Do you have a family plan?",
    "I'm going to Europe for about a week — what are my roaming options?",
    "Is there a discount for students?",
    "Why is my mobile internet so slow?",
    "My eSIM activation failed — what should I do?",
    "How do I check my current data balance?",
]


@st.cache_resource
def get_chain():
    return build_chain()


def _send(question: str):
    st.session_state.pending = question


if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending" not in st.session_state:
    st.session_state.pending = None

with st.sidebar:
    st.header("NovaCell Assistant")
    st.caption("Grounded in FAQs, resolved tickets, official guides, and plan pricing.")
    st.subheader("Sample questions")
    for q in SAMPLE_QUESTIONS:
        st.button(q, key=f"s-{q}", on_click=_send, args=(q,), use_container_width=True)
    st.divider()
    if st.button("Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pending = None
        st.rerun()

st.title("📱 NovaCell Support Chatbot")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Ask a question…")
question = user_input or st.session_state.pending
st.session_state.pending = None

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)
    with st.chat_message("assistant"):
        placeholder = st.empty()
        chain = get_chain()
        streamed = ""
        for token in chain.stream(question):
            streamed += token
            placeholder.markdown(streamed)
    st.session_state.messages.append({"role": "assistant", "content": streamed})
