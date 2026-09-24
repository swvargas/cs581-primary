# lab/ — your RMS build

Clone or develop here, then link the units:

    mkdir -p ~/.config/systemd/user
    cp units/*.service ~/.config/systemd/user/
    systemctl --user daemon-reload
    systemctl --user enable --now plant-rms plant-rms-hmi
    systemctl --user status plant-rms

Lingering is already enabled on your account, so your services survive logout and reboot.
The status board checks that they come back.

Python 3.12 with PEP 668 enforced, so use a venv:

    python3 -m venv .venv && ./.venv/bin/pip install pymodbus flask gunicorn
