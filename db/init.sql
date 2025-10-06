-- ============================
-- Database: sentinel
-- ============================

-- 1. Student/Staff Profiles
CREATE TABLE IF NOT EXISTS profiles (
    id SERIAL PRIMARY KEY,
    entity_type VARCHAR(10) NOT NULL,  -- 'student' or 'staff'
    name VARCHAR(100),
    email VARCHAR(100),
    student_id VARCHAR(50),
    card_id VARCHAR(50),
    device_hash VARCHAR(100),
    department VARCHAR(50)
);

-- 2. Campus Card Swipes
CREATE TABLE IF NOT EXISTS swipes (
    id SERIAL PRIMARY KEY,
    card_id VARCHAR(50),
    location_id VARCHAR(50),
    timestamp TIMESTAMP
);

-- 3. Wi-Fi Association Logs
CREATE TABLE IF NOT EXISTS wifi_logs (
    id SERIAL PRIMARY KEY,
    device_hash VARCHAR(100),
    ap_id VARCHAR(50),
    timestamp TIMESTAMP
);

-- 4. Library Checkouts
CREATE TABLE IF NOT EXISTS library_checkouts (
    id SERIAL PRIMARY KEY,
    student_id VARCHAR(50),
    book_title VARCHAR(200),
    checkout_time TIMESTAMP
);

-- 5. Room/Lab Bookings
CREATE TABLE IF NOT EXISTS bookings (
    id SERIAL PRIMARY KEY,
    entity_id VARCHAR(50),
    room_id VARCHAR(50),
    start_time TIMESTAMP,
    end_time TIMESTAMP
);

-- 6. Free-text notes (helpdesk)
CREATE TABLE IF NOT EXISTS helpdesk_notes (
    id SERIAL PRIMARY KEY,
    entity_id VARCHAR(50),
    note_text TEXT,
    timestamp TIMESTAMP
);

-- ============================
-- Sample data inserts
-- ============================

INSERT INTO profiles (entity_type, name, email, student_id, card_id, device_hash, department)
VALUES 
('student', 'Alice Sharma', 'alice@campus.edu', 'S1001', 'C1001', 'D1001', 'CS'),
('student', 'Bob Kumar', 'bob@campus.edu', 'S1002', 'C1002', 'D1002', 'ME'),
('staff', 'Dr. Neha', 'neha@campus.edu', NULL, 'C2001', 'D2003', 'CS');

INSERT INTO swipes (card_id, location_id, timestamp)
VALUES 
('C1001', 'MainGate', NOW() - INTERVAL '1 hour'),
('C1002', 'Library', NOW() - INTERVAL '2 hour');

INSERT INTO wifi_logs (device_hash, ap_id, timestamp)
VALUES
('D1001', 'AP1', NOW() - INTERVAL '30 minute'),
('D1002', 'AP2', NOW() - INTERVAL '90 minute');

INSERT INTO library_checkouts (student_id, book_title, checkout_time)
VALUES
('S1001', 'Intro to AI', NOW() - INTERVAL '1 day'),
('S1002', 'Data Structures', NOW() - INTERVAL '2 days');

INSERT INTO bookings (entity_id, room_id, start_time, end_time)
VALUES
('S1001', 'Lab101', NOW() - INTERVAL '3 hour', NOW() - INTERVAL '2 hour');

INSERT INTO helpdesk_notes (entity_id, note_text, timestamp)
VALUES
('S1001', 'Laptop not connecting to Wi-Fi', NOW() - INTERVAL '1 hour');
