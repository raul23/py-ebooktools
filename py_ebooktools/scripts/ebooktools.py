#!/usr/bin/env python
"""This script is a Python port of `ebook-tools`_ written in Shell by `na--`_.

References
----------
* `ebook-tools`_

.. URLs

.. external links
.. _ebook-tools: https://github.com/na--/ebook-tools
.. _na--: https://github.com/na--
"""
import argparse

# TODO: remove
# import ipdb

import py_ebooktools
from py_ebooktools import (edit_config, convert_to_txt, find_isbns,
                           split_into_folders)
from py_ebooktools.configs import default_config as default_cfg
from py_ebooktools.utils.genutils import (get_config_dict, init_log,
                                          namespace_to_dict,
                                          override_config_with_args, setup_log)

logger = init_log(__name__, __file__)

# =====================
# Default config values
# =====================
FILES_PER_FOLDER = default_cfg.files_per_folder
FOLDER_PATTERN = default_cfg.folder_pattern
ISBN_REGEX = default_cfg.isbn_regex
LOGGING_FORMATTER = default_cfg.logging_formatter
LOGGING_LEVEL = default_cfg.logging_level
OCR_ONLY_FIRST_LAST_PAGES = default_cfg.ocr_only_first_last_pages
OUTPUT_FILE = default_cfg.output_file
OUTPUT_FILENAME_TEMPLATE = default_cfg.output_filename_template
OUTPUT_FOLDER = default_cfg.output_folder
OUTPUT_METADATA_EXTENSION = default_cfg.output_metadata_extension
START_NUMBER = default_cfg.start_number

# ====================
# Other default values
# ====================
_LOG_CFG = "log"
_MAIN_CFG = "main"


# Ref.: https://stackoverflow.com/a/14117511/14664104
def check_positive(value):
    try:
        # TODO: 2.0 rejected
        ivalue = int(value)
        if ivalue <= 0:
            raise argparse.ArgumentTypeError(
                f"{value} is an invalid positive int value")
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"{value} is an invalid positive int value")
    else:
        return ivalue


def parse_edit_args(main_cfg):
    if main_cfg.reset:
        return edit_config.reset_file(main_cfg.cfg_type, main_cfg.app)
    else:
        return edit_config.edit_file(main_cfg.cfg_type, main_cfg.app)


def process_returned_values(returned_values):
    # ================================
    # Process previous returned values
    # ================================

    def log_opts_overriden(opts_overriden, msg, log_level='info'):
        nb_items = len(opts_overriden)
        for i, (cfg_name, old_v, new_v) in enumerate(opts_overriden):
            msg += f'\t {cfg_name}: {old_v} --> {new_v}'
            if i + 1 < nb_items:
                msg += "\n"
        getattr(logger, log_level)(msg)

    # Process 1st returned values: default args overriden by config options
    if returned_values.default_args_overriden:
        msg = "Default arguments overridden by config options:\n"
        log_opts_overriden(returned_values.default_args_overriden, msg)
    # Process 2nd returned values: config options overriden by args
    if returned_values.config_opts_overridden:
        msg = "Config options overridden by command-line arguments:\n"
        log_opts_overriden(returned_values.config_opts_overridden, msg, 'debug')
    # Process 3rd returned values: arguments not found in config file
    """
    if args_not_found_in_config:
        msg = 'Command-line arguments not found in config file: ' \
              f'\n\t{args_not_found_in_config}'
        logger.debug(msg)
    """


