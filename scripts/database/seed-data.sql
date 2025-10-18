INSERT INTO users (email, full_name, company, plan, subscription_status, monthly_word_count, word_limit, created_at)
VALUES 
    ('demo@translatecloud.com', 'Demo User', 'Demo Company', 'free', 'active', 500, 5000, NOW()),
    ('premium@translatecloud.com', 'Premium User', 'Premium Corp', 'pro', 'active', 15000, 100000, NOW()),
    ('business@translatecloud.com', 'Business User', 'Business Inc', 'business', 'active', 50000, 500000, NOW());

INSERT INTO projects (user_id, name, url, source_lang, target_lang, status, total_words, translated_words, created_at)
VALUES 
    ((SELECT id FROM users WHERE email = 'demo@translatecloud.com'), 'Demo Website', 'https://demo.example.com', 'en', 'es', 'completed', 1200, 1200, NOW()),
    ((SELECT id FROM users WHERE email = 'demo@translatecloud.com'), 'Blog Translation', 'https://blog.example.com', 'en', 'fr', 'in_progress', 3500, 2100, NOW()),
    ((SELECT id FROM users WHERE email = 'premium@translatecloud.com'), 'E-commerce Site', 'https://shop.example.com', 'en', 'de', 'completed', 8500, 8500, NOW()),
    ((SELECT id FROM users WHERE email = 'premium@translatecloud.com'), 'Documentation', 'https://docs.example.com', 'en', 'it', 'in_progress', 12000, 6000, NOW()),
    ((SELECT id FROM users WHERE email = 'business@translatecloud.com'), 'Corporate Website', 'https://corporate.example.com', 'en', 'pt', 'completed', 25000, 25000, NOW());

INSERT INTO translations (project_id, source_lang, target_lang, source_text, translated_text, word_count, engine, status, created_at, translated_at)
VALUES 
    ((SELECT id FROM projects WHERE name = 'Demo Website'), 'en', 'es', 'Welcome to our website', 'Bienvenido a nuestro sitio web', 5, 'marianmt', 'completed', NOW(), NOW()),
    ((SELECT id FROM projects WHERE name = 'Demo Website'), 'en', 'es', 'Contact us for more information', 'Contactenos para mas informacion', 5, 'marianmt', 'completed', NOW(), NOW()),
    ((SELECT id FROM projects WHERE name = 'Blog Translation'), 'en', 'fr', 'Latest news and updates', 'Dernieres nouvelles et mises a jour', 4, 'marianmt', 'completed', NOW(), NOW()),
    ((SELECT id FROM projects WHERE name = 'E-commerce Site'), 'en', 'de', 'Add to cart', 'In den Warenkorb', 3, 'marianmt', 'completed', NOW(), NOW()),
    ((SELECT id FROM projects WHERE name = 'E-commerce Site'), 'en', 'de', 'Checkout', 'Zur Kasse', 1, 'marianmt', 'completed', NOW(), NOW()),
    ((SELECT id FROM projects WHERE name = 'Documentation'), 'en', 'it', 'Getting started guide', 'Guida introduttiva', 3, 'marianmt', 'completed', NOW(), NOW());

INSERT INTO payments (user_id, stripe_payment_intent_id, amount, currency, status, payment_method, created_at, paid_at)
VALUES 
    ((SELECT id FROM users WHERE email = 'premium@translatecloud.com'), 'pi_test_1234567890', 29.99, 'EUR', 'succeeded', 'card', NOW(), NOW()),
    ((SELECT id FROM users WHERE email = 'business@translatecloud.com'), 'pi_test_0987654321', 99.99, 'EUR', 'succeeded', 'card', NOW(), NOW());

SELECT 'Users' as tabla, COUNT(*) as registros FROM users
UNION ALL
SELECT 'Projects', COUNT(*) FROM projects
UNION ALL
SELECT 'Translations', COUNT(*) FROM translations
UNION ALL
SELECT 'Payments', COUNT(*) FROM payments;