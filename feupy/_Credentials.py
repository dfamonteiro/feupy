import getpass as _getpass
import os as _os
import re as _re
import urllib as _urllib

import requests as _requests
import requests_futures.sessions as _sessions

from . import _internal_utils as _utils

__all__ = ["Credentials"]

class Credentials:
    """This class represents your login credentials. It also
    features a non-persistent cache that stores htmls of urls
    previously accessed.

    Properties:
        username (int) # e.g. 201806185
        session  (requests.Session object) # The session that has the login cookies
        cache    (dict) # Maps a url string to an html string

    Methods:
        get_html
        get_html_async
        download
    
    Operators:
        __repr__
    """
    __slots__ = ["username", "session", "cache"]

    def __init__(self, username : int = None, password : str = None):
        """Creates a Credentials object that can be used to access pages with priviledged access.

        Credentials(123456789, "password1") #This will obviously fail
        ValueError: The login credencials aren't valid

        For example, if you happen to be a student, you have privileged access to the course units you are taking.
        If the function doesn't receive a password and/or a username, it will ask the user for them.
        Note: username must be an int and password must a string.
        """

        #This is a modified version of the https://github.com/msramalho/sigpy login function

        AUTH_FAIL = "O conjunto utilizador/senha não é válido." # If this string appears on the HTML answer, the login creds aren't valid:(

        if username == None:
            username = int(input("Username?\n:> up"))
        if password == None:
            password = _getpass.getpass(f"Password for {username}?\n:> ")
        
        if type(username) != int: # Making sure the arguments are strings
            raise TypeError(f"login() 'username' argument must be an int, not '{type(username).__name__}'")
        if type(password) != str:
            raise TypeError(f"login() 'password' argument must be a string, not '{type(password).__name__}'")

        session = _requests.Session()
        credencials = {'p_user': username, 'p_pass': password}
        request = session.post(_utils.SIG_URLS["authentication"], params = credencials) # Sending the creds to sigarra
        if AUTH_FAIL in request.text:
            raise ValueError("The login credencials aren't valid")
        
        self.username = username
        self.session  = session
        self.cache    = {}
    
    def get_html(self, url : str, params : dict = {}):
        """Functionally equivalent to requests.get(url, params).text,
        with scripts and styles removed. The result is stored in cache.
        """
        if params != {}:
            url = url + "?" + _urllib.parse.urlencode(params, doseq = True) # Emulating the RequestsIII library
        
        if url in self.cache:
            pass
        else: # We need to get the page from the web
            request = self.session.get(url) # Getting the webpage
            request.raise_for_status()  # If the request fails, I want to know about it
            html = request.text

            self.cache[url] = _utils.trim_html(html)
        
        return self.cache[url]

    def get_html_async(self, urls, n_workers : int = 10):
        """get_html, but async, give or take.
        Takes a list (or any iterable) of urls and returns a corresponding generator of htmls.
        The htmls have their scripts and styles removed and are stored in cache.
        """

        urls = tuple(urls)

        work_queue = (url for url in urls if url not in self.cache)

        with _sessions.FuturesSession(max_workers = n_workers) as session:
            session.cookies.update(self.session.cookies) # Getting the cookies from the object session to this assynchronous session

            futures = [session.get(url) for url in work_queue]

            for future in futures:
                request = future.result()

                if request.status_code != 200:
                    continue # GTFO
                
                url  = request.url
                html = request.text

                self.cache[url] = _utils.trim_html(html)
        
        return (self.get_html(url) for url in urls)
    
    def download(self, url : str, folder_path : str) -> str:
        """Downloads the file from the given url and saves it
        to the given folder path. It returns the file path.
        If the path doesn't exist, it will be created automatically.
        Note: it only works with sigarra."""

        # https://stackoverflow.com/questions/16694907/download-large-file-in-python-with-requests
        # https://stackoverflow.com/questions/31804799/how-to-get-pdf-filename-with-python-requests

        if "conteudos_service.conteudos_cont" not in url:
            raise ValueError(f"the url argument {url} is not a valid sigarra download url")
        
        # create the cache folder if it does not exist
        if not _os.path.exists(folder_path):
            _os.makedirs(folder_path)
        
        with self.session.get(url) as r:
            r.raise_for_status()
            filename = _re.findall("filename=(.+)", r.headers['content-disposition'])[0][1:-1]
            
            path = _os.path.join(folder_path, filename)
            with open(path, 'wb') as f:
                for chunk in r.iter_content(chunk_size= 2 ** 15):
                    if chunk: # filter out keep-alive new chunks
                        f.write(chunk)
        
        return path
    
    @property
    def __dict__(self): # This is done for compatibility reasons (vars)
        return {attribute : getattr(self, attribute) for attribute in self.__slots__}
    
    def __repr__(self):
        return f"Credentials({self.username})"
