Docutils bullet list:
  $ echo "
  > Docutils Bullet List
  > 
  > - This is item 1 
  > - This is item 2
  > 
  > - Bullets are '-', '*' or '+'. 
  >   Continuing text must be aligned 
  >   after the bullet and whitespace.
  > 
  > Note that a blank line is required 
  > before the first item and after the 
  > last, but is optional between items.
  > " > paragraph.rst
  $ rst2ansi paragraph.rst
  Docutils Bullet List
  
    \u2022 This is item 1
    \u2022 This is item 2
    \u2022 Bullets are '-', '*' or '+'. Continuing text must be aligned after the
    bullet and whitespace.
  
  Note that a blank line is required before the first item and after the last, but
  is optional between items.

Docutils enumerated lists:
  $ echo "
  > Docutils Enumerated List
  > 
  > 3. This is the first item 
  > 4. This is the second item 
  > 5. Enumerators are arabic numbers, 
  >    single letters, or roman numerals 
  > 6. List items should be sequentially 
  >    numbered, but need not start at 1 
  >    (although not all formatters will 
  >    honour the first index). 
  > #. This item is auto-enumerated
  > " > paragraph.rst
  $ rst2ansi paragraph.rst
  Docutils Enumerated List
  
    3. This is the first item
    4. This is the second item
    5. Enumerators are arabic numbers, single letters, or roman numerals
    6. List items should be sequentially numbered, but need not start at 1
    (although not all formatters will honour the first index).
    7. This item is auto-enumerated

Test bullet list:
  $ echo "
  > Simple bullet list
  > 
  > * list 1
  > * list 2 with multiple
  >   lines
  > * list 3
  > " > paragraph.rst
  $ rst2ansi paragraph.rst
  Simple bullet list
  
    \u2022 list 1
    \u2022 list 2 with multiple lines
    \u2022 list 3

Test definition list:
  $ echo "
  > Definition list
  > 
  > Dinner
  >   An evening meal.
  > 
  > Lunch
  >   A meal
  >   typically
  >   taken
  >   mid day
  > 
  > Breakfast
  >   Morning meal that 'breaks' the overnight 'fast'.
  > " > paragraph.rst
  $ rst2ansi paragraph.rst
  Definition list
  
  Dinner
    An evening meal.
  
  Lunch
    A meal typically taken mid day
  
  Breakfast
    Morning meal that 'breaks' the overnight 'fast'.

Option list:
  $ echo "
  > Option List
  > 
  > -a            command-line option 'a' 
  > -b file       options can have arguments 
  >               and long descriptions 
  > --long        options can be long also 
  > --input file  long options can also have 
  >               arguments
  >               TODO: This should work with --input=file also
  > /V            DOS/VMS-style options too
  > --text        This is a long text that should span the line so that I can
  >               see if there is the correct word wrap.  If there
  >               isn't it could be problem, but maybe not.
  > " > paragraph.rst
  $ rst2ansi paragraph.rst
  Option List
  
  -a
      command-line option 'a'
  -b file
      options can have arguments and long descriptions
  --long
      options can be long also
  --input file
      long options can also have arguments TODO: This should work with
      --input=file also
  /V
      DOS/VMS-style options too
  --text
      This is a long text that should span the line so that I can see if there is
      the correct word wrap. If there isn't it could be problem, but maybe
      not.

Check Sub List:
  $ echo "
  > #. numbered
  > #. list
  > 
  >    #. and a
  >    #. sublist
  > 
  > #. end
  > 
  > * unordered
  > * list
  > " > paragraph.rst
  $ rst2ansi paragraph.rst
    1. numbered
    2. list
      1. and a
      2. sublist
    3. end
  
    \u2022 unordered
    \u2022 list
