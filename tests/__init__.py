# This is just to keep python2 docker image happy. For some reason without
# this it fails with the following error:
# AttributeError: 'module' object has no attribute 'tests'
import tests
