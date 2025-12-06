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

INSERT INTO metric (studentID, courseID, category, privacyLevel, description, unit, metricType, metricName, metricValue, metricDate)
VALUES
(7,23,'Study','high','daily study hours','percent','categorical','stress',0.5,'2025-06-13 18:56:48'),
(25,18,'Grades','high','daily study hours','hours','categorical','stress',2.8,'2025-10-28 18:39:28'),
(20,7,'Stress','medium','stress level','hours','categorical','stress',2.8,'2025-03-23 23:28:05'),
(19,13,'Grades','low','daily study hours','score','categorical','stress',1.2,'2025-01-25 04:26:09'),
(19,13,'Study','low','daily study hours','score','categorical','stress',0.8,'2025-09-08 05:03:43'),
(14,14,'Sleep','low','sleep duration','hours','categorical','stress',3.7,'2025-10-21 03:46:15'),
(34,4,'Engagement','medium','daily study hours','percent','numeric','sleep',1.2,'2025-02-20 02:52:12'),
(6,16,'Engagement','medium','stress level','hours','categorical','stress',2.0,'2024-12-12 03:00:25'),
(14,27,'Study','low','daily study hours','percent','numeric','study_hrs',4.0,'2025-06-23 16:47:51'),
(24,29,'Engagement','low','daily study hours','score','numeric','stress',3.2,'2025-05-02 04:10:07'),
(32,20,'Study','low','daily study hours','score','numeric','study_hrs',2.0,'2025-09-04 11:49:23'),
(6,31,'Sleep','medium','sleep duration','percent','numeric','sleep',3.7,'2025-08-11 05:02:21'),
(2,14,'Engagement','medium','stress level','percent','numeric','attendance_pct',3.2,'2025-07-27 18:23:10'),
(26,24,'Stress','high','stress level','hours','numeric','stress',4.0,'2025-04-09 03:37:48'),
(4,24,'Engagement','medium','stress level','score','categorical','stress',3.2,'2025-10-05 20:48:02'),
(6,23,'Engagement','high','stress level','hours','categorical','sleep',1.2,'2025-10-28 13:01:32'),
(10,34,'Grades','high','daily study hours','score','categorical','attendance_pct',1.6,'2024-12-19 09:42:12'),
(25,17,'Grades','high','daily study hours','hours','categorical','study_hrs',3.2,'2025-11-18 06:57:58'),
(24,15,'Sleep','high','sleep duration','hours','numeric','stress',4.5,'2025-01-05 20:08:23'),
(10,27,'Engagement','high','stress level','hours','numeric','attendance_pct',0.5,'2025-01-13 23:22:51'),
(15,15,'Study','low','daily study hours','percent','categorical','stress',4.0,'2025-08-19 17:16:56'),
(24,20,'Engagement','medium','stress level','hours','categorical','sleep',4.0,'2025-09-14 15:07:29'),
(6,23,'Study','high','daily study hours','hours','numeric','stress',3.7,'2025-03-06 14:32:37'),
(22,34,'Engagement','low','daily study hours','score','categorical','sleep',2.8,'2025-10-07 03:15:52'),
(21,29,'Sleep','medium','sleep duration','percent','categorical','stress',0.8,'2025-06-06 20:56:18'),
(10,9,'Engagement','high','stress level','percent','categorical','sleep',0.8,'2025-02-04 08:22:16'),
(2,14,'Grades','low','daily study hours','hours','numeric','attendance_pct',0.5,'2025-01-18 20:45:22'),
(10,17,'Sleep','high','sleep duration','percent','categorical','sleep',2.0,'2025-02-06 13:30:05'),
(8,24,'Stress','high','stress level','score','numeric','stress',2.8,'2025-03-24 02:01:53'),
(35,17,'Study','high','daily study hours','percent','categorical','study_hrs',3.7,'2025-11-26 03:41:43'),
(12,19,'Grades','high','daily study hours','percent','categorical','attendance_pct',0.5,'2025-04-14 01:22:15'),
(21,8,'Stress','low','stress level','score','numeric','stress',3.2,'2024-12-20 17:22:25'),
(27,6,'Engagement','medium','stress level','score','categorical','stress',4.5,'2025-03-05 01:49:42'),
(21,26,'Study','medium','daily study hours','percent','categorical','stress',3.2,'2025-02-25 21:27:20'),
(18,18,'Sleep','low','sleep duration','hours','categorical','sleep',2.8,'2025-03-23 03:30:15'),
(9,2,'Engagement','low','daily study hours','percent','numeric','attendance_pct',0.8,'2025-03-16 03:42:46'),
(34,1,'Grades','high','daily study hours','score','categorical','attendance_pct',0.8,'2025-09-01 04:12:53'),
(17,30,'Engagement','medium','daily study hours','hours','numeric','stress',0.5,'2025-02-16 08:22:01'),
(35,18,'Stress','low','stress level','score','numeric','stress',3.2,'2025-11-11 18:35:20'),
(32,16,'Engagement','high','daily study hours','hours','categorical','attendance_pct',4.0,'2025-05-19 02:43:22'),
(29,26,'Grades','high','daily study hours','score','numeric','attendance_pct',1.6,'2025-09-20 09:01:10'),
(8,20,'Grades','low','daily study hours','hours','categorical','attendance_pct',3.2,'2025-01-07 07:46:59'),
(11,1,'Sleep','medium','sleep duration','percent','numeric','stress',2.8,'2025-02-16 02:31:46'),
(12,15,'Study','medium','daily study hours','percent','numeric','study_hrs',2.8,'2025-10-30 23:08:08'),
(30,16,'Stress','medium','stress level','percent','categorical','stress',1.6,'2025-04-03 09:14:56'),
(27,29,'Engagement','medium','daily study hours','score','categorical','stress',3.2,'2025-01-14 03:19:45'),
(30,26,'Engagement','medium','stress level','score','categorical','sleep',1.6,'2025-11-24 18:06:39'),
(22,19,'Engagement','medium','stress level','hours','numeric','attendance_pct',4.0,'2025-02-20 09:48:03'),
(3,27,'Grades','medium','daily study hours','score','categorical','attendance_pct',2.0,'2025-01-06 16:19:47'),
(8,8,'Grades','high','daily study hours','hours','numeric','study_hrs',2.0,'2025-05-11 04:06:02'),
(30,15,'Stress','high','stress level','score','categorical','stress',3.2,'2025-09-18 06:25:22'),
(20,4,'Engagement','low','stress level','percent','categorical','attendance_pct',1.2,'2025-02-25 19:19:45'),
(4,9,'Sleep','high','sleep duration','percent','numeric','stress',4.5,'2024-12-06 20:10:14'),
(28,10,'Grades','medium','daily study hours','hours','categorical','attendance_pct',0.8,'2025-09-25 13:01:04'),
(4,13,'Engagement','high','daily study hours','percent','numeric','stress',0.5,'2025-01-02 10:09:03'),
(29,11,'Grades','high','daily study hours','score','categorical','attendance_pct',0.8,'2025-07-24 12:52:42'),
(25,18,'Stress','medium','stress level','score','categorical','stress',1.6,'2025-01-13 13:55:28'),
(7,28,'Stress','medium','stress level','score','categorical','stress',3.7,'2025-10-09 01:32:17'),
(14,1,'Sleep','high','sleep duration','percent','numeric','sleep',0.5,'2025-07-23 18:38:33'),
(2,17,'Study','medium','daily study hours','score','numeric','stress',3.2,'2025-05-11 00:56:08'),
(29,33,'Sleep','medium','sleep duration','hours','numeric','sleep',1.2,'2024-12-28 17:38:49'),
(6,26,'Study','medium','daily study hours','hours','categorical','study_hrs',1.2,'2025-04-26 06:51:03'),
(18,33,'Stress','low','stress level','hours','numeric','stress',0.5,'2025-01-06 01:40:03'),
(14,12,'Engagement','low','stress level','percent','categorical','sleep',3.2,'2025-06-15 20:43:15'),
(11,17,'Sleep','low','sleep duration','hours','numeric','stress',4.5,'2025-07-03 22:05:41'),
(20,5,'Sleep','high','sleep duration','hours','numeric','sleep',1.2,'2025-04-07 07:08:36'),
(14,20,'Study','medium','daily study hours','percent','numeric','stress',2.8,'2025-04-26 06:45:01'),
(27,20,'Grades','medium','daily study hours','hours','numeric','attendance_pct',0.5,'2024-12-25 02:15:06'),
(21,25,'Grades','low','daily study hours','percent','numeric','attendance_pct',1.6,'2025-08-28 11:51:34'),
(8,23,'Grades','low','daily study hours','score','numeric','attendance_pct',1.2,'2025-07-17 05:57:27');


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

