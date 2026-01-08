
# 4. Build and run
docker build -t storage-test:latest .
docker volume create storage-test_data
docker run -d --name storage-test -p 5000:5000 \
  -v storage-test_data:/app \
  -e STORAGE_PATH=/app/storage \
  storage-test:latest

# 5. Test it
open http://localhost:5000  # or visit manually
# Upload some files, refresh a few times

# 6. Simulate update
docker stop storage-test
docker rm storage-test
docker rmi storage-test:latest

# 7. Rebuild and restart
docker build -t storage-test:latest .
docker run -d --name storage-test -p 5000:5000 \
  -v storage-test_data:/app \
  -e STORAGE_PATH=/app/storage \
  storage-test:latest

# 8. Check persistence
open http://localhost:5000  # Files and count should be there!
