penetration testing
=====================================================================================================

dikien2012@gmail.com


First Stage:

if you crwal the site for the first time(drop the collection)

./web_crwaler.py --url="http://demo.testfire.net/" -p testfire.net -t testfire


if you want to add urls(modify the collection)

./web_crwaler.py --url="http://demo.testfire.net/" -p testfire.net -t testfire -m 1



Second Stage:

t option is collection name.

p option is payload name.

u is origin url address. The script will not attack urls not in origin url.

o is http connection timeout.

./xss.py -t testfire -p payload/xss_query -u demo.testfire.net

./sql_injection_time.py -t testfire -p payload_file -u demo.testfire.net -o 3

./sql_injection_error.py -t testfire -p payload_file -u deme.testfire.net

./lfi.py -t testfire -p payload_file -u deme.testfire.net

./crlf_injection.py -t testfire -p payload_file -u deme.testfire.net

./open_redirection.py -t testfire



Future Work:

wetkit engine, ajax, screen shot, passive scan, geolocation



Thank you:

http://math.nist.gov/~RPozo/ngraph/webcrawler.html

https://bitbucket.org/chbb/spse
