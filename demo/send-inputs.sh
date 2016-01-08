#!/bin/sh
pts=$1; shift

reseq demo/demo.tsq --replay | sudo ttysend -i $pts
wait 3
tmux kill-session -t demo
