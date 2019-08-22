"""Functions:
    load_cache
    get_html
    reset
    remove_invalid_entries
    get_html_async
"""
import atexit as _atexit
import datetime as _datetime
import os as _os
import random as _random
import re as _re
import shelve as _shelve
import time as _time
import urllib as _urllib

import bs4 as _bs4
import requests as _requests
import requests_futures.sessions as _sessions

from . import _internal_utils as _utils

__all__ = ["load_cache", "get_html", "reset", "remove_invalid_entries", "get_html_async"]

cache = None # This will eventually be the cache object
# The cache is a dictionary-like object whose values are structured in the following way:
# {
#     url0 : (timeout0, html0),
#     url1 : (timeout1, html1),
#     ...
# }
# In which url is a string, timeout is an int or a float (which represents the "due by date" as seconds since epoch), and html is a string
#
# When get_html is called, if the url is not in the cache keys (or the key is present but the cache entry is outdated),
# get_html will first check if the url matches any key in custom_treatments (it matches if key(url) returns True).
# If so the cache will call custom_treatments[key](html), instead of default_treatment(html)
#
# This behaviour was implemented so that commonly accessed pages (curricular units, students, teachers)
# can have their htmls even more shrinked than usual (by returning a timeout and the div with the useful information)

_custom_treatments = {}


############################### Custom treatments ################################

def _is_curricular_unit(url):
    return "ucurr_geral.ficha_uc_view" in url 

def _is_teacher(url):
    return "func_geral.formview" in url

def _is_student(url):
    return "fest_geral.cursos_list" in url

def _trim_curricular_unit(html):
    """Returns a heavily trimmed version of the curricular unit html"""
    html = _utils.trim_html(html)

    soup = _bs4.BeautifulSoup(html, "lxml")

    useful_stuff = soup.find("div", {"id" : "envolvente"})

    useful_stuff.find("div", {"id" : "colunaprincipal"}).decompose() # Remove the left side-bar

    return str(useful_stuff)

def _trim_teacher(html):
    """Returns a heavily trimmed version of the teacher html"""
    html = _utils.trim_html(html)

    soup = _bs4.BeautifulSoup(html, "lxml")

    useful_stuff = soup.find("div", {"id" : "conteudo"})

    return str(useful_stuff)

def _trim_student(html):
    """Returns a heavily trimmed version of the student html"""
    html = _utils.trim_html(html)

    soup = _bs4.BeautifulSoup(html, "lxml")

    useful_stuff = soup.find("div", {"id" : "conteudo-extra"})

    return str(useful_stuff)

def _curricular_unit_treatment(html):
    uc_academic_year = _utils.parse_academic_year(html)

    if uc_academic_year < _utils.get_current_academic_year():
        timeout = _time.time() + _random_radioactive_lifetime(_datetime.timedelta(days = 6*30)) # It is extremely unlikely that a uc page from a previous year will ever change
        return (timeout, _trim_curricular_unit(html))
    else:
        timeout = _time.time() + _random_radioactive_lifetime(_datetime.timedelta(days = 30))
        return (timeout, _trim_curricular_unit(html))

def _teacher_treatment(html):
    timeout = _time.time() + _random_radioactive_lifetime(_datetime.timedelta(days = 2*30))
    return (timeout, _trim_teacher(html))

def _student_treatment(html):
    year  = _utils.get_current_academic_year() + 1
    timeout = _datetime.datetime(year, 9, 20).timestamp() # Only update at the beginning of the next academic year
    return (timeout, _trim_student(html))

############################ End of custom treatments ############################

_custom_treatments = {
    _is_curricular_unit : _curricular_unit_treatment,
    _is_teacher         : _teacher_treatment,
    _is_student         : _student_treatment
}

def load_cache(flag = "c", path = None):
    """Loads the cache from disk and stores it in the variable cache. 
    If the variable cache is different than None, the function will do nothing.

    Refer to this to know what the flag parameter does:
    https://docs.python.org/3/library/dbm.html#dbm.open

    If you wish to save the cache to a folder of your chooosing, 
    set path to an existing directory path.
    """
    global cache

    if cache != None: # There is something already in cache
        return
    
    if path == None:
        path = _os.path.dirname(__file__)
    
    cache = _shelve.open(_os.path.join(path, "cache"), flag = flag)
    
    _atexit.register(cache.close) # This function will be called at program termination, in order to make sure that the cache is saved to disk
    # the cache object itself would most likely save itself on exit, but better be safe than sorry

