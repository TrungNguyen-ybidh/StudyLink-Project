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


insert into dataset (dataID, name, category, source) values (1, 'Grades Import', 'academic', 'csv');
insert into dataset (dataID, name, category, source) values (2, 'Wellness Survey', 'wellness', 'manual');
insert into dataset (dataID, name, category, source) values (3, 'Sleep Tracker', 'wellness', 'csv');
insert into dataset (dataID, name, category, source) values (4, 'Sleep Tracker', 'wellness', 'csv');
insert into dataset (dataID, name, category, source) values (5, 'Advisor Help', 'engagement', 'manual');
insert into dataset (dataID, name, category, source) values (6, 'Sleep Tracker', 'wellness', 'api');
insert into dataset (dataID, name, category, source) values (7, 'Wellness Survey', 'wellness', 'manual');
insert into dataset (dataID, name, category, source) values (8, 'Advisor Help', 'engagement', 'csv');
insert into dataset (dataID, name, category, source) values (9, 'Student Logs', 'metrics', 'api');
insert into dataset (dataID, name, category, source) values (10, 'Sleep Tracker', 'wellness', 'manual');

insert into SystemAdmin (adminID, name, DOB) values (1, 'Stavro Kubat', '1992-09-02');
insert into SystemAdmin (adminID, name, DOB) values (2, 'Sherrie Keast', '1974-01-20');
insert into SystemAdmin (adminID, name, DOB) values (3, 'Conant Fluit', '1997-08-21');
insert into SystemAdmin (adminID, name, DOB) values (4, 'Gwenneth Lally', '1979-04-16');
insert into SystemAdmin (adminID, name, DOB) values (5, 'Audie Gleave', '1994-06-17');
insert into SystemAdmin (adminID, name, DOB) values (6, 'Brandea Wallsam', '2000-01-01');
insert into SystemAdmin (adminID, name, DOB) values (7, 'Avrit Crippes', '1971-03-06');
insert into SystemAdmin (adminID, name, DOB) values (8, 'Elvira Guiduzzi', '1992-04-26');
insert into SystemAdmin (adminID, name, DOB) values (9, 'Talyah Lincoln', '1971-10-07');
insert into SystemAdmin (adminID, name, DOB) values (10, 'Rhianna Goodhand', '1970-05-23');


