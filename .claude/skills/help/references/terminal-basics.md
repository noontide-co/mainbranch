# Terminal Basics for Complete Beginners

Never used Terminal before? This guide explains everything from scratch.

---

## What is Terminal?

Terminal is a text-based way to interact with your computer. Instead of clicking on folders and icons, you type commands.

It looks like a blank screen with a cursor. You type, press Enter, things happen.

**Why use it?** Claude Code runs in Terminal. It's more powerful than a chat window because Claude can actually read and write files on your computer.

---

## Opening Terminal

**Mac:**
1. Press Cmd + Space (opens Spotlight)
2. Type "Terminal"
3. Press Enter

**Windows:**
1. Press Windows key
2. Type "Terminal" or "PowerShell"
3. Press Enter

You'll see a blank screen with a prompt like:
```
username@computer ~ %
```

That's Terminal. You're in.

---

## The Concept of "Being In" a Folder

When you open Terminal, you're "in" a folder. Usually your home folder.

Think of it like this: if Terminal were Finder, what folder would be open right now?

You can change which folder you're "in" by typing commands.

---

## The cd Command

`cd` stands for "change directory" (directory = folder).

```bash
cd ~/Documents/GitHub/vip
```

This tells Terminal: "Go to the vip folder inside GitHub inside Documents inside my home folder."

**The `~` symbol means "my home folder."**

After running this, you're now "in" the vip folder. If you type `claude`, Claude starts with access to everything in that folder.

---

## What "Start Claude in a Folder" Means

When someone says "start Claude in vip," they mean:

1. Open Terminal
2. Type `cd ~/Documents/GitHub/vip` and press Enter
3. Type `claude` and press Enter

Now Claude is running AND it can see all the files in vip.

**Why this matters:** Claude Code can only see files in folders you give it access to. If you start Claude in vip, it sees vip. If you start elsewhere, it doesn't.

---

## The Daily Commands

Every session:
```bash
cd ~/Documents/GitHub/vip
claude
/start
```

That's it. Three lines. Copy and paste them if needed.

1. `cd ~/Documents/GitHub/vip` - Go to the vip folder
2. `claude` - Start Claude Code
3. `/start` - Tell Claude to load your business repo and get ready

---

## Dragging Files and Folders

You can drag things from Finder (Mac) or Explorer (Windows) directly into Terminal.

**Drag a file:** Its full path appears. Useful for telling Claude about a specific file.

**Drag a folder:** Its path appears. You can type `/add-dir ` then drag a folder to add it.

**Example:**
1. Type `/add-dir ` (with the space)
2. Drag your business folder from Finder
3. Press Enter

Claude can now see both vip AND your business folder.

---

## Voice Input

Don't want to type? Use dictation.

**Mac:**
1. Press Fn twice (or the mic key on newer Macs)
2. Speak your command or message
3. Press Fn again to stop

The words appear as text. Works in Terminal just like anywhere else.

**Windows:**
1. Press Windows + H
2. Speak
3. Click the mic to stop

Or use any third-party dictation software.

---

## Common Terminal Confusion

### "I typed something and nothing happened"

Some commands give no output if they succeed. No news is good news.

### "I'm lost - where am I?"

Type `pwd` (print working directory). It shows your current folder.

### "I want to go back"

Type `cd ..` to go up one folder level.

### "I made a typo"

Press the up arrow to see your previous command. Edit and re-run.

### "How do I stop something?"

Press Ctrl + C to cancel the current operation.

---

## You Don't Need to Memorize

Most of the time, you'll just use:
```bash
cd ~/Documents/GitHub/vip
claude
/start
```

That's the whole routine. Everything else, just ask Claude - it can help you with Terminal commands too.

---

## Next Step

Ready to get started? Follow the commands above. Once Claude is running, type `/start` and it'll guide you from there.
