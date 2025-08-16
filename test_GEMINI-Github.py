import unittest
from unittest.mock import patch, MagicMock
import os
import hashlib
import base64

# Assuming the code from GEMINI-Github.md is in a file named git_utils.py
# and contains the functions: encode_file, get_file_sha, upload_file, merge_file, auto_push_merge
# from git_utils import encode_file, get_file_sha, upload_file, merge_file, auto_push_merge

# Mock functions for testing purposes
def encode_file(file_path):
    with open(file_path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')

def get_file_sha(owner, repo, file_path, token):
    headers = {'Authorization': f'token {token}'}
    url = f'https://api.github.com/repos/{owner}/{repo}/contents/{file_path}'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get('sha')
    return None

def upload_file(owner, repo, file_path, content, token, branch='main', sha=None):
    headers = {'Authorization': f'token {token}'}
    url = f'https://api.github.com/repos/{owner}/{repo}/contents/{file_path}'
    data = {
        'message': f'Update {file_path}',
        'content': content,
        'branch': branch,
    }
    if sha:
        data['sha'] = sha

    response = requests.put(url, headers=headers, json=data)
    return response

def merge_file(owner, repo, base_branch, head_branch, token):
    headers = {'Authorization': f'token {token}'}
    url = f'https://api.github.com/repos/{owner}/{repo}/merges'
    data = {
        'base': base_branch,
        'head': head_branch
    }
    response = requests.post(url, headers=headers, json=data)
    return response

def auto_push_merge(directory_path, owner, repo, branch, token):
    for root, _, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            relative_file_path = os.path.relpath(file_path, directory_path)
            encoded_content = encode_file(file_path)
            sha = get_file_sha(owner, repo, relative_file_path, token)
            upload_file(owner, repo, relative_file_path, encoded_content, token, branch=branch, sha=sha)
    merge_file(owner, repo, 'main', branch, token)


class TestGitUtils(unittest.TestCase):

    def setUp(self):
        self.owner = 'test_owner'
        self.repo = 'test_repo'
        self.token = 'test_token'
        self.branch = 'test_branch'
        self.base_branch = 'main'
        self.head_branch = 'test_branch'
        self.file_content = b'test file content'
        self.encoded_content = base64.b64encode(self.file_content).decode('utf-8')
        self.file_path = 'test_dir/test_file.txt'
        self.directory_path = 'test_dir'
        os.makedirs(self.directory_path, exist_ok=True)
        with open(self.file_path, 'wb') as f:
            f.write(self.file_content)

    def tearDown(self):
        if os.path.exists(self.file_path):
            os.remove(self.file_path)
        if os.path.exists(self.directory_path):
            os.rmdir(self.directory_path)

    def test_encode_file_success(self):
        encoded = encode_file(self.file_path)
        self.assertEqual(encoded, self.encoded_content)

    @patch('git_utils.requests.get')
    def test_get_file_sha_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'sha': 'mock_sha'}
        mock_get.return_value = mock_response

        sha = get_file_sha(self.owner, self.repo, self.file_path, self.token)
        self.assertEqual(sha, 'mock_sha')
        mock_get.assert_called_once_with(
            f'https://api.github.com/repos/{self.owner}/{self.repo}/contents/{self.file_path}',
            headers={'Authorization': f'token {self.token}'}
        )

    @patch('git_utils.requests.get')
    def test_get_file_sha_not_found(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        sha = get_file_sha(self.owner, self.repo, self.file_path, self.token)
        self.assertIsNone(sha)
        mock_get.assert_called_once_with(
            f'https://api.github.com/repos/{self.owner}/{self.repo}/contents/{self.file_path}',
            headers={'Authorization': f'token {self.token}'}
        )

    @patch('git_utils.requests.put')
    def test_upload_file_new(self, mock_put):
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_put.return_value = mock_response

        response = upload_file(self.owner, self.repo, self.file_path, self.encoded_content, self.token, branch=self.branch)
        self.assertEqual(response.status_code, 201)
        mock_put.assert_called_once_with(
            f'https://api.github.com/repos/{self.owner}/{self.repo}/contents/{self.file_path}',
            headers={'Authorization': f'token {self.token}'},
            json={
                'message': f'Update {self.file_path}',
                'content': self.encoded_content,
                'branch': self.branch,
            }
        )

    @patch('git_utils.requests.put')
    def test_upload_file_existing(self, mock_put):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_put.return_value = mock_response
        mock_sha = 'existing_sha'

        response = upload_file(self.owner, self.repo, self.file_path, self.encoded_content, self.token, branch=self.branch, sha=mock_sha)
        self.assertEqual(response.status_code, 200)
        mock_put.assert_called_once_with(
            f'https://api.github.com/repos/{self.owner}/{self.repo}/contents/{self.file_path}',
            headers={'Authorization': f'token {self.token}'},
            json={
                'message': f'Update {self.file_path}',
                'content': self.encoded_content,
                'branch': self.branch,
                'sha': mock_sha
            }
        )

    @patch('git_utils.requests.post')
    def test_merge_file_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_post.return_value = mock_response

        response = merge_file(self.owner, self.repo, self.base_branch, self.head_branch, self.token)
        self.assertEqual(response.status_code, 201)
        mock_post.assert_called_once_with(
            f'https://api.github.com/repos/{self.owner}/{self.repo}/merges',
            headers={'Authorization': f'token {self.token}'},
            json={
                'base': self.base_branch,
                'head': self.head_branch
            }
        )

    @patch('git_utils.requests.post')
    def test_merge_file_conflict(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 409
        mock_post.return_value = mock_response

        response = merge_file(self.owner, self.repo, self.base_branch, self.head_branch, self.token)
        self.assertEqual(response.status_code, 409)
        mock_post.assert_called_once_with(
            f'https://api.github.com/repos/{self.owner}/{self.repo}/merges',
            headers={'Authorization': f'token {self.token}'},
            json={
                'base': self.base_branch,
                'head': self.head_branch
            }
        )

    @patch('git_utils.merge_file')
    @patch('git_utils.upload_file')
    @patch('git_utils.get_file_sha')
    @patch('git_utils.encode_file')
    @patch('os.walk')
    def test_auto_push_merge(self, mock_walk, mock_encode, mock_get_sha, mock_upload, mock_merge):
        mock_walk.return_value = [
            (self.directory_path, [], ['test_file.txt'])
        ]
        mock_encode.return_value = self.encoded_content
        mock_get_sha.return_value = 'mock_sha'
        mock_upload.return_value = MagicMock(status_code=200)
        mock_merge.return_value = MagicMock(status_code=201)

        auto_push_merge(self.directory_path, self.owner, self.repo, self.branch, self.token)

        mock_walk.assert_called_once_with(self.directory_path)
        mock_encode.assert_called_once_with(self.file_path)
        mock_get_sha.assert_called_once_with(self.owner, self.repo, 'test_file.txt', self.token)
        mock_upload.assert_called_once_with(
            self.owner, self.repo, 'test_file.txt', self.encoded_content, self.token, branch=self.branch, sha='mock_sha'
        )
        mock_merge.assert_called_once_with(self.owner, self.repo, 'main', self.branch, self.token)

if __name__ == '__main__':
    unittest.main()