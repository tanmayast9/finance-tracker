-- MySQL database setup for Financial Calculators
-- Run this script in MySQL to create the database and tables

CREATE DATABASE IF NOT EXISTS finance_calculators;
USE finance_calculators;

-- Users table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Calculations table
CREATE TABLE calculations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    calculator_type VARCHAR(50) NOT NULL,
    input_data TEXT NOT NULL,
    result_data TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Optional: Create a sample user (password: 'password123')
-- INSERT INTO users (username, email, password_hash) 
-- VALUES ('demo', 'demo@example.com', 'pbkdf2:sha256:600000...');