INSERT INTO advisorReport (studentID, advisorID, reportDesc, timestamps, filePath, type) VALUES
(12, 24, 'Progress Improving', '2026-01-23 13:15:57', '/reports/r10.pdf', 'meeting_note'),
(13, 25, 'Progress Improving', '2026-10-03 20:22:48', '/reports/r1.pdf', 'academic'),
(27, 8, 'Needs Support', '2027-10-27 12:09:09', '/reports/r26.pdf', 'risk'),
(1, 5, 'Progress Improving', '2027-08-05 11:47:08', '/reports/r27.pdf', 'risk'),
(18, 18, 'Strong Performance', '2027-12-01 10:53:32', '/reports/r7.pdf', 'meeting_note'),
(29, 22, 'Progress Improving', '2025-07-28 16:17:23', '/reports/r34.pdf', 'meeting_note'),
(12, 21, 'Strong Performance', '2026-09-05 02:51:08', '/reports/r27.pdf', 'academic'),
(23, 14, 'Progress Improving', '2025-04-24 08:46:59', '/reports/r17.pdf', 'wellness'),
(27, 21, 'Progress Improving', '2026-12-19 05:23:17', '/reports/r7.pdf', 'academic'),
(32, 30, 'Needs Support', '2026-05-14 11:13:50', '/reports/r33.pdf', 'meeting_note'),
(29, 27, 'Strong Performance', '2026-02-19 06:37:33', '/reports/r19.pdf', 'academic'),
(27, 35, 'Strong Performance', '2025-12-29 09:31:39', '/reports/r17.pdf', 'meeting_note'),
(4, 33, 'Needs Support', '2026-12-10 15:30:25', '/reports/r21.pdf', 'academic'),
(9, 21, 'Needs Support', '2026-09-14 03:09:56', '/reports/r28.pdf', 'wellness'),
(6, 4, 'Strong Performance', '2025-10-20 06:58:12', '/reports/r13.pdf', 'academic'),
(10, 22, 'Strong Performance', '2026-08-20 11:00:52', '/reports/r35.pdf', 'meeting_note'),
(29, 26, 'Strong Performance', '2027-04-21 07:10:26', '/reports/r32.pdf', 'academic'),
(26, 2, 'Progress Improving', '2027-03-01 14:33:55', '/reports/r2.pdf', 'academic'),
(8, 3, 'Needs Support', '2025-03-16 10:41:09', '/reports/r31.pdf', 'meeting_note'),
(3, 33, 'Progress Improving', '2025-01-30 12:04:52', '/reports/r1.pdf', 'meeting_note'),
(21, 35, 'Needs Support', '2026-01-23 09:47:07', '/reports/r26.pdf', 'academic'),
(33, 35, 'Strong Performance', '2027-03-25 22:02:13', '/reports/r30.pdf', 'meeting_note'),
(32, 12, 'Needs Support', '2026-07-13 15:53:20', '/reports/r27.pdf', 'meeting_note'),
(5, 10, 'Progress Improving', '2026-09-20 07:06:39', '/reports/r3.pdf', 'risk'),
(17, 20, 'Needs Support', '2026-06-28 04:19:27', '/reports/r7.pdf', 'wellness'),
(22, 23, 'Strong Performance', '2027-04-21 12:34:14', '/reports/r25.pdf', 'academic'),
(2, 27, 'Strong Performance', '2025-04-10 17:22:14', '/reports/r20.pdf', 'academic'),
(29, 11, 'Progress Improving', '2027-01-13 20:34:21', '/reports/r4.pdf', 'meeting_note'),
(27, 21, 'Needs Support', '2025-08-05 05:05:55', '/reports/r25.pdf', 'academic'),
(7, 23, 'Progress Improving', '2026-07-28 10:29:18', '/reports/r8.pdf', 'wellness'),
(24, 17, 'Strong Performance', '2025-05-16 09:53:18', '/reports/r6.pdf', 'meeting_note'),
(7, 1, 'Progress Improving', '2027-06-03 22:19:46', '/reports/r14.pdf', 'academic'),
(21, 7, 'Strong Performance', '2025-10-13 18:00:56', '/reports/r22.pdf', 'meeting_note'),
(31, 11, 'Strong Performance', '2025-07-24 01:53:51', '/reports/r32.pdf', 'meeting_note'),
(11, 3, 'Progress Improving', '2025-05-04 15:50:45', '/reports/r26.pdf', 'risk'),
(7, 9, 'Strong Performance', '2026-03-23 15:04:33', '/reports/r5.pdf', 'meeting_note'),
(1, 3, 'Strong Performance', '2025-10-30 02:36:00', '/reports/r10.pdf', 'meeting_note'),
(29, 10, 'Needs Support', '2025-01-08 20:19:31', '/reports/r4.pdf', 'academic'),
(25, 34, 'Progress Improving', '2024-12-13 21:19:13', '/reports/r30.pdf', 'risk'),
(25, 32, 'Needs Support', '2025-06-01 10:34:54', '/reports/r7.pdf', 'wellness'),
(26, 30, 'Progress Improving', '2026-01-07 00:54:38', '/reports/r10.pdf', 'wellness'),
(9, 5, 'Progress Improving', '2025-03-31 04:51:41', '/reports/r30.pdf', 'academic'),
(6, 24, 'Progress Improving', '2026-12-22 07:33:37', '/reports/r7.pdf', 'academic'),
(5, 9, 'Strong Performance', '2027-09-10 12:24:57', '/reports/r9.pdf', 'academic'),
(4, 34, 'Needs Support', '2026-09-30 21:03:32', '/reports/r36.pdf', 'meeting_note'),
(19, 25, 'Strong Performance', '2025-08-02 06:39:23', '/reports/r7.pdf', 'meeting_note'),
(5, 5, 'Progress Improving', '2025-05-23 20:34:04', '/reports/r24.pdf', 'risk'),
(17, 6, 'Needs Support', '2026-04-30 16:26:20', '/reports/r24.pdf', 'academic'),
(20, 10, 'Needs Support', '2025-09-16 20:51:51', '/reports/r27.pdf', 'meeting_note'),
(14, 7, 'Needs Support', '2025-12-03 06:29:19', '/reports/r30.pdf', 'meeting_note'),
(14, 30, 'Progress Improving', '2025-08-29 09:42:26', '/reports/r28.pdf', 'risk'),
(35, 8, 'Strong Performance', '2025-06-21 12:36:04', '/reports/r23.pdf', 'meeting_note'),
(26, 11, 'Strong Performance', '2027-03-17 01:49:03', '/reports/r23.pdf', 'academic'),
(2, 18, 'Needs Support', '2027-06-16 18:44:12', '/reports/r1.pdf', 'meeting_note'),
(30, 7, 'Needs Support', '2026-09-16 05:33:04', '/reports/r11.pdf', 'meeting_note'),
(26, 32, 'Progress Improving', '2026-10-30 00:51:32', '/reports/r21.pdf', 'wellness'),
(20, 12, 'Strong Performance', '2026-10-05 05:18:58', '/reports/r7.pdf', 'meeting_note'),
(17, 4, 'Needs Support', '2027-09-02 02:30:44', '/reports/r18.pdf', 'risk'),
(4, 13, 'Strong Performance', '2027-08-20 10:01:04', '/reports/r4.pdf', 'academic'),
(2, 24, 'Needs Support', '2026-10-30 00:01:12', '/reports/r9.pdf', 'meeting_note'),
(15, 15, 'Strong Performance', '2027-04-01 10:27:57', '/reports/r9.pdf', 'academic'),
(1, 34, 'Progress Improving', '2025-01-28 03:57:49', '/reports/r30.pdf', 'academic'),
(34, 26, 'Strong Performance', '2026-06-02 10:37:40', '/reports/r25.pdf', 'meeting_note'),
(23, 14, 'Progress Improving', '2025-01-23 14:49:10', '/reports/r36.pdf', 'meeting_note'),
(28, 16, 'Strong Performance', '2024-12-31 13:25:30', '/reports/r21.pdf', 'academic'),
(18, 15, 'Progress Improving', '2026-07-30 13:37:10', '/reports/r30.pdf', 'academic'),
(12, 23, 'Progress Improving', '2026-09-15 07:27:02', '/reports/r16.pdf', 'meeting_note'),
(22, 11, 'Needs Support', '2025-07-25 06:15:58', '/reports/r20.pdf', 'meeting_note'),
(25, 19, 'Needs Support', '2026-06-20 14:24:24', '/reports/r9.pdf', 'wellness'),
(22, 33, 'Progress Improving', '2025-07-24 21:38:02', '/reports/r31.pdf', 'wellness');


