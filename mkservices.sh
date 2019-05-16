printf "Copying service files..."
UUID=$(cat /proc/sys/kernel/random/uuid)
MBPORT=$(cat /tmp/microblogpub_mkconfig_port.txt)
echo "[Unit]" > /usr/lib/systemd/system/poussetaches.service
echo "Description=Lightweight asynchronous task execution service" >> /usr/lib/systemd/system/poussetaches.service
echo "After=network.target" >> /usr/lib/systemd/system/poussetaches.service
echo "[Service]" >> /usr/lib/systemd/system/poussetaches.service
echo "Environment=\"POUSSETACHES_AUTH_KEY=$UUID\"" >> /usr/lib/systemd/system/poussetaches.service
echo "ExecStart=/usr/bin/poussetaches/poussetaches" >> /usr/lib/systemd/system/poussetaches.service
echo "[Install]" >> /usr/lib/systemd/system/poussetaches.service
echo "WantedBy=multi-user.target" >> /usr/lib/systemd/system/poussetaches.service
echo "[Unit]" > /usr/lib/systemd/system/microblog.service
echo "Description=A self-hosted, single-user, ActivityPub powered microblog." >> /usr/lib/systemd/system/microblog.service
echo "After=network.target" >> /usr/lib/systemd/system/microblog.service
echo "[Service]" >> /usr/lib/systemd/system/microblog.service
echo "ExecStart=sh -c '$PWD/start.sh $UUID $MBPORT $PWD'" >> /usr/lib/systemd/system/microblog.service
echo "[Install]" >> /usr/lib/systemd/system/microblog.service
echo "WantedBy=multi-user.target" >> /usr/lib/systemd/system/microblog.service
echo "done"
