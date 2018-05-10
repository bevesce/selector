import unittest

from fuzzy import score
from fuzzy import filter

# Abc -> Abc = 10
# abc -> Abc = 9
# Abc -> abc = 9
# B a -> a B = 8
# b a -> a b = 7
# ab -> acb = 4
# x -> ab = 0

class Test(unittest.TestCase):
    def test_filter(self):
        results = filter(['Abc', 'def', 'ab'], 'Ab')
        self.assertEqual(results, ('Abc', 'ab'))

    def test_exact_match_higher_than_lower_match(self):
        exact_score = score('Abc', 'Ab')
        lower_score = score('Abc', 'ab')
        self.assertTrue(exact_score > lower_score)

    def test_lower_higher_than_split(self):
        lower_score = score('Ab c', 'ab c')
        split_score = score('Ab c', 'c Ab')
        self.assertTrue(lower_score > split_score)

    def test_split_higher_than_lower_split(self):
        split_score = score('Ab c', 'c Ab')
        lower_split_score = score('Ab c', 'c ab')
        self.assertTrue(split_score > lower_split_score)

    def test_fuzzy_higher_than_zero(self):
        fuzzy_score = score('xaxbxcx', 'abc')
        zero_score = score('abc', 'xyz')
        self.assertTrue(fuzzy_score > zero_score)
        self.assertTrue(zero_score == 0 )



if __name__ == '__main__':
    unittest.main()
