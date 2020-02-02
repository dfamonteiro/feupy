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

    Args:
        username (:obj:`int` or :obj:`str`, optional): Your username.
            You will be prompted for your username if you don't pass a username as an argument
        password (:obj:`str`, optional): Your password.
            You will be prompted for your password if you don't pass a password as an argument
        base_url (:obj:`str`, optional): The url of the faculty (in english) (defaults to "https://sigarra.up.pt/feup/en/")
    
    Attributes:
        username (int or str): Your username (e.g. 201806185)
        session  (:obj:`requests.Session`): A :obj:`requests.Session` object that holds the login cookies
        cache    (dict): A dictionary that maps a url string to an html string
        base_url (str): The url of your faculty (in english) (defaults to "https://sigarra.up.pt/feup/en/")

    Example::

        from feupy import Credentials

        username = 201806185
        password = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

        creds = Credentials(username, password)

        # You may instead enter your username and password at runtime
        creds = Credentials()
        # Username?
        # :> up201806185
        # Password for 201806185?
        # :>
    """
    __slots__ = ["username", "session", "cache", "base_url"]

    def __init__(self, username = None, password : str = None, base_url : str = "https://sigarra.up.pt/feup/en/"):
        #This is a modified version of the https://github.com/msramalho/sigpy login function

        AUTH_FAIL = "O conjunto utilizador/senha não é válido." # If this string appears on the HTML answer, the login creds aren't valid:(

        if username == None:
            username = input("Username?\n:> ")
        if password == None:
            password = _getpass.getpass(f"Password for {username}?\n:> ")
        
        session = _requests.Session()
        credencials = {'p_user': username, 'p_pass': password}
        request = session.post(base_url + _utils.SIG_URLS["authentication"], params = credencials) # Sending the creds to sigarra
        if AUTH_FAIL in request.text:
            raise ValueError("The login credencials aren't valid")
        
        self.username = username
        self.session  = session
        self.cache    = {}
        self.base_url = base_url
    
    def get_html(self, url : str, params : dict = {}) -> str:
        """Functionally equivalent to ``requests.get(url, params).text``,
        with scripts and styles removed. If the result is already in cache,
        the method will just return the value from the cache instead of
        making a web request.

        Args:
            url (str): The url of the html to be fetched
            params (:obj:`dict`, optional): the query portion of the url, should you want to include a query
        
        Returns:
            A string which is the html from the requested page url
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
        """:func:`Credentials.get_html`, but async, give or take.

        Takes a list (or any iterable) of urls and returns a corresponding generator of htmls.
        The htmls have their scripts and styles removed and are stored in cache.

        Args:
            urls (iterable(str)): The urls to be accessed
            n_workers (:obj:`int`, optional): The number of workers.
        
        Returns:
            An str generator
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
        """Downloads the file from the given url and saves it to the given folder path.
        If the path doesn't exist, it will be created automatically.
        
        Args:
            url (str): The url of the file to be downloaded
            folder_path (str): The path of the folder you want to download the file to
        
        Returns:
            The path of the file as an str

        """

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
        if self.base_url == "https://sigarra.up.pt/feup/en/":
            return f"Credentials({self.username})"
        else:
            return f"Credentials({self.username}, base_url = {self.base_url})"
