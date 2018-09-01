# MIT License
#
# Copyright (c) 2018 ProWolf
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# pcil v1.0.0 by ProWolf
# https://github.com/prowolf/pcil

from argparse import ArgumentParser
from urllib.request import urlretrieve
import sys
import os

parser = ArgumentParser()
parser.add_argument("-i", "--in", dest="pci_path", default="pci.ids",
                    help="path to output the header file", metavar="PATH")
parser.add_argument("-o", "--out", dest="header_path", default="pcil.h",
                    help="path to output the header file", metavar="PATH")
parser.add_argument("-q", "--quiet", action="store_true", dest="quiet",
                    default=False, help="don't print status messages to stdout")
parser.add_argument("-u", "--url", dest="url",
                    help="URL to request the ids database from", metavar="URL")
args = parser.parse_args()

vendors = list()


def reporthook(block_number, block_size, total_size):
    read_so_far = block_number * block_size
    if total_size > 0:
        percent = read_so_far * 1e2 / total_size
        s = "\r%5.1f%% %*d / %d" % (
            percent, len(str(total_size)), read_so_far, total_size)
        sys.stderr.write(s)
        if read_so_far >= total_size:
            sys.stderr.write("\n")
    else:
        sys.stderr.write("read %d\n" % (read_so_far,))


if __name__ == '__main__':
    pci_path = os.path.join(os.path.dirname(__file__), args.pci_path)
    os.makedirs(os.path.dirname(pci_path), exist_ok=True)
    header_path = os.path.join(os.path.dirname(__file__), args.header_path)
    os.makedirs(os.path.dirname(header_path), exist_ok=True)
    if args.url:
        if args.quiet:
            urlretrieve(args.url, pci_path)
        else:
            print("Downloading id database from " + args.url)
            urlretrieve(args.url, pci_path, reporthook)
            print("Download complete")
            print("The ids database is located at " + pci_path.replace("\\", "/"))
    with open(header_path, "w", encoding="utf8") as header_file:
        header_file.write("""// MIT License
//
// Copyright (c) 2018 ProWolf
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in all
// copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
// SOFTWARE.
//
// This file was generated with a script.
// This header was generated with pcil v1.0.0 by ProWolf
// https://github.com/prowolf/pcil

#ifndef PCIL_H
#define PCIL_H

namespace pcil
{
    inline const char* deviceLookup(uint16_t vendorId, uint16_t deviceId)
    {
        uint32_t key = ((vendorId << 16) | (deviceId));
        switch(key)
        {
""")
        with open(os.path.join(os.path.dirname(__file__), pci_path), "r", encoding="utf8") as pci_file:
            vendorId = 0
            for line in pci_file:
                if not line.startswith("#") and not line.isspace() and not line.startswith("C "):
                    s = line.split("  ")
                    if len(line) - len(line.lstrip('\t')) == 0:
                        vendorId = int(s[0], 16)
                        vendors.append([vendorId, s[1]])
                    elif len(line) - len(line.lstrip('\t')) == 1:
                        deviceId = int(s[0], 16)
                        key = ((vendorId << 16) | deviceId)
                        header_file.write("            case {key}: return \"{name}\";\n".format(key=key, name=s[1].strip().replace("\\", "\\\\").replace("\"", "\\\"")))
                elif line.startswith("C "):
                    break
        header_file.write("""            default: return "Unrecognized Device";
        }
    }
    
    inline const char* vendorLookup(uint16_t vendorId)
    {
        switch(vendorId)
        {
""")
        for vendor in vendors:
            header_file.write("            case {key}: return \"{name}\";\n".format(key=vendor[0], name=vendor[1].strip().replace("\\", "\\\\").replace("\"", "\\\"")))
        header_file.write("""            default: return "Unrecognized Vendor";
        }
    }
}

#endif // PCIL_H
""")
    if not args.quiet:
        print("The header file is located at " + header_path.replace("\\", "/"))
