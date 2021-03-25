import sys
from os.path import abspath, dirname, join

paths = (
    abspath(join(dirname(dirname(__file__)), "services")),
    abspath(join(dirname(dirname(__file__)),
                 "services/text_preprocessor")),
    abspath(join(dirname(dirname(__file__)),
                 "services/t5_large_encoder")),
    abspath(join(dirname(dirname(__file__)),
                 "services/t5_large_summarizer")),
    abspath(join(dirname(dirname(__file__)),
                 "services/text_postprocessor"))
)

for p in paths:
    sys.path.insert(1, p)