INSERT INTO StudyPlan (studentID, status, versionNum, notes, currentCredits) VALUES
(18, 'Archived', 3, 'Plan approved', 20),
(25, 'Active', 2, 'At-risk monitoring', 3),
(23, 'Review', 3, 'Strong', 20),
(20, 'Archived', 1, 'Strong', 20),
(15, 'Active', 1, 'Start', 20),
(27, 'Active', 1, 'At-risk monitoring', 4),
(33, 'Review', 1, 'Plan approved', 2),
(12, 'Archived', 2, 'Strong', 13),
(4, 'Archived', 1, 'Start', 20),
(15, 'Active', 2, 'At-risk monitoring', 5),
(6, 'Active', 2, 'Plan approved', 8),
(14, 'Active', 2, 'Start', 4),
(7, 'Archived', 1, 'Start', 16),
(30, 'Review', 1, 'Strong', 1),
(15, 'Active', 1, 'At-risk monitoring', 7),
(8, 'Review', 3, 'At-risk monitoring', 15),
(28, 'Archived', 2, 'At-risk monitoring', 2),
(27, 'Review', 1, 'Strong', 5),
(13, 'Review', 2, 'Strong', 16),
(19, 'Archived', 1, 'Plan approved', 14),
(18, 'Review', 1, 'Plan approved', 18),
(9, 'Review', 3, 'Start', 11),
(5, 'Review', 3, 'At-risk monitoring', 19),
(13, 'Archived', 2, 'Start', 6),
(7, 'Active', 3, 'Start', 11),
(1, 'Archived', 1, 'Strong', 9),
(17, 'Active', 2, 'At-risk monitoring', 5),
(6, 'Active', 1, 'Strong', 12),
(1, 'Review', 3, 'Start', 10),
(23, 'Review', 3, 'Start', 4),
(25, 'Active', 1, 'Strong', 6),
(6, 'Review', 2, 'Plan approved', 15),
(30, 'Review', 1, 'Plan approved', 14),
(28, 'Active', 2, 'At-risk monitoring', 10),
(1, 'Archived', 1, 'At-risk monitoring', 7);


