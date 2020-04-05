from feupy import Credentials, cache
from pathlib import Path

from .FeupyTestCase import FeupyTestCase

print("In order to test methods that require "
      "priviledged access to sigarra, i.e. student access, "
      "a valid set set of credentials is required")

while True:
    try:
        creds = Credentials()
        break
    except ValueError:
        print("Invalid credentials, please try again")

# We need an empty cache
cache.cache = {}
