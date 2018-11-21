import random

from mediacloud.test.basetest import ApiBaseTest, AdminApiBaseTest

TEST_USER_EMAIL = "mediacloud-testing@media.mit.edu"
TEST_USER_ID = 435


class UserProfileTest(ApiBaseTest):

    def testUserProfile(self):
        profile = self._mc.userProfile()
        self.assertTrue('email' in profile)
        self.assertTrue('auth_roles' in profile)
        self.assertTrue('admin' in profile['auth_roles'])


class AuthTokenTest(ApiBaseTest):

    def testAuthToken(self):
        valid_auth_token = self._config.get('api', 'key')
        fake_auth_token = 'these are not the keys you are looking for'
        # make sure setAuthToken workds
        self._mc.setAuthToken(fake_auth_token)
        self.assertEqual(self._mc._auth_token, fake_auth_token)
        # see a request with a bad key fail
        try:
            self._mc.media(1)
            self.assertFalse(True)
        except:
            self.assertTrue(True)
        # set the key back to a valid one
        self._mc.setAuthToken(valid_auth_token)

    def testUserAuthToken(self):
        # test failure mode
        try:
            self._mc.userAuthToken('user@funkytown.us', '1234')
            self.assertFalse(True)
        except:
            self.assertTrue(True)


class UserProfileTest(AdminApiBaseTest):

    def testUser(self):
        results = self._mc.user(TEST_USER_ID)
        self.assertIn('users', results)
        self.assertEqual(len(results['users']), 1)
        self.assertIn('email', results['users'][0])
        self.assertEqual(results['users'][0]['email'], TEST_USER_EMAIL)

    def testUserList(self):
        results = self._mc.userList(search=TEST_USER_EMAIL)
        self.assertIn('users', results)
        self.assertEqual(len(results['users']), 1)
        self.assertIn('email', results['users'][0])
        self.assertEqual(results['users'][0]['email'], TEST_USER_EMAIL)

    def testUserListPaging(self):
        page1 = self._mc.userList()
        self.assertIn('users', page1)
        page1_ids = [u['auth_users_id'] for u in page1['users']]
        self.assertIn('link_ids', page1)
        self.assertIn('next', page1['link_ids'])
        page2 = self._mc.userList(link_id = page1['link_ids']['next'])
        page2_ids = [u['auth_users_id'] for u in page2['users']]
        # make sure pages don't overlap
        intersection = list(set(page1_ids) & set(page2_ids))
        self.assertEqual(0, len(intersection))

    def testUserListRoles(self):
        results = self._mc.validUserRoles()
        self.assertIn('roles', results)
        self.assertGreater(len(results['roles']), 0)

    def testUserUpdate(self):
        # test updating the user's note
        new_note = "testing user - {}".format(random.randint(1, 101))
        results = self._mc.user(TEST_USER_ID)
        self.assertNotEqual(results['users'][0]['notes'], new_note)
        results = self._mc.userUpdate(TEST_USER_ID, notes=new_note)
        self.assertIn('success', results)
        self.assertTrue(results['success'], 1)
        results = self._mc.user(TEST_USER_ID)
        self.assertEqual(results['users'][0]['notes'], new_note)
