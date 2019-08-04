
> mv xxx.service /lib/systemd/system/

> sudo chmod 644 /lib/systemd/system/xxx.service

> sudo systemctl daemon-reload
> sudo systemctl enable xxx.service


To check status:
> systemctl status xxx.service


Standard out/err are directed to journalctl