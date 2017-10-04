 # -*- coding: utf-8 -*-.
'''
Beause RFC 1738 (specifications for URLs) poses a problem: it limits the use of allowed characters in URLs to 
only a subset of ASCII character set (7 bit):
    0-9A-Za-z
    $-_.+!*(),
    reserved characters (ex. $ + , / : ; = ? @ ...)

may be used unencoded within URLs.

However reserved characters , alought can be used unencoded, these unencoded characters can only be used by URL special syntax purposes.
To use these characters as your personal data usage, you must avoid using them or there will be conflict, or they may be mis-translated as
URL syntax characters. So you have to encode these reserved characters.

So in general, which characters must be encoded in URLs? 
ASCII control characters, Non-ASCII characters (by unicode encoding), Reserved characters


'''

import urllib


a = "http://abc.com?x=John Carner&y='AAA\"BBB+CCC%DDD"

x = urllib.quote(a)
print "encode of {} is {}".format(a,x)

print "decode of {} is {}".format(x, urllib.unquote(x))
