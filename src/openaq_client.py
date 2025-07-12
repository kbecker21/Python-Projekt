import pandas as pd
import numpy as np

from openaq import OpenAQ
from dotenv import load_dotenv

class OpenAQClient:

    def __init__(self):
        """
        Initialisiert den OpenAQ-Client.
        """
        load_dotenv()
        self.client = OpenAQ()

    def get_countries(self):
        resp = self.client.countries.list()
        return pd.DataFrame(resp.results)
   
    def get_parameters(self):
        resp = self.client.parameters.list()
        return pd.DataFrame(resp.results)



    def close(self):
        """
        Schließt den API-Client.
        """
        self.client.close()