def _random_radioactive_lifetime(half_life = _datetime.timedelta(days=2), cutoff = True):
    """Returns a randomly generated lifetime of a radioactive particle with a half-life of half_life seconds
    (a time_delta is also acceptable).
    If cutoff is True (which is by default), if the lifetime generated is bigger than half_life * 4, the function
    will instead return half_life * 4, which is useful if you wish to avoid ridiculously large lifetimes
    This function is used to disperse the timeouts of the cache values.
    """
    if isinstance(half_life, _datetime.timedelta):
        half_life = half_life.total_seconds()

    lambd = 0.693147 / half_life # ln(2)/half-life
    lifetime = _random.expovariate(lambd)

    return min(lifetime, half_life * 4) if cutoff else lifetime

def _default_treatment(html):
    """The default treatment for any url that doesn't match any key in custom_treatments.
    Returns a tuple made of a timeout provided by random_radioactive_lifetime and the html
    without any scripts nor styles, to save space"""

    return (_time.time() + _random_radioactive_lifetime(), _utils.trim_html(html))

def _cache_entry_is_valid(key):
    """Returns True if the cache entry is valid, otherwise returns false"""
    global cache
    return cache[key][0] > _time.time()

def get_html(url, params = {}, use_cache = True):
    """More or less functionally equivalent to requests.get(url, params).text, with the added
    benefit of a persistent cache with customizable html treatment and timeouts, depending on the url.
    
    The curricular units' pages, along with the students' and teachers' pages,
    are modified to reduce their memory footprint. The default treatment removes scripts
    and styles from the html to also reduce their size. If you wish to bypass the cache, set
    use_cache to False, (please note that the html modifications will still be made either way).

    Helpful note: if you know that you are going to make a crapton of requests beforehand, you probably
    should call get_html_async first to populate the cache.
    """
    global cache

    if cache == None:
        load_cache()
    
    if params != {}:
        url = url + "?" + _urllib.parse.urlencode(params, doseq = True) # Emulating the RequestsIII library
    
    if url in cache and _cache_entry_is_valid(url) and use_cache:
        pass
    else: # We need to get the page from the web
        request = _requests.get(url) # Getting the webpage
        request.raise_for_status()  # If the request fails, I want to know about it
        html = request.text

        for match_rule, custom_treatment in _custom_treatments.items(): # Can we apply any custom treatment to the html?
            if match_rule(url):
                cache[url] = custom_treatment(html)
                break
        else:                                                         # If not, use the default treatment
            cache[url] = _default_treatment(html)
    
    return cache[url][1]

def reset():
    """Eliminates all entries from this cache implementation"""
    global cache

    if cache == None:
        load_cache()

    cache.clear()

def remove_invalid_entries(urls = None):
    """Removes all the cache entries in urls that have timed out"""
    global cache

    if cache == None:
        load_cache()

    if urls == None:
        urls = cache.keys()
    
    hit_list = set() # Each element must be unique, otherwise it will be popped twice

    for url in urls:
        if url in cache and not _cache_entry_is_valid(url):
            hit_list.add(url)
    
    for url in hit_list:
        cache.pop(url)

def get_html_async(urls, n_workers = 10, use_cache = True):
    """get_html, but async, give or take.
    Takes a list (or any iterable) of urls and returns a corresponding generator of htmls.
    The htmls have their scripts and styles removed and are stored in cache.
    """
    global cache

    if cache == None:
        load_cache()

    urls = tuple(urls)

    remove_invalid_entries(urls)

    work_queue = (url for url in urls if url not in cache or not use_cache)

    with _sessions.FuturesSession(max_workers = n_workers) as session:
        
        futures = [session.get(url) for url in work_queue]

        for future in futures:
            request = future.result()

            if request.status_code != 200:
                continue # GTFO
            
            url  = request.url
            html = request.text

            for match_rule, custom_treatment in _custom_treatments.items(): # Can we apply any custom treatment to the html?
                if match_rule(url):
                    cache[url] = custom_treatment(html)
                    break
            else:                                                         # If not, use the default treatment
                cache[url] = _default_treatment(html)
    
    return (get_html(url) for url in urls)
