import timeit

import vcr
from nose.tools import *  # flake8: noqa

# Comment line below prevents unittest from deletion in import optimization
# noinspection PyUnresolvedReferences
import unittest

from osf_api_v2_client.settings.local import (
    URL,                # e.g. 'https://staging2.osf.io/api/v2/'
    AUTH1,              # authentication details for USER1
    AUTH2,              # authentication details for USER2
)
from osf_api_v2_client.session import Session
from osf_api_v2_client.utils import (DotNotator,
                                     dotnotator_generator)


# Sessions with different forms of authentication:
# A session authenticated by the user who created the node with
# PRIVATE_NODE_ID
SESSION_AUTH1 = Session(root_url=URL, auth=AUTH1)
# A session authenticated by a user who does NOT have access to
# the node with PRIVATE_NODE_ID
SESSION_AUTH2 = Session(root_url=URL, auth=AUTH2)
# A session that is not authenticated
SESSION_NO_AUTH = Session(root_url=URL)


VCR_CASSETTE_PREFIX = 'fixtures/vcr_cassettes/test_utils/'
VCR_RECORD_MODE = 'new_episodes'  # TODO or 'once' ?


# TODO get rid of this:
def smart_print(string):
    try:
        print(string)
    except UnicodeEncodeError:
        print(string.encode('utf-8'))


class TestDotNotator(unittest.TestCase):

    def setUp(self):
        self.json_dict = {
            u'name': u'Sally',
            u'age': 144,
            u'friends': [
                {u'name': u'Sasha',
                 u'age': 121
                 },
                {u'name': u'Sandy',
                 u'age': 100
                 },
            ],
            u'education': {
                u'Artsy_University':
                    {u'degree': u'BA in Art',
                     u'years_spent': 3,
                     },
                u'High_School':
                    {u'degree': u'Diploma',
                     u'years_spent': 4,
                     }
            },
            }
        self.dn = DotNotator(self.json_dict)

    def test_no_param(self):
        no_param_dn = DotNotator()  # no param --> default: dictionary = None
        assert_true(isinstance(no_param_dn, DotNotator))
        assert_false(no_param_dn)  # assert no_param_dn is empty

    def test_wrong_type_param(self):
        not_dict = 4
        with assert_raises(TypeError):
            DotNotator(not_dict)

    def test_empty_dict_param(self):
        empty_dict = {}
        empty_dn = DotNotator(empty_dict)
        assert_true(isinstance(empty_dn, DotNotator))
        assert_false(empty_dn)  # assert empty_dn is empty

    def test_json_dict_param(self):
        json_dn = DotNotator(self.json_dict)
        assert_true(isinstance(json_dn, DotNotator))
        assert_true(json_dn)  # assert json_dn is not empty
        assert_equal(json_dn[u'name'], u'Sally')
        assert_equal(json_dn[u'age'], 144)
        assert_equal(json_dn.name, u'Sally')
        assert_equal(json_dn.age, 144)

    def test_param_includes_list_of_dicts(self):
        assert_equal(self.dn[u'friends'][0][u'name'], u'Sasha')
        assert_equal(self.dn[u'friends'][1][u'age'], 100)
        assert_equal(self.dn.friends[0].age, 121)
        assert_equal(self.dn.friends[1].name, u'Sandy')

    def test_param_includes_dict_inside_dict(self):
        assert_equal(
            self.dn[u'education'][u'Artsy_University'][u'degree'],
            u'BA in Art')
        assert_equal(
            self.dn[u'education'][u'High_School'][u'years_spent'], 4)
        assert_equal(self.dn.education.Artsy_University.years_spent, 3)
        assert_equal(self.dn.education.High_School.degree, u'Diploma')

    def test_attempt_to_access_nonexistent_key(self):
        with assert_raises(KeyError):
            print(self.dn.education.nonexistent_key)

    def test_modify_key(self):
        self.dn.name = u'Sammy'
        self.dn[u'age'] = 81
        assert_equal(self.dn[u'name'], u'Sammy')
        assert_equal(self.dn.age, 81)

    def test_add_key(self):
        self.dn.new_item1 = u'Hello'
        self.dn[u'new_item2'] = u'world!'
        assert_equal(self.dn[u'new_item1'], u'Hello')
        assert_equal(self.dn.new_item2, u'world!')
        assert_equal('{} {}'.format(self.dn.new_item1, self.dn.new_item2),
                     u'Hello world!')

    # Inspired by (though doesn't fulfill same functionality as) this:
    # http://codereply.com/answer/4ay2xl/python-easily-access-deeply-nested-dict-get-set.html
    def test_add_multiple_layers_of_keys(self):
        self.dn.top_layer = {}
        self.dn.top_layer.middle_layer = {}
        self.dn[u'top_layer'][u'middle_layer'][u'lowest_layer'] = \
            {u'3': u'world!'}
        assert_equal(self.dn[u'top_layer'],
                     {u'middle_layer': {u'lowest_layer': {u'3': u'world!'}}})
        assert_equal(self.dn.top_layer.middle_layer,
                     {u'lowest_layer': {u'3': u'world!'}})
        assert_equal(self.dn.top_layer.middle_layer.lowest_layer,
                     {u'3': u'world!'})
        assert_equal(
            self.dn[u'top_layer'][u'middle_layer'][u'lowest_layer'][u'3'],
            u'world!')
        print(self.dn.age)

    def test_delete_key(self):
        del self.dn.name
        with assert_raises(KeyError):
            print(self.dn[u'name'])
        del self.dn[u'friends'][0][u'name']
        with assert_raises(KeyError):
            print(self.dn.friends[0].name)
        del self.dn.education.Artsy_University
        with assert_raises(KeyError):
            print(self.dn[u'education'][u'Artsy_University'])
        assert_equal(self.dn[u'education'][u'High_School'],
                     {u'degree': 'Diploma', u'years_spent': 4, })

    def test_iter_list(self):
        friends_list = []
        for item in self.dn.friends:
            friends_list.append(item)
        assert_equal(friends_list,
                     [{u'name': u'Sasha',
                       u'age': 121
                       },
                      {u'name': u'Sandy',
                       u'age': 100
                       },
                      ])

    def test_iter_dict(self):
        hs_dict = {}
        for key in self.dn[u'education'][u'High_School']:
            hs_dict[key] = self.dn[u'education'][u'High_School'][key]
        assert_equal(hs_dict,
                     {u'degree': u'Diploma',
                      u'years_spent': 4,
                      })