INSERT INTO PlanBlock (planID, blockType, isLocked, startTime, endTime) VALUES
(3, 'Break', true, '2025-07-11 14:57:32', '2025-07-11 16:28:32'),
(20, 'Break', true, '2025-08-22 02:04:59', '2025-08-22 04:05:59'),
(31, 'Review', true, '2025-10-14 16:23:43', '2025-10-14 19:49:43'),
(29, 'Break', false, '2025-08-20 03:13:28', '2025-08-20 04:44:28'),
(20, 'Break', false, '2025-11-23 03:51:06', '2025-11-23 05:55:06'),
(28, 'Study', true, '2025-08-09 11:40:49', '2025-08-09 13:33:49'),
(26, 'Class', false, '2025-06-16 11:05:07', '2025-06-16 12:34:07'),
(1, 'Study', true, '2025-09-12 16:47:37', '2025-09-12 18:27:37'),
(7, 'Class', false, '2025-05-18 12:42:49', '2025-05-18 14:05:49'),
(9, 'Sleep', true, '2025-01-25 18:59:23', '2025-01-25 22:38:23'),
(15, 'Break', false, '2025-02-04 01:37:37', '2025-02-04 03:01:37'),
(29, 'Break', false, '2025-01-01 15:38:30', '2025-01-01 19:19:30'),
(13, 'Break', false, '2025-07-22 18:04:40', '2025-07-22 19:42:40'),
(35, 'Break', false, '2025-11-23 10:18:00', '2025-11-23 13:30:00'),
(33, 'Break', false, '2025-08-26 11:02:15', '2025-08-26 12:17:15'),
(5, 'Sleep', true, '2025-04-15 09:09:07', '2025-04-15 12:22:07'),
(12, 'Class', true, '2025-09-11 07:13:04', '2025-09-11 09:09:04'),
(6, 'Study', true, '2025-07-15 05:06:45', '2025-07-15 08:33:45'),
(23, 'Break', true, '2025-10-22 15:35:48', '2025-10-22 18:20:48'),
(27, 'Review', false, '2025-03-13 14:29:49', '2025-03-13 16:47:49'),
(19, 'Break', false, '2025-09-13 17:46:19', '2025-09-13 19:49:19'),
(32, 'Break', true, '2025-07-18 21:04:32', '2025-07-19 00:23:32'),
(24, 'Sleep', false, '2025-11-02 15:43:10', '2025-11-02 19:28:10'),
(21, 'Class', true, '2025-10-12 22:57:10', '2025-10-13 00:15:10'),
(3, 'Review', true, '2025-05-15 16:05:25', '2025-05-15 18:46:25'),
(29, 'Study', true, '2025-01-27 22:33:33', '2025-01-28 00:25:33'),
(20, 'Sleep', true, '2024-12-21 07:35:29', '2024-12-21 10:08:29'),
(33, 'Review', true, '2025-06-09 21:26:02', '2025-06-09 23:51:02'),
(31, 'Sleep', false, '2025-10-12 01:16:37', '2025-10-12 02:30:37'),
(30, 'Review', false, '2025-11-09 07:30:14', '2025-11-09 08:43:14'),
(26, 'Review', false, '2025-06-24 09:23:44', '2025-06-24 11:00:44'),
(2, 'Class', true, '2024-12-24 02:15:35', '2024-12-24 04:05:35'),
(7, 'Study', false, '2025-08-23 23:05:34', '2025-08-24 02:15:34'),
(13, 'Class', false, '2025-08-11 08:55:41', '2025-08-11 12:54:41'),
(32, 'Break', false, '2025-11-08 21:32:31', '2025-11-08 23:42:31'),
(24, 'Sleep', true, '2025-03-25 18:50:44', '2025-03-25 22:34:44'),
(15, 'Class', true, '2025-08-27 03:05:31', '2025-08-27 05:54:31'),
(28, 'Break', true, '2025-11-01 04:22:30', '2025-11-01 07:21:30'),
(31, 'Sleep', false, '2025-10-26 05:08:01', '2025-10-26 07:03:01'),
(20, 'Break', false, '2025-08-21 20:45:32', '2025-08-21 23:51:32'),
(18, 'Break', false, '2025-01-27 06:27:40', '2025-01-27 08:45:40'),
(12, 'Class', true, '2025-11-08 10:42:24', '2025-11-08 14:35:24'),
(8, 'Class', false, '2024-12-07 06:02:46', '2024-12-07 07:14:46'),
(23, 'Review', false, '2025-04-11 07:44:03', '2025-04-11 08:46:03'),
(32, 'Class', true, '2025-06-18 14:06:22', '2025-06-18 17:08:22'),
(24, 'Review', true, '2025-07-09 03:25:01', '2025-07-09 04:50:01'),
(6, 'Study', true, '2025-01-07 04:52:45', '2025-01-07 08:30:45'),
(18, 'Sleep', true, '2025-06-14 05:08:00', '2025-06-14 08:21:00'),
(11, 'Study', false, '2025-05-30 16:49:40', '2025-05-30 18:00:40'),
(15, 'Study', false, '2025-09-07 12:38:38', '2025-09-07 14:32:38'),
(16, 'Sleep', false, '2025-03-11 23:56:25', '2025-03-12 01:29:25'),
(18, 'Break', true, '2025-09-12 01:38:45', '2025-09-12 02:42:45'),
(10, 'Review', true, '2025-08-20 12:52:49', '2025-08-20 15:27:49'),
(4, 'Class', true, '2025-09-29 14:57:26', '2025-09-29 16:40:26'),
(18, 'Study', false, '2025-01-10 23:16:52', '2025-01-11 02:03:52'),
(31, 'Study', true, '2025-11-11 18:48:33', '2025-11-11 21:05:33'),
(24, 'Study', true, '2025-12-03 13:38:14', '2025-12-03 17:27:14'),
(35, 'Sleep', false, '2025-10-25 15:56:07', '2025-10-25 19:35:07'),
(4, 'Class', true, '2025-06-15 17:15:26', '2025-06-15 20:16:26'),
(6, 'Break', true, '2025-06-15 17:36:33', '2025-06-15 20:34:33'),
(33, 'Class', true, '2025-06-09 17:18:07', '2025-06-09 18:21:07'),
(18, 'Class', true, '2025-08-02 03:22:41', '2025-08-02 06:29:41'),
(9, 'Sleep', true, '2025-08-20 05:41:52', '2025-08-20 07:18:52'),
(21, 'Class', false, '2025-10-10 19:46:43', '2025-10-10 21:20:43'),
(26, 'Class', true, '2025-11-24 16:09:50', '2025-11-24 19:47:50'),
(4, 'Study', false, '2025-11-21 08:10:57', '2025-11-21 12:00:57'),
(9, 'Sleep', true, '2025-10-23 02:21:17', '2025-10-23 05:33:17'),
(15, 'Study', false, '2025-06-09 18:40:23', '2025-06-09 20:49:23'),
(2, 'Class', true, '2025-05-16 13:19:46', '2025-05-16 15:06:46'),
(28, 'Class', false, '2025-11-06 09:35:13', '2025-11-06 11:07:13');


INSERT INTO term (name, startDate, endDate) VALUES
('Spring 2025', '2025-04-22 01:52:19', '2025-08-22 01:52:19'),
('Spring 2024', '2026-05-29 16:27:47', '2026-08-29 16:27:47'),
('Fall 2025', '2025-12-20 07:00:16', '2026-04-20 07:00:16'),
('Spring 2024', '2025-06-02 13:08:06', '2025-09-02 13:08:06'),
('Fall 2024', '2025-12-22 09:28:54', '2026-04-22 09:28:54');


