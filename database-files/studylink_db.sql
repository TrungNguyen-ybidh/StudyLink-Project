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
('Luella', 'Caghan', 'luella.caghannortheastern.edu', 'Computer Science'),
('Foster', 'De Meyer', 'foster.de meyernortheastern.edu', 'Business'),
('Andrea', 'McFadden', 'andrea.mcfaddennortheastern.edu', 'Psychology'),
('Godiva', 'Thorrington', 'godiva.thorringtonnortheastern.edu', 'Business'),
('Marco', 'Warlawe', 'marco.warlawenortheastern.edu', 'Mathematics'),
('Hermie', 'Woollard', 'hermie.woollardnortheastern.edu', 'Psychology'),
('Morgana', 'Orring', 'morgana.orringnortheastern.edu', 'Business'),
('Ahmed', 'Jiroutek', 'ahmed.jirouteknortheastern.edu', 'Mathematics'),
('Tedda', 'Rosencrantz', 'tedda.rosencrantznortheastern.edu', 'Business'),
('Therine', 'Clemo', 'therine.clemonortheastern.edu', 'Business'),
('Haskell', 'Malthus', 'haskell.malthusnortheastern.edu', 'Business'),
('Ardella', 'Copeman', 'ardella.copemannortheastern.edu', 'Mathematics'),
('Mallory', 'Pindred', 'mallory.pindrednortheastern.edu', 'Computer Science'),
('Herbert', 'Hagger', 'herbert.haggernortheastern.edu', 'Psychology'),
('Paquito', 'Campsall', 'paquito.campsallnortheastern.edu', 'Business'),
('Allegra', 'Kelf', 'allegra.kelfnortheastern.edu', 'Mathematics'),
('Gracie', 'Pycock', 'gracie.pycocknortheastern.edu', 'Engineering'),
('Craggie', 'Espinay', 'craggie.espinaynortheastern.edu', 'Business'),
('Brewster', 'McCuis', 'brewster.mccuisnortheastern.edu', 'Business'),
('Terry', 'Brendel', 'terry.brendelnortheastern.edu', 'Business'),
('Damita', 'Di Bernardo', 'damita.di bernardonortheastern.edu', 'Business'),
('Sam', 'Hasluck', 'sam.haslucknortheastern.edu', 'Engineering'),
('Shaun', 'Canete', 'shaun.canetenortheastern.edu', 'Psychology'),
('Willa', 'Sweetman', 'willa.sweetmannortheastern.edu', 'Engineering'),
('Elmo', 'Capaldo', 'elmo.capaldonortheastern.edu', 'Engineering'),
('Judah', 'Lantoph', 'judah.lantophnortheastern.edu', 'Psychology'),
('Woodman', 'Epple', 'woodman.epplenortheastern.edu', 'Psychology'),
('Kit', 'Swancott', 'kit.swancottnortheastern.edu', 'Psychology'),
('Maurita', 'Valti', 'maurita.valtinortheastern.edu', 'Psychology'),
('Jude', 'Whines', 'jude.whinesnortheastern.edu', 'Mathematics'),
('Randy', 'Stroder', 'randy.strodernortheastern.edu', 'Psychology'),
('Kettie', 'Velten', 'kettie.veltennortheastern.edu', 'Computer Science'),
('Bram', 'Monshall', 'bram.monshallnortheastern.edu', 'Business'),
('Kalinda', 'Duiguid', 'kalinda.duiguidnortheastern.edu', 'Engineering'),
('Kassandra', 'Corey', 'kassandra.coreynortheastern.edu', 'Engineering');

