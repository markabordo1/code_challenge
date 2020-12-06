import abc
import json
import requests
from collections import Counter

from app import environment


class WebRequestHandler(object):
    """
    Helper class to manage web client session with external API
    """

    def __init__(self):
        self.session = requests.Session()

    def get_url(self, url, headers={}):
        """
        :param url: URL to hit with GET request
        :param headers: contains header values for requests 
        :type headers: dict
        """
        # todo maybe add some logging here or auditing 
        try:
            print('sending GET request to: %s' % url)
            response = self.session.get(url, headers=headers)        
            if response.status_code != 200:
                response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            raise e
 
    def post_url(self, url, data=None, headers={}):
        """
        :param url: URL to hit with POST request
        :param headers: contains header values for requests 
        :type headers: dict        
        :param data: holds POST body information
        :type data: json or dict
        """
        try:
            response = self.session.post(url, headers=headers, data=data)
            if response.status_code != 200:
                raise 'there was an error processing your request'
            return response
        except requests.exceptions.RequestException as e:
            raise e


class BaseRepo(metaclass=abc.ABCMeta):
    """
    Parent repo class as a scafold for different scm providers
    """
    def __init__(self, username):
        """
        :param username: repo username 
        :type username: str
        """
        self.username = username
        self.client = WebRequestHandler()

        self._repo_data = None
        self._watcher_count = None
        self._followers_count = None
        self._topics_count = None


    @property
    @abc.abstractmethod
    def _get_repo_data(self):
        """
        Gets and stores all the repos of a username
        """
        return NotImplemented

    @property
    @abc.abstractmethod
    def followers_count(self):
        """
        Grabs all the followers of a repo
        """
        return NotImplemented

    @property
    @abc.abstractmethod
    def public_repos_count(self):
        """
        From the repo attribute, get the count of public repos
        """
        return NotImplemented

    @property
    @abc.abstractmethod
    def forked_repos_count(self):
        """
        From the repo attribute, get the count of forked repos
        """
        return NotImplemented

    @property
    @abc.abstractmethod
    def watcher_count(self):
        """
        Total count of user watching all the repositories of a user
        """
        return NotImplemented

    @property
    @abc.abstractmethod
    def language_count(self):
        """
        Language grouped by frequency 
        """
        return NotImplemented

    @property
    @abc.abstractmethod
    def languages(self):
        """
        List of distinct lanauges used across a username
        """
        return NotImplemented

    @property
    @abc.abstractmethod
    def topics(self):
        """
        Topics grouped by frequency 
        """
        return NotImplemented

    @property
    @abc.abstractmethod
    def topics_list(self):
        """
        List of distinct topics across a username
        """
        return NotImplemented

    @abc.abstractmethod
    def get_summary(self):
        """
        Convenience function to tabulate summary of data from each scm provider
        """
        return NotImplemented

    def clear_repo_data(self):
        """
        Convenience function to clear stored data points
        """
        self._repo_data = None
        self._watcher_data = None
        self._followers_count = None
        self._topics_count = None


class GitHubRepo(BaseRepo):

    def __init__(self, *args, **kwargs):
        self._headers = {'Authorization': 'token %s' % environment.GITHUB_AUTH_TOKEN} if environment.GITHUB_AUTH_ENABLED else None
        super(GitHubRepo, self).__init__(*args, **kwargs)
        self._get_repo_data


    @property
    def _get_repo_data(self):
        if not self._repo_data:
            repo_list = []
            url = environment.GITHUB_BASE_URL + 'users/{0}/repos?per_page=100&page=1'.format(self.username)
            while True:
                repo_page = self.client.get_url(url, headers=self._headers)
                repo_list += repo_page.json()
                if 'next' in repo_page.links:
                    url = repo_page.links['next']['url']
                else:
                    break
            self._repo_data = repo_list
        return self._repo_data

    @property
    def followers_count(self):
        # To get followers, GITHUB has a separate endpoint to get followers for a user
        if not self._followers_count:
            followers_count = 0
            url = environment.GITHUB_BASE_URL + 'users/%s/followers?per_page=100&page=1' % self.username
            while True:
                followers_page = self.client.get_url(url, headers=self._headers)
                followers_page_count = len(followers_page.json())
                followers_count += followers_page_count
                if 'next' in followers_page.links:
                    url = followers_page.links['next']['url']
                else:
                    break
            self._followers_count = followers_count
        return self._followers_count

    @property
    def public_repos_count(self):
        return sum(1 for _ in (repo for repo in self._get_repo_data if not repo['fork']))

    @property
    def forked_repos_count(self):
        return sum(1 for _ in (repo for repo in self._get_repo_data if repo['fork']))

    @property
    def watcher_count(self):
        return sum(repo['watchers'] for repo in self._get_repo_data)

    @property
    def languages(self):
        return list(self.language_count.keys())

    @property
    def language_count(self):
        return Counter((repo['language'] for repo in self._get_repo_data if not repo['fork']))

    @property
    def topics(self):
        if not self._topics_count:
            # this header is for a test version for grabbing topics but suffices for this situation 12/5/2020
            headers = {'Accept': 'application/vnd.github.mercy-preview+json'}
            headers = {**headers, **self._headers} if self._headers else headers
            topics_count = Counter()
            for repo in self._get_repo_data:
                url = environment.GITHUB_BASE_URL + 'repos/' + self.username + '/' + repo['name'] + '/topics'
                topics_page = self.client.get_url(url, headers=headers)
                topics_count.update(topic for topic in json.loads(topics_page.text)['names'])
            self._topics_count = topics_count
        return self._topics_count

    @property
    def topics_list(self):
        return list(self.topics.keys())

    def get_summary(self):
        return {
            'followers_count': self.followers_count,
            'public_repos_count': self.public_repos_count,
            'forked_repos_count': self.forked_repos_count,
            'watcher_count': self.watcher_count,
            'language_count': self.language_count,
            'languages': self.languages,
            'topics': self.topics,
            'topics_list': self.topics_list
        }