INSERT INTO CourseSelection (termID, courseCode, courseName, location, credits, instructor, department, Date, startTime, endTime) VALUES
(2, 1228, 'Statistics for Business', 'Washington Hall 902', 2, 'Leicester Budleigh', 'Business', '2026-05-11', '16:05:41', '18:02:41'),
(4, 1487, 'Environmental Science', 'Franklin Hall 601', 4, 'Naoma Reddle', 'Engineering', '2026-01-05', '12:10:58', '13:52:58'),
(4, 1407, 'Music Theory', 'Madison Hall 707', 3, 'Carie Mechem', 'Psychology', '2025-10-20', '13:10:50', '14:29:50'),
(1, 2115, 'Statistics for Business', 'Madison Hall 707', 3, 'Sebastiano Reburn', 'Business', '2026-03-02', '10:06:34', '11:37:34'),
(2, 2266, 'History of Art', 'Robinson Hall 205', 4, 'Joanie Noden', 'Psychology', '2026-04-10', '13:25:23', '14:34:23'),
(3, 2594, 'Public Speaking', 'Robinson Hall 205', 2, 'Durant Picopp', 'Psychology', '2025-03-31', '15:53:05', '16:53:05'),
(1, 2133, 'Music Theory', 'Adams Hall 503', 4, 'Wright Binne', 'Psychology', '2025-03-12', '10:18:28', '11:27:28'),
(2, 1619, 'Introduction to Psychology', 'Washington Hall 902', 4, 'Bondy Stear', 'Psychology', '2026-02-16', '8:27:16', '09:51:16'),
(3, 1678, 'Computer Science 101', 'Johnson Hall 402', 2, 'Riki Andryushin', 'Computer Science', '2026-06-29', '11:01:58', '12:03:58'),
(3, 1182, 'Statistics for Business', 'Johnson Hall 402', 4, 'Basia Leeman', 'Business', '2025-03-09', '15:18:59', '16:56:59'),
(5, 1823, 'Computer Science 101', 'Johnson Hall 402', 3, 'Micheil Ortsmann', 'Computer Science', '2026-11-30', '13:25:13', '14:58:13'),
(2, 1514, 'Introduction to Psychology', 'Franklin Hall 601', 4, 'Dylan Antoniottii', 'Psychology', '2026-10-29', '16:24:31', '17:47:31'),
(3, 2775, 'Introduction to Psychology', 'Smith Hall 101', 3, 'Bail Weiner', 'Psychology', '2025-06-18', '15:37:05', '16:48:05'),
(3, 2487, 'Chemistry Lab', 'Jefferson Hall 1001', 4, 'Wendie Poll', 'Engineering', '2026-11-27', '12:41:20', '14:39:20'),
(3, 1476, 'Music Theory', 'Kennedy Hall 310', 3, 'Druci Vallender', 'Psychology', '2025-04-26', '8:37:52', '09:45:52'),
(1, 1926, 'Public Speaking', 'Johnson Hall 402', 2, 'Nigel Brayne', 'Psychology', '2026-02-07', '10:58:06', '12:29:06'),
(3, 1376, 'Creative Writing Workshop', 'Robinson Hall 205', 4, 'Baily Hilling', 'Psychology', '2025-11-10', '14:13:52', '15:13:52'),
(4, 1097, 'Statistics for Business', 'Smith Hall 101', 2, 'Mina Tewes', 'Business', '2026-07-12', '12:56:35', '14:32:35'),
(3, 2882, 'Introduction to Psychology', 'Robinson Hall 205', 4, 'Margaretta Graal', 'Psychology', '2025-07-01', '14:54:49', '16:01:49'),
(3, 1449, 'Chemistry Lab', 'Lincoln Hall 810', 4, 'Abram Houseman', 'Engineering', '2025-10-18', '9:05:12', '11:01:12'),
(3, 2948, 'History of Art', 'Madison Hall 707', 4, 'Aurelia Dmytryk', 'Psychology', '2025-12-02', '14:00:20', '15:03:20'),
(2, 2300, 'Philosophy of Ethics', 'Washington Hall 902', 3, 'Bruce Drinnan', 'Psychology', '2025-02-15', '15:34:51', '17:21:51'),
(3, 2721, 'Computer Science 101', 'Adams Hall 503', 4, 'Annelise Flook', 'Computer Science', '2025-02-07', '13:30:30', '14:57:30'),
(2, 1056, 'Public Speaking', 'Franklin Hall 601', 3, 'Agosto Carthy', 'Business', '2025-04-01', '12:45:24', '14:31:24'),
(1, 1485, 'Introduction to Psychology', 'Franklin Hall 601', 2, 'Packston Boater', 'Psychology', '2026-07-31', '11:10:50', '12:41:50'),
(5, 1210, 'Music Theory', 'Franklin Hall 601', 4, 'Jessee Connue', 'Psychology', '2025-09-04', '9:14:33', '10:15:33'),
(1, 2083, 'History of Art', 'Franklin Hall 601', 3, 'Spike Carratt', 'Psychology', '2024-12-24', '15:24:06', '17:06:06'),
(2, 1703, 'Statistics for Business', 'Lincoln Hall 810', 2, 'Melitta Edwin', 'Business', '2026-12-03', '8:30:21', '09:38:21'),
(3, 1204, 'Music Theory', 'Smith Hall 101', 2, 'Remy Geaney', 'Psychology', '2025-04-09', '11:42:30', '13:41:30'),
(4, 1322, 'Public Speaking', 'Smith Hall 101', 2, 'Aile Wauchope', 'Psychology', '2026-03-22', '10:38:41', '11:44:41'),
(1, 2333, 'Chemistry Lab', 'Washington Hall 902', 2, 'Laureen Denisard', 'Engineering', '2024-12-16', '8:24:42', '09:38:42'),
(5, 2225, 'Creative Writing Workshop', 'Washington Hall 902', 2, 'Walden Wethers', 'Psychology', '2025-10-14', '13:58:10', '15:13:10'),
(2, 1836, 'Music Theory', 'Johnson Hall 402', 3, 'Teriann Maffini', 'Psychology', '2025-08-22', '15:25:19', '16:43:19'),
(5, 1438, 'Philosophy of Ethics', 'Robinson Hall 205', 2, 'Madelin Gillbe', 'Psychology', '2026-04-08', '16:06:06', '17:57:06'),
(4, 1077, 'Computer Science 101', 'Lincoln Hall 810', 4, 'Cordie Rehorek', 'Computer Science', '2026-07-20', '16:11:08', '17:24:08');