# class TestFileGenerator(unittest.TestCase):
#     TODO fix this
#     @my_vcr.use_cassette()
#     def test_few_files(self):
#         for file in SESSION_AUTH1.get_file_generator(PUBLIC_NODE_ID):
#             file_to_download = requests.get(file.links.self)
#             filepath = "test_file_generator/test_few_files/{}/{}".format(file.provider, file.name)
#             print("Downloading file: {}".format(filepath))
#             os.makedirs(os.path.dirname(filepath), exist_ok=True)  # Create directory for file if it doesn't exist
#             # Name the new file with the name of the file given in the API
#             with open(filepath, "wb") as new_file:
#                 new_file.write(file_to_download.content)
#     # TODO how to assert that files exist?


class TestDotNotatorGenerator(unittest.TestCase):

    dot_notator_generator_vcr = vcr.VCR(
        cassette_library_dir='{}test_dot_notator_generator'.format(
            VCR_CASSETTE_PREFIX),
        record_mode=VCR_RECORD_MODE
    )

    @dot_notator_generator_vcr.use_cassette()
    def test_defaults(self):
        # TODO modify this
        """
        num_requested should == -1, meaning all items should be returned
        """
        big_gen = dotnotator_generator(
            "https://staging2.osf.io/api/v2/users/se6py/nodes/")
        with assert_raises(StopIteration):
            print(next(big_gen))
            print(next(big_gen))
            print(next(big_gen))
            print(next(big_gen))
            print(next(big_gen))
            print(next(big_gen))
            print(next(big_gen))
            print(next(big_gen))
            print(next(big_gen))
            print(next(big_gen))
            print(next(big_gen))
            print(next(big_gen))
            print(next(big_gen))
            print(next(big_gen))
            print(next(big_gen))

    @dot_notator_generator_vcr.use_cassette()
    def test_num_requested_negative1(self):
        # TODO write this test
        """
        Test that generator responds correctly when num_requested == -1
        vs any other number.
        """
        pass

    @dot_notator_generator_vcr.use_cassette()
    def test_num_requested_positive(self):
        """
        request 4; 4 items should be returned
        """
        gen = dotnotator_generator(
            "https://staging2.osf.io/api/v2/nodes/xtf45/files/?path=%2F&provider=googledrive",
            num_requested=4)
        for item in gen:
            print("{}: {}: {}".format(item.provider,
                                      item.name,
                                      item.links.self))


# class TestTimes(unittest.TestCase):
#     # TODO get rid of this class
#
#     @vcr.use_cassette(record_mode='new_episodes')
#     def test_dn_json(self):
#
#         dn_list = []
#         for user in SESSION_AUTH1.get_user_generator(num_requested=50):
#             dn_list.append(user)
#
#         def time_dn():
#             for u in dn_list:
#                 x = u.fullname
#
#         json_list = []
#         for user in SESSION_AUTH1.get_json_user_generator(num_requested=50):
#             json_list.append(user)
#
#         def time_json():
#
#             for data_item in json_list:
#                 y = data_item[u'fullname']
#
#         print('------ NUM_REQUESTED = 50 ------')
#         print('TIME_DN: 1ST TIME: {}'.format(timeit.timeit(time_dn)))
#         print('TIME_DN: 2ND TIME: {}'.format(timeit.timeit(time_dn)))
#         print('TIME_JSON: 1ST TIME: {}'.format(timeit.timeit(time_json)))
#         print('TIME_JSON: 2ND TIME: {}'.format(timeit.timeit(time_json)))