INSERT INTO importJob (errorCount, jobType, StartTime, endTime, Status, adminID)
VALUES
(2, 'Metric Import', NOW(), NOW(), 'Completed', 1),
(1, 'Calendar Sync', NOW(), NOW(), 'Failed', 2),
(0, 'Student Update', NOW(), NOW(), 'Completed', 3);
insert into importJob (jobID, errorCount, jobType, startTime, endTime, adminID) values (1, 2, 'Calendar Sync', '2025-11-08 19:06:35', '2025-11-08 21:58:35', 1);
insert into importJob (jobID, errorCount, jobType, startTime, endTime, adminID) values (2, 18, 'Course Import', '2025-11-22 11:41:28', '2025-11-22 13:00:28', 10);
insert into importJob (jobID, errorCount, jobType, startTime, endTime, adminID) values (3, 8, 'Student Update', '2025-05-08 02:19:11', '2025-05-08 04:35:11', 1);
insert into importJob (jobID, errorCount, jobType, startTime, endTime, adminID) values (4, 5, 'Course Import', '2025-11-13 15:40:36', '2025-11-13 17:18:36', 3);
insert into importJob (jobID, errorCount, jobType, startTime, endTime, adminID) values (5, 16, 'Metric Import', '2025-01-18 13:17:59', '2025-01-18 15:10:59', 5);
insert into importJob (jobID, errorCount, jobType, startTime, endTime, adminID) values (6, 15, 'Calendar Sync', '2025-08-21 09:45:55', '2025-08-21 10:27:55', 10);
insert into importJob (jobID, errorCount, jobType, startTime, endTime, adminID) values (7, 17, 'Student Update', '2025-01-17 06:47:13', '2025-01-17 08:53:13', 6);
insert into importJob (jobID, errorCount, jobType, startTime, endTime, adminID) values (8, 10, 'Student Update', '2025-08-13 17:25:00', '2025-08-13 18:28:00', 9);
insert into importJob (jobID, errorCount, jobType, startTime, endTime, adminID) values (9, 17, 'Course Import', '2025-11-19 22:25:43', '2025-11-20 00:39:43', 5);
insert into importJob (jobID, errorCount, jobType, startTime, endTime, adminID) values (10, 14, 'Course Import', '2025-11-05 14:19:06', '2025-11-05 16:17:06', 11);
insert into importJob (jobID, errorCount, jobType, startTime, endTime, adminID) values (11, 10, 'Student Update', '2025-11-03 23:32:17', '2025-11-04 01:05:17', 11);
insert into importJob (jobID, errorCount, jobType, startTime, endTime, adminID) values (12, 20, 'Student Update', '2025-12-05 10:33:29', '2025-12-05 12:33:29', 7);
insert into importJob (jobID, errorCount, jobType, startTime, endTime, adminID) values (13, 19, 'Course Import', '2025-11-09 06:52:08', '2025-11-09 07:51:08', 3);
insert into importJob (jobID, errorCount, jobType, startTime, endTime, adminID) values (14, 0, 'Student Update', '2025-05-04 10:53:10', '2025-05-04 12:21:10', 5);
insert into importJob (jobID, errorCount, jobType, startTime, endTime, adminID) values (15, 13, 'Student Update', '2025-06-13 02:44:26', '2025-06-13 05:07:26', 6);
insert into importJob (jobID, errorCount, jobType, startTime, endTime, adminID) values (16, 16, 'Calendar Sync', '2025-04-14 04:23:49', '2025-04-14 05:19:49', 9);
insert into importJob (jobID, errorCount, jobType, startTime, endTime, adminID) values (17, 16, 'Metric Import', '2025-09-27 21:02:02', '2025-09-27 23:57:02', 11);
insert into importJob (jobID, errorCount, jobType, startTime, endTime, adminID) values (18, 19, 'Student Update', '2024-12-10 19:15:48', '2024-12-10 19:52:48', 10);
insert into importJob (jobID, errorCount, jobType, startTime, endTime, adminID) values (19, 9, 'Calendar Sync', '2025-02-16 10:02:32', '2025-02-16 12:13:32', 9);
insert into importJob (jobID, errorCount, jobType, startTime, endTime, adminID) values (20, 1, 'Metric Import', '2025-09-27 03:39:06', '2025-09-27 05:01:06', 3);
insert into importJob (jobID, errorCount, jobType, startTime, endTime, adminID) values (21, 20, 'Course Import', '2025-07-25 13:18:14', '2025-07-25 15:31:14', 6);
insert into importJob (jobID, errorCount, jobType, startTime, endTime, adminID) values (22, 20, 'Calendar Sync', '2025-05-31 08:19:16', '2025-05-31 09:35:16', 10);
insert into importJob (jobID, errorCount, jobType, startTime, endTime, adminID) values (23, 5, 'Metric Import', '2025-08-15 04:03:16', '2025-08-15 05:34:16', 2);
insert into importJob (jobID, errorCount, jobType, startTime, endTime, adminID) values (24, 10, 'Student Update', '2025-07-19 04:49:14', '2025-07-19 06:49:14', 4);
insert into importJob (jobID, errorCount, jobType, startTime, endTime, adminID) values (25, 3, 'Course Import', '2025-10-06 21:19:12', '2025-10-06 22:17:12', 3);
insert into importJob (jobID, errorCount, jobType, startTime, endTime, adminID) values (26, 6, 'Course Import', '2025-05-18 20:02:23', '2025-05-18 21:24:23', 4);
insert into importJob (jobID, errorCount, jobType, startTime, endTime, adminID) values (27, 19, 'Course Import', '2024-12-26 02:08:18', '2024-12-26 02:44:18', 3);
insert into importJob (jobID, errorCount, jobType, startTime, endTime, adminID) values (28, 13, 'Course Import', '2025-07-13 15:51:34', '2025-07-13 16:27:34', 8);
insert into importJob (jobID, errorCount, jobType, startTime, endTime, adminID) values (29, 6, 'Student Update', '2025-02-28 23:37:26', '2025-03-01 01:43:26', 9);
insert into importJob (jobID, errorCount, jobType, startTime, endTime, adminID) values (30, 15, 'Course Import', '2025-06-01 04:50:00', '2025-06-01 06:40:00', 10);
insert into importJob (jobID, errorCount, jobType, startTime, endTime, adminID) values (31, 17, 'Student Update', '2025-03-07 03:56:53', '2025-03-07 04:31:53', 4);
insert into importJob (jobID, errorCount, jobType, startTime, endTime, adminID) values (32, 2, 'Student Update', '2025-09-06 22:46:43', '2025-09-07 00:26:43', 3);
insert into importJob (jobID, errorCount, jobType, startTime, endTime, adminID) values (33, 8, 'Course Import', '2025-11-28 11:00:49', '2025-11-28 13:00:49', 4);
insert into importJob (jobID, errorCount, jobType, startTime, endTime, adminID) values (34, 6, 'Student Update', '2025-03-23 14:14:01', '2025-03-23 15:32:01', 10);
insert into importJob (jobID, errorCount, jobType, startTime, endTime, adminID) values (35, 11, 'Student Update', '2025-08-10 18:35:18', '2025-08-10 21:14:18', 5);
# Rows

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


