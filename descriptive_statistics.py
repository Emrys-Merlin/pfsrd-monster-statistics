import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
sns.set()
import os

from sklearn.cluster import MeanShift
from scipy.stats import norm
from tqdm import tqdm

def plot_distribution(series, path, title='', xlabel=None):
    '''Plot a histogram of a series with mean, std and median

    :name series: Series with the counts
    :name path: Path where the image is saved to
    :name title: Title for the graph
    :name xlabel: xlabel of the graph
    '''
    mean = series.mean()
    std = series.std()
    median = series.median()

    cp = sns.color_palette()

    plt.figure(figsize=(16,9))
    sns.distplot(series.dropna())
    ylim = plt.ylim()
    plt.plot([mean]*2, ylim, label='mean', c=cp[1])
    plt.plot([mean+std]*2, ylim, label='std', c=cp[1], linestyle='dashed')
    plt.plot([mean-std]*2, ylim, c=cp[1], linestyle='dashed')
    plt.plot([median]*2, ylim, label='median', c=cp[2])
    plt.legend()
    plt.title(title)
    if xlabel is None:
        xlabel = title
    plt.xlabel(xlabel)
    plt.savefig(path)
    plt.close()

def plot_important_distributions(m, path):
    names = ['CR', 'AC', 'cmd']
    titles = ['Challenge rating', 'Armor class', 'Combat maneuver defense']

    for name, title in zip(names, titles):
        fn = os.path.join(path, name+'.png')
        plot_distribution(m[name], fn, title)

def plot_cr_count(m, path):
    count = m.groupby('CR').count()
    count = count.reset_index()

    plt.figure(figsize=(16, 9))
    sns.lineplot(x='CR', y='Name', data=count, label='Total')
    sns.lineplot(x='CR', y='AC', data=count, label='Armor Class')
    sns.lineplot(x='CR', y='cmd', data=count, label='Combat Maneuver Defense')
    plt.title('Count of samples by challenge rating')
    plt.xlabel('Challenge Rating')
    plt.ylabel('Count')
    fn = os.path.join(path, 'count.png')
    plt.savefig(fn)
    plt.close()

def plot_distribution_with_fits(series, fn, title='', xlabel=None):
    mean = series.mean()
    std = series.std()
    median = series.median()
    mi = series.min()
    ma = series.max()

    x_lin = np.linspace(mi, ma, num=200)
    y_normal = norm.pdf(x_lin, mean, std)

    ms = MeanShift().fit(series.dropna().values.reshape(-1, 1))
    cluster = ms.cluster_centers_[0]

    cp = sns.color_palette()

    plt.figure(figsize=(16, 9))
    sns.distplot(series.dropna(), label='Data')
    sns.lineplot(x=x_lin, y=y_normal, label='Gaussian approximation')
    ylim = plt.ylim()
    plt.plot([mean]*2, ylim, label='Mean', c=cp[2])
    plt.plot([mean+std]*2, ylim, label='Std', c=cp[2], linestyle='dashed')
    plt.plot([mean-std]*2, ylim, c=cp[2], linestyle='dashed')
    plt.plot([median]*2, ylim, label='Median', c=cp[3])
    plt.plot([cluster]*2, ylim, label='MAP', c=cp[4])
    plt.legend()
    plt.title(title)
    if xlabel is None:
        xlabel = title
    plt.xlabel(xlabel)
    plt.savefig(fn)
    plt.close()

def plot_ac_cmd_distr_for_cr_with_fits(m, path):
    names = ['AC', 'cmd']
    subdirs = [
        os.path.join(path, 'ac'),
        os.path.join(path, 'cmd')
        ]
    long_names = ['Armor Class', 'Combat Maneuver Defense']

    for subdir in subdirs:
        if not os.path.exists(subdir):
            os.makedirs(subdir)

    for i in tqdm(range(1, 21)):
        sub_df = m[m['CR'] == i]

        for name, subdir, lname in zip(names, subdirs, long_names):
            fn = os.path.join(subdir, f'{name}_cr{i:02d}.png')
            plot_distribution_with_fits(sub_df[name], fn, title=lname)

def plot_ac_cmd_over_cr(m, path):
    names = ['AC', 'cmd']
    long_names = ['Armor Class', 'Combat Maneuver Defense']

    for name, lname in zip(names, long_names):
        plt.figure(figsize=(16,9))
        sns.lineplot(x='CR', y='AC', data=m, label='Mean with Std')
        fn = os.path.join(path, f'{name.lower()}_over_cr.png')
        plt.legend()
        plt.title(f'{lname} over Challenge Rating')
        plt.xlabel('Challenge Rating')
        plt.ylabel(lname)
        plt.savefig(fn)
        plt.close()


if __name__ == '__main__':
    from dotenv import dotenv_values
    from monsters import Monsters

    path = dotenv_values()['MONSTER_PATH']

    m = Monsters(path)

    results_path = './results'

    if not os.path.exists(results_path):
        print('Creating results folder.')
        os.makedirs(results_path)

    plot_important_distributions(m, results_path)
    plot_cr_count(m, results_path)
    plot_ac_cmd_distr_for_cr_with_fits(m, results_path)
    plot_ac_cmd_over_cr(m, results_path)