INSERT INTO student (fName, lName, email, enrollmentYear, advisorID, major, minor, GPA, riskFlag, enrollmentStatus, totalCredits) VALUES
('Mimi', 'Bibey', 'mimi.bibeynortheastern.edu', 2024, 4, 'Data Science', 'Data Science', 3.0, false, 'Probation', 55),
('Lolita', 'Aggis', 'lolita.aggisnortheastern.edu', 2026, 33, 'Software Engineering', 'Business', 3.48, true, 'Active', 10),
('Percy', 'Bicknell', 'percy.bicknellnortheastern.edu', 2021, 25, 'Engineering', 'Biology', 2.41, false, 'Enrolled', 102),
('Millard', 'Boriston', 'millard.boristonnortheastern.edu', 2023, 3, 'Economics', 'Computer Science', 3.15, true, 'Enrolled', 80),
('Franni', 'Petracci', 'franni.petraccinortheastern.edu', 2025, 28, 'Psychology', 'Engineering', 3.8, false, 'Active', 47),
('Xylina', 'Mayor', 'xylina.mayornortheastern.edu', 2023, 8, 'Economics', 'Psychology', 3.05, false, 'Active', 3),
('Rahal', 'Wilce', 'rahal.wilcenortheastern.edu', 2023, 20, 'Economics', 'Biology', 2.57, false, 'Leave', 27),
('Corny', 'Plumb', 'corny.plumbnortheastern.edu', 2023, 3, 'Engineering', 'Economics', 2.38, false, 'Leave', 127),
('Salim', 'Burhill', 'salim.burhillnortheastern.edu', 2021, 9, 'Business', 'Business', 3.05, true, 'Leave', 107),
('Byron', 'Fossitt', 'byron.fossittnortheastern.edu', 2025, 12, 'Biology', 'Biology', 2.81, false, 'Enrolled', 120),
('Roxane', 'Klimek', 'roxane.klimeknortheastern.edu', 2024, 16, 'Psychology', 'Data Science', 2.62, false, 'Active', 49),
('Adrien', 'Brownjohn', 'adrien.brownjohnnortheastern.edu', 2026, 36, 'Computer Science', 'Business', 2.94, true, 'Probation', 15),
('Melosa', 'Beeden', 'melosa.beedennortheastern.edu', 2021, 21, 'Engineering', 'Data Science', 3.88, false, 'Active', 103),
('Brina', 'Esome', 'brina.esomenortheastern.edu', 2025, 17, 'Engineering', 'Engineering', 3.25, false, 'Active', 56),
('Mag', 'McKelvie', 'mag.mckelvienortheastern.edu', 2026, 4, 'Computer Science', 'Engineering', 3.45, true, 'Leave', 11),
('Durand', 'Canto', 'durand.cantonortheastern.edu', 2022, 14, 'Software Engineering', 'Software Engineering', 2.43, true, 'Probation', 50),
('Fax', 'Algie', 'fax.algienortheastern.edu', 2022, 25, 'Software Engineering', 'Economics', 3.08, false, 'Probation', 120),
('Bale', 'Brandes', 'bale.brandesnortheastern.edu', 2021, 14, 'Engineering', 'Software Engineering', 2.17, true, 'Probation', 63),
('Duff', 'Limerick', 'duff.limericknortheastern.edu', 2026, 25, 'Psychology', 'Psychology', 3.77, true, 'Leave', 47),
('Meir', 'Verbrugge', 'meir.verbruggenortheastern.edu', 2021, 8, 'Business', 'Software Engineering', 3.58, true, 'Probation', 35),
('Marney', 'Hulme', 'marney.hulmenortheastern.edu', 2021, 32, 'Biology', 'Economics', 3.93, true, 'Probation', 110),
('Nathaniel', 'Cripwell', 'nathaniel.cripwellnortheastern.edu', 2023, 9, 'Economics', 'Engineering', 3.87, false, 'Enrolled', 35),
('Cookie', 'Scrine', 'cookie.scrinenortheastern.edu', 2026, 20, 'Engineering', 'Economics', 2.84, false, 'Probation', 8),
('Ritchie', 'Mammatt', 'ritchie.mammattnortheastern.edu', 2022, 14, 'Psychology', 'Economics', 3.18, true, 'Probation', 59),
('Alwyn', 'Natwick', 'alwyn.natwicknortheastern.edu', 2026, 24, 'Computer Science', 'Psychology', 3.69, true, 'Enrolled', 78),
('Bourke', 'Humpherson', 'bourke.humphersonnortheastern.edu', 2022, 10, 'Business', 'Biology', 2.12, true, 'Enrolled', 27),
('Lorie', 'Tuny', 'lorie.tunynortheastern.edu', 2022, 19, 'Computer Science', 'Engineering', 2.6, false, 'Enrolled', 80),
('Fredi', 'Theobold', 'fredi.theoboldnortheastern.edu', 2021, 13, 'Software Engineering', 'Engineering', 2.25, false, 'Active', 68),
('Katya', 'Tobin', 'katya.tobinnortheastern.edu', 2026, 7, 'Software Engineering', 'Psychology', 2.05, true, 'Enrolled', 76),
('Jim', 'Clackson', 'jim.clacksonnortheastern.edu', 2022, 21, 'Economics', 'Business', 3.29, false, 'Enrolled', 81),
('Carine', 'Gozzard', 'carine.gozzardnortheastern.edu', 2022, 36, 'Engineering', 'Engineering', 2.55, true, 'Probation', 108),
('Crystal', 'Scroggie', 'crystal.scroggienortheastern.edu', 2023, 18, 'Psychology', 'Business', 2.12, false, 'Probation', 40),
('Mellie', 'Skynner', 'mellie.skynnernortheastern.edu', 2022, 26, 'Economics', 'Data Science', 3.28, true, 'Probation', 110),
('Marice', 'Paradise', 'marice.paradisenortheastern.edu', 2025, 17, 'Software Engineering', 'Software Engineering', 3.34, false, 'Enrolled', 43),
('Cedric', 'Collis', 'cedric.collisnortheastern.edu', 2024, 33, 'Psychology', 'Psychology', 3.87, false, 'Active', 122);

INSERT INTO metric(studentID, category, privacyLevel, description, unit, metricType, metricName, metricValue)
VALUES
(1,'Study', 'low', 'Daily study hours', 'hours', 'numeric', 'study_hr', '3'),
(2, 'Sleep', 'medium', 'Sleep duration', 'hours', 'numeric', 'sleep', '7'),
(3, 'Stress', 'high', 'Stress level', 'score', 'numeric', 'stress', '5');


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