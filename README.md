GitHub Stars
============

This is the Python script to fetch metadata for the most top-rated repositories
on GitHub. "rated" here means "having most stargazers". This project (successfully)
deals with multiple quirks of working with GitHub API:

1. 30/minute, 5000/hour ratelimit in general
2. 1000 results limit in Search
3. Random network errors

As of Nov. 12, 2016, all repos with >= 50 stars can be collected.

Setup
-----
[PyGitHub](https://github.com/PyGithub/PyGithub) must be installed:
```
pip3 install -r requirements.txt
```
Besides, you must get the token to access GitHub API at full limit
(Settings -> Personal access tokens).

Usage
-----
```
python3 github_stars.py -i abcdefabcdefabcdefabcdefabcdefabcdefabcd -o repos.pickle
```
See `--help` for optional arguments. You can change "pickle" to "json".

How it works
------------
There are two stages. On the first stage, we plan how we will fetch data from
Search API. With the "updated" dual-order hack, we can suck 2000 results from
a single query. So we probe star intervals which yield less than 2000, e.g.
50..50, 90..91 or 356..371. The second stage is doing actual massive API requests.

License
-------
MIT.