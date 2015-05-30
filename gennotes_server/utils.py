import os

from distutils import util


def to_bool(env, default='false'):
    """
    Convert a string to a bool.
    """
    return bool(util.strtobool(os.getenv(env, default)))


def map_chrom_to_index(chrom_str):
    "Converts chromosome labels to standard GenNotes chromosome index."
    if chrom_str.startswith('chr' or 'Chr'):
        chrom_str = chrom_str[3:]
    if chrom_str.startswith('ch' or 'Ch'):
        chrom_str = chrom_str[2:]
    try:
        return str(int(chrom_str))
    except ValueError:
        if chrom_str == 'X':
            return '23'
        elif chrom_str == 'Y':
            return '24'
        elif chrom_str in ['M', 'MT']:
            return '25'
    raise ValueError("Can't determine chromosome for {0}".format(chrom_str))
