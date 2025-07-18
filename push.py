import subprocess


def get_commit_message() -> str:
    """
    Extract the first non-empty line from TODO.md to use as the commit message.

    Returns
    -------
    str
        The commit message string.
    """
    with open("TODO.md", "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                return line
    return ""


def git_push(commit_message: str) -> None:
    """
    Run git commands to add, commit, and push changes.

    Parameters
    ----------
    commit_message : str
        The message to use for the git commit.
    """
    commands = [
        "git add .",
        f'git commit -m "{commit_message}"',
        "git push"
    ]

    for command in commands:
        print(f"Running: {command}")
        subprocess.run(command, shell=True, check=True)


if __name__ == "__main__":
    commit_message = get_commit_message()

    if not commit_message:
        raise ValueError("Commit message cannot be empty or just whitespace.")

    git_push(commit_message)
