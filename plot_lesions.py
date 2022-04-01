# Hernando Martinez April 2022
# generates plots from results from quantify_lesions.py


# %%
import sys
import os
import pandas as pd
import matplotlib.pyplot as plt

AUD_FILE = 'auditory_projections_caudoputamen_proportions.txt'


def add_aud_proj(ax, aud_file):
    if os.path.exists(aud_file):
        # read as pandas
        df = pd.read_csv(aud_file)
        ax.fill_between(25 / 1000 * df['25umpx_atlas_position'],
                        df['coverage'],
                        '-',
                        label='AUD projections',
                        color='red',
                        alpha=.1)
    
    return ax


def generate_lesion_plot_all(path_to_file):
    dir_path = os.path.dirname(path_to_file)
    f_name = os.path.basename(path_to_file).split('.')[0]
    out_path = os.path.join(dir_path, f_name)
    # read as pandas
    df = pd.read_csv(path_to_file)
    colors = ['black', 'blue']
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

    # fig.show()
    # save
    plt.tight_layout()
    plt.savefig(out_path + '_all.pdf', transparent=True, bbox_inches='tight')
    
    # return df


# ptf = '/mnt/c/Users/herny/Desktop/SWC/Data/Microscopy_Data/Histology_of_tail_lesions/Chronic_lesions/Processed_data/quantify_lesions_output.txt'
# df = generate_lesion_plot(ptf)

def generate_lesion_plot_individuals(path_to_file):
    dir_path = os.path.dirname(path_to_file)
    f_name = os.path.basename(path_to_file).split('.')[0]
    out_path = os.path.join(dir_path, f_name)
    # read as pandas
    df = pd.read_csv(path_to_file)
    colors = ['black', 'blue']
    animals = df.mouse_name.unique()
    _, axs = plt.subplots(len(animals), 1, figsize=[12, 2 * len(animals)],
                          sharex=True, sharey=True)
    axs = axs.ravel()

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
                'o-',
                label=eg,
                color=color,
                alpha=.5)

        ax.set_xlabel('Anterio-posterior axis position (mm)')
        ax.set_ylabel('Striatal area covered by cells (%)')
        ax.set_title(an_name)
    
    #TODO add the amount of coverage of auditory input

    # fig.show()
    # save
    plt.tight_layout()
    plt.savefig(out_path + '_individuals.pdf', transparent=True, bbox_inches='tight')
    
    
# %%
if __name__ == '__main__':
    # check input
    if len(sys.argv) not in [2]:
        sys.exit('Incorrect number of arguments, please run like this:\
            python {} path_to_output_file'.format(os.path.basename(__file__)))
    # catch input
    infile = sys.argv[1]
    # check if file is there
    if not os.path.exists(infile):
        sys.exit('{} does not exist'.format(infile))

    # get information about the auditory projections
    
    # generate a plot with all data
    generate_lesion_plot_all(infile)
    # generate a plot for each mouse
    generate_lesion_plot_individuals(infile)
    print('Done')


# %%

