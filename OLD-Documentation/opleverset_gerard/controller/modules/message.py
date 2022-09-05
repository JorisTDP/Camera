#!python3.9
from typing import List

try:
   import cPickle as pickle
except ModuleNotFoundError:
   import pickle


class Message():
    """
    Message class for communication and event management

    ...

    Attributes
    ----------
    name : str
        the name of the message, default = "status"
    args : List[str]
        the arguments of the message, default = []

    Methods
    -------
    from_bytes(bytes)
        Decodes an encoded message object back into it's original state

    encode()
        Turns the message object into ascii encoded bytes to be sent over a 
        socket connection
    """

    def __init__(self, name: str, args: List) -> None:
        """
        Parameters
        ----------
        name : str
            The name of the message
        args : List[str], optional
            The arguments of the message
        """

        # Prevent Messages from not having names so we don't need useless error
        # handling in other classes.
        if name == None: raise ValueError("name argument can not be None.")

        self.name = name

        # An empty list should be created to avoid errors later if no arguements
        # are passed in this message.
        if args == None: self.args = []
        else: self.args = args

    @classmethod
    def from_bytes(cls, bytes: str):
        return pickle.loads(bytes)

    def encode(self) -> bytes:
        return pickle.dumps(self)

    def __str__(self) -> str:
        """Turns message object into one string. name and args are seperated
        with ';', args are seperated with ','
        ...
        Returns
        -------
        str
            Message in string form as per communication protocol
        """
        # Convert all arguments into strings
        arg_strings = [str(arg) for arg in self.args]

        args_string = ""

        if len(self.args) > 0: args_string = ",".join(arg_strings)

        return f"{self.name};{args_string}"

    def __eq__(self, other) -> bool:
        return (self.name == other.name and self.args == other.args)
    

    