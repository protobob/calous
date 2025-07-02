1. /chat.add and /chat.remove should be removed. No longer make sense, in app mode it was a nice feature, but as a service number of chats should be consistent.
2. Fix chat count constants:
    a. remove MAX_CHATS, makes no sens to have this if service starts with a certain amount and there is no /chat.add or /chat.remove
    b. remove DEFAULT_NUM_CHATS, again this is deprecated and show be removed
    c. keep SERVER_DEFAULT_NUM_CHATS, this should be the only constant we use now, 
    d. fix __main__.py entry point to only use c, all references to b and c should be removed from this and any other files
3. Go over the whole codebase and look for problems or issues that need to be addressed.