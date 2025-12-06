-- Drop and create database
DROP DATABASE IF EXISTS study_link;
CREATE DATABASE study_link;
USE study_link;


-- Drop tables in reverse FK order
DROP TABLE IF EXISTS CourseSelectionStudent;
DROP TABLE IF EXISTS attEvent;
DROP TABLE IF EXISTS reminder;
DROP TABLE IF EXISTS assignment;
DROP TABLE IF EXISTS CourseSelection;
DROP TABLE IF EXISTS event;
DROP TABLE IF EXISTS term;
DROP TABLE IF EXISTS PlanBlock;
DROP TABLE IF EXISTS StudyPlan;
DROP TABLE IF EXISTS advisorReport;
DROP TABLE IF EXISTS CalendarConnection;
DROP TABLE IF EXISTS StudySummary;
DROP TABLE IF EXISTS metric;
DROP TABLE IF EXISTS student;
DROP TABLE IF EXISTS advisor;
DROP TABLE IF EXISTS DataError;
DROP TABLE IF EXISTS ImportJobError;
DROP TABLE IF EXISTS ImportJob_Metric;
DROP TABLE IF EXISTS recordedAt;
DROP TABLE IF EXISTS upload;
DROP TABLE IF EXISTS importJob;
DROP TABLE IF EXISTS systemAdmin;
DROP TABLE IF EXISTS dataset;


-- Create tables
CREATE TABLE advisor (
   advisorID INT AUTO_INCREMENT PRIMARY KEY,
   fname VARCHAR(100) NOT NULL,
   lName VARCHAR(100) NOT NULL,
   department VARCHAR(100) NOT NULL,
   email VARCHAR(100) NOT NULL
);


CREATE TABLE student (
   studentID INT AUTO_INCREMENT PRIMARY KEY,
   fName VARCHAR(100) NOT NULL,
   lName VARCHAR(100) NOT NULL,
   email VARCHAR(100) NOT NULL UNIQUE,
   enrollmentYear YEAR,
   major VARCHAR(100),
   minor VARCHAR(100),
   GPA DECIMAL(3,2) NOT NULL,
   riskFlag BOOLEAN,
   enrollmentStatus VARCHAR(50) NOT NULL,
   totalCredits INT,
   advisorID INT,
   FOREIGN KEY (advisorID) REFERENCES advisor(advisorID)
       ON DELETE CASCADE
       ON UPDATE CASCADE
);


CREATE TABLE advisorReport (
   reportID INT AUTO_INCREMENT PRIMARY KEY,
   studentID INT,
   advisorID INT,
   reportDesc TEXT,
   dateCreated DATETIME DEFAULT CURRENT_TIMESTAMP,
   timestamps DATETIME,
   filePath VARCHAR(255),
   type VARCHAR(50),
   description longtext,
   FOREIGN KEY (studentID) REFERENCES student(studentID)
       ON DELETE CASCADE
       ON UPDATE CASCADE,
   FOREIGN KEY (advisorID) REFERENCES advisor(advisorID)
       ON DELETE CASCADE
       ON UPDATE CASCADE
);


CREATE TABLE CalendarConnection (
   externalCalendarID INT AUTO_INCREMENT PRIMARY KEY,
   studentID INT NOT NULL,
   lastSyncedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
   syncStatus VARCHAR(50),
   FOREIGN KEY (studentID) REFERENCES student(studentID)
       ON DELETE CASCADE
       ON UPDATE CASCADE
);


CREATE TABLE StudyPlan (
   planID INT AUTO_INCREMENT PRIMARY KEY,
   studentID INT NOT NULL,
   status VARCHAR(50),
   versionNum INT,
   notes TEXT,
   dateCreated DATETIME DEFAULT CURRENT_TIMESTAMP,
   currentCredits INT,
   FOREIGN KEY (studentID) REFERENCES student(studentID)
       ON DELETE CASCADE
       ON UPDATE CASCADE
);


