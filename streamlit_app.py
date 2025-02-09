import streamlit as st
from openai import OpenAI


def reset_chat_history():
    st.session_state.messages = []
    # Doesnt clear the prompt for some reason
    # st.session_state.system_prompt_input = ""
    # st.session_state.data_context = ""


if __name__ == '__main__':
    st.title("LLM Demo")

    data_context = st.text_area("Data", "Insert any context/information for the LLM. \nIt will be concatenated to the system prompt",
                                height=34*6)
    system_prompt_input = st.text_area("System Prompt", "Any instructions to the LLM to describe its role or persona...", height=34*4)
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
    # if llm_init:
    full_prompt = f"{system_prompt_input.strip()}\n\n{data_context.strip()}"
    # print(full_prompt)
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
