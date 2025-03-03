#!/bin/bash


# define alias, script and run commands file locations
ALIAS="nightcore-to-youtube"
SCRIPT="$(dirname $(realpath "$0"))/nightcore_to_youtube.sh"
RC="$HOME/.bashrc"

# chrome profile to use cookies
CHROME_PROFILE="Profile 34"


# alias
echo "Setting up alias for script: $SCRIPT"

if ! grep -q "alias $ALIAS=" "$RC"; then
    echo "" >> "$RC"  # add blank line before alias
    echo "alias $ALIAS='$SCRIPT'" >> "$RC"
    source "$RC"
    echo "You can now use \`$ALIAS\` to run script"
else
    echo "Alias for script already exists. Use \`$ALIAS\`"
fi


# chrome profile
echo "Setting up Chrome profile"

if cd "$HOME/.config"; then
    if cp -r "google-chrome/$CHROME_PROFILE" "microsoft-edge/"; then
        echo "Chrome profile successfully set"
    else
        echo "Failed to copy Chrome profile" >&2
    fi
else
    echo "Failed to change directory to: \"$HOME/.config\"" >&2
fi
