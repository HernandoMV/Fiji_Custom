# Hernando M. Vergara, SWC
# Feb 2021
# text_manipulation.py
# generic functions


def get_core_names(file_names, core_name):
    out_names = []
    for name in file_names:
        if core_name in name:
            # parse for the Slices
            name_pieces = name.split('_')
            mr_index_array = [i for i, s in enumerate(name_pieces) if 'manualROI-' in s]
            # check that there is only one occurrence
            if len(mr_index_array) == 1:
                out_names.append('_'.join(name_pieces[0:(mr_index_array[0] + 1)]))
            else:
                raise NameError('Your file name should not contain slice-')
    return set(out_names)