CREATE TABLE PlanBlock (
   blockID INT AUTO_INCREMENT PRIMARY KEY,
   planID INT NOT NULL,
   blockType VARCHAR(50),
   isLocked BOOLEAN NOT NULL,
   startTime DATETIME,
   endTime DATETIME,
   FOREIGN KEY (planID) REFERENCES StudyPlan(planID)
       ON DELETE CASCADE
       ON UPDATE CASCADE
);


CREATE TABLE event (
   eventID INT AUTO_INCREMENT PRIMARY KEY,
   name VARCHAR(100) NOT NULL,
   type VARCHAR(50),
   location VARCHAR(100),
   date DATE NOT NULL,
   startTime TIME NOT NULL,
   endTime TIME
);


CREATE TABLE attEvent (
   studentID INT NOT NULL,
   eventID INT NOT NULL,
   PRIMARY KEY (studentID, eventID),
   FOREIGN KEY (studentID) REFERENCES student(studentID)
       ON DELETE CASCADE
       ON UPDATE CASCADE,
   FOREIGN KEY (eventID) REFERENCES event(eventID)
       ON DELETE CASCADE
       ON UPDATE CASCADE
);


CREATE TABLE term (
   termID INT AUTO_INCREMENT PRIMARY KEY,
   name VARCHAR(100) NOT NULL,
   startDate DATE NOT NULL,
   endDate DATE NOT NULL
);


CREATE TABLE CourseSelection (
   courseID INT AUTO_INCREMENT PRIMARY KEY,
   termID INT NOT NULL,
   courseCode VARCHAR(20) NOT NULL,
   courseName VARCHAR(150) NOT NULL,
   location VARCHAR(100),
   credits INT NOT NULL,
   instructor VARCHAR(100),
   department VARCHAR(100) NOT NULL,
   date DATE,
   startTime TIME,
   endTime TIME,
   FOREIGN KEY (termID) REFERENCES term(termID)
       ON DELETE CASCADE
       ON UPDATE CASCADE
);


CREATE TABLE CourseSelectionStudent(
   studentID INT NOT NULL,
   courseID INT NOT NULL,
   PRIMARY KEY (studentID, courseID),
   FOREIGN KEY (studentID) REFERENCES student(studentID)
       ON DELETE CASCADE
       ON UPDATE CASCADE,
   FOREIGN KEY (courseID) REFERENCES CourseSelection(courseID)
       ON DELETE CASCADE
       ON UPDATE CASCADE
);


CREATE TABLE assignment (
   assignmentID INT AUTO_INCREMENT PRIMARY KEY,
   courseID INT NOT NULL,
   title VARCHAR(150) NOT NULL,
   scoreReceived DECIMAL(5,2),
   weight DECIMAL(5,2),
   status VARCHAR(50),
   assignmentType VARCHAR(50),
   assignmentDate DATE NOT NULL,
   assignmentTime TIME NOT NULL,
   maxScore INT NOT NULL,
   FOREIGN KEY (courseID) REFERENCES CourseSelection(courseID)
       ON DELETE CASCADE
       ON UPDATE CASCADE
);


CREATE TABLE reminder (
   reminderID INT AUTO_INCREMENT PRIMARY KEY,
   eventID INT NOT NULL,
   assignmentID INT NOT NULL,
   message TEXT,
   isActive BOOLEAN NOT NULL,
   date DATE NOT NULL,
   time TIME NOT NULL,
   FOREIGN KEY (eventID) REFERENCES event(eventID)
       ON DELETE CASCADE
       ON UPDATE CASCADE,
   FOREIGN KEY (assignmentID) REFERENCES assignment(assignmentID)
       ON DELETE CASCADE
       ON UPDATE CASCADE
);


CREATE TABLE StudySummary (
   summaryID INT AUTO_INCREMENT PRIMARY KEY,
   totalStudyHrs DECIMAL(5,2),
   avgStudyHrs DECIMAL(4,2),
   avgSleep DECIMAL(4,2),
   periodStart DATETIME,
   periodEnd DATETIME,
   studentID INT NOT NULL,
   FOREIGN KEY (studentID) REFERENCES student(studentID)
       ON DELETE CASCADE
       ON UPDATE CASCADE
);


