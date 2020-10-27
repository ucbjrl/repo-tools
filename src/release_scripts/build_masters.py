"""Updates chisel-release master branch to latest master hash"""

import os
import sys
import getopt

from release_scripts.git_utils.tools import Tools
from release_scripts.git_utils.step_counter import StepCounter


def usage():
    print(f"Usage: {sys.argv[0]} --repo <repo-dir> --branch <repo-dir-branch> [options]")
    print(f"options are:")
    print(f"     --start-step <start_step>    (or -s)")
    print(f"     --stop-step <stop_step>      (or -e")
    print(f"     --list-only                  (or -l)")


def main():
    try:
        opts, args = getopt.getopt(
            sys.argv[1:],
            "lhr:s:e:",
            ["help", "repo=", "start-step=", "stop-step=", "list-only"]
        )
    except getopt.GetoptError as err:
        print(err)
        usage()
        sys.exit(2)

    release_dir = ""
    start_step = -1
    stop_step = 1000
    list_only = False
    counter = StepCounter()

    for option, value in opts:
        if option in ("--repo", "-r"):
            release_dir = value
        elif option in ("--start-step", "-s"):
            start_step = int(value)
        elif option in ("--stop-step", "-e"):
            stop_step = int(value)
        elif option in ("--list-only", "-l"):
            list_only = True
        elif option in ("--help", "-h"):
            usage()
            exit(1)
        else:
            print(f"Unhandled command line option: {option}")
            usage()
            assert False

    if release_dir == "":
        usage()
        exit(1)

    tools = Tools("build_masters", release_dir)

    if not list_only:
        if release_dir == "":
            print(f"Error: --repo must be specified to run this script")
            usage()
            exit(1)
        else:
            print(f"chisel-release directory is {os.getcwd()}")
    else:
        print(f"These are the steps to be executed for the {tools.task_name} script")

    tools.set_start_step(start_step)
    tools.set_stop_step(stop_step)
    tools.set_list_only(list_only)

    tools.checkout_branch(counter.next_step(), "master")

    tools.git_pull(counter.next_step())

    tools.run_submodule_update_recursive(counter.next_step())

    tools.run_make_pull(counter.next_step())

    tools.run_make_clean_install(counter.next_step())

    tools.run_make_test(counter.next_step())

    tools.git_add_dash_u(counter.next_step())

    tools.git_commit(counter.next_step(), "Bump master branches")

    tools.git_push(counter.next_step())


if __name__ == "__main__":
    main()
