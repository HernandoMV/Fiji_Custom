# Hernando Martinez April 2022
# generates plots from results from quantify_lesions.py


# %%
import sys
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from math import ceil

AUD_FILE = 'auditory_projections_caudoputamen_proportions.txt'
BADSL_FILE = 'slices_to_remove_intermodes.txt'


def beautify_axis(ax, botax=False):
    ax.axis('on')
    ax.set_ylim(-0.05, 1.05)
    ax.set_xlim(4.3, 7.7)
    ax.tick_params(axis='both', direction='in')
    # get rid of the frame
    for spine in ax.spines.values():
        spine.set_visible(False)

    if ax.is_first_col():
        # set y ticks
        ax.set_yticks([0, .5, 1])
        ax.set_yticklabels(['0', '50', '100'])
    else:
        ax.set_ylabel('')
        ax.set_yticks([])

    if ax.is_last_row() or botax:
        # set x ticks
        ax.set_xticks([4.5, 5.5, 6.5, 7.5])
        ax.set_xticklabels(['4.5', '5.5', '6.5', '7.5'])
        pass
    else:
        ax.set_xlabel('')
        ax.set_xticks([])


def remove_bad_slices(df, bfile):
    idxs_to_remove = []
    with open(bfile, 'r') as f:
        lines = f.readlines()
    for line in lines:
        # parse
        p = line.split('_')
        # find index in dataframe
        mask = np.logical_and(df.mouse_name == p[0], df.slide == int(p[2].split('-')[1]))
        mask = np.logical_and(mask, df.slice == int(p[3].split('-')[1]))
        idx = df[mask].index[0]
        # append
        idxs_to_remove.append(idx)
    # remove and return
    return df.drop(idxs_to_remove)


def get_out_name(pathname):
    dir_path = os.path.dirname(pathname)
    f_name = os.path.basename(pathname).split('.')[0]
    return dir_path, os.path.join(dir_path, f_name)


def add_aud_proj(ax, aud_file):
    if os.path.exists(aud_file):
        # read as pandas
        df = pd.read_csv(aud_file)
        ax.fill_between(25 / 1000 * df['25umpx_atlas_position'],
                        df['coverage'],
                        '-',
                        label='AUD projections',
                        color='black',
                        alpha=.1)

    return ax


def generate_lesion_plot_all(path_to_file):
    dir_path, out_path = get_out_name(path_to_file)
    # read as pandas
    df = pd.read_csv(path_to_file)
    # remove bad slices
    df = remove_bad_slices(df, os.path.join(dir_path, BADSL_FILE))
    colors = ['black', 'red']
    _, ax = plt.subplots(1, 1, figsize=[12, 5])

    # add the amount of coverage of auditory input
    ax = add_aud_proj(ax, os.path.join(dir_path, AUD_FILE))

    for animal in df.mouse_name.unique():
        an_df = df[df.mouse_name == animal]
        an_df = an_df.sort_values('25umpx_atlas_position')
        eg = an_df.experimental_group.unique()[0]
        if eg == 'control':
            color = colors[0]
        if eg == 'lesion':
            color = colors[1]
        ax.plot(25 / 1000 * an_df['25umpx_atlas_position'],
                an_df['proportion_intact'],
                'o-',
                label=eg,
                color=color,
                alpha=.5)

    ax.set_xlabel('Anterio-posterior axis position (mm)')
    ax.set_ylabel('Striatal area covered by cells (%)')
    # set y ticks
    ax.set_yticks([0, .5, 1])
    ax.set_yticklabels(['0', '50', '100'])

    # fig.show()
    # save
    plt.tight_layout()
    plt.savefig(out_path + '_all.pdf', transparent=True, bbox_inches='tight')


def generate_lesion_plot_individuals(path_to_file):
    dir_path, out_path = get_out_name(path_to_file)
    # read as pandas
    df = pd.read_csv(path_to_file)
    # remove bad slices
    df = remove_bad_slices(df, os.path.join(dir_path, BADSL_FILE))
    colors = ['grey', 'red']
    ncols = 5
    animals = df.mouse_name.unique()
    fig, axs = plt.subplots(ceil(len(animals) / ncols), ncols,
                            figsize=[12, int(2 / ncols * len(animals))])
                            # sharex=True, sharey=True)
    axs = axs.ravel()
    for ax in axs:
        ax.axis('off')
    
    for i, animal in enumerate(animals):
        ax = axs[i]
        an_df = df[df.mouse_name == animal]
        an_df = an_df.sort_values('25umpx_atlas_position')
        an_name = an_df.mouse_name.unique()[0]
        eg = an_df.experimental_group.unique()[0]
        if eg == 'control':
            color = colors[0]
        if eg == 'lesion':
            color = colors[1]
        
        # add the amount of coverage of auditory input
        ax = add_aud_proj(ax, os.path.join(dir_path, AUD_FILE))
        
        ax.plot(25 / 1000 * an_df['25umpx_atlas_position'],
                an_df['proportion_intact'],
                '-',
                label=eg,
                color=color,
                alpha=1)

        ax.text(0.3, 0.3, an_name, size=12, transform=ax.transAxes)
        botax = False
        if i in [8, 9]:
            botax = True
        beautify_axis(ax, botax)
        # ax.set_xlabel('Anterio-posterior axis position (mm)')
        # ax.set_ylabel('Striatal area covered by cells (%)')
    
    fig.text(0.5, 0.0, 'Anterio-posterior axis position (mm)', ha='center')
    fig.text(0.0, 0.5, 'Striatal area covered by cells (%)', va='center', rotation='vertical')
    # fig.show()
    # save
    plt.tight_layout()
    plt.savefig(out_path + '_individuals.pdf', transparent=True, bbox_inches='tight')


