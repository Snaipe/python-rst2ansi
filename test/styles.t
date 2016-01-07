Test foreground colors:

  $ echo ':ansi-fg-black:`black`' > styles.rst
  $ echo ':ansi-fg-red:`red`' >> styles.rst
  $ echo ':ansi-fg-green:`green`' >> styles.rst
  $ echo ':ansi-fg-yellow:`yellow`' >> styles.rst
  $ echo ':ansi-fg-blue:`blue`' >> styles.rst
  $ echo ':ansi-fg-magenta:`magenta`' >> styles.rst
  $ echo ':ansi-fg-cyan:`cyan`' >> styles.rst
  $ echo ':ansi-fg-white:`white`' >> styles.rst
  $ rst2ansi styles.rst
  \x1b[30mblack\x1b[0m \x1b[31mred\x1b[0m \x1b[32mgreen\x1b[0m \x1b[33myellow\x1b[0m \x1b[34mblue\x1b[0m \x1b[35mmagenta\x1b[0m \x1b[36mcyan\x1b[0m \x1b[37mwhite\x1b[0m (esc)

Test background colors:

  $ echo ':ansi-bg-black:`black`' > styles.rst
  $ echo ':ansi-bg-red:`red`' >> styles.rst
  $ echo ':ansi-bg-green:`green`' >> styles.rst
  $ echo ':ansi-bg-yellow:`yellow`' >> styles.rst
  $ echo ':ansi-bg-blue:`blue`' >> styles.rst
  $ echo ':ansi-bg-magenta:`magenta`' >> styles.rst
  $ echo ':ansi-bg-cyan:`cyan`' >> styles.rst
  $ echo ':ansi-bg-white:`white`' >> styles.rst
  $ rst2ansi styles.rst
  \x1b[40mblack\x1b[0m \x1b[41mred\x1b[0m \x1b[42mgreen\x1b[0m \x1b[43myellow\x1b[0m \x1b[44mblue\x1b[0m \x1b[45mmagenta\x1b[0m \x1b[46mcyan\x1b[0m \x1b[47mwhite\x1b[0m (esc)

Test styles:

  $ echo ':ansi-bold:`bold`' > styles.rst
  $ echo ':ansi-dim:`dim`' >> styles.rst
  $ echo ':ansi-italic:`italic`' >> styles.rst
  $ echo ':ansi-underline:`underline`' >> styles.rst
  $ echo ':ansi-blink:`blink`' >> styles.rst
  $ echo ':ansi-blink-fast:`blink-fast`' >> styles.rst
  $ echo ':ansi-inverse:`inverse`' >> styles.rst
  $ echo ':ansi-conceal:`conceal`' >> styles.rst
  $ echo ':ansi-strikethrough:`strikethrough`' >> styles.rst
  $ rst2ansi styles.rst
  \x1b[1mbold\x1b[0m \x1b[2mdim\x1b[0m \x1b[3mitalic\x1b[0m \x1b[4munderline\x1b[0m \x1b[5mblink\x1b[0m \x1b[6mblink-fast\x1b[0m \x1b[7minverse\x1b[0m \x1b[8mconceal\x1b[0m \x1b[9mstrikethrough\x1b[0m (esc)

Test standard reStructuredText text decorations:

  $ echo '*emphasis*' > styles.rst
  $ echo '**strong emphasis**' >> styles.rst
  $ rst2ansi styles.rst
  \x1b[3memphasis\x1b[0m \x1b[1mstrong emphasis\x1b[0m (esc)

Test role coalescing:

  $ echo '
  > .. role:: blue-and-bold
  >     :class: ansi-bold ansi-fg-blue
  > 
  > :blue-and-bold:`test`
  > ' > styles.rst
  $ rst2ansi styles.rst
  \x1b[1;34mtest\x1b[0m (esc)
