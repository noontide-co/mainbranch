---
type: educational
topic: anti-cloud-backup
status: stub
last-updated: 2026-04-29
---

# Why your financial ledger doesn't belong in iCloud, Drive, or Dropbox

## Why we don't recommend consumer cloud sync

Consumer cloud sync products (iCloud Drive, Google Drive, Dropbox, OneDrive) are designed for convenience: a folder on your laptop that mirrors to a server you don't own. That convenience comes from defaults that are wrong for financial records.

First, **subpoena exposure**. Every major US cloud provider publishes a transparency report documenting thousands of warrants and subpoenas served against user data per year. iCloud Drive content is decryptable by Apple under standard legal process unless you've explicitly enabled Advanced Data Protection (still off by default in 2026). Google and Dropbox encrypt at rest with keys they hold. Your `core/finance/ledger.beancount` becomes a third-party record under the third-party doctrine the moment it touches their servers — which means the bar to access it is a subpoena, not a warrant.

Second, **encryption-at-rest is not end-to-end encryption**. Marketing copy on these products often blurs the line. "Encrypted at rest" means the disk is encrypted; the provider holds the key. Anyone who compels the provider — or breaches them — gets plaintext. Beancount files are plaintext. Account numbers, vendor names, transaction memos, headcount payroll details: all of it readable by anyone the provider hands the key to.

Third, **silent corruption and conflict resolution**. Dropbox famously creates `filename (Devon's Mac Studio's conflicted copy 2026-04-12).beancount` files when two devices touch a file at once. iCloud has truncated files mid-sync more than once in documented cases. For a ledger you are going to balance and audit, "the cloud quietly corrupted line 4,182" is not an acceptable failure mode.

Fourth, **vendor lock-in**. The day Dropbox raises prices, removes a feature, or terminates your account for a TOS dispute, your data is wherever they say it is. With self-hosted git you carry the repo to a new origin in one `git remote set-url`.

## What we recommend instead

A three-layer setup that keeps you in control:

1. **Forgejo** (self-hosted git) is the primary working copy. You commit to a repo on a server you own — a Mac mini in a closet, a Hetzner box, a Synology NAS running Docker. `git push` is the sync mechanism. Conflicts surface as merge conflicts, not silent overwrites.
2. **Backblaze B2** is the encrypted off-site backup. `restic` snapshots the working tree (and the Forgejo data dir) on a schedule. The encryption key lives on your machine; B2 holds ciphertext. Subpoenaed B2 hands over noise.
3. **Time Machine** is the local snapshot recovery. macOS already does this if you plug in an external drive. It saves you from "I just `rm -rf core/finance/`" within seconds, not hours.

The combination is cheaper than Dropbox Pro, gives you forensic git history, and keeps the encryption key out of any vendor's hands.

## Setup walkthrough

1. Stand up Forgejo on a machine you own. Easiest path is Docker on a home server:
   ```bash
   docker run -d --name forgejo \
     -p 3000:3000 -p 222:22 \
     -v /opt/forgejo:/data \
     codeberg.org/forgejo/forgejo:7
   ```
   Visit `http://your-server.local:3000`, create the admin user, create a private repo named after your business.

2. Point your `core/finance/` directory at it:
   ```bash
   cd ~/your-business
   git init
   git remote add origin git@your-server.local:devon/your-business.git
   git add core/finance/
   git commit -m "[init] finance ledger"
   git push -u origin main
   ```

3. Install `restic` and configure a B2 bucket:
   ```bash
   brew install restic
   # Create a B2 application key with read+write on a new private bucket.
   export B2_ACCOUNT_ID="<keyID>"
   export B2_ACCOUNT_KEY="<applicationKey>"
   export RESTIC_REPOSITORY="b2:your-bucket-name:/"
   export RESTIC_PASSWORD="$(openssl rand -base64 32)"  # WRITE THIS DOWN
   restic init
   ```
   Save `RESTIC_PASSWORD` somewhere offline (paper, hardware key, password manager you trust). Without it, the backup is unrecoverable — that is the point.

4. Schedule a daily snapshot via `launchd` (macOS) or `cron`:
   ```bash
   restic backup ~/your-business --exclude='node_modules' --exclude='.venv'
   restic forget --keep-daily 7 --keep-weekly 4 --keep-monthly 12 --prune
   ```

5. Confirm Time Machine is on and pointed at an external SSD. macOS does the rest.

6. Run a recovery drill once. Pick a non-critical file, delete it, and restore it from each of the three layers (`git checkout`, `restic restore`, Time Machine). If any layer fails the drill, fix it now, not when you actually need it.

Cost at typical scale: Forgejo on existing hardware is free. B2 storage runs roughly $6/TB/month, and a finance ledger plus business repo will sit comfortably under 1 GB for years. Total operating cost: under $1/month.

## Honest limitations

This stack does not solve **availability**. If your home server is offline, your collaborators can't push. If you travel and your laptop is lost, you're cloning from B2, which takes longer than a Dropbox sync. For a single-operator business the trade-off is fine; for a 5-person team you want a managed Forgejo or Gitea on a VPS instead of a closet box. It also requires you to remember the restic password — losing it loses the backup. A 30-second failover plan and a hardware-key-stored copy of the password is part of the deal.

## Resources

- Forgejo docs: https://forgejo.org/docs/
- Restic docs: https://restic.readthedocs.io/
- Backblaze B2 pricing: https://www.backblaze.com/cloud-storage/pricing
- Apple's "Government Information Requests" transparency report: https://www.apple.com/legal/transparency/