def generate_lesion_plot_all_binned(path_to_file):
    dir_path, out_path = get_out_name(path_to_file)
    # read as pandas
    df = pd.read_csv(path_to_file)
    # remove bad slices
    df = remove_bad_slices(df, os.path.join(dir_path, BADSL_FILE))

    # bin the data and calculate the relative loss to the controls
    # bin every 250 microns (10 slices)
    sl_to_bin = 10
    df["binned_position"] = (df['25umpx_atlas_position'] // sl_to_bin) * sl_to_bin + sl_to_bin / 2
    # get the mean and std
    data_mean = df.groupby(['binned_position', 'experimental_group'])["proportion_intact"].mean().reset_index()
    st_err_mean = df.groupby(['binned_position', 'experimental_group'])["proportion_intact"].std().reset_index()
    data_mean['low_bound'] = data_mean['proportion_intact'] - st_err_mean['proportion_intact']
    data_mean['high_bound'] = data_mean['proportion_intact'] + st_err_mean['proportion_intact']

    # calculate the relative reduction at each point
    dfles = data_mean[data_mean.experimental_group == 'lesion'].copy()
    dfcon = data_mean[data_mean.experimental_group == 'control'].copy()
    xs = list(np.sort(dfles.binned_position.unique()))
    ys_rel = []
    ys_high = []
    ys_low = []
    for i, x in enumerate(xs):
        # find the mean of control
        if x in list(dfcon.binned_position):
            ycon = dfcon[dfcon.binned_position == x].proportion_intact.iloc[0]
        else:
            # interpolate THIS WILL FAIL IF IT IS IN THE EDGE
            lb = dfcon[dfcon.binned_position == xs[i - 1]].proportion_intact.iloc[0]
            hb = dfcon[dfcon.binned_position == xs[i + 1]].proportion_intact.iloc[0]
            ycon = (lb + hb) / 2
        y = dfles[dfles.binned_position == x].proportion_intact.iloc[0] / ycon
        ys_rel.append(y)
        std = dfles[dfles.binned_position == x].high_bound.iloc[0] - dfles[dfles.binned_position == x].proportion_intact.iloc[0]
        ys_high.append(y + std)
        ys_low.append(y - std)

    color = 'red'
    _, ax = plt.subplots(1, 1, figsize=[12, 5])

    # add the amount of coverage of auditory input
    ax = add_aud_proj(ax, os.path.join(dir_path, AUD_FILE))

    x = [25 / 1000 * val for val in xs]
    plt.plot(x, ys_rel, color=color)
    plt.fill_between(x, ys_low, ys_high, where=ys_high >= ys_low, color=color, alpha=.2, interpolate=False)

    ax.set_xlabel('Anterio-posterior axis position (mm)')
    ax.set_ylabel('Striatal area covered by cells (%)')
    # set y ticks
    ax.set_yticks([0, .5, 1])
    ax.set_yticklabels(['0', '50', '100'])

    # fig.show()
    # save
    plt.tight_layout()
    plt.savefig(out_path + '_all_binned.pdf', transparent=True, bbox_inches='tight')

    
# %%
if __name__ == '__main__':
    # check input
    # if len(sys.argv) not in [2]:
    #     sys.exit('Incorrect number of arguments, please run like this:\
    #         python {} path_to_output_file'.format(os.path.basename(__file__)))
    # # catch input
    # infile = sys.argv[1]
    # # check if file is there
    # if not os.path.exists(infile):
    #     sys.exit('{} does not exist'.format(infile))

    infile = '/mnt/c/Users/herny/Desktop/SWC/Data/Microscopy_Data/Histology_of_tail_lesions/Chronic_lesions/Processed_data/quantify_lesions_output.txt'
    
    # generate a plot with all data
    print('   --- plotting all data...')
    # generate_lesion_plot_all(infile)
    # generate a plot for each mouse
    print('   --- plotting individual animals...')
    # generate_lesion_plot_individuals(infile)
    print('   --- plotting all animals binned...')
    generate_lesion_plot_all_binned(infile)
    print('Done')


# %%

