#!/usr/bin/python

"""
MS3 Prep Tool

Walks through the current directory and all sub-directories, and checks all assemblies and modules
to ensure they have a title and abstract. Adds the abstract tag when missing and an appropriate
abstract target can be found. Reports all assemblies and modules missing these two elements.

Created by: Andrew Dahms
Created on: 10 September, 2020
Updated on: 01 October, 2020
"""

import os
import sys

__no_op__ = False
__files_missing_abstracts__ = []
__abstract_tag__ = '[role="_abstract"]'
__resource_tag__ = '[role="_additional-resources"]'



def print_header():
    print('==================================================')
    print('MS3 Prep                                          ')
    print('==================================================')
    print()


# Test for abstract tag
def test_abstract(lines, noop, file_name):

    processed_lines = []

    has_abstract = any(__abstract_tag__ in line for line in lines)

    if has_abstract:

        return lines

    else:

        line_count = len(lines)

        line_no = 0

        abstract_search_complete = False

        while line_no < line_count:

            # Ignore lines that start with common prefixes before the abstract
            if lines[line_no].strip() == '' or lines[line_no].strip().startswith(
                    ('#', '/', '[', '=', 'ifdef','ifndef','assembly_','toc','include',':')):

                processed_lines.append(lines[line_no])

                line_no += 1

            else:

                # If we've reached a line that starts with one of these characters, something has gone wrong
                if not abstract_search_complete and lines[line_no].strip().startswith(('|', '*', 'include', '.')):

                    __files_missing_abstracts__.append(file_name)

                    abstract_search_complete = True

                # If we've reached any other line, we declare it the abstract
                elif not abstract_search_complete:

                    if not has_abstract and not noop:
                        processed_lines.append(__abstract_tag__ + '\n')

                        has_abstract = True

                        abstract_search_complete = True

                processed_lines.append(lines[line_no])

                line_no += 1

        return processed_lines


# Test for additional resources tag
def test_additional_resources(lines, noop):

    processed_lines = []

    line_count = len(lines)

    line_no = 0

    while line_no < line_count:

        if lines[line_no].strip().startswith('.Additional resources') or lines[line_no].startswith('== Additional resources'):

            if line_no > 1:

                if lines[line_no - 1].strip() != __resource_tag__:

                    if not noop:

                        processed_lines.append(__resource_tag__ + '\n')

        processed_lines.append(lines[line_no])

        line_no += 1

    return processed_lines


def test_syntax_updates(lines, noop):

    processed_lines = []

    line_count = len(lines)

    line_no = 0

    while line_no < line_count:

        if lines[line_no].strip().__contains__(':system-module-type:'):

            if not noop:

                lines[line_no] = lines[line_no].replace(':system-module-type:',':_module-type:')

        processed_lines.append(lines[line_no])

        line_no += 1

    return processed_lines

# Main processing routine
def process(noop):

    files_missing_titles = []

    for dir_name, sub_dir_list, file_list in os.walk('.'):

        # Skip private directories
        if dir_name.startswith('./.'):
            continue

        # Print processing message
        print('Processing %s...' % dir_name)

        # Process all AsciiDoc files that start with valid prefixes
        for file_name in file_list:

            if file_name.endswith('adoc') and file_name != 'master.adoc':

                lines = open(os.path.abspath(dir_name) + '/' + file_name, 'r').readlines()

                # Test for title
                has_title = any(line.strip().startswith('= ') for line in lines)

                if not has_title:
                    files_missing_titles.append(os.path.abspath(dir_name) + '/' + file_name)

                # Test for abstract tag
                lines = test_abstract(lines, noop, os.path.abspath(dir_name) + '/' + file_name)

                # Test for additional resources tag
                lines = test_additional_resources(lines, noop)

                # Test for syntax updates
                lines = test_syntax_updates(lines, noop)

                # Write the results to an output file of the same name and location as the original
                with open(os.path.abspath(dir_name) + '/' + file_name, 'w') as output_file:

                    for line in lines:

                        output_file.write(line)

    # Report results
    print()
    print('Run complete.')
    print()

    # Report missing title results
    print('Files missing a title:')

    for title in files_missing_titles:
        print('    ' + title)

    print()
    print ('Total: ' + str(len(files_missing_titles)))
    print()

    # Report missing abstract results
    print('Files missing an abstract:')

    for title in __files_missing_abstracts__:
        print('    ' + title)

    print()
    print ('Total: ' + str(len(__files_missing_abstracts__)))
    print()


if __name__ == "__main__":

    for arg in sys.argv[1:]:

        if arg == '--no-op':
            __no_op__ = True
        if arg == '--alternate':
            __abstract_tag__ = '[role="system__abstract"]'
            __resource_tag__ = '[role="system__additional-resources"]'

    print_header()

    try:

        print('This script will check all modules and assemblies under the current directory and perform the following actions:\n')
        print('  1. Add the system abstract tag if missing')
        print('  2. Add the additional resources tag if missing')
        print('  3. Report all files missing a title')
        print('  4. Report all files missing a suitable abstract\n')

        input_proceed = input('Proceed? (Y/N): ')

        if input_proceed.strip().upper() == 'Y':

            process(__no_op__)

    except KeyboardInterrupt:

        print('\n\nOperation cancelled...\n')
