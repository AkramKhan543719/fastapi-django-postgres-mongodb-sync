@echo off

cd /d "C:\Users\PathanMohammedAkramK\OneDrive - Proglint\Desktop\deepstream-postgres-mongodb-sync\django_backend"

"C:\Users\PathanMohammedAkramK\AppData\Local\Programs\Python\Python39\python.exe" manage.py sync_postgres_to_mongo >> sync_cron.log 2>&1