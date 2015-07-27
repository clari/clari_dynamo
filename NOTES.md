Summary: Can get about 1,000 requests per second on single node when response 
less than 15ms, and 75 requests per second when response takes 2 seconds. 

Able to get the following performance with these settings on 2014 MacbookPro
    'server.socket_host':       '0.0.0.0',
    'server.socket_port':       55555,
    'server.thread_pool':       300,
    'server.socket_queue_size': 200,
    'server.socket_timeout':    20,
    
➜  ~  ab -k -c 150 -n 600 http://0.0.0.0:55555/sleep/2000
This is ApacheBench, Version 2.3 <$Revision: 1554214 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking 0.0.0.0 (be patient)
Completed 100 requests
Completed 200 requests
Completed 300 requests
Completed 400 requests
Completed 500 requests
Completed 600 requests
Finished 600 requests


Server Software:        CherryPy/3.6.0
Server Hostname:        0.0.0.0
Server Port:            55555

Document Path:          /sleep/2000
Document Length:        12 bytes

Concurrency Level:      150
Time taken for tests:   8.144 seconds
Complete requests:      600
Failed requests:        0
Keep-Alive requests:    600
Total transferred:      105000 bytes
HTML transferred:       7200 bytes
Requests per second:    73.67 [#/sec] (mean)
Time per request:       2035.983 [ms] (mean)
Time per request:       13.573 [ms] (mean, across all concurrent requests)
Transfer rate:          12.59 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    1   1.9      0       7
Processing:  2003 2021  26.4   2008    2102
Waiting:     2002 2021  26.4   2008    2102
Total:       2003 2022  27.5   2008    2103

Percentage of the requests served within a certain time (ms)
  50%   2008
  66%   2013
  75%   2021
  80%   2037
  90%   2075
  95%   2090
  98%   2098
  99%   2101
 100%   2103 (longest request)
  
 
cherrypy.config.update({
    'server.socket_host':       '0.0.0.0',
    'server.socket_port':       int(os.environ.get('PORT', '55555')),
    'server.thread_pool':       150,  # Number of parallel requests
    'server.socket_queue_size': 200,  # Number of requests that can wait for thread
    'server.socket_timeout':    20,
})  
 
~  ab -k -c 150 -n 600 http://0.0.0.0:55555/sleep/2000
This is ApacheBench, Version 2.3 <$Revision: 1554214 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking 0.0.0.0 (be patient)
Completed 100 requests
Completed 200 requests
Completed 300 requests
Completed 400 requests
Completed 500 requests
Completed 600 requests
Finished 600 requests


Server Software:        CherryPy/3.6.0
Server Hostname:        0.0.0.0
Server Port:            55555

Document Path:          /sleep/2000
Document Length:        12 bytes

Concurrency Level:      150
Time taken for tests:   8.200 seconds
Complete requests:      600
Failed requests:        0
Keep-Alive requests:    600
Total transferred:      105000 bytes
HTML transferred:       7200 bytes
Requests per second:    73.17 [#/sec] (mean)
Time per request:       2049.925 [ms] (mean)
Time per request:       13.666 [ms] (mean, across all concurrent requests)
Transfer rate:          12.51 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    1   1.9      0       6
Processing:  2001 2026  37.1   2008    2160
Waiting:     2001 2026  37.1   2008    2160
Total:       2001 2027  38.1   2008    2162

Percentage of the requests served within a certain time (ms)
  50%   2008
  66%   2016
  75%   2027
  80%   2036
  90%   2091
  95%   2135
  98%   2144
  99%   2159
 100%   2162 (longest request) 
 
 
 ➜  ~  ab -k -c 150 -n 600 http://0.0.0.0:55555/sleep/1
This is ApacheBench, Version 2.3 <$Revision: 1554214 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking 0.0.0.0 (be patient)
Completed 100 requests
Completed 200 requests
Completed 300 requests
Completed 400 requests
Completed 500 requests
Completed 600 requests
Finished 600 requests


Server Software:        CherryPy/3.6.0
Server Hostname:        0.0.0.0
Server Port:            55555

Document Path:          /sleep/1
Document Length:        1090 bytes

Concurrency Level:      150
Time taken for tests:   0.571 seconds
Complete requests:      600
Failed requests:        0
Non-2xx responses:      600
Keep-Alive requests:    600
Total transferred:      789000 bytes
HTML transferred:       654000 bytes
Requests per second:    1051.59 [#/sec] (mean)
Time per request:       142.641 [ms] (mean)
Time per request:       0.951 [ms] (mean, across all concurrent requests)
Transfer rate:          1350.44 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    1   2.6      0       9
Processing:    40  135  51.9    133     313
Waiting:       40  135  51.9    132     313
Total:         45  137  52.4    133     315

Percentage of the requests served within a certain time (ms)
  50%    133
  66%    137
  75%    140
  80%    141
  90%    215
  95%    269
  98%    297
  99%    306
 100%    315 (longest request)