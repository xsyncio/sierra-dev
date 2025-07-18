import subprocess


def get_commit_message():
    """Get the commit message from TODO.md."""
    with open("TODO.md", "r") as f:
        return f.readline().strip()


def git_push(commit_message: str):
    """Run the git commands in the terminal."""
    commands = [
        "git add *",
        f"git commit -m '{commit_message}'",
        "git push"
    ]

    for command in commands:
        print(f"Running: {command}")
        subprocess.run(command, shell=True, check=False)


if __name__ == "__main__":
    commit_message = get_commit_message()
    git_push(commit_message)

