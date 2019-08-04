
> sudo mv bikemon.service /lib/systemd/system/

> sudo chmod 644 /lib/systemd/system/bikemon.service

> sudo systemctl daemon-reload
> sudo systemctl enable bikemon.service


To check status:
> systemctl status bikemon.service


To see standard out/err:
> journalctl -u bikemon.service