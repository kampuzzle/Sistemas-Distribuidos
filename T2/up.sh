# execute "docker compose up -d", wait 2 secods, then "python3 main.py  "
docker-compose down
docker-compose up -d
sleep 2
python3 main.py