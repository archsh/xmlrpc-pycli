#!/usr/bin/env python
import xmlrpclib
import os
import sys
import re

__VERSION__ = '0.9.0'

def params_parser(pl):
    brackets0 = ('[','(','{')
    brackets1 = (']',')','}')
    quotes = ('"',"'")
    if not pl or len(pl.strip())<1:
        return None
    params = list()
    heap = list()
    i=0
    n=0
    while i<len(pl):
        if pl[i] in brackets0:
            if (not heap) or (heap[-1] not in quotes):
                heap.append(pl[i])
        elif pl[i] in brackets1 and heap and heap[-1] in brackets0:
            if brackets1.index(pl[i]) == brackets0.index(heap[-1]):
                heap.pop()
        elif pl[i] in quotes:
            if (not heap) or (heap[-1] not in quotes):
                heap.append(pl[i])
            elif pl[i] == heap[-1]:
                heap.pop()
        if ',' == pl[i] and not heap:
            params.append(pl[n:i])
            n=i+1
        i+=1
        #if heap: print 'Heap: %s' % heap
    if i>n:
        params.append(pl[n:i])
    #print params
    return params

class XMLRPC_Caller(object):
    __version__ = '0.9.0'
    def __init__(self,rpcurl):
        self._xmlrpcURL = rpcurl
        self._xmlrpcHandle = xmlrpclib.ServerProxy(rpcurl)
        self._patten1 = re.compile(r'^([a-zA-z0-9_.]+)\((.*)\)$')
        self._patten2 = re.compile(r'^([a-zA-z0-9_.]+)=(\S+)$')
    
    def process(self,commandline):
        m = self._patten1.match(commandline)
        if not m:
            print ' # < %s > is not a valid call.' % commandline
            return None
        method = m.group(1)
        paramline = m.group(2)
        #print 'method = %s' % method
        #print 'paramline = %s' % (paramline if paramline else 'NULL')
        if not paramline:
            params = None
        else:
            params = list()
            paramstrings = params_parser(paramline)
            for s in paramstrings:
                try:
                    params.append(eval(s))
                except Exception,e:
                    print '# < %s > is not a valid argument.' % s
                    return None
        try:
            if(params):
                result = getattr(self._xmlrpcHandle,method)(*params)
            else:
                result = getattr(self._xmlrpcHandle,method)()
        except xmlrpclib.Fault, f:
            print ' # Failure: %s' % f
            return None
        return result

    @classmethod
    def version(self):
        return self.__version__

def usage(scriptname):
    print '''
    Usage:
        %s XMLRPC-URL
        for example: %s http://localhost/bugzilla/xmlrpc.cgi
''' % (scriptname, scriptname)

if __name__ == '__main__':
    print " XML-RPC Caller (for DEBUG) v%s" % __VERSION__
    if len(sys.argv) < 2:
        rpcurl = raw_input(' Please enter the URL of XML-RPC:> ')
    else:
        rpcurl = sys.argv[1]
    caller = XMLRPC_Caller(rpcurl)
    
    print ' XML-RPC Caller(v%s) initialized with %s.' % (XMLRPC_Caller.version(),rpcurl)
    print " Please enter the remote method or type 'exit' or 'quit' to finish."
    print " For example:> Bug.get(ids=[1,2])\n"
    while True:
        cmd = raw_input('> ').strip()
        if len(cmd) <= 0:
            continue
        if cmd == 'exit' or cmd == 'quit':
            break
        else:
            #result=params_parser(cmd)
            result = caller.process(cmd)
            print 'Result:\n'+'-'*120
            print result
            print '-'*120+'\n'
    print '\n------\nGood Bye!'
