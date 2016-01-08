#!/bin/sh

echo "" > out.rst

tmux new-session -s demo -n rst2ansi -d 'nvim out.rst -c ":set nobackup" -c ":set noswapfile"'
tmux splitw -t demo -h 'zsh ./demo/autoreload.sh'
tmux lastp -t demo
tmux -2 attach-session -t demo