INSERT INTO assignment (courseID, title, scoreReceived, weight, status, assignmentDate, assignmentTime, maxScore)
VALUES
(11, 'Lab', 42, 2.90, 'reviewing', '2025-06-21', '15:21:24', 100),
(24, 'Quiz', 19, 1.30, 'submitted', '2025-11-27', '16:26:16', 100),
(9, 'Exam', 27, 2.20, 'submitted', '2025-04-21', '21:59:46', 100),
(1, 'Project', 46, 2.00, 'reviewing', '2025-08-20', '12:44:05', 100),
(22, 'Project', 79, 1.50, 'graded', '2025-03-09', '10:12:36', 100),
(4, 'Lab', 5, 2.90, 'graded', '2025-04-01', '0:49:58', 100),
(30, 'Homework', 62, 1.10, 'reviewing', '2025-03-07', '9:00:16', 100),
(32, 'Homework', 39, 2.30, 'reviewing', '2025-04-20', '11:35:15', 100),
(6, 'Exam', 6, 2.40, 'submitted', '2025-03-09', '11:53:08', 100),
(22, 'Homework', 93, 1.70, 'graded', '2025-07-21', '6:03:12', 100),
(1, 'Homework', 28, 2.00, 'reviewing', '2025-07-12', '14:06:05', 100),
(9, 'Exam', 22, 2.70, 'submitted', '2025-11-15', '19:52:51', 100),
(12, 'Quiz', 50, 2.30, 'submitted', '2025-03-16', '3:37:08', 100),
(11, 'Project', 11, 1.50, 'reviewing', '2025-10-19', '2:20:31', 100),
(2, 'Lab', 7, 1.90, 'submitted', '2025-05-02', '15:46:57', 100),
(19, 'Homework', 80, 2.60, 'graded', '2025-09-13', '9:32:21', 100),
(14, 'Lab', 99, 1.30, 'reviewing', '2024-12-21', '15:18:13', 100),
(18, 'Exam', 55, 1.40, 'graded', '2025-02-17', '11:18:39', 100),
(19, 'Quiz', 81, 2.90, 'reviewing', '2025-04-24', '18:49:14', 100),
(28, 'Quiz', 60, 2.20, 'reviewing', '2025-02-14', '13:52:33', 100),
(24, 'Exam', 20, 1.60, 'submitted', '2025-11-03', '4:46:57', 100),
(12, 'Homework', 18, 2.30, 'graded', '2025-11-17', '14:58:00', 100),
(33, 'Exam', 84, 1.10, 'reviewing', '2025-06-07', '18:25:54', 100),
(7, 'Exam', 92, 1.60, 'graded', '2025-05-21', '6:13:32', 100),
(25, 'Quiz', 68, 1.40, 'reviewing', '2025-06-10', '17:44:44', 100),
(3, 'Project', 75, 1.10, 'reviewing', '2025-11-03', '14:52:03', 100),
(26, 'Project', 79, 1.10, 'graded', '2025-08-23', '9:30:48', 100),
(9, 'Exam', 24, 2.00, 'reviewing', '2024-12-15', '0:41:23', 100),
(30, 'Project', 4, 1.20, 'reviewing', '2025-10-08', '10:23:07', 100),
(24, 'Homework', 44, 1.10, 'submitted', '2025-09-27', '19:31:02', 100),
(22, 'Lab', 8, 1.20, 'submitted', '2025-02-14', '16:31:05', 100),
(32, 'Lab', 33, 1.10, 'submitted', '2025-10-10', '15:39:01', 100),
(20, 'Exam', 83, 2.80, 'reviewing', '2025-06-16', '11:25:09', 100),
(8, 'Exam', 71, 2.50, 'submitted', '2025-11-15', '19:00:00', 100),
(11, 'Quiz', 25, 1.50, 'reviewing', '2024-12-09', '11:50:55', 100),
(13, 'Project', 78, 2.80, 'graded', '2025-04-06', '11:36:57', 100),
(34, 'Project', 31, 2.50, 'reviewing', '2025-08-24', '14:11:48', 100),
(2, 'Lab', 72, 1.70, 'reviewing', '2025-02-24', '3:59:05', 100),
(14, 'Homework', 51, 2.40, 'submitted', '2025-02-15', '12:58:17', 100),
(16, 'Quiz', 94, 1.40, 'submitted', '2025-05-19', '15:39:35', 100),
(14, 'Homework', 26, 2.00, 'graded', '2025-06-24', '13:08:08', 100),
(11, 'Exam', 80, 2.90, 'reviewing', '2025-05-22', '2:33:32', 100),
(34, 'Project', 34, 2.80, 'reviewing', '2025-07-08', '11:28:42', 100),
(31, 'Lab', 5, 1.90, 'graded', '2025-08-03', '13:58:59', 100),
(6, 'Exam', 1, 2.80, 'submitted', '2025-05-30', '11:53:08', 100),
(17, 'Exam', 61, 2.20, 'graded', '2025-09-05', '0:17:48', 100),
(14, 'Quiz', 94, 1.90, 'graded', '2025-10-02', '5:41:03', 100),
(27, 'Homework', 50, 1.50, 'reviewing', '2025-06-19', '13:45:03', 100),
(18, 'Lab', 97, 2.80, 'submitted', '2025-10-17', '17:17:07', 100),
(27, 'Quiz', 35, 2.50, 'graded', '2025-06-06', '14:13:52', 100),
(35, 'Lab', 65, 2.30, 'submitted', '2025-08-17', '6:42:52', 100),
(15, 'Exam', 27, 2.20, 'graded', '2025-05-08', '10:42:18', 100),
(18, 'Exam', 68, 2.70, 'graded', '2025-04-17', '7:01:47', 100),
(20, 'Lab', 53, 2.80, 'submitted', '2025-03-16', '9:14:02', 100),
(13, 'Exam', 82, 1.80, 'graded', '2025-01-09', '16:11:10', 100),
(2, 'Exam', 0, 2.00, 'reviewing', '2025-02-07', '18:33:08', 100),
(22, 'Quiz', 92, 2.20, 'graded', '2025-11-29', '2:03:23', 100),
(13, 'Quiz', 1, 1.50, 'reviewing', '2025-03-23', '7:02:07', 100),
(30, 'Exam', 77, 2.00, 'graded', '2025-11-09', '12:06:12', 100),
(11, 'Project', 87, 1.90, 'reviewing', '2025-03-06', '13:35:37', 100),
(7, 'Project', 55, 2.80, 'graded', '2025-02-03', '16:57:40', 100),
(23, 'Quiz', 87, 1.70, 'graded', '2025-08-08', '20:38:23', 100),
(31, 'Homework', 88, 2.30, 'reviewing', '2025-05-14', '15:45:41', 100),
(32, 'Project', 93, 1.30, 'graded', '2025-02-27', '9:20:13', 100),
(18, 'Project', 99, 1.80, 'reviewing', '2025-05-06', '21:16:42', 100),
(14, 'Quiz', 56, 1.30, 'graded', '2025-05-02', '9:13:35', 100),
(35, 'Lab', 18, 1.20, 'reviewing', '2024-12-23', '0:08:46', 100),
(35, 'Project', 62, 1.60, 'submitted', '2024-12-29', '6:23:18', 100),
(26, 'Project', 60, 2.30, 'reviewing', '2025-04-28', '10:46:33', 100),
(33, 'Exam', 99, 2.10, 'graded', '2025-08-09', '3:45:01', 100);



INSERT INTO event (name, type, location, date, startTime, endTime) VALUES
('Workshop: Time Management', 'workshop', 'Quiet Room 7', '2025-01-10', '7:06:47', '08:38:47'),
('Workshop: Time Management', 'workshop', 'Training Room 4', '2025-03-25', '8:42:13', '09:51:13'),
('Midterm Review', 'study', 'Collaboration Room 5', '2025-10-12', '1:30:13', '02:44:13'),
('Office Hours', 'meeting', 'Training Room 4', '2026-01-08', '8:35:17', '09:51:17'),
('Workshop: Time Management', 'workshop', 'Study Room 3', '2025-09-09', '0:34:07', '01:35:07'),
('Office Hours', 'meeting', 'Meeting Room 2', '2024-12-12', '7:31:39', '08:44:39'),
('Office Hours', 'meeting', 'Presentation Room 6', '2025-06-29', '3:58:37', '05:45:37'),
('Office Hours', 'meeting', 'Workshop Room 9', '2025-07-12', '5:04:17', '06:30:17'),
('Workshop: Time Management', 'workshop', 'Study Room 3', '2025-06-11', '5:10:57', '06:51:57'),
('Midterm Review', 'study', 'Training Room 4', '2025-11-12', '6:44:06', '08:18:06'),
('Workshop: Time Management', 'workshop', 'Workshop Room 9', '2025-02-25', '0:57:24', '02:45:24'),
('Office Hours', 'meeting', 'Breakout Room 1', '2026-10-31', '3:15:42', '04:24:42'),
('Workshop: Time Management', 'workshop', 'Training Room 4', '2025-08-29', '5:59:04', '07:47:04'),
('Workshop: Time Management', 'workshop', 'Quiet Room 7', '2024-12-10', '0:10:34', '01:51:34'),
('Midterm Review', 'study', 'Conference Room A', '2026-12-03', '5:18:29', '06:48:29'),
('Workshop: Time Management', 'workshop', 'Study Room 3', '2026-01-28', '0:31:53', '02:11:53'),
('Office Hours', 'meeting', 'Brainstorming Room 8', '2026-04-24', '2:56:19', '04:02:19'),
('Study Session', 'study', 'Collaboration Room 5', '2026-08-12', '4:26:05', '05:30:05'),
('Midterm Review', 'study', 'Quiet Room 7', '2026-05-30', '7:13:02', '08:36:02'),
('Office Hours', 'meeting', 'Presentation Room 6', '2025-12-25', '4:40:35', '06:05:35'),
('Office Hours', 'meeting', 'Training Room 4', '2026-09-10', '0:15:05', '01:23:05'),
('Midterm Review', 'study', 'Brainstorming Room 8', '2024-12-26', '8:26:58', '10:26:58'),
('Workshop: Time Management', 'workshop', 'Breakout Room 1', '2026-12-04', '2:44:34', '04:18:34'),
('Office Hours', 'meeting', 'Meeting Room 2', '2025-05-17', '5:37:44', '06:48:44'),
('Study Session', 'study', 'Quiet Room 7', '2026-03-30', '6:06:58', '07:44:58'),
('Study Session', 'study', 'Training Room 4', '2026-07-31', '0:21:15', '02:09:15'),
('Midterm Review', 'study', 'Quiet Room 7', '2025-05-26', '1:47:45', '02:54:45'),
('Midterm Review', 'study', 'Quiet Room 7', '2026-08-07', '2:03:27', '03:16:27'),
('Workshop: Time Management', 'workshop', 'Collaboration Room 5', '2026-10-30', '6:47:04', '08:04:04'),
('Office Hours', 'meeting', 'Presentation Room 6', '2026-02-27', '7:44:58', '08:54:58'),
('Study Session', 'study', 'Training Room 4', '2025-06-09', '7:42:19', '09:39:19'),
('Midterm Review', 'study', 'Meeting Room 2', '2025-07-17', '2:39:00', '04:39:00'),
('Study Session', 'study', 'Collaboration Room 5', '2025-12-31', '5:29:29', '06:32:29'),
('Midterm Review', 'study', 'Workshop Room 9', '2026-07-28', '6:46:58', '08:35:58'),
('Office Hours', 'meeting', 'Meeting Room 2', '2025-06-26', '8:09:33', '09:31:33');


