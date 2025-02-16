#!/bin/bash

profile="Profile 34"

if cd "$HOME/.config"; then
    if cp -r "google-chrome/$profile" "microsoft-edge/"; then
        echo "Chrome profile successfully updated"
    else
        echo "Failed to copy Chrome profile" >&2
    fi
else
    echo "Failed to change directory to: \"$HOME/.config\"" >&2
fi

