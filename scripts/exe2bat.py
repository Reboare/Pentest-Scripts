# Useful for Converting a file to a series of batch commands
# Currently uses certutil for decoding but there are other options
import sys
import base64

def read_file(filename):
    b64data = None
    with open(filename, 'rb') as ret:
        data = ret.read()
        b64data = (data.encode('hex').upper())

    return b64data

def chunk_array(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]

if len(sys.argv) != 3:
    print 'exe2bat.py inputfile outputfile'

inputf = sys.argv[1]
outputf = sys.argv[2]

data = read_file(inputf)
chunked = chunk_array(data, 1200)

for cmd in chunked:
    print 'echo {0} >> {1}.base64'.format(cmd, outputf)
    print 'dir {0}.base64'.format(outputf)
print 'certutil -decodehex {0}.base64 {0}'.format(outputf)