INSERT INTO reminder (eventID, assignmentID, message, isActive, date, time)
VALUES
(20, 1, 'due soon', 0, '2025-11-27', '9:01:39'),
(1, 22, 'due soon', 0, '2026-01-21', '13:30:19'),
(4, 35, 'need help', 1, '2024-12-06', '21:31:33'),
(13, 37, 'Exam tomorrow', 1, '2026-04-10', '19:19:39'),
(33, 61, 'due soon', 1, '2026-11-22', '13:32:31'),
(15, 16, 'Exam tomorrow', 1, '2025-12-21', '12:35:40'),
(21, 11, 'due soon', 0, '2026-06-01', '12:34:31'),
(6, 35, 'need help', 1, '2025-10-31', '10:08:30'),
(35, 58, 'due soon', 1, '2025-08-24', '11:46:20'),
(28, 56, 'Exam tomorrow', 1, '2024-12-24', '20:08:52'),
(11, 15, 'due soon', 0, '2026-02-18', '8:16:00'),
(25, 14, 'Exam tomorrow', 1, '2025-12-03', '18:20:18'),
(17, 48, 'Exam tomorrow', 0, '2025-02-02', '11:11:39'),
(7, 64, 'Exam tomorrow', 1, '2025-12-24', '10:01:49'),
(16, 50, 'Exam tomorrow', 1, '2025-08-09', '9:08:39'),
(18, 25, 'Exam tomorrow', 1, '2025-12-03', '21:34:02'),
(5, 43, 'need help', 1, '2025-04-24', '9:47:18'),
(24, 10, 'need help', 0, '2025-10-01', '18:40:03'),
(12, 5, 'Exam tomorrow', 0, '2025-07-26', '12:03:13'),
(8, 66, 'due soon', 1, '2025-08-10', '19:06:32'),
(6, 11, 'need help', 1, '2026-05-07', '10:55:24'),
(11, 64, 'Exam tomorrow', 1, '2025-01-15', '18:00:27'),
(32, 2, 'Exam tomorrow', 1, '2025-03-11', '16:43:46'),
(9, 18, 'Exam tomorrow', 0, '2026-07-18', '10:26:45'),
(2, 34, 'need help', 0, '2024-12-10', '10:40:49'),
(17, 44, 'Exam tomorrow', 0, '2025-01-25', '17:03:49'),
(25, 69, 'need help', 1, '2025-11-23', '16:33:20'),
(19, 64, 'Exam tomorrow', 0, '2025-03-27', '20:07:38'),
(1, 36, 'Exam tomorrow', 1, '2025-04-30', '21:08:49'),
(10, 32, 'Exam tomorrow', 1, '2025-08-06', '20:25:16'),
(29, 41, 'Exam tomorrow', 0, '2025-08-19', '18:07:48'),
(4, 3, 'need help', 0, '2025-01-21', '15:34:51'),
(3, 6, 'need help', 0, '2025-02-01', '15:27:58'),
(26, 33, 'need help', 0, '2025-05-16', '10:42:53'),
(7, 53, 'Exam tomorrow', 1, '2025-01-04', '16:13:39'),
(3, 36, 'Exam tomorrow', 1, '2025-05-01', '16:54:49'),
(9, 63, 'need help', 0, '2025-05-10', '9:12:47'),
(30, 49, 'need help', 0, '2025-01-21', '16:18:21'),
(27, 9, 'Exam tomorrow', 1, '2025-09-26', '17:39:45'),
(17, 62, 'Exam tomorrow', 1, '2025-11-18', '13:38:59'),
(14, 33, 'need help', 1, '2025-05-01', '21:09:37'),
(8, 6, 'need help', 1, '2025-07-07', '19:15:35'),
(28, 50, 'Exam tomorrow', 1, '2026-10-19', '15:00:53'),
(24, 54, 'Exam tomorrow', 0, '2025-03-15', '18:19:11'),
(5, 41, 'Exam tomorrow', 0, '2025-08-27', '13:40:23'),
(23, 57, 'need help', 0, '2025-11-19', '21:00:34'),
(22, 38, 'Exam tomorrow', 1, '2025-07-06', '12:34:21'),
(13, 31, 'Exam tomorrow', 1, '2025-11-14', '17:24:08'),
(18, 26, 'Exam tomorrow', 1, '2025-11-24', '19:44:11'),
(26, 65, 'Exam tomorrow', 0, '2025-06-09', '13:35:23'),
(31, 47, 'due soon', 0, '2025-03-20', '11:28:05'),
(10, 21, 'Exam tomorrow', 0, '2025-09-22', '10:50:09'),
(16, 52, 'Exam tomorrow', 1, '2025-01-08', '12:08:25'),
(21, 12, 'Exam tomorrow', 0, '2025-10-26', '11:13:52'),
(12, 46, 'Exam tomorrow', 1, '2025-11-22', '13:33:07'),
(19, 24, 'Exam tomorrow', 0, '2025-09-11', '17:32:29'),
(32, 7, 'Exam tomorrow', 0, '2025-01-26', '9:43:17'),
(30, 68, 'need help', 0, '2025-11-06', '14:46:37'),
(29, 17, 'need help', 1, '2025-11-27', '21:00:49'),
(15, 59, 'Exam tomorrow', 1, '2025-02-15', '9:37:22'),
(23, 29, 'Exam tomorrow', 1, '2025-11-06', '11:07:02'),
(20, 39, 'Exam tomorrow', 1, '2025-09-02', '12:40:09'),
(14, 18, 'Exam tomorrow', 1, '2026-03-20', '12:51:38'),
(31, 55, 'need help', 1, '2026-02-22', '20:45:03'),
(27, 23, 'Exam tomorrow', 1, '2025-02-01', '15:05:13'),
(33, 19, 'Exam tomorrow', 1, '2025-11-17', '18:10:03'),
(2, 30, 'Exam tomorrow', 0, '2025-10-15', '11:09:20'),
(34, 4, 'Exam tomorrow', 0, '2025-11-11', '14:38:50'),
(22, 28, 'Exam tomorrow', 0, '2025-11-20', '15:33:25'),
(4, 45, 'Exam tomorrow', 1, '2025-02-04', '10:34:10');



