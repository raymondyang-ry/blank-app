import streamlit as st
import os
from openai import OpenAI
from litellm import completion

def set_env():
    """
    Inital envs, can also use dotenv for more complex configs 
    """
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
    os.environ["ANTHROPIC_API_KEY"] = st.secrets["ANTHROPIC_API_KEY"]

def reset_chat_history():
    st.session_state.messages = []

def set_full_prompt(data_context, system_prompt_input, customer_persona, history):
    """
    Wrapper for prompt, any prompt formatting can be done here and will be store in st.session_state["full_prompt"]
    """
    st.session_state["full_prompt"] = "\n".join([data_context, system_prompt_input, customer_persona, history])

def get_model_name(st_option):
    """
    Simple Look up from Streamlit drop down menu -> litellm model name
    """
    model_mapping = {
        "Claude Haiku 3.5":"anthropic/claude-3-5-haiku-20241022",
        "Claude Sonnet 3.5":"anthropic/claude-3-5-sonnet-20241022",
        "OpenAI 4o-mini":"openai/gpt-4o-mini",
        "OpenAI 4o":"openai/gpt-4o"
    }
    print(f"Model chosen: {model_mapping[st_option]}")
    return model_mapping[st_option] 

def call_model_completion(model_name):
    """
    Use litellm completion api to call the llm. Returns a generator object for streamlite to stream.
    """
    chat_msgs = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
    sys_prompt = [{"role":"system", "content":st.session_state["full_prompt"]}]
    # print(chat_msgs)
    # print(sys_prompt)
    stream = completion(model=model_name,
               messages=sys_prompt + chat_msgs,
               stream=True)
    for chunk in stream:
        # Extract the 'content' from the 'message' in each chunk
        delta = chunk["choices"][0]["delta"]
        text_chunk = delta.get("content", None)
        if text_chunk:
            yield text_chunk
    # return stream

if __name__ == '__main__':
    set_env() 
    st.title("LLM Demo")

    option = st.selectbox(
        "LLM Model",
        ("Claude Haiku 3.5", "Claude Sonnet 3.5", "OpenAI 4o-mini", "OpenAI 4o"),
    )
    model_name = get_model_name(option)
    pixels_per_row = 34
    data_context = st.text_area("Data", "The data for the LLM to understand as well as how to use it",
                                height=pixels_per_row*4)
    system_prompt_input = st.text_area("System Prompt", "Any instructions to the LLM to describe its role",
                                height=pixels_per_row*4)
    customer_persona = st.text_area("Customer Personal", "Any instructions about the customer the LLM would be responding to",
                                height=pixels_per_row*4)
    history = st.text_area("Previous Conversation", "Insert any historical conversations real or mock up to give the LLM examples",
                                height=pixels_per_row*4)

    left, middle, right = st.columns(3)
    llm_init = left.button("Initialize LLM", type="primary", on_click=set_full_prompt, 
                           args=(data_context, system_prompt_input, customer_persona, history))
    reset_chat = right.button("Reset LLM", type="primary", on_click=reset_chat_history)

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

        with st.chat_message("assistant"):
            stream = call_model_completion(model_name)
            response = st.write_stream(stream)
        # response is a list after the generator finishes with the first being the actual content
        st.session_state.messages.append({"role": "assistant", "content": response})
        print(f"\nThere are currently {len(st.session_state.messages)} Messages\n")
        print(st.session_state.messages)
