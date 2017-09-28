import os, sys
sys.stdout.write(repr(os.getenv('PYPKI_PKIROOT')))
sys.stdout.flush()