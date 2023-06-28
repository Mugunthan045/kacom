USE kacom_users;
CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
  username VARCHAR(255) UNIQUE,
  email VARCHAR(255) UNIQUE,
  password VARCHAR(255),
  is_active TINYINT(1)
);

