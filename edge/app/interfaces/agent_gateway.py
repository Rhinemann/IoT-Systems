from abc import ABC, abstractmethod


class AgentGateway(ABC):
    """
    Abstract class representing the Agent Gateway interface.
    All agent gateway adapters must implement these methods.
    """

    @abstractmethod
    def on_message(self, client, userdata, msg):
        """
        Method to handle incoming messages from the agent.
        Parameters:
            client: MQTT client instance.
            userdata: Any additional user data passed to the MQTT client.
            msg: The MQTT message received from the agent.
        """
        pass

    @abstractmethod
    def connect(self):
        """
        Method to establish a connection to the agent.
        """
        pass

    @abstractmethod
    def loop_forever(self):
        """
        Method to await for new messages.
        """
        pass
