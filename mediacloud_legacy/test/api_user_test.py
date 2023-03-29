import random
import os

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
        valid_auth_token = os.getenv("MC_API_KEY")
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


class UserAuthTest(AdminApiBaseTest):

    def testUser(self):
        results = self._mc.user(TEST_USER_ID)
        self.assertIn('users', results)
        self.assertEqual(len(results['users']), 1)
        self.assertIn('email', results['users'][0])
        self.assertEqual(results['users'][0]['email'], TEST_USER_EMAIL)
        self.assertIn('weekly_requests_limit', results['users'][0])
        self.assertIn('active', results['users'][0])
        self.assertIn('max_topic_stories', results['users'][0])
        self.assertEqual(results['users'][0]['active'], 1)

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
        page2 = self._mc.userList(link_id=page1['link_ids']['next'])
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

    def testUserConsented(self):
        # make sure value is there
        u1 = self._mc.user(TEST_USER_ID)
        self.assertTrue(u1['users'][0]['has_consented'])
        # update to false
        response = self._mc.userUpdate(TEST_USER_ID, has_consented=False)
        self.assertIn('success', response)
        self.assertEqual(response['success'], 1)
        # verify it is false
        u2 = self._mc.user(TEST_USER_ID)
        self.assertFalse(u2['users'][0]['has_consented'])
        # update back to true
        results2 = self._mc.userUpdate(TEST_USER_ID, has_consented=True)
        self.assertIn('success', results2)
        self.assertEqual(results2['success'], 1)
        # verify it is true
        u3 = self._mc.user(TEST_USER_ID)
        self.assertTrue(u3['users'][0]['has_consented'])

# verified this one manually
#    def testUserDelete(self):
#        results = self._mc.userDelete(3835)
#        self.assertEqual(results['success'], 1)