def setup_argparser():
    """Setup the argument parser for the command-line script.

    Returns
    -------
    parser : argparse.ArgumentParser
        Argument parser.

    """
    # Setup the parser
    parser = argparse.ArgumentParser(
        description='''\
This program is a Python port of ebook-tools written in Shell by na-- (See
https://github.com/na--/ebook-tools).

This program is a collection of tools for automated and
semi-automated organization and management of large ebook collections.

See subcommands below for a list of the tools that can be used.
''',
        formatter_class=argparse.RawDescriptionHelpFormatter)
    default_msg = " (default: {})"
    # ===============
    # General options
    # ===============
    # TODO: package name too? instead of program name
    parser.add_argument('--version', action='version',
                        version=f'%(prog)s v{py_ebooktools.__version__}')
    parser.add_argument("-q", "--quiet", action="store_true",
                        help="Enable quiet mode, i.e. nothing will be printed.")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help='''Print various debugging information, e.g. print
                        traceback when there is an exception.''')
    parser.add_argument(
        "-d", "--dry-run", dest='dry_run', action="store_true",
        help='''If this is enabled, no file rename/move/symlink/etc.
        operations will actually be executed.''')
    parser.add_argument(
        "-r", "--reverse", dest='file_sort_reverse', action="store_true",
        help='''If this is enabled, the files will be sorted in reverse
        (i.e. descending) order. By default, they are sorted in ascending
        order.''')
    parser.add_argument(
        '--loglvl', dest='logging_level',
        choices=['debug', 'info', 'warning', 'error'],
        help='Set logging level for all loggers.'
             + default_msg.format(LOGGING_LEVEL))
    parser.add_argument(
        '--logfmt', dest='logging_formatter',
        choices=['console', 'simple', 'only_msg'],
        help='Set logging formatter for all loggers.'
             + default_msg.format(LOGGING_FORMATTER))
    # ===========================================================================
    # Options related to extracting ISBNs from files and finding metadata by ISBN
    # ===========================================================================
    parser_isbns_group = parser.add_argument_group(
        title='Options related to extracting ISBNS from files and finding '
              'metadata by ISBN')
    # TODO: add look-ahead and look-behind info, see https://bit.ly/2OYsY76
    parser_isbns_group.add_argument(
        "-i", "--isbn-regex", dest='isbn_regex',
        help='''This is the regular expression used to match ISBN-like
        numbers in the supplied books.''' + default_msg.format(ISBN_REGEX))
    # ===============
    # Options for OCR
    # ===============
    parser_ocr_group = parser.add_argument_group(
        title='Options for OCR')
    parser_ocr_group.add_argument(
        "--ocr", "--ocr-enabled", dest='ocr_enabled',
        choices=['always', 'true', 'false'],
        help='''Whether to enable OCR for .pdf, .djvu and image files. It is
        disabled by default.''')
    parser_ocr_group.add_argument(
        "--ocrop", "--ocr-only-first-last-pages",
        dest='ocr_only_first_last_pages', metavar='PAGES', nargs=2,
        help='''Value (n,m) instructs the scripts to convert only the first n
        and last m pages when OCR-ing ebooks.'''
             + default_msg.format(OCR_ONLY_FIRST_LAST_PAGES))
    # =============================================
    # Options related to the input and output files
    # =============================================
    parser_input_output_group = parser.add_argument_group(
        title='Options related to the input and output files')
    parser_input_output_group.add_argument(
        '--oft', '--output-filename-template', dest='output_filename_template',
        metavar='TEMPLATE',
        help='''This specifies how the filenames of the organized files will
        look. It is a bash string that is evaluated so it can be very flexible
        (and also potentially unsafe).''' +
             default_msg.format(OUTPUT_FILENAME_TEMPLATE))
    parser_input_output_group.add_argument(
        '--ome', '--output-metadata-extension', dest='output_metadata_extension',
        metavar='EXTENSION',
        help='''If keep_metadata is enabled, this is the extension of the
        additional metadata file that is saved next to each newly renamed file.'''
             + default_msg.format(OUTPUT_METADATA_EXTENSION))
    # ===========
    # Subcommands
    # ===========
    subparsers = parser.add_subparsers(
        title='subcommands', description=None, dest='subcommand', required=True,
        help=None)
    # TODO: add aliases, see https://bit.ly/3s2fq87
    # ==========
    # Edit files
    # ==========
    # create the parser for the "edit" command
    parser_edit = subparsers.add_parser(
        'edit', help='''Edit a configuration file.''')
    parser_edit.add_argument(
        'cfg_type', choices=[_MAIN_CFG, _LOG_CFG],
        help='''The config file to edit which can either be the main
            configuration file ('{}') or the logging configuration file
            ('{}').'''.format(_MAIN_CFG, _LOG_CFG))
    group_edit = parser_edit.add_mutually_exclusive_group()
    group_edit.add_argument(
        '-a', '--app', metavar='NAME', nargs='?',
        help='''Name of the application to use for editing the config file. If
        no name is given, then the default application for opening this type of
        file will be used.''')
    group_edit.add_argument(
        "-r", "--reset", action="store_true",
        help='''Reset a configuration file ('config' or 'log') with factory
        default values.''')
    parser_edit.set_defaults(func=parse_edit_args)
    # ==============
    # Convert to txt
    # ==============
    # create the parser for the "convert" command
    parser_convert = subparsers.add_parser(
        'convert',
        help='''Convert the supplied file to a text file. It can optionally
        also use *OCR* for `.pdf`, `.djvu` and image files.''')
    parser_convert.add_argument(
        'input_file',
        help='''The input file to be converted to a text file.''')
    parser_convert.add_argument(
        '-o', '--output-file', dest='output_file', metavar='OUTPUT',
        help='''The output file text. By default, it is saved in the current
        working directory.''' + default_msg.format(OUTPUT_FILE))
    parser_convert.set_defaults(func=convert_to_txt.convert)
    # ==========
    # Find ISBNs
    # ==========
    # create the parser for the "find" command
    parser_find = subparsers.add_parser(
        'find',
        help='''Try to find valid ISBNs inside a file or in a string if no file
        was specified. Searching for ISBNs in files uses progressively more
        resource-intensive methods until some ISBNs are found.''')
    parser_find.add_argument(
        'input_data',
        help='''Can either be the path to a file or a string. The input will
        be searched for ISBNs.''')
    parser_find.set_defaults(func=find_isbns.find)
    # ==================
    # split-into-folders
    # ==================
    # create the parser for the "split-into-folders" command
    parser_split_into_folders = subparsers.add_parser(
        'split',
        help='''Split the supplied ebook files (and the accompanying metadata
        files if present) into folders with consecutive names that each contain
        the specified number of files.''')
    parser_split_into_folders.add_argument(
        'folder_with_books',
        help='''Folder with books which will be recursively scanned for files.
        The found files (and the accompanying metadata files if present) will
        be split into folders with consecutive names that each contain the
        specified number of files. The default value is the current working
        directory.''')
    parser_split_into_folders.add_argument(
        '-o', '--output-folder', dest='output_folder', metavar='PATH',
        help='''The output folder in which all the new consecutively named
        folders will be created. The default is the current working
        directory.''' + default_msg.format(OUTPUT_FOLDER))
    parser_split_into_folders.add_argument(
        '-s', '--start-number', dest='start_number', type=int,
        help='''The number of the first folder.'''
             + default_msg.format(START_NUMBER))
    parser_split_into_folders.add_argument(
        '-f', '--folder-pattern', dest='folder_pattern', metavar='PATTERN',
        help='''The print format string that specifies the pattern with which
        new folders will be created. By default it creates folders like
        00000000, 00001000, 00002000, .....'''
             + default_msg.format(FOLDER_PATTERN).replace('%', '%%'))
    parser_split_into_folders.add_argument(
        '--fpf', '--files-per-folder', dest='files_per_folder',
        type=check_positive,
        help='''How many files should be moved to each folder.'''
             + default_msg.format(FILES_PER_FOLDER))
    parser_split_into_folders.set_defaults(func=split_into_folders.split)
    return parser


