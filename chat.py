import streamlit as st
import json
from constants import OPENAI_INITIAL_CONVERSATION
from openai import OpenAI
import time
from dotenv import load_dotenv

load_dotenv()


@st.cache_resource()
def get_cached_openai_service():
    return OpenAI()


def response_generator(response):
    for word in response.split():
        yield word + " "
        time.sleep(0.05)


def main():
    # Initialize OpenAI Client
    open_ai = get_cached_openai_service()

    # Initialize session state
    if "message_count" not in st.session_state:
        st.session_state.message_count = 0

    if "display_conversation" not in st.session_state:
        st.session_state.display_conversation = []

    if "gpt_conversation" not in st.session_state:
        st.session_state.gpt_conversation = OPENAI_INITIAL_CONVERSATION

        # Add user's events today to the conversation history befor sending.
        st.session_state.gpt_conversation.append(
            {"role": "user", "content": "Initial message"}
        )

        completion = open_ai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=st.session_state.gpt_conversation,
        )
        response = completion.choices[0].message.content

        response_object = json.loads(response)
        response_msg = response_object["message"]
        st.session_state.gpt_conversation.append(
            {"role": "assistant", "content": response}
        )
        st.session_state.display_conversation.append(
            {"role": "assistant", "content": response_msg.replace("\n", "  \n")}
        )
        print(response)

    # Streamlit Page
    st.title("Scheduling Assistant")

    # Display chat history
    for message in st.session_state.display_conversation:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_placeholder = st.empty()
    assistant_placeholder = st.empty()

    # React to user input
    if st.session_state.message_count > 10:
        st.warning(
            "You have passed your limit of 10 messages. In order to keep this service free, there is a 10 message limit per user. Please contact alexanderzhu07@gmail.com for any questions."
        )

    elif prompt := st.chat_input("Message the Scheduling Assistant"):
        st.session_state.message_count += 1

        # Display user message in chat message container
        with user_placeholder:
            st.chat_message("user").markdown(prompt)
        # Add user message to chat history
        st.session_state.display_conversation.append(
            {"role": "user", "content": prompt}
        )
        st.session_state.gpt_conversation.append({"role": "user", "content": prompt})

        # Send message to Open AI
        completion = open_ai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=st.session_state.gpt_conversation,
        )

        response = completion.choices[0].message.content

        # Parse the Open AI response into an object as needed
        response_object = json.loads(response)
        print(response_object)
        response_msg = response_object["message"]

        # Display assistant response in chat message container
        with assistant_placeholder:
            with st.chat_message("assistant"):
                # st.write_stream(response_generator(response_msg))
                st.markdown(response_msg.replace("\n", "  \n"))

        # Add assistant response to chat history
        st.session_state.display_conversation.append(
            {"role": "assistant", "content": response_msg}
        )
        st.session_state.gpt_conversation.append(
            {"role": "assistant", "content": response}
        )

        # Any actions here based on the response received


if __name__ == "__main__":
    main()
