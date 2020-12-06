import mock
import unittest 

import app
from app.repo import BitbucketRepo, GitHubRepo, BaseRepo


class MockBitbucketRepoRequestResponse(object):
    def json(self):
        return {
            'pagelen': 5,
            'values': [
                {'repo': 'data1'},
                {'repo': 'data2'},

            ],
            'page': 1,
            'size': 40
        }
    

class MockGithubRepoRequestResponse(object):
    def json(self):
        return [
            {'repo': 'data1', 'fork': True},
            {'repo': 'data2', 'fork': False},
            {'repo': 'data3', 'fork': False}
        ]
                
    @property
    def links(self):
        return {
            'notnext': {
                'url': 'this is blank'
                }
        }

class MockGithubFollowRequestResponse(object):
    def json(self):
        return [
            {'follower': 'data1'},
            {'follower': 'data2'}
        ]
                
    @property
    def links(self):
        return {
            'notnext': {
                'url': 'this is blank'
                }
        }


class MockFollowersRequestResponse(object):
    def json(self):
        return [{'test': 'data'}, {'test': 'data'}]

    @property
    def links(self):
        return {
            'test': 'data'
        }


class TestBaseRepoObject(unittest.TestCase):
    @mock.patch.multiple(BaseRepo, __abstractmethods__=set(), followers_count=mock.Mock(return_value=5))
    def test_instantiate(self):
        repo_provider = BaseRepo('mark2')
        # test a method on abstract class
        self.assertEqual(repo_provider.followers_count(), 5)

        # test non abstract method - clear_repo_data function
        repo_provider._repo_data = {'test': 'data'}
        self.assertEqual(repo_provider._repo_data, {'test': 'data'})
        repo_provider.clear_repo_data()
        self.assertEqual(repo_provider._repo_data, None)

        #test setting property manually fails
        with self.assertRaises(Exception):
            repo_provider.public_repos_count = 'not a number'

    def test_missing_attributes(self):
        with self.assertRaises(TypeError):
            BaseRepo('someone')
            

class test_GithubRepo(unittest.TestCase):

    @mock.patch.object(app.repo.WebRequestHandler, 'get_url')
    def test_get_repo_data(self, mock_webclient):
        mock_webclient.return_value = MockGithubRepoRequestResponse()
        github = GitHubRepo('somerepo')
        # test getting repo data
        self.assertEqual(github._get_repo_data, [{'repo': 'data1', 'fork': True}, {'repo': 'data2', 'fork': False}, {'repo': 'data3', 'fork': False}])
        self.assertEqual(github.public_repos_count, 2)
        self.assertEqual(github.forked_repos_count, 1)

    @mock.patch.object(app.repo.WebRequestHandler, 'get_url')
    def test_get_github_followers(self, mock_webclient):
        mock_webclient.return_value = MockGithubFollowRequestResponse()
        github = GitHubRepo('mark1')
        self.assertEqual(github.followers_count, 2)


if __name__ == '__main__':
    unittest.main()