# Functions calls through the python interface are rather slow. Fortunately,
# for most symboles, we do not need to perform a function call. Their spelling
# never changes and is consequently provided by this spelling cache.
SpellingCache = {
    # 0: CompletionChunk.Kind("Optional"),
    # 1: CompletionChunk.Kind("TypedText"),
    # 2: CompletionChunk.Kind("Text"),
    # 3: CompletionChunk.Kind("Placeholder"),
    # 4: CompletionChunk.Kind("Informative"),
    # 5 : CompletionChunk.Kind("CurrentParameter"),
    6: '(',  # CompletionChunk.Kind("LeftParen"),
    7: ')',  # CompletionChunk.Kind("RightParen"),
    8: '[',  # CompletionChunk.Kind("LeftBracket"),
    9: ']',  # CompletionChunk.Kind("RightBracket"),
    10: '{',  # CompletionChunk.Kind("LeftBrace"),
    11: '}',  # CompletionChunk.Kind("RightBrace"),
    12: '<',  # CompletionChunk.Kind("LeftAngle"),
    13: '>',  # CompletionChunk.Kind("RightAngle"),
    14: ', ',  # CompletionChunk.Kind("Comma"),
    # 15: CompletionChunk.Kind("ResultType"),
    16: ':',  # CompletionChunk.Kind("Colon"),
    17: ';',  # CompletionChunk.Kind("SemiColon"),
    18: '=',  # CompletionChunk.Kind("Equal"),
    19: ' ',  # CompletionChunk.Kind("HorizontalSpace"),
    # 20: CompletionChunk.Kind("VerticalSpace")
}
