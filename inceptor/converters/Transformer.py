import base64
import os
import re
import subprocess
import sys
from abc import ABC, abstractmethod

from config.Config import Config


class Transformer(ABC):

    def __init__(self):
        super(Transformer, self).__init__()
        self.filetype = None
        self.debug = Config().get_boolean("DEBUG", "LOADERS")


    @abstractmethod
    def transform(self, target):
        pass

    def set_architecture(self, arch="x64"):
        pass

    def set_additional_arguments(self, **kwargs):
        pass
