from argparse import ArgumentParser
from urllib.request import urlretrieve
import sys
import os
import re

parser = ArgumentParser()
parser.add_argument("-g", "--gpu", action="store_true", dest="gpuonly",
                    default=False, help="only write gpu info to the header file")
parser.add_argument("-o", "--out", dest="path", default="pcil.h",
                    help="Path to output the header file", metavar="PATH")
parser.add_argument("-q", "--quiet", action="store_true", dest="quiet",
                    default=False, help="don't print status messages to stdout")
parser.add_argument("-u", "--url", dest="url",
                    help="URL to request the ids database from", metavar="URL")
args = parser.parse_args()


def reporthook(blocknum, blocksize, totalsize):
    readsofar = blocknum * blocksize
    if totalsize > 0:
        percent = readsofar * 1e2 / totalsize
        s = "\r%5.1f%% %*d / %d" % (
            percent, len(str(totalsize)), readsofar, totalsize)
        sys.stderr.write(s)
        if readsofar >= totalsize: # near the end
            sys.stderr.write("\n")
    else:  # total size is unknown
        sys.stderr.write("read %d\n" % (readsofar,))


if __name__ == '__main__':
    path = os.path.join(os.path.dirname(__file__), args.path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if args.url:
        if args.quiet:
            urlretrieve(args.url, 'pci.ids')
        else:
            print("Downloading id database from " + args.url)
            urlretrieve(args.url, 'pci.ids', reporthook)
            print("Download complete")
    with open(path, "w", encoding="utf8") as headerfile:
        headerfile.write("""#ifndef PCIL_H
#define PCIL_H
#include <map>

namespace pcil
{
    typedef std::map<uint32_t, const char*> table;
    
    static table create_map()
    {
        table m;
""")
        with open(os.path.join(os.path.dirname(__file__), "pci.ids"), "r", encoding="utf8") as pcifile:
            i = 0
            for line in pcifile:
                if line.startswith("#") or line.isspace():
                    continue
                vendorId = int("03E8", 16)
                deviceId = i
                key = ((vendorId << 16) | deviceId)
                headerfile.write("        m[{key}] = \"{name}\";\n".format(key=key, name=line.strip().replace("\\", "\\\\").replace("\"", "\\\"")))
                i += 1
        headerfile.write("""        return m;
    }
    
    static const table names = create_map();
    
    inline const char* lookup(uint16_t vendorId, uint16_t deviceId)
    {
        uint32_t key = ((vendorId << 16) | (deviceId));

        if(names.count(key))
        {
            return names.at(key);
        }
        else
        {
            return "Unrecognized device";
        }
    }
}
#endif // PCIL_H
""")
    if not args.quiet:
        print("The header file is located at " + path)