INSERT INTO attEvent (studentID, eventID) VALUES
(1, 16),
(16, 33),
(9, 17),
(29, 31),
(4, 30),
(28, 13),
(6, 22),
(11, 4),
(29, 5),
(29, 14),
(2, 14),
(25, 25),
(13, 16),
(5, 14),
(11, 18),
(16, 27),
(1, 3),
(21, 24),
(32, 21),
(20, 11),
(20, 14),
(22, 27),
(4, 10),
(24, 10),
(20, 6),
(13, 7),
(16, 16),
(7, 11),
(33, 23),
(21, 5),
(1, 25),
(29, 7),
(31, 12),
(34, 22),
(21, 13),
(10, 2),
(30, 20),
(14, 27),
(34, 33),
(27, 31),
(10, 6),
(1, 5),
(32, 18),
(17, 16),
(15, 8),
(2, 26),
(18, 32),
(7, 7),
(34, 11),
(18, 12),
(32, 29),
(4, 27),
(28, 4),
(32, 35),
(23, 30),
(28, 11),
(16, 19),
(29, 4),
(10, 26),
(33, 21),
(34, 29),
(19, 14),
(18, 24),
(21, 12),
(8, 29),
(16, 5),
(29, 25),
(23, 13),
(20, 2),
(30, 15),
(17, 11),
(6, 19),
(4, 31),
(33, 10),
(11, 33),
(32, 25),
(29, 10),
(20, 1),
(7, 2),
(8, 17),
(11, 10),
(31, 11),
(7, 33),
(20, 13),
(4, 14),
(20, 3),
(28, 27),
(2, 12),
(17, 25),
(18, 28),
(17, 26),
(25, 29),
(6, 28),
(1, 11),
(16, 31),
(20, 17),
(25, 10),
(33, 24),
(18, 34),
(26, 5),
(13, 26),
(30, 21),
(28, 9),
(26, 22),
(13, 13),
(4, 22),
(12, 3),
(33, 11),
(5, 13),
(7, 14),
(6, 24),
(35, 2),
(27, 16),
(16, 34),
(17, 31),
(10, 23),
(3, 12),
(24, 20),
(27, 10),
(27, 26),
(15, 9),
(13, 20),
(23, 14),
(28, 25),
(8, 2),
(26, 7),
(33, 35),
(33, 22),
(22, 8),
(8, 32),
(14, 32),
(27, 21),
(12, 32),
(15, 22),
(25, 27),
(2, 15),
(19, 35),
(11, 23),
(22, 21),
(35, 5),
(2, 4),
(21, 21),
(4, 15),
(3, 6),
(12, 22),
(11, 17),
(26, 24),
(12, 17),
(5, 20),
(31, 32),
(24, 8),
(7, 1),
(15, 6),
(18, 17),
(29, 27),
(7, 23),
(9, 23),
(23, 3),
(17, 33),
(11, 6),
(30, 24),
(11, 1),
(18, 30),
(14, 22),
(1, 26),
(21, 25),
(21, 34),
(14, 6),
(25, 32),
(35, 33),
(21, 20),
(9, 7),
(33, 7),
(10, 22),
(22, 28),
(8, 20),
(10, 17),
(8, 3),
(9, 6),
(27, 5),
(8, 6),
(4, 17),
(14, 19),
(6, 15),
(26, 18),
(7, 17),
(35, 7),
(22, 17),
(22, 23),
(15, 4),
(17, 20),
(1, 21),
(7, 4),
(12, 14),
(1, 6),
(30, 5),
(7, 28),
(1, 13),
(15, 3),
(19, 3),
(14, 18),
(20, 27),
(5, 30),
(16, 12),
(16, 24),
(4, 24),
(1, 29);

INSERT INTO CourseSelectionStudent (studentID, courseID) VALUES
(31, 21),
(26, 10),
(33, 29),
(1, 10),
(14, 21),
(32, 21),
(1, 28),
(19, 31),
(24, 22),
(1, 1),
(12, 17),
(3, 33),
(34, 14),
(18, 19),
(23, 32),
(22, 17),
(6, 3),
(15, 10),
(27, 19),
(12, 27),
(25, 20),
(26, 34),
(21, 29),
(12, 14),
(33, 11),
(28, 34),
(31, 11),
(21, 4),
(8, 12),
(25, 35),
(34, 32),
(27, 8),
(10, 19),
(24, 15),
(2, 15),
(9, 33),
(13, 17),
(22, 22),
(3, 16),
(18, 28),
(20, 12),
(18, 18),
(28, 2),
(13, 3),
(28, 10),
(22, 13),
(4, 34),
(24, 25),
(27, 14),
(9, 24),
(20, 14),
(32, 32),
(16, 18),
(20, 16),
(1, 9),
(27, 21),
(29, 28),
(11, 25),
(5, 13),
(5, 25),
(15, 13),
(10, 29),
(21, 27),
(23, 22),
(19, 2),
(7, 35),
(23, 35),
(13, 35),
(28, 15),
(14, 27),
(34, 9),
(26, 3),
(10, 22),
(6, 35),
(18, 24),
(16, 33),
(35, 2),
(27, 11),
(35, 6),
(15, 8),
(5, 30),
(33, 19),
(26, 31),
(1, 26),
(30, 15),
(8, 26),
(11, 8),
(13, 4),
(7, 8),
(25, 13),
(29, 17),
(28, 18),
(16, 7),
(25, 8),
(30, 8),
(24, 27),
(8, 30),
(1, 5),
(5, 12),
(7, 18),
(15, 1),
(25, 31),
(20, 20),
(17, 1),
(3, 20),
(4, 30),
(27, 29),
(10, 14),
(15, 19),
(1, 17),
(21, 2),
(17, 9),
(9, 7),
(30, 2),
(32, 24),
(29, 12),
(27, 24),
(31, 14),
(29, 6),
(4, 17),
(20, 8),
(26, 5),
(9, 11),
(3, 19),
(4, 1),
(29, 9),
(12, 22),
(17, 16),
(18, 22),
(14, 35),
(12, 3),
(19, 23),
(6, 6),
(25, 23),
(24, 18),
(15, 21),
(3, 26),
(6, 5),
(5, 11),
(16, 24),
(9, 5),
(13, 10),
(11, 16),
(34, 20),
(20, 11),
(10, 12),
(14, 23),
(15, 20),
(11, 34),
(13, 1),
(27, 12),
(16, 10),
(10, 23),
(30, 13),
(22, 8),
(19, 18),
(34, 21),
(2, 12),
(18, 16),
(22, 27),
(6, 18),
(4, 10),
(33, 22),
(26, 4),
(25, 30),
(34, 12),
(26, 35),
(12, 4),
(12, 10),
(21, 18),
(2, 16),
(7, 10),
(4, 7),
(5, 8),
(14, 28),
(32, 17),
(31, 4),
(34, 34),
(12, 12),
(18, 20),
(19, 3),
(27, 35),
(4, 11),
(26, 16),
(9, 15),
(31, 22),
(9, 19),
(17, 21),
(26, 7),
(10, 16),
(8, 1),
(21, 8),
(10, 30),
(10, 18),
(6, 13),
(23, 10),
(27, 10),
(33, 18),
(35, 33),
(32, 14),
(27, 18),
(25, 16),
(24, 14),
(9, 28),
(24, 23),
(5, 23),
(10, 2),
(1, 33),
(35, 5),
(33, 32),
(28, 21),
(33, 6),
(2, 29),
(16, 13),
(19, 14),
(4, 6),
(12, 7),
(33, 1),
(22, 1),
(7, 26),
(5, 35),
(18, 9),
(34, 7),
(9, 14),
(30, 35),
(4, 22),
(34, 25),
(4, 20);