
-- ----------------------------
-- Database: drms
-- ----------------------------
CREATE DATABASE IF NOT EXISTS drms;
USE drms;

-- ----------------------------
-- Table: reliefcenters
-- ----------------------------
CREATE TABLE IF NOT EXISTS reliefcenters (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    location VARCHAR(200) NOT NULL,
    capacity INT NOT NULL,
    supplies_stock INT NOT NULL
);

-- ----------------------------
-- Table: volunteers
-- ----------------------------
CREATE TABLE IF NOT EXISTS volunteers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    skills VARCHAR(200) NOT NULL,
    availability VARCHAR(50) NOT NULL,
    assigned_center_id INT,
    FOREIGN KEY (assigned_center_id) REFERENCES reliefcenters(id)
);

-- ----------------------------
-- Table: victims
-- ----------------------------
CREATE TABLE IF NOT EXISTS victims (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    location VARCHAR(200) NOT NULL,
    need_type VARCHAR(100) NOT NULL,
    assigned_center_id INT,
    FOREIGN KEY (assigned_center_id) REFERENCES reliefcenters(id)
);

-- ----------------------------
-- Table: supplies
-- ----------------------------
CREATE TABLE IF NOT EXISTS supplies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    item_name VARCHAR(100) NOT NULL,
    quantity INT NOT NULL,
    center_id INT NOT NULL,
    FOREIGN KEY (center_id) REFERENCES reliefcenters(id)
);

-- ----------------------------
-- Table: donations
-- ----------------------------
CREATE TABLE IF NOT EXISTS donations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    donor_name VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL,
    amount DECIMAL(10,2),
    item_name VARCHAR(100),
    quantity INT,
    center_id INT,
    FOREIGN KEY (center_id) REFERENCES reliefcenters(id)
);

-- ----------------------------
-- Table: users
-- ----------------------------
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role ENUM('Admin','Volunteer','Victim','Donor') NOT NULL
);

-- ----------------------------
-- Table: alerts
-- ----------------------------
CREATE TABLE IF NOT EXISTS alerts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    center_id INT,
    item_name VARCHAR(100),
    quantity INT,
    alert_date DATETIME,
    FOREIGN KEY (center_id) REFERENCES reliefcenters(id)
);

-- ----------------------------
-- Table: volunteer_tasks
-- ----------------------------
CREATE TABLE IF NOT EXISTS volunteer_tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    volunteer_id INT NOT NULL,
    victim_id INT,
    task_description VARCHAR(255),
    date_assigned DATE,
    date_completed DATE,
    FOREIGN KEY (volunteer_id) REFERENCES volunteers(id),
    FOREIGN KEY (victim_id) REFERENCES victims(id)
);

-- ----------------------------
-- Views
-- ----------------------------
CREATE OR REPLACE VIEW LowSuppliesView AS
SELECT id, name, location, supplies_stock
FROM reliefcenters
WHERE supplies_stock < 50;

CREATE OR REPLACE VIEW TopVolunteersView AS
SELECT v.id, v.name, v.skills, v.assigned_center_id, COUNT(t.id) AS tasks_completed
FROM volunteers v
JOIN volunteer_tasks t ON v.id = t.volunteer_id
GROUP BY v.id
HAVING tasks_completed >= 3;

-- ----------------------------
-- Triggers
-- ----------------------------
DELIMITER $$
CREATE TRIGGER AssignVictimTrigger
BEFORE INSERT ON victims
FOR EACH ROW
BEGIN
    DECLARE center_id INT;
    SELECT id INTO center_id
    FROM reliefcenters
    ORDER BY capacity - supplies_stock DESC
    LIMIT 1;
    SET NEW.assigned_center_id = center_id;
END$$
DELIMITER ;

DELIMITER $$
CREATE TRIGGER DonationUpdateTrigger
AFTER INSERT ON donations
FOR EACH ROW
BEGIN
    IF NEW.type != 'Money' THEN
        UPDATE supplies
        SET quantity = quantity + NEW.quantity
        WHERE item_name = NEW.item_name
        AND center_id = NEW.center_id;
    END IF;
END$$
DELIMITER ;

DELIMITER $$
CREATE TRIGGER SupplyAlertTrigger
AFTER UPDATE ON supplies
FOR EACH ROW
BEGIN
    IF NEW.quantity < 50 THEN
        INSERT INTO alerts (center_id, item_name, quantity, alert_date)
        VALUES (NEW.center_id, NEW.item_name, NEW.quantity, NOW());
    END IF;
END$$
DELIMITER ;

-- ----------------------------
-- Initial Data
-- ----------------------------
INSERT INTO reliefcenters (name, location, capacity, supplies_stock) VALUES
('Hope Center', 'City A', 150, 200),
('Unity Shelter', 'City B', 100, 150),
('Care Hub', 'City C', 200, 300),
('Safe Haven', 'City D', 120, 180),
('Relief Point', 'City E', 180, 250);

INSERT INTO volunteers (name, skills, availability, assigned_center_id) VALUES
('Alice', 'First Aid', 'Weekdays', 1),
('Bob', 'Cooking', 'Weekends', 2),
('Charlie', 'Driving', 'Weekdays', 3),
('Diana', 'Counseling', 'Weekends', 4),
('Ethan', 'Logistics', 'Weekdays', 5);

INSERT INTO victims (name, location, need_type, assigned_center_id) VALUES
('Sam', 'City A', 'Food', 1),
('Lily', 'City B', 'Medical', 2),
('Kevin', 'City C', 'Shelter', 3),
('Nina', 'City D', 'Clothing', 4),
('Oscar', 'City E', 'Food', 5);

INSERT INTO supplies (item_name, quantity, center_id) VALUES
('Rice', 100, 1),
('Medicine', 50, 2),
('Blankets', 30, 3),
('Water Bottles', 80, 4),
('Canned Food', 60, 5);

INSERT INTO donations (donor_name, type, amount, item_name, quantity, center_id) VALUES
('John', 'Money', 500.00, NULL, NULL, 1),
('Mary', 'Food', NULL, 'Rice', 1, 2),
('Steve', 'Clothes', NULL, 'Jackets', 1, 3),
('Laura', 'Money', 300.00, NULL, NULL, 4),
('Tom', 'Medicine', NULL, 'Painkillers', 1, 5);

