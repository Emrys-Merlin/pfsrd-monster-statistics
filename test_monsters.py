from monsters import Monsters

from tempfile import TemporaryDirectory
import pandas as pd
import numpy as np
import os

class TestMonsters():

    @classmethod
    def setup_class(cls):
        print('Test')
        cls.tmp_dir = TemporaryDirectory()

    @classmethod
    def teardown_class(cls):
        pass

    def test_init_auxiliary_computations(self):
        d = {}
        for i, score in enumerate(['Str', 'Dex', 'Con', 'Wis', 'Int', 'Cha']):
            d[score] = [6 + 2*i]*2

        d['Size'] = ['Tiny', 'Large']
        d['HD'] = ['1d8', '2d6']
        d['CR'] = [1, 17]

        df = pd.DataFrame(d)
        path = os.path.join(self.tmp_dir.name, 'tmp.xlsx')
        df.to_excel(path)

        m = Monsters(path)

        for i, mod in enumerate(['str', 'dex', 'con', 'wis', 'int', 'cha']):
            mod += '_mod'
            assert m.loc[0, mod] == i - 2

        assert m.loc[0, 'size_mod'] == -2
        assert m.loc[1, 'size_mod'] == 1

        assert m.loc[0, 'n_hd'] == 1
        assert m.loc[1, 'n_hd'] == 2

        assert m.loc[0, 'cmd'] == 10 -2 + 1 -2 -1 

    def test_hit_prob_and_expected_damage(self):
        n = 3
        d = {}

        for score in ['Str', 'Dex', 'Con', 'Wis', 'Int', 'Cha']:
            d[score] = [10]*2*n

        d['Size'] = ['Medium']*n + ['Large']*n
        d['HD'] = ['5d12']*n + ['25d8']*n
        d['CR'] = [4]*n + [7]*n
        d['AC'] = list(range(n)) + list(range(30, 30+n))
        df = pd.DataFrame(d)

        path = os.path.join(self.tmp_dir.name, 'tmp.xlsx')
        df.to_excel(path)

        m = Monsters(path)

        for p in m.hit_probability([20], 4):
            np.testing.assert_almost_equal(p, 1.0)

        for mean, std in m.expected_damage(['1d6+7'], [20], 4):
            np.testing.assert_almost_equal(mean, 10.5)
            np.testing.assert_almost_equal(std, np.sqrt(35/12))

        for p in m.hit_probability([0], 7):
            np.testing.assert_almost_equal(p, 0.0)

        for mean, std in m.expected_damage(['1d6+7'], [0], 7):
            np.testing.assert_almost_equal(mean, 0.0)
            np.testing.assert_almost_equal(std, 0.0)