class BitbucketRepo(BaseRepo):

    def __init__(self, *args, **kwargs):
        super(BitbucketRepo, self).__init__(*args, **kwargs)
        self._get_repo_data

    @property
    def _get_repo_data(self):
        if not self._repo_data:
            repo_list = []
            # 100 is the bitbucket max per page
            url = environment.BITBUCKET_BASE_URL + 'repositories/' + self.username + '?pagelen=100'

            while True:
                repo_page = self.client.get_url(url)
                repo_page_list = repo_page.json()
                repo_list += repo_page_list['values']

                if 'next' in repo_page_list:
                    url = repo_page_list['next']
                else:
                    break
            self._repo_data = repo_list
        return self._repo_data

    @property
    def followers_count(self):
        # 100 is the bitbucket max per page
        # note 'size' is available in the response which is the total number of objects in the response however
        # bitbucket states that `This is an optional element that is not provided in all responses, as it can be expensive to compute.`
        if not self._followers_count:

            url = environment.BITBUCKET_BASE_URL + 'teams/' + self.username + '/followers?pagelen=100'
            followers_count = 0

            while True:
                followers_page = self.client.get_url(url)
                followers_page_list = followers_page.json()
                if 'next' in followers_page_list:
                    url = followers_page_list['next']
                    followers_count += 100
                else:
                    followers_count += len(followers_page_list['values'])
                    break
    
            self._followers_count = followers_count
        return self._followers_count
    
    @property
    def public_repos_count(self):
        return sum(1 for _ in (repo for repo in self._get_repo_data if not 'parent' in repo))

    @property
    def forked_repos_count(self):
        return sum(1 for _ in (repo for repo in self._get_repo_data if 'parent' in repo))

    @property
    def watcher_count(self):
        # watchers for bitbucket are accessed through a separate endpoint which is part of the repo data dict
        if not self._watcher_count:
            watcher_count = 0
            for repo in self._get_repo_data:
                url = repo['links']['watchers']['href'] + '?pagelen=100'
                while True:
                    watchers_page = self.client.get_url(url)
                    watchers_data = watchers_page.json()
                    if 'next' in watchers_data:
                        url = watchers_data['next']
                        watcher_count += 100
                    else:
                        watcher_count += len(watchers_data['values'])
                        break

            self._watcher_count = watcher_count
        return self._watcher_count
            
    @property
    def languages(self):
        return list(self.language_count.keys())

    @property
    def language_count(self):
        return Counter((repo['language'] for repo in self._get_repo_data if not 'parent' in repo))

    @property
    def topics(self):
        # There are no topics in bitbucket
        return Counter({})

    @property
    def topics_list(self):
        # There are no topics in bitbucket
        return []

    def get_summary(self):
        return {
            'followers_count': self.followers_count,
            'public_repos_count': self.public_repos_count,
            'forked_repos_count': self.forked_repos_count,
            'watcher_count': self.watcher_count,
            'language_count': self.language_count,
            'languages': self.languages,
            'topics': self.topics,
            'topics_list': self.topics_list
        }