import argparse
import datetime
import subprocess
import re

# This script was built to analyse "hot" spots in a repo for IN4315 (Software
# Architecture) at Delft University of Technology.
# While not perfect it allowed us to analyse what areas of the code were
# touched the most in a given period.

# The tool creates a list tuples with each a file and the amount of commits
# that touched this file. This is then translated up to folder level as all
# files under a folder are aggregated to produce a min/avg/max amount of
# ‘commits that touched a file’ for a given folder (only the changed files
# are taken in to account).

# The output will be presented in a 'human readable' format with a minimum,
# average and maximum amount of commits touched for each folder.


parser = argparse.ArgumentParser()
parser.add_argument("--after",
                    help="The datetime after which to analyse the commits (in "
                         "ISO8601) format.",
                    default=None)
parser.add_argument("--before",
                    help="The datetime after which to analyse the commits (in "
                         "ISO8601) format.",
                    default=datetime.datetime.utcnow())
parser.add_argument("--sort-depth", action="store_true",
                    help="Whether to sort the result by folder depth.")
parser.add_argument("--no-header", action="store_true",
                    help="Whether to disable the data header in the results "
                         "file.")
parser.add_argument("-o", "--out", help="Where to write the results to.")

args = parser.parse_args()

if not args.after:
    raise Exception("Please provide an after datetime using the --after flag.")

if not args.before:
    raise Exception("Please provide a before datetime using the --before flag.")

if not args.out:
    raise Exception("Please provide a file to store the results using the "
                    "--out flag.")


def find_commits_in_range(after, before):
    """Use git to find all commit hashes in a given period."""
    return subprocess.check_output(
        ["git", "log",
         "--after={}".format(after),
         "--before={}".format(before),
         "--format=format:\"%H\""]) \
        .decode("utf-8") \
        .replace("\"", "") \
        .split("\n")


def find_files_changed_for_commit(commit_hash):
    """Use git to find the files touched by a commit."""
    return subprocess.check_output(
        # git diff-tree --no-commit-id --name-only -r bd61ad98
        ["git", "diff-tree", "--no-commit-id", "--name-only", "-r",
         commit_hash]) \
        .decode("utf-8") \
        .split("\n")


def find_folders(file):
    """Find all parent folders for a given filepath."""
    if "/" not in file:
        # In case there is no / its a root item.
        return ["/"]
    matches = re.match(r'^(.*/)([^/]*)$', file)
    folder = matches[1]
    # Add the folder and repeat the process by removing the trailing slash.
    return find_folders(folder[:len(folder) - 1]) + [folder]


# __ Actual Logic __
# Find all the commit hashes in the given range.
commits_in_range = find_commits_in_range(args.after, args.before)
print("Found {} commits in the range {} - {}".format(len(commits_in_range),
                                                     args.after, args.before))
items_touched = {}
folders_touched = set()


def note_touched(entry):
    """Simple helper function to note touched files."""
    if entry in items_touched:
        items_touched[entry] += 1
    else:
        items_touched[entry] = 1


# For each file in a commit, note that the file and folders it is placed in
# are touched.
for commit in commits_in_range:
    files_changed = find_files_changed_for_commit(commit)
    for file in files_changed:
        # Add the parent folders to the folders_touched set.
        [folders_touched.add(folder) for folder in find_folders(file)]
        note_touched(file)

# Make a list out of our dictionary with tuples: (file, #commitsTouched).
items_touched_list = [(k, v) for k, v in items_touched.items()]

aggregate_folder_touched = []
for folder in folders_touched:
    # Add possible filters here for folders we are not interested in.
    # Filter out tests folder
    if "tests/" in folder:
        continue

    # Create a list of 'commits touched count' for all files in this folder.
    touched_count = [item[1] for item in items_touched_list if
                     folder in item[0]]

    # Add the folder to the results list as tuples: (min, avg, max, folder).
    aggregate_folder_touched.append((
        min(touched_count),
        int(sum(touched_count) / len(touched_count)),
        max(touched_count),
        folder))

if args.sort_depth:
    # Sort the list by depth of the folders.
    aggregate_folder_touched.sort(
        key=lambda x: len([c for c in x[3] if c == "/"]),
        reverse=False)
else:
    # Else sort the list by highest avg value.
    aggregate_folder_touched.sort(key=lambda x: x[1], reverse=True)

# Write the output to file.
with open(args.out, "w") as f:
    if not args.no_header:
        # Write header line.
        f.write("MIN\tAVG\tMAX\tFOLDER\n")
    # Write results to file.
    f.writelines(
        ["{}\t{}\t{}\t{}\n".format(entry[0], entry[1], entry[2], entry[3])
         for entry in aggregate_folder_touched])
