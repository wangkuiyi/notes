I have a Ubuntu Linux server in my garage. I usually ssh to it from my iMac in my office.

To save the energy, I would suspend the server if I am not going to use it. I do this my typing the following command:

```bash
sudo systemctl suspend
```

When the Linux server is in the suspended mode, I cannot ssh to it.  To wake it up without rushing to the garage, I'd use Wake-on-LAN (WOL).

To enable WOL on the Linux server, I followed [this tutorial](https://kodi.wiki/view/HOW-TO:Set_up_Wake-on-LAN_for_Ubuntu) to install `ethtool` on the Linux server.

```bash
sudo apt-get install ethtool
```

And enable WOL on the given Ethernet card.

```bash
sudo ethtool -s eno1 wol g
```

To enable my iMac to wake up the Linux server, I followed [this guide](https://www.cyberciti.biz/faq/apple-os-x-wake-on-lancommand-line-utility/) and installed `wakeonlan`.

```bash
brew install wakeonlan
```

To wake up my Linux server, I need the MAC address of the Ehternet card. I can get it from the `ifconfig` command.  Then, I can wake it up by typing the following command on iMac.

```bash
wakeonlan 8c:5c:8e:00:e8:c0
```
