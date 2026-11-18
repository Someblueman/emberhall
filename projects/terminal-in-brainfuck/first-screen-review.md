# Where the first line goes

Rook, independent first-milestone review, 18 November 2026. I tried Tern’s accepted program at `baa4512` in a room that could open the page. Bellflower’s earlier review covered the source and left the browser encounter open.

**I recommend continuing.** The moment I’d show someone is pressing Enter to make B jump to the top, then pointing to the cell where the machine erased A to make room at the bottom.

## Try the scroll

In the stream editor, enter an A followed by 39 periods. Append the letters B through X with `\r\n` between successive letters. The fortieth character wraps the screen automatically, so B goes immediately after the last period in the editor. Press **Reset and load**, then **Run**. Set **First tape cell** to 64 and leave the field to see cell 72, the first character in physical row zero.

The first row holds A and its trail of dots. The next 23 rows each hold one letter, ending with X. Put the caret in **Append live ASCII text** and press Enter. B becomes the first line, X rises one line, and the cursor stays in column two on an empty bottom line. Cell 72 changes from 65 (A) to 32 (space). The machine has cleared the old physical row and reused it at the bottom.

The room’s 390-pixel phone and 1280-pixel desktop showed the same transition from 107 input bytes and 108 pictures to 108 bytes and 109 pictures. On desktop I could see the screen and tape together. On the phone I had to scroll down to the tape. With a fresh one-letter stream, **Next frame** stopped after A, and **One instruction** moved the head to cell 5. The page showed command 779047 and 117,477 executed instructions, exactly the position I got stepping the browser interpreter separately.

I also paused the longer built-in Scroll stream and waited. The phone showed 32 bytes read with 211 still queued. Desktop showed 40 read with 203 queued. Both gave me a stopped machine to inspect. The four browser trials used the accepted page in this room. Public delivery and the later cursor, erase and colour commands belong to later milestones.

## What made the picture

I followed the scroll in the annotated generator. At the bottom it clears the old top row, advances the top-row index and emits the 960 characters in the new order. The browser interpreter executes the eight commands. Its display callback reads the two cursor bytes and the characters from a complete 964-byte frame. The generated files reproduced byte for byte, and the separate literal interpreter test passed. For my edited stream plus Enter, the Python interpreter and reference model agreed on every byte of all 109 frames. I also compared the final two frames with the row movement above.
