import os
from dotenv import load_dotenv 

from langchain_openai import ChatOpenAI
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.output_parsers import StrOutputParser

from .prompts import system_prompt, feedback_request_prompt
from .utils import running_from_docker_container


# Tandem Buddy Language Partner Class        
class LanguagePartner():

    def __init__(self, model_name:str ="gpt-4o-mini", system_prompt:str=system_prompt) -> None:
        """Initialize the Language Partner class.

        The constructor sets up the chat model, message history, and conversation chain.

        Args:
            model_name (str, optional): OpenAI model name. Defaults to "gpt-4o-mini".
            system_prompt (str, optional): System Prompt used as imput for the model.
             Defaults to system_prompt.

        Raises:
            ValueError: OPENAI_API_KEY not found
        """        
        if not running_from_docker_container():
            load_dotenv()
            api_key = os.getenv("OPENAI_API_KEY")
        else:
            api_key = os.environ.get("OPENAI_API_KEY")

        if not api_key:
            raise ValueError("OPENAI_API_KEY not found")
        
        self.system_prompt = system_prompt

        self.model_name = model_name
        self.chat_model = ChatOpenAI(model=self.model_name)
        self.chat_history = ChatMessageHistory()
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            MessagesPlaceholder(variable_name="history"),
            ChatPromptTemplate.from_template("{input}")
        ])

        # Create chain
        chain = prompt | self.chat_model | StrOutputParser()

        self.conversation_chain = RunnableWithMessageHistory(
            chain,
            lambda session_id: self.chat_history,
            input_messages_key="input",
            history_messages_key="history",
        )

    def get_response(self, user_input: str) -> str:
        """Get the model's response to user input.

        Args:
            user_input (str): The transcript of the user's input message.

        Returns:
            str: The model's response to the user's input in text format.
        """        
        response = self.conversation_chain.invoke(
            {"input": user_input},
            config={"configurable": {"session_id": "default"}}
        )
        return response
    
    def get_detailed_feedback(self):
        """Provide detailed feedback on the user's performance
        during the conversation.

        Returns:
            str: Detailed feedback on the conversation so far.
        """        
        return self.get_response(feedback_request_prompt)
    
    def reset_conversation(self):
        """Reset the conversation history.
        """        
        self.chat_history.clear()
        
    def _simulate_conversation(self):
        """Example method to simulate a conversation with the Language Partner.

        This method demonstrates how to interact with the LanguagePartner class
        by simulating a conversation and requesting feedback, and tests the functionality.
        """        
        tutor = LanguagePartner()

        # Simulate conversation
        print("=== Starting Conversation ===\n")
        
        response1 = tutor.get_response("Hola, ¿cómo estás?")
        print("Student: Hola, ¿cómo estás?\n")
        print(f"Tutor: {response1}\n")
        
        response2 = tutor.get_response("Yo es estudiante y me gusta mucho aprender español")
        print("Yo es estudiante y me gusta mucho aprender español\n")
        print(f"Tutor: {response2}\n")
        
        response3 = tutor.get_response("Ayer yo fui al parque con mis amigos")
        print("Ayer yo fui al parque con mis amigos\n")
        print(f"Tutor: {response3}\n")
        
        # Get detailed feedback
        print("\n=== Requesting Detailed Feedback ===\n")
        feedback = tutor.get_detailed_feedback()
        print(feedback)
        
    
# if __name__ == "__main__":
#     practice = LanguagePartner()
#     practice._simulate_conversation()