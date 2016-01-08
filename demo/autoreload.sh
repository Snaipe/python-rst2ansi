clear
export PYTHONPATH=.
while true;
    do inotifywait -e modify out.rst 2>/dev/null >/dev/null
    clear
    ./bin/rst2ansi out.rst
done
