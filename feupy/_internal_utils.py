import io
import re
from datetime import datetime, time
from functools import reduce

import bs4
import requests
from bs4 import BeautifulSoup
from lxml.html.clean import Cleaner
from PIL import Image

SIG_URLS = {
    "authentication"                      : "vld_validacao.validacao",
    "student page"                        : "fest_geral.cursos_list",
    "academic pathway"                    : "fest_geral.curso_percurso_academico_view",
    "position in the plan"                : "fest_geral.curso_posicao_plano_view",
    "courses units"                       : "fest_geral.ucurr_inscricoes_list",
    "status and more"                     : "fest_geral.estatutos_regimes_view",
    "ingress data"                        : "fest_geral.info_ingresso_view",
    "classes data"                        : "it_geral.resultado_aluno",
    "personal timetable"                  : "hor_geral.estudantes_view",
    "picture"                             : "fotografias_service.foto",
    "curricular unit"                     : "ucurr_geral.ficha_uc_view",
    "curricular unit students"            : "fest_geral.estudantes_inscritos_list",
    "curricular unit other occurrences"   : "ucurr_geral.ficha_uc_list",
    "curricular unit statistics"          : "est_geral.dist_result_ocorr",
    "curricular unit grades distribution" : "est_geral.dist_result_ocorr_detail",
    "curricular unit stats history"       : "est_geral.ucurr_result_resumo",
    "curricular unit classes"             : "it_listagem.lista_cursos_disciplina",
    "curricular unit results"             : "lres_geral.show_pautas_resul",
    "curricular unit timetable"           : "hor_geral.ucurr_view",
    "curricular unit exams"               : "exa_geral.mapa_de_exames",
    "teacher"                             : "func_geral.formview",
    "course"                              : "cur_geral.cur_view",
    "course classes"                      : "hor_geral.lista_turmas_curso",
    "course exams"                        : "exa_geral.mapa_de_exames",
    "redirection page"                    : "vld_entidades_geral.entidade_pagina"
}


def get_current_academic_year():
    today = datetime.now()
    if today.month >= 9:# 9 -> September
        return today.year
    else:
        return today.year - 1

def scrape_html_table(bs_table, f = lambda tags_list, index : list( map(lambda tag: tag.string, tags_list) )):
    """
    Returns a nested list based on the contents of the table

    html = \"\"\"<table class="formulario">
        <tr>
            <td class="very important stuff">Hotel</td>
            <td>Trivago</td>
        </tr>
        <tr>
            <td class="the class name doesn't matter">A</td>
            <td>B</td>
            <td>C</td>
        </tr>
    </table>\"\"\"
    table_soup = BeautifulSoup(html, 'lxml').table #if it's not a table, you'll get a TypeError
    print(scrape_html_table(table_soup))
    #[['Hotel', 'Trivago'], ['A', 'B', 'C']]

    There is an optional second argument that lets you define a function that operates over each row of the table(tags_list),
    which is internally represented as a list of BeautifulSoup "th" and "td" tags. The second argument of the funtion 
    is an integer that represents the index of the table row (starts at 0)

    #ex1: do nothing
    print(scrape_html_table(table_soup, lambda tags_list, index : tags_list))
    #[[<td class="very important stuff">Hotel</td>, <td>Trivago</td>], [<td class="the class name doesn't matter">A</td>, <td>B</td>, <td>C</td>]]

    #ex2: make a list of the first column of the table
    print(scrape_html_table(table_soup, lambda tags_list, index : tags_list[0].string))
    #['Hotel', 'A']

    #ex3: make a list of the tags' names
    print(scrape_html_table(table_soup, lambda tags_list, index : list(map(lambda tag : tag.name, tags_list))))
    #[['td', 'td'], ['td', 'td', 'td']]

    Don't forget that you can use the capabilities of the BeautifulSoup library to do whatever you want with these tag objects
    """
    if type(bs_table) != bs4.element.Tag:
        raise TypeError("scrape_html_table() 'bs_table' argument must be a bs4.element.Tag, not '{0}'".format( type(bs_table).__name__ ))

    if type(f).__name__ != "function": # Look, it works:/
        raise TypeError("scrape_html_table() 'f' argument must be a function, not '{0}'".format( type(f).__name__ ))
    
    if bs_table.name != "table" and bs_table.name != "thead" and bs_table.name != "tbody":
        raise ValueError("The tag element must be a table, not '{0}'".format(bs_table.name))

    result = []
    for index, tr in enumerate(bs_table.find_all("tr", recursive = False)):  # split the table into table rows
        tags = tr.find_all(["th", "td"], recursive = False)                  # split the table row into table header and data tags
        result.append(f(tags, index))                                        # apply f to the tags list and append to result
    
    return result

def trim_html(html):
    """Takes a html string as input and returns the html without any styles nor javascript"""
    cleaner = Cleaner()

    cleaner.scripts         = True
    cleaner.javascript      = True  # Get rid of the javascript and the style
    cleaner.style           = True

    cleaner.meta            = False # Keeping the meta tags is important for page redirection purposes
    cleaner.safe_attrs_only = False

    return cleaner.clean_html(html)

def parse_academic_year(html):
    """Searches the html for r"(\\d\\d\\d\\d)/\\d\\d\\d\\d" and returns the
    first occurrence as an int. If no match is found, it will raise
    a AttributeError exception
    Eg: parse_academic_year("2018/2019 2020/2021") -> 2018
    """
    html = str(html) # must be a string (bs4 objects also work)

    academic_year = int(re.findall(r"(\d\d\d\d)/\d\d\d\d", html)[0])
    return academic_year

def get_image(url, params = None):
    """Fetches the image from the url and returns it as a PIL.Image object.
    If you need to be logged in to access the image you may want to check
    out the Credentials get_image function"""
    request = requests.get(url, params)
    image = Image.open(io.BytesIO(request.content))

    return image

