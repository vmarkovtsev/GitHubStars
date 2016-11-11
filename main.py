import argparse
import pickle
import sys
from time import sleep

from github import Github as GitHub, RateLimitExceededException


class GitHubStars(object):
    QUERY_LIMIT = 1000

    def __init__(self, login_or_token, password=None, **kwargs):
        self._start_index = kwargs.pop("start", 50)
        kwargs.setdefault("per_page", 100)
        self._api = GitHub(login_or_token, password=password, **kwargs)

    @property
    def start_index(self):
        return self._start_index

    @start_index.setter
    def start_index(self, value):
        assert value > 0
        self._start_index = value

    def make_plan(self):
        start = self._start_index
        offset = 0
        m = 1
        plan = []
        per_page = self._api.per_page
        self._api.per_page = 1
        while True:
            try:
                length = self._api.search_repositories(
                    "stars:%d..%d" % (start, start + offset)).totalCount
            except RateLimitExceededException:
                print("Hit rate limit, sleeping 60 seconds...")
                sleep(60)
                continue
            if length == 0:
                break
            if length < self.QUERY_LIMIT:
                offset += m
                m *= 2
            else:
                step = offset - m // 2
                plan.append((start, start + step))
                print("p %d..%d" % plan[-1])
                m = max(1, m // 2)
                start += step + 1
        self._api.per_page = per_page
        return plan

    def read_plan(self, file_name):
        plan = []
        with open(file_name, "r") as fin:
            for line in fin:
                if line[0] == "p":
                    line = line[1:]
                line = line.strip()
                s, f = line.split("..")
                plan.append((int(s), int(f)))
        return plan

    def fetch(self, plan):
        repos = []
        for p in plan:
            print("f %d..%d" % p)
            query = self._api.search_repositories(
                "stars:%d..%d" % p, sort="updated", order="asc")
            repos.extend(query)
            if query.totalCount > self.QUERY_LIMIT:
                query = self._api.search_repositories(
                    "stars:%d..%d" % p, sort="updated", order="desc")
                assert query.totalCount <= self.QUERY_LIMIT * 2
                for i, r in enumerate(query):
                    if i > query.totalCount - 1000:
                        break
                    repos.append(r)
        return repos


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--token", "Github API token", required=True)
    parser.add_argument("-p", "--plan", "Path to file with the fetch plan")
    parser.add_argument("--save-plan", "Path to file where to write the "
                                       "resulting fetch plan")
    parser.add_argument("-o", "--output", "Path to the output JSON")
    return parser.parse_args()


def main():
    args = parse_args()
    stars = GitHubStars(args.token)
    if args.plan:
        plan = stars.read_plan(args.plan)
    stars.start_index = plan[-1][1] + 1
    plan += stars.make_plan()
    print("----plan----")
    print(plan)
    repos = stars.fetch(plan)
    with open("repos.pickle", "wb") as fout:
        pickle.dump(repos, fout, protocol=-1)
    print("The result was written to repos.pickle")


if __name__ == "__main__":
    sys.exit(main())