insert into advisor (fname, lName, email, department) values ('Salvatore', 'Swapp', 'salvatore.swappnortheastern.edu', 'Business');
insert into advisor (fname, lName, email, department) values ('Isidora', 'Murfin', 'isidora.murfinnortheastern.edu', 'Psychology');
insert into advisor (fname, lName, email, department) values ('Lindon', 'Ellul', 'lindon.ellulnortheastern.edu', 'Mathematics');
insert into advisor (fname, lName, email, department) values ('Tally', 'Cockran', 'tally.cockrannortheastern.edu', 'Mathematics');
insert into advisor (fname, lName, email, department) values ('Westley', 'Mattityahou', 'westley.mattityahounortheastern.edu', 'Computer Science');
insert into advisor (fname, lName, email, department) values ('Hetti', 'Masdin', 'hetti.masdinnortheastern.edu', 'Business');
insert into advisor (fname, lName, email, department) values ('Tracey', 'Howland', 'tracey.howlandnortheastern.edu', 'Computer Science');
insert into advisor (fname, lName, email, department) values ('Roberto', 'Dansken', 'roberto.danskennortheastern.edu', 'Psychology');
insert into advisor (fname, lName, email, department) values ('Ange', 'Shervil', 'ange.shervilnortheastern.edu', 'Psychology');
insert into advisor (fname, lName, email, department) values ('Tori', 'Narducci', 'tori.narduccinortheastern.edu', 'Mathematics');
insert into advisor (fname, lName, email, department) values ('Elly', 'Vango', 'elly.vangonortheastern.edu', 'Engineering');
insert into advisor (fname, lName, email, department) values ('Angele', 'Worts', 'angele.wortsnortheastern.edu', 'Engineering');
insert into advisor (fname, lName, email, department) values ('Adrea', 'Bassil', 'adrea.bassilnortheastern.edu', 'Psychology');
insert into advisor (fname, lName, email, department) values ('Krishnah', 'Bargh', 'krishnah.barghnortheastern.edu', 'Mathematics');
insert into advisor (fname, lName, email, department) values ('Vince', 'Mound', 'vince.moundnortheastern.edu', 'Engineering');
insert into advisor (fname, lName, email, department) values ('Burnard', 'Jeannequin', 'burnard.jeannequinnortheastern.edu', 'Psychology');
insert into advisor (fname, lName, email, department) values ('Alix', 'Portchmouth', 'alix.portchmouthnortheastern.edu', 'Engineering');
insert into advisor (fname, lName, email, department) values ('Mose', 'Chisnall', 'mose.chisnallnortheastern.edu', 'Engineering');
insert into advisor (fname, lName, email, department) values ('Amerigo', 'Elleray', 'amerigo.elleraynortheastern.edu', 'Psychology');
insert into advisor (fname, lName, email, department) values ('Tait', 'Witul', 'tait.witulnortheastern.edu', 'Computer Science');
insert into advisor (fname, lName, email, department) values ('Didi', 'Lewry', 'didi.lewrynortheastern.edu', 'Business');
insert into advisor (fname, lName, email, department) values ('Rodrique', 'Alcock', 'rodrique.alcocknortheastern.edu', 'Computer Science');
insert into advisor (fname, lName, email, department) values ('Caritta', 'Kitching', 'caritta.kitchingnortheastern.edu', 'Computer Science');
insert into advisor (fname, lName, email, department) values ('Tabina', 'Petrichat', 'tabina.petrichatnortheastern.edu', 'Computer Science');
insert into advisor (fname, lName, email, department) values ('Letty', 'Callacher', 'letty.callachernortheastern.edu', 'Computer Science');
insert into advisor (fname, lName, email, department) values ('Jard', 'Coughlan', 'jard.coughlannortheastern.edu', 'Psychology');
insert into advisor (fname, lName, email, department) values ('Kalindi', 'Chillingsworth', 'kalindi.chillingsworthnortheastern.edu', 'Mathematics');
insert into advisor (fname, lName, email, department) values ('Libbie', 'Trainer', 'libbie.trainernortheastern.edu', 'Engineering');
insert into advisor (fname, lName, email, department) values ('Bjorn', 'Cawtheray', 'bjorn.cawtheraynortheastern.edu', 'Engineering');
insert into advisor (fname, lName, email, department) values ('Elfrida', 'Priddle', 'elfrida.priddlenortheastern.edu', 'Mathematics');
insert into advisor (fname, lName, email, department) values ('Jannel', 'Ferrieroi', 'jannel.ferrieroinortheastern.edu', 'Psychology');
insert into advisor (fname, lName, email, department) values ('Chrissy', 'Depke', 'chrissy.depkenortheastern.edu', 'Computer Science');
insert into advisor (fname, lName, email, department) values ('Lonna', 'Human', 'lonna.humannortheastern.edu', 'Psychology');
insert into advisor (fname, lName, email, department) values ('Rita', 'Ruslinge', 'rita.ruslingenortheastern.edu', 'Psychology');
insert into advisor (fname, lName, email, department) values ('Averil', 'Monteaux', 'averil.monteauxnortheastern.edu', 'Engineering');


