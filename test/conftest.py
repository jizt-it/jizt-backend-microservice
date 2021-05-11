import sys
from os.path import abspath, dirname, join

paths = (
    abspath(join(dirname(dirname(__file__)), "services/summarization")),
    abspath(join(dirname(dirname(__file__)),
                 "services/summarization/text_preprocessor")),
    abspath(join(dirname(dirname(__file__)),
                 "services/summarization/t5_large_encoder")),
    abspath(join(dirname(dirname(__file__)),
                 "services/summarization/t5_large_summarizer")),
    abspath(join(dirname(dirname(__file__)),
                 "services/summarization/text_postprocessor"))
)

for p in paths:
    sys.path.insert(1, p)
