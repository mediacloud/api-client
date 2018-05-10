import time
from mediacloud.test.basetest import ApiBaseTest, AdminApiBaseTest


class ApiTagsTest(ApiBaseTest):

    def testTags(self):
        tag = self._mc.tag(8876989)  # US mainstream media
        self.assertEqual(tag['tags_id'], 8876989)
        self.assertEqual(tag['tag'], 'JP')
        self.assertEqual(tag['tag_sets_id'], 597)

    def testTagList(self):
        # verify it only pulls tags from that one set
        first_list = self._mc.tagList(597)
        self.assertEqual(len(first_list), 20)
        ignore = [self.assertEqual(tag['tag_sets_id'], 597) for tag in first_list]
        # make sure paging through a set works right
        second_list = self._mc.tagList(597, int(first_list[19]['tags_id'])-1)
        self.assertEqual(len(second_list), 20)
        ignore = [self.assertEqual(tag['tag_sets_id'], 597) for tag in second_list]
        self.assertEqual(first_list[19]['tags_id'], second_list[0]['tags_id'])
        # make sure you can pull a longer list of tags
        longer_list = self._mc.tagList(597, 0, 150)
        self.assertEqual(len(longer_list), 150)
        ignore = [self.assertEqual(tag['tag_sets_id'], 597) for tag in longer_list]
        longest_list = self._mc.tagList(597, 0, 200)
        self.assertEqual(len(longest_list), 173)
        ignore = [self.assertEqual(tag['tag_sets_id'], 597) for tag in longest_list]
        # try getting only the public tags in the set
        full_list = self._mc.tagList(6, rows=200)
        public_list = self._mc.tagList(6, rows=200, public_only=True)
        self.assertNotEqual(len(full_list), len(public_list))

    def testTagListMultpleSets(self):
        search = "Ghana"
        collection1_id = 5 # collections
        collection2_id= 556 # GV
        list_1 = self._mc.tagList(collection1_id, name_like=search)
        self.assertTrue(len(list_1) > 0)
        list_2 = self._mc.tagList(collection2_id, name_like=search)
        self.assertTrue(len(list_2) > 0)
        combined_list = self._mc.tagList([collection1_id, collection2_id], name_like=search)
        self.assertEqual(len(combined_list), len(list_1) + len(list_2))

    def testTagListSimilar(self):
        collection_tags = self._mc.tagList(similar_tags_id=8876989)
        self.assertEqual(20, len(collection_tags))

    def testTagListSearch(self):
        # verify search works at all
        collection_tags = self._mc.tagList(name_like="collection")
        self.assertTrue(len(collection_tags) > 0, "Got %d tags matching 'collection'" % len(collection_tags))
        # verify search works on tags without descriptions
        geo_tags = self._mc.tagList(name_like="geonames_")
        self.assertTrue(len(geo_tags) > 0, "Got %d tags matching 'geonames_'" % len(geo_tags))


class ApiTagSetsTest(ApiBaseTest):

    def testTagSet(self):
        tagSet = self._mc.tagSet(597)
        self.assertEqual(tagSet['tag_sets_id'], 597)
        self.assertEqual(tagSet['name'], 'gv_country')

    def testTagSetList(self):
        first_list = self._mc.tagSetList()
        self.assertEqual(len(first_list), 20)
        second_list = self._mc.tagSetList(int(first_list[19]['tag_sets_id'])-1)
        self.assertEqual(len(second_list), 20)
        self.assertEqual(first_list[19]['tag_sets_id'], second_list[0]['tag_sets_id'])
        longer_list = self._mc.tagSetList(0, 50)
        self.assertEqual(len(longer_list), 50)


class AdminApiTaggingTest(AdminApiBaseTest):

    def testTagCreate(self):
        new_tag_name = 'test-create-tag-'+str(int(time.time()))
        self._mc.createTag(TEST_TAG_SET_ID, new_tag_name, 'Test Create Tag', 'this is just a test tag')
        # now search for it by name
        results = self._mc.tagList(name_like=new_tag_name)
        self.assertNotEqual(0, len(results))

    def testTagUpdate(self):
        example_tag_id = TEST_TAG_ID_1
        # change the name, label and description
        self._mc.updateTag(example_tag_id, 'modified tag', 'modified label', 'modified description')
        modified_tag = self._mc.tag(example_tag_id)
        self.assertEqual(modified_tag['tag'], 'modified tag')
        self.assertEqual(modified_tag['label'], 'modified label')
        self.assertEqual(modified_tag['description'], 'modified description')
        # set it back
        self._mc.updateTag(example_tag_id, 'example tag', 'example label', 'This is an example tag used in api client test scripts')
        modified_tag = self._mc.tag(example_tag_id)
        self.assertEqual(modified_tag['tag'], 'example tag')
        self.assertEqual(modified_tag['label'], 'example label')
        self.assertEqual(modified_tag['description'], 'This is an example tag used in api client test scripts')

    def testTagSetUpdate(self):
        example_tag_sets_id = TEST_TAG_SET_ID
        # change the name, label and description
        self._mc.updateTagSet(example_tag_sets_id, TEST_USER_EMAIL, 'modified label', 'modified description')
        modified_tag = self._mc.tagSet(example_tag_sets_id)
        self.assertEqual(modified_tag['name'], TEST_USER_EMAIL)
        self.assertEqual(modified_tag['label'], 'modified label')
        self.assertEqual(modified_tag['description'], 'modified description')
        # set it back
        self._mc.updateTagSet(example_tag_sets_id, TEST_USER_EMAIL, 'rahulbot', 'The tag set of Rahul!')
        modified_tag = self._mc.tagSet(example_tag_sets_id)
        self.assertEqual(modified_tag['name'], TEST_USER_EMAIL)
        self.assertEqual(modified_tag['label'], 'rahulbot')
        self.assertEqual(modified_tag['description'], 'The tag set of Rahul!')



