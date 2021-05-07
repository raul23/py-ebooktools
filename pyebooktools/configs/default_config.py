"""Options for the ebooktools.py script

`ebooktools.py`_ is a Python port of the Shell scripts `ebook-tools` developed
by `na--`_ for organizing and managing ebook collections.

The options are described in full details in the Python project's `README`_

IMPORTANT: these options can also be passed to the Python script
`ebooktools.py`_ via command-line parameters. Also, command-line parameters
supersede the variables defined in this configuration file. Most parameters are
not required and if nothing is specified, the default value will be used.

The options are separated based on sections:
1. General options
  1.1 General control flags
  1.2 Options related to extracting ISBNs from files and finding metadata by ISBN
  1.3 Options for OCR
  1.4 Options related to extracting and searching for non-ISBN metadata
  1.5 Options related to the input and output files
  1.6 Miscellaneous options
2. Subcommand options
  2.1 convert_to_txt
  2.2 edit_config
  2.3 find_isbns
  2.4 fix_ebooks
  2.5 interactive_organizer
  2.6 organize_ebooks
    2.6.1 Specific options for organizing files
    2.6.2 Output options
  2.7 remove_extras
  2.8 rename_calibre_library
  2.9 split_into_folders

References
----------
* `ebook-tools`_

.. external links
.. _ebook-tools: https://github.com/na--/ebook-tools
.. _ebooktools.py: https://github.com/raul23/pyebooktools/blob/master/pyebooktools/scripts/ebooktools.py
.. _na--: https://github.com/na--
.. _README: https://github.com/raul23/pyebooktools#readme
"""
import os

from pyebooktools.configs import get_without_isbn_ignore


# ==================
# 1. General options
# ==================
# All of these options are part of the common library and may affect some or
# all of the subcommands.

# 1.1 General control flags
# =========================
quiet = False
verbose = False
dry_run = False
symlink_only = False
keep_metadata = False
logging_level = 'info'
logging_formatter = 'only_msg'

# 1.2 Options related to extracting ISBNs from files and finding metadata by ISBN
# ===============================================================================
isbn_regex = '(?<![0-9])(-?9-?7[789]-?)?((-?[0-9]-?){9}[0-9xX])(?![0-9])'
isbn_blacklist_regex = '^(0123456789|([0-9xX])\\2{9})$'
isbn_direct_grep_files = '^text/(plain|xml|html)$'
isbn_ignored_files = '^(image/(gif|svg.+)|application/(x-shockwave-flash|CDFV2|vnd.ms-opentype|x-font-ttf|x-dosexec|vnd.ms-excel|x-java-applet)|audio/.+|video/.+)$'
isbn_grep_rf_scan_first = 400
isbn_grep_rf_reverse_last = 50
# False to disable the functionality or (first_lines,last_lines) to enable it
isbn_grep_reorder_files = (isbn_grep_rf_scan_first, isbn_grep_rf_reverse_last)
# NOTE: If you use Calibre versions that are older than 2.84, it's required to
# manually set the following option to an empty string.
isbn_metadata_fetch_order = ['Goodreads', 'Amazon.com', 'Google', 'ISBNDB', 'WorldCat xISBN', 'OZON.ru']

# 1.3 Options for OCR
# ===================
ocr_enabled = False
ocr_only_first_last_pages = (7, 3)
ocr_command = 'tesseract_wrapper'

# 1.4 Options related to extracting and searching for non-ISBN metadata
# =====================================================================
token_min_length = 3
tokens_to_ignore = 'ebook|book|novel|series|ed(ition)?|vol(ume)?|${RE_YEAR}'
organize_without_isbn_sources = ['Goodreads' ,'Amazon.com', 'Google']

# 1.5 Options related to the input and output files
# =================================================
output_folder = os.getcwd()
output_filename_template = "${d[AUTHORS]// & /, } - ${d[SERIES]:+[${d[SERIES]}] " \
                           "- }${d[TITLE]/:/ -}${d[PUBLISHED]:+ (${d[PUBLISHED]%%-*})}" \
                           "${d[ISBN]:+ [${d[ISBN]}]}.${d[EXT]}"
# If `keep_metadata` is enabled, this is the extension of the additional
# metadata file that is saved next to each newly renamed file.
output_metadata_extension = 'meta'

# 1.6 Miscellaneous options
# =========================
# file_sort_flags = []
# Reverse sort
reverse = False
# debug_prefix_length = 40

# =====================
# 2. Subcommand options
# =====================

# 2.1 convert_to_txt
# ==================
# Some of the general options affect this subcommand's behavior a lot, especially
# the OCR ones (see '1.3 Options for OCR').
output_file = 'output.txt'

# 2.2 edit_config
# ===============
# Name of the application to use for editing the config file.
# If no name is given, then the default application for opening this type of
# file will be used.
app = None

# 2.3 find_isbns
# ==============
# Some general options affect this subcommand (especially the ones related to
# extracting ISBNs from files, see section 1.2 above).
isbn_ret_separator = '\n'

# 2.4 fix_ebooks
# ==============
# output_folder is by default current directory

# 2.5 interactive_organizer
# =========================
# output_folders = []
# quick_mode = False
# custom_move_base_dir = None
# restore_original_base_dir = None
# diacritic_difference_masking = ?
# match_partial_words = False

# 2.6 organize_ebooks
# ===================
# 2.6.1 Specific options for organizing files
# -------------------------------------------
corruption_check_only = False
tested_archive_extensions = '^(7z|bz2|chm|arj|cab|gz|tgz|gzip|zip|rar|xz|tar|epub|docx|odt|ods|cbr|cbz|maff|iso)$'
organize_without_isbn = False
without_isbn_ignore = get_without_isbn_ignore()
# TODO: why '?' in pptx, see https://bit.ly/2ryWlgt
pamphlet_included_files = '\.(png|jpg|jpeg|gif|bmp|svg|csv|pptx?)$'
pamphlet_excluded_files = '\.(chm|epub|cbr|cbz|mobi|lit|pdb)$'
pamphlet_max_pdf_pages = 50
pamphlet_max_filesize_kib = 250

# 2.6.2 Output options
# --------------------
# output_folder is by default current directory
# If organize_without_isbn is enabled, this is the folder to which all ebooks
# that were renamed based on non-ISBN metadata will be moved to.
output_folder_uncertain = None
# If specified, corrupt files will be moved to this folder.
output_folder_corrupt = None
# If specified, pamphlets will be moved to this folder.
output_folder_pamphlets = None

# 2.8 remove_extras
# =================
# output_folder is by default current directory

# 2.8 rename_calibre_library
# ==========================
# output_folder is by default current directory
save_metadata = 'recreate'

# 2.9 split_into_folders
# ======================
# output_folder is by default current directory
start_number = 0
folder_pattern = '%05d000'
files_per_folder = 1000
