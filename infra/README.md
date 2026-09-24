# Submitting your SSH public key

You need an account on the lab server to do W3. Accounts are created from the public key
you commit here.

## 1. Generate a key pair, if you do not already have one

    ssh-keygen -t ed25519 -C "your-email@u.boisestate.edu"

Accept the default location. A passphrase is a good idea.

That produces two files:

    ~/.ssh/id_ed25519       <- PRIVATE. Never leaves your machine. Never goes in a repo.
    ~/.ssh/id_ed25519.pub   <- PUBLIC. This is the one you commit.

## 2. Commit the PUBLIC key

    cp ~/.ssh/id_ed25519.pub infra/ssh-key.pub
    git add infra/ssh-key.pub && git commit -m "infra: add ssh public key" && git push

## 3. Check it

The file should be one line starting with `ssh-ed25519` and ending with your comment.
If it starts with `-----BEGIN` you have copied the **private** key. Stop, do not commit it,
and if you already did, generate a new pair and tell me, because the old one is compromised
the moment it is pushed.

The provisioning script refuses any file containing a private key and validates every key
with `ssh-keygen -l -f` before it is installed.

## Why through the repo and not email

Public keys are public; there is nothing secret to protect here. Putting it in the repo means
it is version controlled, auditable, and already in a place the course tooling reads.