CREATE TABLE metric (
   metricID INT AUTO_INCREMENT PRIMARY KEY,
   studentID INT NOT NULL,
   courseID INT,
   category VARCHAR(100),
   privacyLevel VARCHAR(100),
   description LONGTEXT,
   unit VARCHAR(50),
   metricType VARCHAR(100),
   metricName VARCHAR(100),
   metricValue VARCHAR(100),
   metricDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   FOREIGN KEY (studentID) REFERENCES student(studentID)
       ON DELETE CASCADE
       ON UPDATE CASCADE,
   FOREIGN KEY (courseID) REFERENCES CourseSelection(courseID)
       ON DELETE CASCADE
       ON UPDATE CASCADE
);


CREATE TABLE dataset (
   dataID INT AUTO_INCREMENT PRIMARY KEY,
   name VARCHAR(100) NOT NULL,
   category VARCHAR(50) NOT NULL,
   source VARCHAR(100),
   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE upload (
   uploadID INT AUTO_INCREMENT PRIMARY KEY,
   dataID INT NOT NULL,
   metricID INT NOT NULL,
   filePath VARCHAR(255),
   uploadDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   FOREIGN KEY (dataID) REFERENCES dataset(dataID)
       ON DELETE CASCADE
       ON UPDATE CASCADE,
   FOREIGN KEY (metricID) REFERENCES metric(metricID)
       ON DELETE CASCADE
       ON UPDATE CASCADE
);


CREATE TABLE SystemAdmin (
   adminID INT AUTO_INCREMENT PRIMARY KEY,
   name VARCHAR(100) NOT NULL,
   DOB DATE
);


CREATE TABLE importJob (
   jobID INT AUTO_INCREMENT PRIMARY KEY,
   errorCount INT,
   jobType VARCHAR(100) NOT NULL,
   startTime DATETIME,
   endTime DATETIME,
   status VARCHAR(50) NOT NULL,
   adminID INT NOT NULL,
   FOREIGN KEY (adminID) REFERENCES SystemAdmin(adminID)
       ON DELETE CASCADE
       ON UPDATE CASCADE
);


CREATE TABLE ImportJob_Metric (
   jobID INT NOT NULL,
   metricID INT NOT NULL,
   PRIMARY KEY (jobID, metricID),
   FOREIGN KEY (jobID) REFERENCES importJob(jobID)
       ON DELETE CASCADE
       ON UPDATE CASCADE,
   FOREIGN KEY (metricID) REFERENCES metric(metricID)
       ON DELETE CASCADE
       ON UPDATE CASCADE
);


CREATE TABLE ImportJobError (
   errorID INT AUTO_INCREMENT PRIMARY KEY,
   jobID INT NOT NULL,
   FOREIGN KEY (jobID) REFERENCES importJob(jobID)
       ON DELETE CASCADE
       ON UPDATE CASCADE
);


CREATE TABLE DataError (
   errorID INT,
   adminID INT,
   detectedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   errorType VARCHAR(100),
   errorStatus VARCHAR(100),
   PRIMARY KEY (errorID, adminID),
   FOREIGN KEY (errorID) REFERENCES ImportJobError(errorID)
       ON DELETE CASCADE
       ON UPDATE CASCADE,
   FOREIGN KEY (adminID) REFERENCES SystemAdmin(adminID)
       ON DELETE CASCADE
       ON UPDATE CASCADE
);


INSERT INTO SystemAdmin (adminID, name, DOB) VALUES
(1, 'Alidia Kigelman', '1982-05-23'),
(2, 'Adrienne Doreward', '1999-10-18'),
(3, 'Fifine Cutchey', '1998-05-11'),
(4, 'Verla Wightman', '1997-08-13'),
(5, 'Elinore Orts', '1977-09-06'),
(6, 'Derick Kiddy', '1981-08-25'),
(7, 'Edgar Verrill', '1979-03-08'),
(8, 'Paten Vitte', '1991-08-08'),
(9, 'Cora Alibone', '1981-08-21'),
(10, 'Avril Bigglestone', '1970-10-08');

INSERT INTO importJob (errorCount, jobType, StartTime, endTime, Status, adminID)
VALUES
(2, 'Metric Import', '2025-01-01 10:00:00', '2025-01-01 10:30:00', 'Completed', 1),
(0, 'Student Data Import', '2025-01-02 11:00:00', '2025-01-02 11:20:00', 'Completed', 2),
(1, 'Course Data Import', '2025-01-03 09:30:00', '2025-01-03 10:00:00', 'Failed', 3);


INSERT INTO ImportJobError (jobID)
VALUES
(1),
(2),
(3);


INSERT INTO DataError (errorID, adminID)
VALUES
(1,1),
(2,2),
(3,3);


INSERT INTO advisor (fname, lName, email, department) VALUES
('Layne', 'Maile', 'layne.maile@northeastern.edu', 'Mathematics'),
('Georgena', 'Ashdown', 'georgena.ashdown@northeastern.edu', 'Engineering'),
('Cosetta', 'Krout', 'cosetta.krout@northeastern.edu', 'Business'),
('Celie', 'Simenon', 'celie.simenon@northeastern.edu', 'Psychology'),
('Alphard', 'Birchett', 'alphard.birchett@northeastern.edu', 'Business'),
('Fernandina', 'Alessandrelli', 'fernandina.alessandrelli@northeastern.edu', 'Business'),
('Delilah', 'Moore', 'delilah.moore@northeastern.edu', 'Mathematics'),
('Fedora', 'Eustes', 'fedora.eustes@northeastern.edu', 'Engineering'),
('Amalle', 'Blackleech', 'amalle.blackleech@northeastern.edu', 'Psychology'),
('Pearl', 'Ubsdale', 'pearl.ubsdale@northeastern.edu', 'Psychology'),
('Munroe', 'Wantling', 'munroe.wantling@northeastern.edu', 'Computer Science'),
('Jaye', 'Rau', 'jaye.rau@northeastern.edu', 'Business'),
('Holly-anne', 'Klosterman', 'holly-anne.klosterman@northeastern.edu', 'Psychology'),
('Palmer', 'Jessep', 'palmer.jessep@northeastern.edu', 'Business'),
('Burty', 'McBlain', 'burty.mcblain@northeastern.edu', 'Engineering'),
('Gavrielle', 'Bunner', 'gavrielle.bunner@northeastern.edu', 'Engineering'),
('Sigismondo', 'Coan', 'sigismondo.coan@northeastern.edu', 'Psychology'),
('Prue', 'Bridson', 'prue.bridson@northeastern.edu', 'Computer Science'),
('Allissa', 'Thomson', 'allissa.thomson@northeastern.edu', 'Business'),
('Leigh', 'Boldry', 'leigh.boldry@northeastern.edu', 'Mathematics'),
('Germaine', 'Daish', 'germaine.daish@northeastern.edu', 'Business'),
('Gustaf', 'Pester', 'gustaf.pester@northeastern.edu', 'Psychology'),
('Jerrilyn', 'Liptrod', 'jerrilyn.liptrod@northeastern.edu', 'Engineering'),
('Margit', 'Dandy', 'margit.dandy@northeastern.edu', 'Business'),
('Aluino', 'Viste', 'aluino.viste@northeastern.edu', 'Mathematics'),
('Anders', 'Chaplyn', 'anders.chaplyn@northeastern.edu', 'Business'),
('Davy', 'Crambie', 'davy.crambie@northeastern.edu', 'Psychology'),
('Inger', 'Hansel', 'inger.hansel@northeastern.edu', 'Business'),
('Quintin', 'Elder', 'quintin.elder@northeastern.edu', 'Mathematics'),
('Wright', 'Alcoran', 'wright.alcoran@northeastern.edu', 'Mathematics'),
('Max', 'Rodolphe', 'max.rodolphe@northeastern.edu', 'Computer Science'),
('Cornelia', 'Deeney', 'cornelia.deeney@northeastern.edu', 'Business'),
('Theressa', 'Mangon', 'theressa.mangon@northeastern.edu', 'Psychology'),
('Saunder', 'Tweddle', 'saunder.tweddle@northeastern.edu', 'Psychology'),
('Tome', 'Berardt', 'tome.berardt@northeastern.edu', 'Psychology');


INSERT INTO student (fName, lName, email, enrollmentYear, advisorID, major, minor, GPA, riskFlag, enrollmentStatus, totalCredits) VALUES
('Eyde', 'Posthill', 'eyde.posthill@northeastern.edu', 2025, 4, 'Data Science', 'Computer Science', 2.92, false, 'Enrolled', 128),
('Stevena', 'Large', 'stevena.large@northeastern.edu', 2023, 27, 'Business', 'Data Science', 2.83, true, 'Leave', 5),
('Rudolph', 'Comelini', 'rudolph.comelini@northeastern.edu', 2023, 26, 'Data Science', 'Computer Science', 2.21, true, 'Active', 59),
('Godfry', 'Ackermann', 'godfry.ackermann@northeastern.edu', 2026, 5, 'Business', 'Engineering', 3.15, true, 'Probation', 87),
('Wileen', 'Hughes', 'wileen.hughes@northeastern.edu', 2022, 15, 'Economics', 'Economics', 2.21, true, 'Probation', 114),
('Melania', 'Heeps', 'melania.heeps@northeastern.edu', 2025, 34, 'Software Engineering', 'Software Engineering', 3.37, false, 'Enrolled', 54),
('Chester', 'McClaurie', 'chester.mcclaurie@northeastern.edu', 2026, 3, 'Data Science', 'Business', 2.11, false, 'Enrolled', 77),
('Haslett', 'Tabour', 'haslett.tabour@northeastern.edu', 2024, 33, 'Engineering', 'Psychology', 2.67, false, 'Active', 100),
('Marcellina', 'Bretherick', 'marcellina.bretherick@northeastern.edu', 2023, 8, 'Biology', 'Computer Science', 2.46, false, 'Enrolled', 41),
('Norbie', 'Matanin', 'norbie.matanin@northeastern.edu', 2024, 2, 'Psychology', 'Psychology', 3.27, true, 'Leave', 94),
('Bertram', 'Baswall', 'bertram.baswall@northeastern.edu', 2025, 21, 'Economics', 'Business', 3.89, true, 'Probation', 84),
('Ruperta', 'Stile', 'ruperta.stile@northeastern.edu', 2022, 12, 'Biology', 'Software Engineering', 2.01, true, 'Active', 127),
('Muire', 'Hundall', 'muire.hundall@northeastern.edu', 2026, 11, 'Business', 'Engineering', 3.84, false, 'Leave', 90),
('Emmit', 'Tabrett', 'emmit.tabrett@northeastern.edu', 2022, 6, 'Engineering', 'Psychology', 2.6, true, 'Leave', 124),
('Rowan', 'Karys', 'rowan.karys@northeastern.edu', 2022, 33, 'Software Engineering', 'Software Engineering', 3.21, true, 'Active', 51),
('Alleyn', 'Heindrich', 'alleyn.heindrich@northeastern.edu', 2022, 2, 'Psychology', 'Psychology', 2.42, true, 'Probation', 101),
('Gabbie', 'Coulman', 'gabbie.coulman@northeastern.edu', 2025, 28, 'Computer Science', 'Software Engineering', 2.43, true, 'Active', 17),
('Lori', 'Seid', 'lori.seid@northeastern.edu', 2023, 25, 'Software Engineering', 'Business', 2.31, false, 'Enrolled', 42),
('Kara', 'Posvner', 'kara.posvner@northeastern.edu', 2021, 10, 'Software Engineering', 'Software Engineering', 2.4, true, 'Leave', 85),
('Arlena', 'Webb-Bowen', 'arlena.webb-bowen@northeastern.edu', 2023, 2, 'Economics', 'Economics', 2.84, false, 'Enrolled', 80),
('Hamel', 'Fitkin', 'hamel.fitkin@northeastern.edu', 2025, 17, 'Business', 'Economics', 3.61, true, 'Probation', 43),
('Turner', 'Backes', 'turner.backes@northeastern.edu', 2023, 8, 'Data Science', 'Data Science', 3.41, true, 'Active', 99),
('Wileen', 'Mintoft', 'wileen.mintoft@northeastern.edu', 2021, 19, 'Business', 'Business', 2.11, true, 'Leave', 126),
('Maurizia', 'Fendlen', 'maurizia.fendlen@northeastern.edu', 2023, 29, 'Business', 'Software Engineering', 3.54, true, 'Leave', 6),
('Aloin', 'Jodlowski', 'aloin.jodlowski@northeastern.edu', 2026, 17, 'Economics', 'Economics', 2.51, true, 'Probation', 76),
('Dougy', 'Dolohunty', 'dougy.dolohunty@northeastern.edu', 2026, 29, 'Data Science', 'Data Science', 3.32, false, 'Leave', 29),
('Dix', 'Mankor', 'dix.mankor@northeastern.edu', 2025, 15, 'Biology', 'Data Science', 2.93, false, 'Active', 46),
('Melessa', 'Escofier', 'melessa.escofier@northeastern.edu', 2021, 4, 'Computer Science', 'Economics', 2.88, true, 'Probation', 25),
('Ruperta', 'Everill', 'ruperta.everill@northeastern.edu', 2024, 21, 'Economics', 'Psychology', 3.14, false, 'Probation', 43),
('Fey', 'Yashin', 'fey.yashin@northeastern.edu', 2025, 24, 'Psychology', 'Software Engineering', 2.09, true, 'Probation', 65),
('Iorgos', 'Radin', 'iorgos.radin@northeastern.edu', 2022, 32, 'Software Engineering', 'Software Engineering', 3.41, true, 'Probation', 64),
('Stacee', 'Sever', 'stacee.sever@northeastern.edu', 2024, 25, 'Economics', 'Software Engineering', 3.83, true, 'Probation', 68),
('Zena', 'Faichnie', 'zena.faichnie@northeastern.edu', 2021, 23, 'Data Science', 'Engineering', 3.01, true, 'Enrolled', 47),
('Rozina', 'Fullard', 'rozina.fullard@northeastern.edu', 2022, 35, 'Engineering', 'Psychology', 2.69, true, 'Leave', 116),
('Tim', 'Vakhrushin', 'tim.vakhrushin@northeastern.edu', 2021, 28, 'Biology', 'Biology', 2.96, true, 'Leave', 22);

INSERT INTO metric(studentID, category, privacyLevel, description, unit, metricType, metricName, metricValue)
VALUES
(1,'Study', 'low', 'Daily study hours', 'hours', 'numeric', 'study_hr', '3'),
(2, 'Sleep', 'medium', 'Sleep duration', 'hours', 'numeric', 'sleep', '7'),
(3, 'Stress', 'high', 'Stress level', 'score', 'numeric', 'stress', '5');

INSERT INTO dataset (name, category, source) VALUES
('Study Data', 'academic', 'student_upload'),
('Sleep Data', 'wellness', 'wearable_device'),
('Stress Data', 'wellness', 'self_reported');

INSERT INTO upload (dataID, metricID, filePath)
VALUES
(1, 1, '/files/study1.csv'),
(2, 2, '/files/sleep2.csv'),
(3, 3, '/files/stress3.csv');


INSERT INTO ImportJob_Metric (jobID, metricID)
VALUES
(1, 1),
(2,2),
(3,3);


INSERT INTO StudySummary (totalStudyHrs, avgStudyHrs, avgSleep, periodStart, periodEnd, studentID)
VALUES
(15, 3, 7, '2025-01-01', '2025-01-07', 1),
(10, 2, 6, '2025-01-01', '2025-01-07', 2),
(5, 1, 5, '2025-01-01', '2025-01-07', 3);


INSERT INTO CalendarConnection (studentID, externalCalendarID, lastSyncedAt, syncStatus)
VALUES
(1, 101,  NOW(), 'synced'),
(2, 102, NOW(), 'pending'),
(3, 103, NOW(), 'failed');


INSERT INTO advisorReport(studentID, advisorID, reportDesc, timestamps, filePath, type)
VALUES
(1, 1,'Progress improving', NOW(), '/reports/r1.pdf', 'academic'),
(2, 2,'Strong performance', NOW(), '/reports/r2.pdf', 'wellness'),
(3, 3,'Needs support', NOW(), '/reports/r3.pdf', 'risk');


INSERT INTO StudyPlan (studentID, status, versionNum, notes, currentCredits)
VALUES
(1, 'Active', 1, 'Plan approved', 15),
(2, 'Active', 1, 'Strong start', 12),
(3, 'Review', 2, 'At-risk monitoring', 6);


INSERT INTO PlanBlock (planID, blockType, isLocked, startTime, endTime)
VALUES
(1, 'Study', 0, '2025-01-10 10:00', '2025-01-10 12:00'),
(2, 'Class', 1, '2025-01-11 09:00', '2025-01-11 11:00'),
(3, 'Review', 0, '2025-01-12 14:00', '2025-01-12 16:00');


INSERT INTO term (name, startDate, endDate)
VALUES
('Spring 2025', '2025-01-05', '2025-05-01'),
('Summer 2025', '2025-05-20', '2025-08-10'),
('Fall 2025', '2025-09-01', '2025-12-20');


INSERT INTO CourseSelection (courseID, termID, courseCode, courseName, location, credits, instructor, department, date, startTime, endTime)
VALUES
(1, 2, 2500, 'Fundamentals of CS', 'Room 101', 4, 'Dr. Allen', 'Khoury','2025-02-01', '09:00', '10:05' ),
(2, 2,1100, 'Intro Biology', 'Room 202', 3, 'Dr. Kim', 'COS','2025-06-10', '10:00', '11:40'),
(3, 1, 2000, 'Finance Basics', 'Room 303', 3, 'Dr. White', 'DAmore McKim','2025-09-15', '13:00', '14:40');


INSERT INTO assignment(courseID, title, scoreReceived, weight, status, assignmentType, assignmentDate, assignmentTime, maxScore)
VALUES
(1, 'HW1', 95, 0.1, 'graded', 'homework', '2025-02-10', '23:59',100),
(2, 'Lab1', 88, 1.5, 'submitted', 'lab', '2025-06-20', '17:00',100),
(3, 'Exam1', 75, 0.3, 'graded', 'exam', '2025-09-20', '10:00',100);


INSERT INTO event(eventID, name, type, location, date, startTime, endTime)
VALUES
(1,'Study Group', 'academic', 'Library', '2025-02-05', '15:00','18:00'),
(2,'Career Fair', 'career', 'Hall A',  '2025-03-10', '11:00','14:00'),
(3,'Tutoring Session', 'academic', 'Room 150', '2025-04-01', '14:00','16:00');


INSERT INTO reminder (eventID, assignmentID, message, isActive, date, time)
VALUES
(1, 1, 'Study group reminder', 1, '2025-02-04', '20:00'),
(2, 2, 'Lab due soon', 1, '2025-06-18', '18:00'),
(3, 3, 'Exam tomorrow', 1, '2025-09-19', '19:00');


INSERT INTO attEvent (studentID, eventID)
VALUES
(1, 1),
(2, 2),
(3, 3);


INSERT INTO CourseSelectionStudent (studentID, courseID)
VALUES
(1,1),
(2,2),
(3,3);