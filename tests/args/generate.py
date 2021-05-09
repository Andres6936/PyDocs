import sys, os

lcldoc = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, lcldoc)

from cldoc import cmdgenerate

if __name__ == '__main__':
    cmdgenerate.run('-I../../example/transport -fPIC --')