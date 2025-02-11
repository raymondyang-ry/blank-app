import streamlit as st
from openai import OpenAI


def reset_chat_history():
    st.session_state.messages = []



if __name__ == '__main__':
    st.title("LLM Demo")
    pixels_per_row = 34
    data_context = st.text_area("Data", "The data for the LLM to understand as well as how to use it",
                                height=pixels_per_row*4)
    system_prompt_input = st.text_area("System Prompt", "Any instructions to the LLM to describe its role",
                                height=pixels_per_row*4)
    customer_persona = st.text_area("Customer Personal", "Any instructions about the customer the LLM would be responding to",
                                height=pixels_per_row*4)
    history = st.text_area("Previous Conversation", "Insert any historical conversations real or mock up to give the LLM examples",
                                height=pixels_per_row*4)
    # combining the prompt
    full_prompt = "\n".join([data_context, system_prompt_input, customer_persona, history])
    left, middle, right = st.columns(3)
    llm_init = left.button("Initialize LLM", type="primary")
    reset_chat = right.button("Reset LLM", type="primary", on_click=reset_chat_history)

    # Set OpenAI API key from Streamlit secrets
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    # Set a default model
    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-4o-mini"

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("What is up?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)
        chat_msgs = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            stream = client.chat.completions.create(
                model=st.session_state["openai_model"],
                messages=[{"role":"developer", "content":full_prompt}] + chat_msgs,
                stream=True,
            )
            response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})
