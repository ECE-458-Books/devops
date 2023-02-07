sudo ufw default allow outgoing
sudo ufw default allow incoming

sudo ufw allow ssh
sudo ufw allow 80/tcp comment 'accept Nginx'
sudo ufw allow 433/tcp comment 'accept HTTPS connections'
sudo ufw allow 3000/tcp comment 'accept React Node connections'
sudo ufw allow 5432/tcp comment 'accept PostgreSQL connections'

sudo ufw enable