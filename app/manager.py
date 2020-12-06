from app.repo import GitHubRepo, BitbucketRepo
from collections import Counter


def get_aggregate_repo_data(username):
    """
    This function takes a username and manages the different instances of SCM providers for the aggregate
    :param username: the username to get data on
    :type username: str
    """
    github = GitHubRepo(username)
    bitbucket = BitbucketRepo(username)
    github_summary = github.get_summary()
    bitbucket_summary = bitbucket.get_summary()
    # add new scm providers here
    return combine_summaries([github_summary, bitbucket_summary])


def combine_summaries(summaries):
    """
    A convenience method to combine the summary output of BaseRepo objects
    :param summaries: a list of dictionaries from the get_summary() output from one of more BaseReop objects
    :type summaries: list
    """
    # todo make this cleaner?
    aggregate = {
        'followers_count': 0,
        'public_repos_count': 0,
        'forked_repos_count': 0,
        'watcher_count': 0,
        'languages': [],
        'topics_list': [],
        'language_count': Counter({}),
        'topics': Counter({})
    }
    for summary in summaries:
        aggregate['followers_count'] += summary['followers_count']
        aggregate['public_repos_count'] += summary['public_repos_count']
        aggregate['forked_repos_count'] += summary['forked_repos_count']
        aggregate['watcher_count'] += summary['watcher_count']
        aggregate['languages'] += summary['languages']
        aggregate['topics_list'] += summary['topics_list']
        aggregate['language_count'] = aggregate['language_count'] + summary['language_count']
        aggregate['topics'] = aggregate['topics'] + summary['topics']
    return aggregate
