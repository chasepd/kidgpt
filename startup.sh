#!/bin/bash
until mysql -h"$MYSQL_HOST" -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" -e "USE $MYSQL_DATABASE"; do
  echo "Waiting for MySQL..."
  sleep 2
done

echo "MySQL is ready, continuing..."

exec "$@"
