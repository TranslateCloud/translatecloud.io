CREATE USER translatecloud_api WITH PASSWORD 'ApiUser2025Secure!';
GRANT CONNECT ON DATABASE postgres TO translatecloud_api;
GRANT USAGE ON SCHEMA public TO translatecloud_api;
GRANT SELECT, INSERT, UPDATE ON users TO translatecloud_api;
GRANT SELECT, INSERT, UPDATE ON projects TO translatecloud_api;
GRANT SELECT, INSERT, UPDATE ON translations TO translatecloud_api;
GRANT SELECT, INSERT ON payments TO translatecloud_api;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO translatecloud_api;