insert into student (fName, lName, email, enrollmentYear, major, minor, GPA, riskFlag, totalCredits, advisorID) values ('Belva', 'Mabbett', 'belva.mabbettnortheastern.edu', 2021, 'Data Science', 'Business', 2.34, true, 123.44, 27);
insert into student (fName, lName, email, enrollmentYear, major, minor, GPA, riskFlag, totalCredits, advisorID) values ('Archibaldo', 'Harmes', 'archibaldo.harmesnortheastern.edu', 2022, 'Engineering', 'Software Engineering', 2.35, true, 109.55, 35);
insert into student (fName, lName, email, enrollmentYear, major, minor, GPA, riskFlag, totalCredits, advisorID) values ('Itch', 'Durkin', 'itch.durkinnortheastern.edu', 2021, 'Computer Science', 'Computer Science', 2.05, true, 69.56, 28);
insert into student (fName, lName, email, enrollmentYear, major, minor, GPA, riskFlag, totalCredits, advisorID) values ('Art', 'Cartmael', 'art.cartmaelnortheastern.edu', 2023, 'Psychology', 'Economics', 2.37, true, 113.45, 30);
insert into student (fName, lName, email, enrollmentYear, major, minor, GPA, riskFlag, totalCredits, advisorID) values ('Felice', 'Venton', 'felice.ventonnortheastern.edu', 2022, 'Business', 'Economics', 3.3, false, 16.25, 26);
insert into student (fName, lName, email, enrollmentYear, major, minor, GPA, riskFlag, totalCredits, advisorID) values ('Hadlee', 'Annets', 'hadlee.annetsnortheastern.edu', 2023, 'Engineering', 'Computer Science', 3.34, false, 58.0, 1);
insert into student (fName, lName, email, enrollmentYear, major, minor, GPA, riskFlag, totalCredits, advisorID) values ('Marcille', 'Gallemore', 'marcille.gallemorenortheastern.edu', 2023, 'Data Science', 'Computer Science', 3.7, true, 8.58, 8);
insert into student (fName, lName, email, enrollmentYear, major, minor, GPA, riskFlag, totalCredits, advisorID) values ('Cindra', 'Osmund', 'cindra.osmundnortheastern.edu', 2021, 'Engineering', 'Data Science', 3.75, false, 8.83, 2);
insert into student (fName, lName, email, enrollmentYear, major, minor, GPA, riskFlag, totalCredits, advisorID) values ('Harriet', 'Wason', 'harriet.wasonnortheastern.edu', 2024, 'Economics', 'Computer Science', 2.26, false, 127.92, 3);
insert into student (fName, lName, email, enrollmentYear, major, minor, GPA, riskFlag, totalCredits, advisorID) values ('Niles', 'Affuso', 'niles.affusonortheastern.edu', 2024, 'Business', 'Economics', 2.69, false, 21.97, 27);
insert into student (fName, lName, email, enrollmentYear, major, minor, GPA, riskFlag, totalCredits, advisorID) values ('Belicia', 'Ivanilov', 'belicia.ivanilovnortheastern.edu', 2024, 'Business', 'Computer Science', 3.47, false, 114.41, 1);
insert into student (fName, lName, email, enrollmentYear, major, minor, GPA, riskFlag, totalCredits, advisorID) values ('Elsworth', 'Crafter', 'elsworth.crafternortheastern.edu', 2021, 'Engineering', 'Economics', 2.58, true, 14.14, 17);
insert into student (fName, lName, email, enrollmentYear, major, minor, GPA, riskFlag, totalCredits, advisorID) values ('Garry', 'Cleverly', 'garry.cleverlynortheastern.edu', 2022, 'Engineering', 'Biology', 3.1, true, 29.63, 17);
insert into student (fName, lName, email, enrollmentYear, major, minor, GPA, riskFlag, totalCredits, advisorID) values ('Ronald', 'Duplan', 'ronald.duplannortheastern.edu', 2021, 'Engineering', 'Economics', 2.65, true, 7.94, 9);
insert into student (fName, lName, email, enrollmentYear, major, minor, GPA, riskFlag, totalCredits, advisorID) values ('Phoebe', 'St. Quintin', 'phoebe.st. quintinnortheastern.edu', 2021, 'Psychology', 'Psychology', 2.62, true, 86.66, 7);
insert into student (fName, lName, email, enrollmentYear, major, minor, GPA, riskFlag, totalCredits, advisorID) values ('Freddi', 'Cardillo', 'freddi.cardillonortheastern.edu', 2023, 'Software Engineering', 'Biology', 2.87, false, 75.53, 23);
insert into student (fName, lName, email, enrollmentYear, major, minor, GPA, riskFlag, totalCredits, advisorID) values ('Deni', 'Curtis', 'deni.curtisnortheastern.edu', 2025, 'Engineering', 'Software Engineering', 4.0, false, 64.6, 36);
insert into student (fName, lName, email, enrollmentYear, major, minor, GPA, riskFlag, totalCredits, advisorID) values ('Kristina', 'Upstone', 'kristina.upstonenortheastern.edu', 2025, 'Psychology', 'Data Science', 2.24, true, 86.44, 16);
insert into student (fName, lName, email, enrollmentYear, major, minor, GPA, riskFlag, totalCredits, advisorID) values ('Sallee', 'Shales', 'sallee.shalesnortheastern.edu', 2023, 'Software Engineering', 'Data Science', 2.91, true, 54.46, 30);
insert into student (fName, lName, email, enrollmentYear, major, minor, GPA, riskFlag, totalCredits, advisorID) values ('Stanislaus', 'Pritchett', 'stanislaus.pritchettnortheastern.edu', 2023, 'Psychology', 'Psychology', 2.16, true, 72.92, 25);
insert into student (fName, lName, email, enrollmentYear, major, minor, GPA, riskFlag, totalCredits, advisorID) values ('Averil', 'Seaward', 'averil.seawardnortheastern.edu', 2021, 'Data Science', 'Business', 3.47, false, 100.25, 35);
insert into student (fName, lName, email, enrollmentYear, major, minor, GPA, riskFlag, totalCredits, advisorID) values ('Riva', 'Raiman', 'riva.raimannortheastern.edu', 2024, 'Biology', 'Biology', 3.6, false, 48.37, 33);
insert into student (fName, lName, email, enrollmentYear, major, minor, GPA, riskFlag, totalCredits, advisorID) values ('Flora', 'Armit', 'flora.armitnortheastern.edu', 2025, 'Software Engineering', 'Business', 3.31, false, 39.27, 15);
insert into student (fName, lName, email, enrollmentYear, major, minor, GPA, riskFlag, totalCredits, advisorID) values ('Yard', 'Restieaux', 'yard.restieauxnortheastern.edu', 2023, 'Engineering', 'Psychology', 3.59, true, 91.29, 31);
insert into student (fName, lName, email, enrollmentYear, major, minor, GPA, riskFlag, totalCredits, advisorID) values ('Susann', 'Nickols', 'susann.nickolsnortheastern.edu', 2025, 'Software Engineering', 'Data Science', 2.98, false, 102.64, 33);
insert into student (fName, lName, email, enrollmentYear, major, minor, GPA, riskFlag, totalCredits, advisorID) values ('Mella', 'Davall', 'mella.davallnortheastern.edu', 2025, 'Business', 'Economics', 2.26, false, 120.62, 10);
insert into student (fName, lName, email, enrollmentYear, major, minor, GPA, riskFlag, totalCredits, advisorID) values ('Tara', 'Greason', 'tara.greasonnortheastern.edu', 2022, 'Psychology', 'Economics', 2.84, true, 112.45, 23);
insert into student (fName, lName, email, enrollmentYear, major, minor, GPA, riskFlag, totalCredits, advisorID) values ('Shannah', 'Wapplington', 'shannah.wapplingtonnortheastern.edu', 2026, 'Biology', 'Engineering', 3.83, false, 8.22, 20);
insert into student (fName, lName, email, enrollmentYear, major, minor, GPA, riskFlag, totalCredits, advisorID) values ('Justus', 'Amies', 'justus.amiesnortheastern.edu', 2021, 'Data Science', 'Software Engineering', 2.1, true, 73.68, 3);
insert into student (fName, lName, email, enrollmentYear, major, minor, GPA, riskFlag, totalCredits, advisorID) values ('Lowe', 'Ambrose', 'lowe.ambrosenortheastern.edu', 2024, 'Engineering', 'Data Science', 3.7, false, 18.28, 1);
insert into student (fName, lName, email, enrollmentYear, major, minor, GPA, riskFlag, totalCredits, advisorID) values ('Thomasin', 'Rape', 'thomasin.rapenortheastern.edu', 2026, 'Economics', 'Biology', 3.37, false, 46.37, 4);
insert into student (fName, lName, email, enrollmentYear, major, minor, GPA, riskFlag, totalCredits, advisorID) values ('Bette-ann', 'McGraffin', 'bette-ann.mcgraffinnortheastern.edu', 2024, 'Software Engineering', 'Economics', 2.42, true, 7.43, 15);
insert into student (fName, lName, email, enrollmentYear, major, minor, GPA, riskFlag, totalCredits, advisorID) values ('Franni', 'Guilder', 'franni.guildernortheastern.edu', 2024, 'Biology', 'Economics', 2.98, true, 43.98, 21);
insert into student (fName, lName, email, enrollmentYear, major, minor, GPA, riskFlag, totalCredits, advisorID) values ('Aubrette', 'Lefwich', 'aubrette.lefwichnortheastern.edu', 2026, 'Data Science', 'Economics', 2.73, true, 107.67, 26);
insert into student (fName, lName, email, enrollmentYear, major, minor, GPA, riskFlag, totalCredits, advisorID) values ('Cammy', 'Steddall', 'cammy.steddallnortheastern.edu', 2025, 'Psychology', 'Software Engineering', 3.81, false, 59.15, 2);


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