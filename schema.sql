CREATE DATABASE IF NOT EXISTS lab3_flask;
USE lab3_flask;

CREATE TABLE IF NOT EXISTS admins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario VARCHAR(80) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL,
    password_hash VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    rol VARCHAR(20) NOT NULL DEFAULT 'usuario'
);

CREATE TABLE IF NOT EXISTS login_codes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    admin_id INT NOT NULL,
    codigo VARCHAR(6) NOT NULL,
    expires_at DATETIME NOT NULL,
    usado BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (admin_id) REFERENCES admins(id)
);

INSERT IGNORE INTO usuarios (id, nombre, email, rol)
VALUES
(1, 'Juan Perez', 'juan@demo.com', 'usuario'),
(2, 'Maria Lopez', 'maria@demo.com', 'admin');
