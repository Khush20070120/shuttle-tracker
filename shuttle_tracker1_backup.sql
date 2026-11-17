-- MySQL dump 10.13  Distrib 9.6.0, for macos26.3 (arm64)
--
-- Host: localhost    Database: shuttle_tracker1
-- ------------------------------------------------------
-- Server version	9.6.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `Bus`
--

DROP TABLE IF EXISTS `Bus`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Bus` (
  `bus_id` int NOT NULL AUTO_INCREMENT,
  `bus_number` varchar(10) DEFAULT NULL,
  `capacity` int DEFAULT NULL,
  `departure_time` time DEFAULT NULL,
  `arrival_time` time DEFAULT NULL,
  PRIMARY KEY (`bus_id`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Bus`
--

LOCK TABLES `Bus` WRITE;
/*!40000 ALTER TABLE `Bus` DISABLE KEYS */;
/*!40000 ALTER TABLE `Bus` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `LoginLogs`
--

DROP TABLE IF EXISTS `LoginLogs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `LoginLogs` (
  `log_id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) DEFAULT NULL,
  `role` varchar(10) DEFAULT NULL,
  `login_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`log_id`)
) ENGINE=InnoDB AUTO_INCREMENT=31 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `LoginLogs`
--

LOCK TABLES `LoginLogs` WRITE;
/*!40000 ALTER TABLE `LoginLogs` DISABLE KEYS */;
INSERT INTO `LoginLogs` VALUES (1,'user 1','user','2026-04-19 13:41:46'),(2,'admin','admin','2026-04-19 13:50:26'),(3,'user1','user','2026-04-19 13:52:26'),(4,'admin','admin','2026-04-19 13:55:51'),(5,'admin','admin','2026-04-19 13:59:57'),(6,'user1','user','2026-04-19 14:49:51'),(7,'admin','admin','2026-04-19 14:50:09'),(8,'admin','admin','2026-04-19 14:52:13'),(9,'user1','user','2026-04-19 14:52:33'),(10,'admin','admin','2026-04-19 14:58:42'),(11,'admin','admin','2026-04-19 15:12:39'),(12,'user 1','user','2026-04-19 15:14:18'),(13,'admin','admin','2026-04-19 15:15:06'),(14,'admin','admin','2026-04-19 15:28:53'),(15,'user 1','user','2026-04-19 15:29:18'),(16,'2admin1','admin','2026-04-19 15:30:13'),(17,'user1','user','2026-04-19 16:25:17'),(18,'user1','user','2026-04-19 16:31:50'),(19,'admin','admin','2026-04-19 16:32:16'),(20,'admin','admin','2026-04-19 19:59:49'),(21,'admin','admin','2026-04-20 07:45:22'),(22,'admin','admin','2026-04-20 07:51:47'),(23,'admin','admin','2026-04-23 09:19:28'),(24,'user1','user','2026-04-23 09:22:19'),(25,'Khushaggarwal111@gmail.com','admin','2026-11-04 16:48:46'),(26,'Khushaggarwal111@gmail.com','admin','2026-11-04 16:48:57'),(27,'a','admin','2026-11-17 06:49:21'),(28,'khush','user','2026-11-17 06:57:59'),(29,'Khushaggarwal111@gmail.com','admin','2026-11-17 07:45:50'),(30,'admin','admin','2026-11-17 09:06:19');
/*!40000 ALTER TABLE `LoginLogs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Route`
--

DROP TABLE IF EXISTS `Route`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Route` (
  `route_id` int NOT NULL AUTO_INCREMENT,
  `source` varchar(50) DEFAULT NULL,
  `destination` varchar(50) DEFAULT NULL,
  `departure_time` time DEFAULT NULL,
  `arrival_time` time DEFAULT NULL,
  PRIMARY KEY (`route_id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Route`
--

LOCK TABLES `Route` WRITE;
/*!40000 ALTER TABLE `Route` DISABLE KEYS */;
INSERT INTO `Route` VALUES (7,'College','City Center','08:00:00','09:00:00'),(8,'Hostel','Campus','21:10:00','10:00:00'),(9,'IILM','GIRLS Hostel','10:20:00','12:20:00');
/*!40000 ALTER TABLE `Route` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Users`
--

DROP TABLE IF EXISTS `Users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Users` (
  `user_id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  `role` varchar(10) DEFAULT 'user',
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Users`
--

LOCK TABLES `Users` WRITE;
/*!40000 ALTER TABLE `Users` DISABLE KEYS */;
INSERT INTO `Users` VALUES (3,'admin','pbkdf2:sha256:1000000$TAiXl1gq9HYBnSly$0a0f4f136509dab21f81620364aa6543963b352c18510fcd34d060515423f31e','admin'),(4,'admin1','pbkdf2:sha256:1000000$btClV8ymLhxkuqdT$cd2ff36bc58ce54b57cd63efd9e5232ad956a95c117adb9b19b42d7456d5ab7c','user'),(5,'user 1','pbkdf2:sha256:1000000$wLhHJVV69P3sH2ZQ$d0d757468b6eb41b3d546616d2b8097e6fdc6118fe0220dcbe907d7610efb72a','user'),(7,'admin11','pbkdf2:sha256:1000000$BgQBlOKWUOh9qTEX$c3d0b42e12d3e2f10155f75832e914adb65421df1e0a97122f72897d415b5aae','user'),(8,'user1','pbkdf2:sha256:1000000$qsnc9MywrR2WGSWG$5bcf055e279550e5e0b8ef4c4f133f2af6ae1117c5fc4f1d870ce3ee1a41bbbd','user'),(10,'2admin1','pbkdf2:sha256:1000000$1lo8MUZvsKv8d805$167c23fa0e35d030d05aef761392ff89d62ce100693dd95bf2cb50e754363b94','admin'),(11,'user12','pbkdf2:sha256:1000000$5Uttg3gC53UY9Glk$cc98989c1f368c26c27708bb00dc9ccda9bc91c6b8c80565b17166dfe99bdda6','user'),(12,'Khushaggarwal111@gmail.com','pbkdf2:sha256:1000000$V8LDjeCDcQ6JyyXm$4fd01e794237f1038cf6a5395fe983c0c9eda6cbc7a0acb106eb0db778084386','admin'),(13,'a','pbkdf2:sha256:1000000$vBT9QyVcRapFPTgP$8e7380fbc1b11c37261db5061f70649c3cc2fffe069874ec955491ea317f7acb','admin'),(14,'khush','pbkdf2:sha256:1000000$ESRUf0YowGlC0k1X$fd5ca179c4f76a5e1fb445183fbef253b8b6b152f8aad86835fa5d1946f5dda3','user');
/*!40000 ALTER TABLE `Users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-11-17 14:41:35
