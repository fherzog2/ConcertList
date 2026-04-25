import os
import subprocess
import tempfile

def get_subprocess_output(args):
    return subprocess.check_output(args).decode("utf8").strip()

def get_version_information():
    """ Get current version info from git: commit hash and date and whether there are uncommitted changes. """
    commit_hash = get_subprocess_output(["git", "rev-parse", "--verify", "HEAD"])
    committer_date = get_subprocess_output(["git", "log", "-1", "--format=%cs"])
    uncommitted_changes = get_subprocess_output(["git", "diff-index", "--name-status", "HEAD"])

    info_str = f"Commit {commit_hash[:12]}, {committer_date}"

    if len(uncommitted_changes) > 0:
        info_str += ", with uncommitted changes"

    return info_str

if __name__ == "__main__":
    APPNAME = "ConcertList"

    source_dir = os.path.dirname(__file__)
    install_dir = os.path.expanduser(f"~/pyinstaller_{APPNAME}")

    subprocess.check_output(["pip", "install", "PyInstaller"])

    version_info = get_version_information()
    print("version_info:", version_info)

    with tempfile.TemporaryDirectory() as tmpdirname:
        version_path = os.path.join(tmpdirname, "version.txt")
        with open(version_path, "w") as f:
            f.write(version_info)

        os.makedirs(install_dir, exist_ok=True)
        os.chdir(install_dir)
        subprocess.check_output(["pyinstaller", f"--name={APPNAME}", "--add-data", f"{version_path}:.", "-y", os.path.join(source_dir, "main.pyw")])