def main():
    try:
        parser = setup_argparser()
        args = parser.parse_args()
        # Get main cfg dict
        main_cfg = argparse.Namespace(**get_config_dict('main'))
        returned_values = override_config_with_args(main_cfg, parser)
        setup_log(main_cfg.quiet, main_cfg.verbose,
                  logging_level=main_cfg.logging_level,
                  logging_formatter=main_cfg.logging_formatter)
        # Override main configuration from file with command-line arguments
        process_returned_values(returned_values)
    except AssertionError as e:
        # TODO (IMPORTANT): use same logic as in Darth-Vader-RPi
        # TODO: add KeyboardInterruptError
        logger.error(e)
        return 1
    else:
        if args.subcommand == 'edit':
            return args.func(main_cfg)
        else:
            return args.func(**namespace_to_dict(main_cfg))


if __name__ == '__main__':
    # Convert
    # ebooktools convert -o ~/test/ebooktools/output.txt ~/test/ebooktools/pdf_to_convert.pdf
    #
    # Convert with debug and ocr=always
    # ebooktools --ocr always convert -o ~/test/ebooktools/output.txt ~/test/ebooktools/pdf_to_convert.pdf
    #
    # Find
    # ebooktools --loglvl debug --logfmt console find "978-3-319-667744 978-1-292-02608-4 0000000000 0123456789 1111111111"
    #
    # Split
    # ebooktools --loglvl debug --logfmt simple split -o output_folder/ folder_with_books/
    # ebooktools --loglvl debug --logfmt simple split --fpf 3
    retcode = main()
    msg = f'Program exited with {retcode}'
    if retcode == 1:
        logger.error(msg)
    else:
        logger.info(msg)
