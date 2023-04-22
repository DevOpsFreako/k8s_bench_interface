#!/workspace/development/frappe-bench/env/bin/python
import argparse
import os
import re
import sys

import git
import semantic_version

NO_CHANGES_DRY_RUN = "No changes will be made as --dry-run was specified."

cli_print = print  # noqa: T002,T202


def main():
    parser = get_parse_args()
    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        return

    if not args.dry_run:
        validate_bump(args=args)
        validate_repo(args=args)

    if args.dry_run:
        cli_print(NO_CHANGES_DRY_RUN)

    update_app_version(args=args)

    if args.tag and not (args.major or args.minor or args.patch):
        update_image_version(args=args)
        update_template_version(args=args)

    if not args.dry_run:
        git_commit_tag_push(args=args)


def git_commit_tag_push(args: argparse.Namespace):
    repo = git.Repo(os.getcwd())
    versions = get_versions(args=args)
    app_version = versions.get("bump_version")
    image_tag = versions.get("bump_image_tag")
    commit_message = "chore: publish release\n"
    if app_version:
        commit_message += f"\napp version: {app_version}"
    if image_tag:
        commit_message += f"\nhelm chart version: {image_tag}"

    cli_print(f"git tag: {app_version}")
    cli_print("")
    cli_print("Commit, tag and push to git repository with commit message:")
    cli_print("")
    cli_print(commit_message)

    if args.dry_run:
        return

    repo.git.add(all=True)
    repo.git.commit("-m", commit_message)

    if app_version:
        repo.create_tag(app_version, message=f"Released {app_version}")

    git_ssh_command = os.environ.get("GIT_SSH_COMMAND")
    if git_ssh_command:
        repo.git.update_environment(GIT_SSH_COMMAND=git_ssh_command)
    repo.git.push(args.remote, "--follow-tags")


def get_parse_args():
    parser = argparse.ArgumentParser(
        description="Release script for k8s bench interface", add_help=True
    )
    parser.add_argument(
        "-m",
        "--major",
        action="store_true",
        help="Bump major semver",
    )
    parser.add_argument(
        "-n",
        "--minor",
        action="store_true",
        help="Bump minor semver",
    )
    parser.add_argument(
        "-p",
        "--patch",
        action="store_true",
        help="Bump patch semver",
    )
    parser.add_argument(
        "-t",
        "--tag",
        action="store_true",
        help="Bump tag increment",
    )
    parser.add_argument(
        "-d",
        "--dry-run",
        action="store_true",
        help="DO NOT make changes",
    )
    group = parser.add_argument_group("options")
    group.add_argument(
        "--remote",
        action="store_true",
        default="upstream",
        help="Git remote to tag and push",
    )

    return parser


def validate_repo(args):
    repo = git.Repo(os.getcwd())
    if str(repo.active_branch) != "main":
        cli_print("Make sure you are on main branch")
        sys.exit(1)

    if repo.is_dirty():
        cli_print("Make sure you have committed changes")
        sys.exit(1)


def validate_bump(args: argparse.Namespace):
    version = get_versions(args)
    is_bump_invalid = False
    invalid_bump_error = "Invalid Bump\n"
    bump_version = version.get("bump_version")
    current_version = version.get("current_version")

    if semantic_version.Version(bump_version) <= semantic_version.Version(
        current_version
    ):
        is_bump_invalid = True
        invalid_bump_error += (
            f"Cannot bump app from {current_version} to {bump_version}\n"  # noqa: E501
        )

    if is_bump_invalid:
        cli_print(invalid_bump_error)
        sys.exit(1)


def get_versions(args: argparse.Namespace):
    bump_image_tag = None
    bump_version = None
    current_image_tag = None
    current_version = __import__(
        "k8s_bench_interface.k8s_bench_interface"
    ).__version__  # noqa: E501

    with open("/workspace/ci/version.txt") as ver_buffer:
        current_image_tag = ver_buffer.read().strip()

    if args.tag:
        tag_version, tag_release = current_image_tag.split("-")
        bump_image_tag = f"{tag_version}-{int(tag_release)+1}"

    if args.major:
        bump_version = (
            semantic_version.Version(
                current_version,
            )
            .next_major()
            .__str__()
        )
    elif args.minor:
        bump_version = (
            semantic_version.Version(
                current_version,
            )
            .next_minor()
            .__str__()
        )
    elif args.patch:
        bump_version = (
            semantic_version.Version(
                current_version,
            )
            .next_patch()
            .__str__()
        )
    else:
        bump_version = current_version

    bump_image_tag = bump_image_tag or current_image_tag
    return {
        "current_version": current_version,
        "current_image_tag": current_image_tag,
        "bump_version": bump_version,
        "bump_image_tag": bump_image_tag,
    }


def update_app_version(args: argparse.Namespace):
    versions = get_versions(args)
    version = versions.get("bump_version")
    if args.major or args.minor or args.patch:
        cli_print(f"Bumped app version to {version}")
        if not args.dry_run:
            with open(
                "k8s_bench_interface/__init__.py",
                "r+",
            ) as f:
                content = f.read()
                content = re.sub(
                    r"__version__ = .*", f'__version__ = "{version}"', content
                )
                f.seek(0)
                f.truncate()
                f.write(content)

        image_version = f"{version}-0"
        update_image_version(args, version=image_version)
        update_template_version(args, version=image_version)


def update_image_version(args: argparse.Namespace, version=None):
    versions = get_versions(args)
    version = version or versions.get("bump_image_tag")
    cli_print(f"Bumped image tag to {version}")
    if not args.dry_run:
        with open("ci/version.txt", "r+") as f:
            f.seek(0)
            f.truncate()
            f.write(f"{version}\n")


def update_template_version(args: argparse.Namespace, version=None):
    versions = get_versions(args)
    version = version or versions.get("bump_image_tag")
    cli_print(f"Bumped values-template.yaml image tag to {version}")
    if not args.dry_run:
        with open("values-template.yaml", "r+") as f:
            content = f.read()
            content = re.sub(r"tag: .*", f"tag: {version}", content)
            content = re.sub(
                r"registry.gitlab.com/castlecraft/k8s_bench_interface/bench:.*",  # noqa: E501
                f"registry.gitlab.com/castlecraft/k8s_bench_interface/bench:{version}",  # noqa: E501
                content,
            )
            f.seek(0)
            f.truncate()
            f.write(content)


if __name__ == "__main__":
    main()
