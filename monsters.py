import pandas as pd
import numpy as np

from scipy.stats import norm
from statsmodels.distributions.empirical_distribution import ECDF

class Monsters(pd.DataFrame):
    '''Encapsulates the Pathfinder monster manual dataset

    During loading some additional auxiliary quantities are computed.
    '''
    def __init__(self, path):
        df = pd.read_excel(path)
        super(Monsters, self).__init__(df)
        self._compute_all_ability_modifiers()
        self._compute_size_modifiers()
        self._estimate_hd()
        self._estimate_cmd()
        self._group_by_cr()

    def _compute_all_ability_modifiers(self):
        names = ['Str', 'Dex', 'Con', 'Int', 'Wis', 'Cha']
        for name in names:
            self._compute_ability_modifiers(name)

    def _compute_ability_modifiers(self, name):
        if self[name].dtype != np.float and self[name].dtype != np.int:
            self[name].replace({'-': np.nan}, inplace=True)
        mod_name = name.lower() + '_mod'
        self[mod_name] = (self[name] - 10) // 2

    def _compute_size_modifiers(self):
        size2mod = {
            'Fine': -8,
            'Diminutive': -4,
            'Tiny': -2,
            'Small': -1,
            'Medium': 0,
            'Large': 1,
            'Huge': 2,
            'Gargantuan': 4,
            'Colossal': 8,
        }

        self['size_mod'] = self['Size'].map(size2mod)

    def _estimate_hd(self):
        self['n_hd'] = self['HD'].str.split('d', expand=True)[0]
        self.loc[~self['n_hd'].str.isdigit(), 'n_hd'] = np.nan
        self['n_hd'] = self['n_hd'].astype('float')

    def _estimate_cmd(self):
        self['cmd'] = 10. + self['str_mod'] + self['dex_mod'] + self['size_mod'] + self['n_hd']

    def _group_by_cr(self):
        self.cr = self.groupby('CR').agg(['mean', 'std'])
        self.cr = self.cr.reset_index()

    def hit_probability(self, ar_offsets, cr, ar_die=20, defense='AC', use_ecdf=True):
        '''Compute the probability to hit given AR die and offset and the monster challenge rating. Optionally the used defense can be specified.

        :name ar_offsets: Offsets to your attack roll you want to compute the hit probability for
        :name cr: Challenge rating of monsters you want the average hit probability for
        :name ar_die: Your attack roll die. So far only a single die is supported.
        :name defense: The defense skill used. Can be 'AC' or 'cmd'.
        :name use_exdf: If true use the empirical cumulative distribution function to compute the probabilities. Otherwise a Gaussian distribution is assumed.
        :return: Generates a probability for each offset specified
        '''

        if use_ecdf:
            cdf = ECDF(self.loc[self['CR'] == cr, defense].values)
        else:
            mean = self.cr.loc[self.cr['CR'] == cr, (defense, 'mean')].values[0]
            std = self.cr.loc[self.cr['CR'] == cr, (defense, 'std')].values[0]
            def cdf(x):
                return norm.cdf(x, mean, std)

        ps = []
        for offset in ar_offsets:
            p = 0.
            for i in range(ar_die):
                ar = i + 1 + offset
                p += cdf(ar)/ar_die

            yield p

    def expected_damage(self, dmg_rolls, ar_offsets, cr, ar_die = 20, defense='AC', use_ecdf=True):
        '''Computes the expected damage + standard deviation with the given attack and damage roles

        :name dmg_rolls: List of damage rolls each in the form '1d10+3d6+7+8'
        :name ar_offsets: Offsets to your attack roll you want to compute the hit probability for (Must have the same length as dmg_rolls)
        :name cr: Challenge rating of monsters you want the average hit probability for
        :name ar_die: Your attack roll die. So far only a single die is supported.
        :name defense: The defense skill used. Can be 'AC' or 'cmd'.
        :name use_exdf: If true use the empirical cumulative distribution function to compute the probabilities. Otherwise a Gaussian distribution is assumed.
        :return: Generates the mean damage and standard deviation of damage according to the specified dice and offset
        '''
        assert len(dmg_rolls) == len(ar_offsets)

        for i, p in enumerate(self.hit_probability(ar_offsets, cr, ar_die, defense, use_ecdf)):
            mean_dmg, var_dmg = self._expected_var_dmg(dmg_rolls[i])

            yield mean_dmg*p, np.sqrt(var_dmg*p)

    def _expected_var_dmg(self, dmg_roll):
        mean = 0.
        var = 0.

        for dr in dmg_roll.split('+'):
            if 'd' in dr:
                mult, die = dr.split('d')
                if len(mult) == 0:
                    mult = 1
                else:
                    mult = int(mult)

                die = int(die)
                mean += mult * (die + 1)/2
                var += mult * (die**2 - 1)/12
            else:
                mean += int(dr)

        return mean, var



if __name__ == '__main__':
    from dotenv import dotenv_values
    parsed = dotenv_values()
    path = parsed['MONSTER_PATH']
    m = Monsters(path)
    print(m.head())
    print(m.cr.head())

    for p in m.hit_probability([15], 10):
        print(p)
