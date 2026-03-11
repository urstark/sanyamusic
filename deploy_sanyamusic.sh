#!/usr/bin/env bash
# ------------------------------------------------------------
# Deploy the current local SANYAMUSIC code to three remote repos
# ------------------------------------------------------------

# 1️⃣  Path to the *source* you are working on
SRC_ROOT="C:/Users/MY-PC/Downloads/dev/sanyamusic"

# 2️⃣  Remote repositories (feel free to edit/add more)
declare -A REPOS=(
    ["Sanyamusic"]="https://github.com/urSTARK/Sanyamusic.git"
    ["aykamusic"]="https://github.com/urstark/aykamusic.git"
    ["Sanyamusicx"]="https://github.com/urSTARK/Sanyamusicx.git"
)

# 3️⃣  Where to place the clones (you can change this folder)
BASE_DIR="C:/Users/MY-PC/Downloads/dev"

# ------------------------------------------------------------
# Helper: copy source → destination (preserves hidden files)
copy_source () {
    local dest="$1"
    # Remove old content but keep .git folder
    find "$dest" -mindepth 1 -maxdepth 1 ! -name ".git" -exec rm -rf {} +
    # Copy everything from source into destination
    cp -a "$SRC_ROOT"/. "$dest"/
}

# ------------------------------------------------------------
# Main loop – process each repo
for name url in "${!REPOS[@]}"; do
    echo "=== Processing $name ==="
    DEST_DIR="${BASE_DIR}/${name}"

    # Clone if the folder does not exist yet
    if [ ! -d "$DEST_DIR/.git" ]; then
        echo "Cloning $url → $DEST_DIR"
        git clone "$url" "$DEST_DIR"
    else
        echo "Repo already cloned at $DEST_DIR – pulling latest"
        (cd "$DEST_DIR" && git fetch --all && git reset --hard origin/main)
    fi

    # Copy the updated source code over the repo
    echo "Copying current code into $DEST_DIR"
    copy_source "$DEST_DIR"

    # Commit & push
    (
        cd "$DEST_DIR"
        git add -A
        # Only create a commit if there are actual changes
        if ! git diff-index --quiet HEAD; then
            git commit -m "- 𝑆𝑎𝑛𝑦𝑎 ♪"
            git push origin main
            echo "✅ Pushed to $name"
        else
            echo "⚡ No changes to commit for $name"
        fi
    )
    echo ""
done

echo "All done! 🎉"
