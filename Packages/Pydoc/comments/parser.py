from pyparsing import *


class Parser:
    ParserElement.setDefaultWhitespaceChars(' \t\r')

    identifier = Word(alphas + '_', alphanums + '_')

    brief = restOfLine.setResultsName('brief') + lineEnd

    paramdesc = restOfLine + ZeroOrMore(lineEnd + ~('@' | lineEnd) + Regex('[^\n]+')) + lineEnd.suppress()
    param = '@' + identifier.setResultsName('name') + White() + Combine(paramdesc).setResultsName('description')

    preparams = ZeroOrMore(param.setResultsName('preparam', listAllMatches=True))
    postparams = ZeroOrMore(param.setResultsName('postparam', listAllMatches=True))

    bodyline = NotAny('@') + (lineEnd | (Regex('[^\n]+') + lineEnd))
    body = ZeroOrMore(lineEnd) + Combine(ZeroOrMore(bodyline)).setResultsName('body')

    doc = brief + preparams + body + postparams

    @staticmethod
    def parse(s):
        return Parser.doc.parseString(s)
