-- MySQL dump 10.13  Distrib 8.0.46, for Linux (x86_64)
--
-- Host: localhost    Database: test
-- ------------------------------------------------------
-- Server version	8.0.46

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
-- Table structure for table `assign_subcontractors`
--

DROP TABLE IF EXISTS `assign_subcontractors`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `assign_subcontractors` (
  `PMC_no` int DEFAULT NULL,
  `Contractor_Id` int DEFAULT NULL,
  `Village_Id` int DEFAULT NULL,
  KEY `Contractor_Id` (`Contractor_Id`),
  KEY `Village_Id` (`Village_Id`),
  CONSTRAINT `assign_subcontractors_ibfk_1` FOREIGN KEY (`Contractor_Id`) REFERENCES `subcontractors` (`Contractor_Id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `assign_subcontractors_ibfk_2` FOREIGN KEY (`Village_Id`) REFERENCES `villages` (`Village_Id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_assign_contractor` FOREIGN KEY (`Contractor_Id`) REFERENCES `subcontractors` (`Contractor_Id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `assign_subcontractors`
--

LOCK TABLES `assign_subcontractors` WRITE;
/*!40000 ALTER TABLE `assign_subcontractors` DISABLE KEYS */;
/*!40000 ALTER TABLE `assign_subcontractors` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `balance_to_debit`
--

DROP TABLE IF EXISTS `balance_to_debit`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `balance_to_debit` (
  `id` int NOT NULL AUTO_INCREMENT,
  `contractor_id` int NOT NULL,
  `balance_debit` decimal(15,2) NOT NULL DEFAULT '0.00',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_contractor` (`contractor_id`),
  CONSTRAINT `balance_to_debit_ibfk_1` FOREIGN KEY (`contractor_id`) REFERENCES `subcontractors` (`Contractor_Id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `balance_to_debit`
--

LOCK TABLES `balance_to_debit` WRITE;
/*!40000 ALTER TABLE `balance_to_debit` DISABLE KEYS */;
/*!40000 ALTER TABLE `balance_to_debit` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `blocks`
--

DROP TABLE IF EXISTS `blocks`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `blocks` (
  `Block_Id` int NOT NULL AUTO_INCREMENT,
  `Block_Name` varchar(255) NOT NULL,
  `District_id` int NOT NULL,
  `status` varchar(20) NOT NULL DEFAULT 'Active',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`Block_Id`),
  KEY `District_id` (`District_id`),
  CONSTRAINT `blocks_ibfk_1` FOREIGN KEY (`District_id`) REFERENCES `districts` (`District_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `blocks`
--

LOCK TABLES `blocks` WRITE;
/*!40000 ALTER TABLE `blocks` DISABLE KEYS */;
INSERT INTO `blocks` VALUES (1,'UGD',1,'Active','2026-09-28 11:52:31');
/*!40000 ALTER TABLE `blocks` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `credit_note`
--

DROP TABLE IF EXISTS `credit_note`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `credit_note` (
  `Credit_Note_Id` int NOT NULL AUTO_INCREMENT,
  `PMC_No` int DEFAULT NULL,
  `Invoice_Details` varchar(256) DEFAULT NULL,
  `Basic_Amount` decimal(15,2) DEFAULT NULL,
  `Debit_Amount` decimal(15,2) DEFAULT NULL,
  `After_Debit_Amount` decimal(15,2) DEFAULT NULL,
  `GST_Amount` decimal(15,2) DEFAULT NULL,
  `Amount` decimal(15,2) DEFAULT NULL,
  `Final_Amount` decimal(15,2) DEFAULT NULL,
  `Payment_Amount` decimal(15,2) DEFAULT NULL,
  `Total_Amount` decimal(15,2) DEFAULT NULL,
  `UTR` varchar(255) DEFAULT NULL,
  `Contractor_Id` int DEFAULT NULL,
  `invoice_no` varchar(100) DEFAULT NULL,
  `uploaded_file_id` int DEFAULT NULL,
  PRIMARY KEY (`Credit_Note_Id`),
  KEY `fk_creditnote_contractor` (`Contractor_Id`),
  CONSTRAINT `fk_creditnote_contractor` FOREIGN KEY (`Contractor_Id`) REFERENCES `subcontractors` (`Contractor_Id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `credit_note`
--

LOCK TABLES `credit_note` WRITE;
/*!40000 ALTER TABLE `credit_note` DISABLE KEYS */;
/*!40000 ALTER TABLE `credit_note` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `credit_notes`
--

DROP TABLE IF EXISTS `credit_notes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `credit_notes` (
  `Credit_Note_Id` int NOT NULL AUTO_INCREMENT,
  `PMC_No` varchar(100) DEFAULT NULL,
  `Invoice_No` varchar(100) DEFAULT NULL,
  `Basic_Amount` decimal(15,2) DEFAULT '0.00',
  `Final_Amount` decimal(15,2) DEFAULT '0.00',
  `Total_Amount` decimal(15,2) DEFAULT '0.00',
  `Contractor_Id` int DEFAULT NULL,
  PRIMARY KEY (`Credit_Note_Id`),
  KEY `Contractor_Id` (`Contractor_Id`),
  CONSTRAINT `credit_notes_ibfk_1` FOREIGN KEY (`Contractor_Id`) REFERENCES `subcontractors` (`Contractor_Id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `credit_notes`
--

LOCK TABLES `credit_notes` WRITE;
/*!40000 ALTER TABLE `credit_notes` DISABLE KEYS */;
/*!40000 ALTER TABLE `credit_notes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `districts`
--

DROP TABLE IF EXISTS `districts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `districts` (
  `District_id` int NOT NULL AUTO_INCREMENT,
  `District_Name` varchar(255) NOT NULL,
  `State_Id` int NOT NULL,
  `status` varchar(20) NOT NULL DEFAULT 'Active',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`District_id`),
  KEY `State_Id` (`State_Id`),
  CONSTRAINT `districts_ibfk_1` FOREIGN KEY (`State_Id`) REFERENCES `states` (`State_Id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `districts`
--

LOCK TABLES `districts` WRITE;
/*!40000 ALTER TABLE `districts` DISABLE KEYS */;
INSERT INTO `districts` VALUES (1,'Solapur',1,'Active','2026-09-28 11:52:21');
/*!40000 ALTER TABLE `districts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `gst_release`
--

DROP TABLE IF EXISTS `gst_release`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gst_release` (
  `GST_Release_Id` int NOT NULL AUTO_INCREMENT,
  `PMC_No` int DEFAULT NULL,
  `invoice_no` varchar(100) DEFAULT NULL,
  `Basic_Amount` decimal(10,2) DEFAULT NULL,
  `Final_Amount` decimal(10,2) DEFAULT NULL,
  `Total_Amount` decimal(10,2) DEFAULT NULL,
  `UTR` varchar(255) DEFAULT NULL,
  `Contractor_Id` int DEFAULT NULL,
  PRIMARY KEY (`GST_Release_Id`),
  UNIQUE KEY `UTR` (`UTR`),
  KEY `fk_gstrelease_contractor` (`Contractor_Id`),
  CONSTRAINT `fk_gstrelease_contractor` FOREIGN KEY (`Contractor_Id`) REFERENCES `subcontractors` (`Contractor_Id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `gst_release`
--

LOCK TABLES `gst_release` WRITE;
/*!40000 ALTER TABLE `gst_release` DISABLE KEYS */;
/*!40000 ALTER TABLE `gst_release` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `gst_releases`
--

DROP TABLE IF EXISTS `gst_releases`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gst_releases` (
  `GST_Release_Id` int NOT NULL AUTO_INCREMENT,
  `PMC_No` varchar(100) DEFAULT NULL,
  `Invoice_No` varchar(100) DEFAULT NULL,
  `Basic_Amount` decimal(15,2) DEFAULT '0.00',
  `Final_Amount` decimal(15,2) DEFAULT '0.00',
  `Total_Amount` decimal(15,2) DEFAULT '0.00',
  `UTR` varchar(500) DEFAULT NULL,
  `Contractor_ID` int DEFAULT NULL,
  `sort_order` int DEFAULT NULL,
  `uploaded_file_id` int DEFAULT NULL,
  `Invoice_Date` date DEFAULT NULL,
  PRIMARY KEY (`GST_Release_Id`),
  KEY `Contractor_ID` (`Contractor_ID`),
  CONSTRAINT `gst_releases_ibfk_1` FOREIGN KEY (`Contractor_ID`) REFERENCES `subcontractors` (`Contractor_Id`)
) ENGINE=InnoDB AUTO_INCREMENT=48 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `gst_releases`
--

LOCK TABLES `gst_releases` WRITE;
/*!40000 ALTER TABLE `gst_releases` DISABLE KEYS */;
INSERT INTO `gst_releases` VALUES (37,'67112','1',136175.22,136175.22,178312.00,'13-03-2025NEFT/AXISP00633086699/SSMH24/2671/S KCONSTRUCTION/SBIN0017530 178312.00',2,2,1,NULL),(38,'67112','2',197353.62,197353.62,975804.00,'16-04-2025NEFT/AXISP00651599302/SSMH25/53/S KCONSTRUCTION/SBIN0017530 975804.00',2,4,1,NULL),(39,'67112','4',491680.80,491680.80,2662851.00,'16-12-2025 NEFT/AXISP00751241446/SNSMH25/2303/S K CONSTRUCTION/SBIN0017530 2662851.00',2,8,1,NULL),(40,'67112','5',622485.00,622485.00,2000000.00,'02-01-2026NEFT/AXISP00756246991/SNSMH25/2549/S KCONSTRUCTION/SBIN0017530 2000000.00',2,10,1,NULL),(41,'67112','6',989415.00,989415.00,622486.00,'29-01-2026 NEFT/AXISP00763644150/SNSMH25/2895/S K CONSTRUCTION/SBIN0017530 622486.00',2,12,1,NULL),(42,'67112','7',699840.00,699840.00,989416.00,'24-02-2026 NEFT/AXISP00771920100/SNSMH25/3319/S K CONSTRUCTION/SBIN0017530 989416.00',2,13,1,NULL),(43,'67112','8',7623000.00,7623000.00,699841.00,'25/03/2026 NEFT/AXISP00781410614/SNSMH25/37 16/S K CONSTRUCTION/SBIN0017530 6,99,841.00',2,15,1,NULL),(44,'67112','3',22513.68,22513.68,311040.00,'31/08/2026 NEFT/AXISP00831810006/SNSMH26/19 36/S K CONSTRUCTION/SBIN0017530 3,11,040.00',2,22,1,NULL),(45,'73275','1',114625.62,114625.62,114626.00,'06/05/2026 NEFT/AXISP00795743176/SNSMH26/04 35/SANKET GURURAJ VIB/MAHB0001686 1,14,626.00',4,2,2,NULL),(46,'73275','2',48888.00,48888.00,48888.00,'28/07/2026 NEFT/AXISP00821082699/SNSMH26/15 24/SANKET GURURAJ VIB/MAHB0001686 48,888.00',4,4,2,NULL),(47,'73275','3',67902.84,67902.84,67903.00,'21/09/2026 NEFT/AXISP00839204135/SNSMH26/21 98/SANKET GURURAJ VIB/MAHB0001686 67,903.00',4,6,2,NULL);
/*!40000 ALTER TABLE `gst_releases` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `hold_release`
--

DROP TABLE IF EXISTS `hold_release`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `hold_release` (
  `Hold_Release_Id` int NOT NULL AUTO_INCREMENT,
  `PMC_No` int DEFAULT NULL,
  `invoice_no` varchar(100) DEFAULT NULL,
  `Invoice_Details` varchar(256) DEFAULT NULL,
  `Basic_Amount` decimal(10,2) DEFAULT NULL,
  `Final_Amount` decimal(10,2) DEFAULT NULL,
  `Total_Amount` decimal(10,2) DEFAULT NULL,
  `UTR` varchar(256) DEFAULT NULL,
  `Contractor_Id` int DEFAULT NULL,
  `uploaded_file_id` int DEFAULT NULL,
  PRIMARY KEY (`Hold_Release_Id`),
  UNIQUE KEY `UTR_PMC_UNIQUE` (`UTR`,`PMC_No`),
  KEY `fk_contractor_id` (`Contractor_Id`),
  CONSTRAINT `fk_contractor_id` FOREIGN KEY (`Contractor_Id`) REFERENCES `subcontractors` (`Contractor_Id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `hold_release`
--

LOCK TABLES `hold_release` WRITE;
/*!40000 ALTER TABLE `hold_release` DISABLE KEYS */;
INSERT INTO `hold_release` VALUES (7,67112,'4','Hold Release Note',218524.80,218524.80,10000000.00,'08/04/2026 NEFT/AXISP00787003041/SNSMH26/00 32/S K CONSTRUCTION/SBIN0017530 1,00,00,000.00',2,1),(8,67112,'5','Hold Release Note',276660.00,276660.00,10000000.00,'15/04/2026 NEFT/AXISP00788745845/SNSMH26/0174/S K CONSTRUCTION/SBIN0017530 1,00,00,000.00',2,1),(9,67112,'6','Hold Release Note',439740.00,439740.00,7623000.00,'23/04/2026 NEFT/AXISP00790687258/SNSMH26/03 20/S K CONSTRUCTION/SBIN0017530 76,23,000.00',2,1),(10,67112,'7','Hold Release Note',311040.00,311040.00,12609500.00,'28/04/2026 NEFT/AXISP00791632686/SNSMH26/0175/S K CONSTRUCTION/SBIN0017530 1,26,09,500.00',2,1),(11,67112,'8 - Part 1','Hold Release Note',500000.00,500000.00,495185.00,'30/07/2026 NEFT/AXISP00821657052/SNSMH26/15 70/S K CONSTRUCTION/SBIN0017530 4,95,185.00',2,1),(12,67112,'8 - Part 2','Hold Release Note',500000.00,500000.00,439740.00,'14/08/2026 NEFT/AXISP00827698588/SNSMH26/1692/S K CONSTRUCTION/SBIN0017530 4,39,740.00',2,1),(13,73275,'1','Hold Release Note',31840.45,31840.45,0.00,NULL,4,2);
/*!40000 ALTER TABLE `hold_release` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `hold_types`
--

DROP TABLE IF EXISTS `hold_types`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `hold_types` (
  `hold_type_id` int NOT NULL AUTO_INCREMENT,
  `hold_type` varchar(500) DEFAULT NULL,
  `hold_category` varchar(100) DEFAULT 'Miscellaneous',
  `description` text,
  `default_hold_percentage` decimal(5,2) DEFAULT NULL,
  `status` varchar(20) DEFAULT 'Active',
  `created_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `last_updated_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `include_in_hold` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`hold_type_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `hold_types`
--

LOCK TABLES `hold_types` WRITE;
/*!40000 ALTER TABLE `hold_types` DISABLE KEYS */;
INSERT INTO `hold_types` VALUES (1,'Extra_Hold','Miscellaneous',NULL,NULL,'Active','2026-09-28 11:51:33','2026-09-28 11:51:33',1),(2,'Maintaninece_RR','Maintenance',NULL,4.00,'Active','2026-09-28 11:54:16','2026-09-28 11:54:16',1),(3,'Testing_ Deposit_RR','Testing Deposit',NULL,8.00,'Active','2026-09-28 11:54:32','2026-09-28 11:54:32',1),(4,'SD_RR','Security Deposit',NULL,10.00,'Active','2026-09-28 11:54:45','2026-09-28 11:54:45',1);
/*!40000 ALTER TABLE `hold_types` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `invoice`
--

DROP TABLE IF EXISTS `invoice`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `invoice` (
  `Invoice_Id` int NOT NULL AUTO_INCREMENT,
  `PMC_No` int DEFAULT NULL,
  `Village_Id` int DEFAULT NULL,
  `Work_Type` varchar(250) DEFAULT NULL,
  `Invoice_Details` text,
  `Invoice_Date` date DEFAULT NULL,
  `invoice_no` varchar(100) DEFAULT NULL,
  `Basic_Amount` decimal(15,2) DEFAULT NULL,
  `Debit_Amount` decimal(15,2) DEFAULT NULL,
  `After_Debit_Amount` decimal(15,2) DEFAULT NULL,
  `Amount` decimal(15,2) DEFAULT NULL,
  `GST_Amount` decimal(15,2) DEFAULT NULL,
  `TDS_Amount` decimal(15,2) DEFAULT NULL,
  `SD_Amount` decimal(15,2) DEFAULT NULL,
  `On_Commission` decimal(15,2) DEFAULT NULL,
  `Hydro_Testing` decimal(15,2) DEFAULT NULL,
  `Hold_Amount` varchar(50) DEFAULT NULL,
  `GST_SD_Amount` decimal(15,2) DEFAULT NULL,
  `Final_Amount` decimal(15,2) DEFAULT NULL,
  `Contractor_Id` int DEFAULT NULL,
  PRIMARY KEY (`Invoice_Id`),
  KEY `Village_Id` (`Village_Id`),
  KEY `fk_invoice_contractor` (`Contractor_Id`),
  CONSTRAINT `fk_invoice_contractor` FOREIGN KEY (`Contractor_Id`) REFERENCES `subcontractors` (`Contractor_Id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `invoice_ibfk_1` FOREIGN KEY (`Village_Id`) REFERENCES `villages` (`Village_Id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `invoice`
--

LOCK TABLES `invoice` WRITE;
/*!40000 ALTER TABLE `invoice` DISABLE KEYS */;
/*!40000 ALTER TABLE `invoice` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `invoice_holds`
--

DROP TABLE IF EXISTS `invoice_holds`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `invoice_holds` (
  `id` int NOT NULL AUTO_INCREMENT,
  `Subcontractor_Id` int DEFAULT NULL,
  `Invoice_Id` int DEFAULT NULL,
  `hold_type_id` int DEFAULT NULL,
  `hold_amount` decimal(15,2) DEFAULT '0.00',
  PRIMARY KEY (`id`),
  KEY `Invoice_Id` (`Invoice_Id`),
  KEY `hold_type_id` (`hold_type_id`),
  CONSTRAINT `invoice_holds_ibfk_1` FOREIGN KEY (`Invoice_Id`) REFERENCES `invoices` (`Invoice_Id`) ON DELETE CASCADE,
  CONSTRAINT `invoice_holds_ibfk_2` FOREIGN KEY (`hold_type_id`) REFERENCES `hold_types` (`hold_type_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `invoice_holds`
--

LOCK TABLES `invoice_holds` WRITE;
/*!40000 ALTER TABLE `invoice_holds` DISABLE KEYS */;
/*!40000 ALTER TABLE `invoice_holds` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `invoice_subcontractor_hold_join`
--

DROP TABLE IF EXISTS `invoice_subcontractor_hold_join`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `invoice_subcontractor_hold_join` (
  `join_id` int NOT NULL AUTO_INCREMENT,
  `Contractor_Id` int DEFAULT NULL,
  `Invoice_Id` int DEFAULT NULL,
  `hold_type_id` int DEFAULT NULL,
  `hold_amount` decimal(15,2) DEFAULT NULL,
  PRIMARY KEY (`join_id`),
  KEY `Contractor_Id` (`Contractor_Id`),
  KEY `Invoice_Id` (`Invoice_Id`),
  KEY `hold_type_id` (`hold_type_id`),
  CONSTRAINT `fk_holdjoin_contractor` FOREIGN KEY (`Contractor_Id`) REFERENCES `subcontractors` (`Contractor_Id`) ON DELETE CASCADE,
  CONSTRAINT `fk_holdjoin_invoice` FOREIGN KEY (`Invoice_Id`) REFERENCES `invoices` (`Invoice_Id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `invoice_subcontractor_hold_join_ibfk_1` FOREIGN KEY (`Contractor_Id`) REFERENCES `subcontractors` (`Contractor_Id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `invoice_subcontractor_hold_join_ibfk_3` FOREIGN KEY (`hold_type_id`) REFERENCES `hold_types` (`hold_type_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=52 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `invoice_subcontractor_hold_join`
--

LOCK TABLES `invoice_subcontractor_hold_join` WRITE;
/*!40000 ALTER TABLE `invoice_subcontractor_hold_join` DISABLE KEYS */;
INSERT INTO `invoice_subcontractor_hold_join` VALUES (31,2,43,4,273156.00),(32,2,43,3,218524.80),(33,2,43,2,109262.40),(34,2,44,4,345825.00),(35,2,44,3,276660.00),(36,2,44,2,138330.00),(37,2,45,4,549675.00),(38,2,45,3,439740.00),(39,2,45,2,219870.00),(40,2,46,4,388800.00),(41,2,46,3,311040.00),(42,2,46,2,155520.00),(43,2,47,4,4235000.00),(44,2,47,3,3388000.00),(45,2,47,2,1694000.00),(46,4,57,1,12642.00),(47,4,58,1,3759.00),(48,4,58,4,1234.00),(49,4,58,3,546.00),(50,4,58,2,346.00),(51,4,59,1,4714.50);
/*!40000 ALTER TABLE `invoice_subcontractor_hold_join` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `invoices`
--

DROP TABLE IF EXISTS `invoices`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `invoices` (
  `Invoice_Id` int NOT NULL AUTO_INCREMENT,
  `PMC_No` int DEFAULT NULL,
  `Village_Id` int DEFAULT NULL,
  `Work_Type` varchar(255) DEFAULT NULL,
  `Invoice_Details` text,
  `Invoice_Date` date DEFAULT NULL,
  `Invoice_No` varchar(100) DEFAULT NULL,
  `Basic_Amount` decimal(15,2) DEFAULT '0.00',
  `Debit_Amount` decimal(15,2) DEFAULT '0.00',
  `After_Debit_Amount` decimal(15,2) DEFAULT '0.00',
  `Amount` decimal(15,2) DEFAULT '0.00',
  `GST_Amount` decimal(15,2) DEFAULT '0.00',
  `TDS_Amount` decimal(15,2) DEFAULT '0.00',
  `SD_Amount` decimal(15,2) DEFAULT '0.00',
  `On_Commission` decimal(15,2) DEFAULT '0.00',
  `Hydro_Testing` decimal(15,2) DEFAULT '0.00',
  `GST_SD_Amount` decimal(15,2) DEFAULT '0.00',
  `Final_Amount` decimal(15,2) DEFAULT '0.00',
  `Subcontractor_Id` int DEFAULT NULL,
  `Is_Extra` tinyint DEFAULT '0',
  `sort_order` int DEFAULT NULL,
  `uploaded_file_id` int DEFAULT NULL,
  `Village_Wise_Advance` decimal(15,2) DEFAULT NULL,
  PRIMARY KEY (`Invoice_Id`),
  KEY `Village_Id` (`Village_Id`),
  KEY `Subcontractor_Id` (`Subcontractor_Id`),
  CONSTRAINT `invoices_ibfk_1` FOREIGN KEY (`Village_Id`) REFERENCES `villages` (`Village_Id`),
  CONSTRAINT `invoices_ibfk_2` FOREIGN KEY (`Subcontractor_Id`) REFERENCES `subcontractors` (`Contractor_Id`)
) ENGINE=InnoDB AUTO_INCREMENT=61 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `invoices`
--

LOCK TABLES `invoices` WRITE;
/*!40000 ALTER TABLE `invoices` DISABLE KEYS */;
INSERT INTO `invoices` VALUES (40,67112,1,'pipeline work','Solapur Village Pipeline Work','2025-02-20','1',758084.00,1555.00,756529.00,892704.22,136175.22,7565.29,37826.45,0.00,37826.45,136175.22,673311.00,2,0,1,1,NULL),(41,67112,1,'pipeline work','Solapur Village Pipeline Work','2025-03-24','2',1213409.00,117000.00,1096409.00,1293762.62,197353.62,10964.09,54820.45,0.00,54820.45,197353.62,975804.00,2,0,3,1,NULL),(42,67112,1,'pipeline work','Solapur Village Pipeline Work','2026-06-25','3',125076.00,0.00,125076.00,147589.68,22513.68,1250.76,6253.80,0.00,6253.80,22513.68,111318.00,2,0,5,1,NULL),(43,67112,1,'rr work','Solapur Village RR Work','2025-10-14','4',2731560.00,0.00,2731560.00,3223240.80,491680.80,27315.60,0.00,0.00,0.00,491680.80,2103301.00,2,0,6,1,NULL),(44,67112,1,'rr work','Solapur Village RR Work','2025-12-04','5',3458250.00,0.00,3458250.00,4080735.00,622485.00,34582.50,0.00,0.00,0.00,622485.00,2662853.00,2,0,7,1,NULL),(45,67112,1,'rr work','Solapur Village RR Work','2025-12-18','6',5496750.00,0.00,5496750.00,6486165.00,989415.00,54967.50,0.00,0.00,0.00,989415.00,4232498.00,2,0,9,1,NULL),(46,67112,1,'rr work','Solapur Village RR Work','2026-02-18','7',3888000.00,0.00,3888000.00,4587840.00,699840.00,38880.00,0.00,0.00,0.00,699840.00,2993760.00,2,0,11,1,NULL),(47,67112,1,'rr work','Solapur Village RR Work','2026-03-25','8',42350000.00,0.00,42350000.00,49973000.00,7623000.00,423500.00,0.00,0.00,0.00,7623000.00,32609500.00,2,0,14,1,NULL),(48,67112,NULL,NULL,'Hold Release Note',NULL,'4',218524.80,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,218524.80,2,0,16,1,NULL),(49,67112,NULL,NULL,'Hold Release Note',NULL,'5',276660.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,276660.00,2,0,17,1,NULL),(50,67112,NULL,NULL,'Hold Release Note',NULL,'6',439740.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,439740.00,2,0,18,1,NULL),(51,67112,NULL,NULL,'Hold Release Note',NULL,'7',311040.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,311040.00,2,0,19,1,NULL),(52,67112,NULL,NULL,'Hold Release Note',NULL,'8 - Part 1',500000.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,500000.00,2,0,20,1,NULL),(53,67112,NULL,NULL,'Hold Release Note',NULL,'8 - Part 2',500000.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,500000.00,2,0,21,1,NULL),(54,67112,NULL,NULL,'',NULL,NULL,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,2,0,23,1,NULL),(55,67112,NULL,NULL,'',NULL,NULL,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,2,0,24,1,NULL),(56,67112,NULL,NULL,'',NULL,NULL,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,2,0,25,1,NULL),(57,73275,1,'pipeline work','Solapur Village Pipeline Work','2026-03-20','1',803737.00,166928.00,636809.00,751434.62,114625.62,6368.09,31840.45,0.00,31840.45,114625.62,554118.00,4,0,1,2,NULL),(58,73275,1,'pipeline work','Solapur Village Pipeline Work','2026-06-19','2',300687.00,29087.00,271600.00,320488.00,48888.00,2716.00,13580.00,0.00,13580.00,48888.00,235839.00,4,0,3,2,NULL),(59,73275,1,'pipeline work','Solapur Village Pipeline Work','2026-08-21','3',377238.00,0.00,377238.00,445140.84,67902.84,3772.38,18861.90,0.00,18861.90,67902.84,331027.00,4,0,5,2,NULL),(60,73275,NULL,NULL,'Hold Release Note',NULL,'1',31840.45,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,31840.45,4,0,7,2,NULL);
/*!40000 ALTER TABLE `invoices` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `items`
--

DROP TABLE IF EXISTS `items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `items` (
  `item_id` int NOT NULL AUTO_INCREMENT,
  `item_type` int NOT NULL,
  `item_name` varchar(255) NOT NULL,
  PRIMARY KEY (`item_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `items`
--

LOCK TABLES `items` WRITE;
/*!40000 ALTER TABLE `items` DISABLE KEYS */;
/*!40000 ALTER TABLE `items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `payment`
--

DROP TABLE IF EXISTS `payment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `payment` (
  `Payment_Id` int NOT NULL AUTO_INCREMENT,
  `PMC_No` int DEFAULT NULL,
  `invoice_no` varchar(100) DEFAULT NULL,
  `Amount_with_TDS` decimal(10,2) DEFAULT NULL,
  `TDS_Payment_Amount` decimal(10,2) DEFAULT NULL,
  `TDS_Percentage` decimal(5,2) NOT NULL DEFAULT '0.00',
  `Amount_after_TDS_Deduction` decimal(10,2) DEFAULT NULL,
  `UTR` varchar(255) DEFAULT NULL,
  `Payment_Date` date DEFAULT NULL,
  `Payment_Status` varchar(50) NOT NULL DEFAULT 'Paid',
  `Invoice_Id` int DEFAULT NULL,
  PRIMARY KEY (`Payment_Id`),
  UNIQUE KEY `UTR_PMC_UNIQUE` (`UTR`,`PMC_No`),
  KEY `fk_payment_invoice` (`Invoice_Id`),
  CONSTRAINT `fk_payment_invoices` FOREIGN KEY (`Invoice_Id`) REFERENCES `invoices` (`Invoice_Id`)
) ENGINE=InnoDB AUTO_INCREMENT=60 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payment`
--

LOCK TABLES `payment` WRITE;
/*!40000 ALTER TABLE `payment` DISABLE KEYS */;
INSERT INTO `payment` VALUES (40,67112,'1',502565.29,7565.29,0.00,495000.00,'18-02-2025NEFT/AXISP00618257367/SSMH24/2423/S KCONSTRUCTION/SBIN0017530 495000.00',NULL,'Paid',40),(41,67112,'2',147139.09,10964.09,0.00,136175.00,'24-03-2025NEFT/AXISP00637389506/SSMH24/2914/S K CONSTRUCTION/SBIN0017530 136175.00',NULL,'Paid',41),(42,67112,'3',198604.76,1250.76,0.00,197354.00,'29-05-2025NEFT/AXISP00671284014/SSMH25/848/S K CONSTRUCTION/SBIN0017530 197354.00',NULL,'Paid',42),(43,67112,'4',138632.60,27315.60,0.00,111317.00,'16-09-2025 NEFT/AXISP00716025636/SNSMH25/1277/S K CONSTRUCTION/SBIN0017530 111317.00',NULL,'Paid',43),(44,67112,'5',2137883.50,34582.50,0.00,2103301.00,'31-10-2025 NEFT/AXISP00735672881/SNSMH25/1810/S K CONSTRUCTION/SBIN0017530 2103301.00',NULL,'Paid',44),(45,67112,'6',546648.50,54967.50,0.00,491681.00,'20-12-2025 NEFT/AXISP00752366218/SNSMH25/2446/S K CONSTRUCTION/SBIN0017530 491681.00',NULL,'Paid',45),(46,67112,'7',2271376.00,38880.00,0.00,2232496.00,'09-01-2026 NEFT/AXISP00759220650/SNSMH25/2549B/S K CONSTRUCTION/SBIN0017530 2232496.00',NULL,'Paid',46),(47,67112,'8',3417259.00,423500.00,0.00,2993759.00,'27-02-2026 NEFT/AXISP00773143303/SNSMH25/3316A/S K CONSTRUCTION/SBIN0017530 2993759.00',NULL,'Paid',47),(48,67112,'4',10000000.00,0.00,0.00,10000000.00,'08/04/2026 NEFT/AXISP00787003041/SNSMH26/00 32/S K CONSTRUCTION/SBIN0017530 1,00,00,000.00',NULL,'Paid',48),(49,67112,'5',10000000.00,0.00,0.00,10000000.00,'15/04/2026 NEFT/AXISP00788745845/SNSMH26/0174/S K CONSTRUCTION/SBIN0017530 1,00,00,000.00',NULL,'Paid',49),(50,67112,'6',7623000.00,0.00,0.00,7623000.00,'23/04/2026 NEFT/AXISP00790687258/SNSMH26/03 20/S K CONSTRUCTION/SBIN0017530 76,23,000.00',NULL,'Paid',50),(51,67112,'7',12609500.00,0.00,0.00,12609500.00,'28/04/2026 NEFT/AXISP00791632686/SNSMH26/0175/S K CONSTRUCTION/SBIN0017530 1,26,09,500.00',NULL,'Paid',51),(52,67112,'8 - Part 1',495185.00,0.00,0.00,495185.00,'30/07/2026 NEFT/AXISP00821657052/SNSMH26/15 70/S K CONSTRUCTION/SBIN0017530 4,95,185.00',NULL,'Paid',52),(53,67112,'8 - Part 2',439740.00,0.00,0.00,439740.00,'14/08/2026 NEFT/AXISP00827698588/SNSMH26/1692/S K CONSTRUCTION/SBIN0017530 4,39,740.00',NULL,'Paid',53),(54,67112,NULL,500000.00,0.00,0.00,500000.00,'07/09/2026 NEFT/AXISP00835116502/SNSMH26/2056/S K CONSTRUCTION/SBIN0017530\n5,00,000.00',NULL,'Paid',54),(55,67112,NULL,500000.00,0.00,0.00,500000.00,'18/09/2026 NEFT/AXISP00838306515/SNSMH26/21 30A/S K CONSTRUCTION/SBIN0017530 5,00,000.00',NULL,'Paid',55),(56,67112,NULL,22514.00,0.00,0.00,22514.00,'23/09/2026 NEFT/AXISP00840278878/SNSMH26/22 15/S K CONSTRUCTION/SBIN0017530 22,514.00',NULL,'Paid',56),(57,73275,'1',560487.09,6368.09,0.00,554119.00,'31/03/2026 NEFT/AXISP00784010068/SNSMH25/3832/SANKET GURURAJ VIB/MAHB0001686\n5,54,119.00',NULL,'Paid',57),(58,73275,'2',240681.00,2716.00,0.00,237965.00,'01/07/2026 NEFT/AXISP00813559065/SNSMH26/12 19/SANKET GURURAJ VIB/MAHB0001686 2,37,965.00',NULL,'Paid',58),(59,73275,'3',334799.38,3772.38,0.00,331027.00,'25/08/2026 NEFT/AXISP00830202867/SNSMH26/18 91/SANKET GURURAJ VIB/MAHB0001686 3,31,027.00',NULL,'Paid',59);
/*!40000 ALTER TABLE `payment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `payments`
--

DROP TABLE IF EXISTS `payments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `payments` (
  `Payment_Id` int NOT NULL AUTO_INCREMENT,
  `PMC_No` int DEFAULT NULL,
  `Invoice_No` varchar(100) DEFAULT NULL,
  `Payment_Amount` decimal(15,2) DEFAULT '0.00',
  `TDS_Payment_Amount` decimal(15,2) DEFAULT '0.00',
  `Total_Amount` decimal(15,2) DEFAULT '0.00',
  `UTR` varchar(100) DEFAULT NULL,
  `Invoice_Id` int DEFAULT NULL,
  PRIMARY KEY (`Payment_Id`),
  KEY `Invoice_Id` (`Invoice_Id`),
  CONSTRAINT `payments_ibfk_1` FOREIGN KEY (`Invoice_Id`) REFERENCES `invoices` (`Invoice_Id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payments`
--

LOCK TABLES `payments` WRITE;
/*!40000 ALTER TABLE `payments` DISABLE KEYS */;
/*!40000 ALTER TABLE `payments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `states`
--

DROP TABLE IF EXISTS `states`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `states` (
  `State_Id` int NOT NULL AUTO_INCREMENT,
  `State_Name` varchar(255) NOT NULL,
  `status` varchar(20) NOT NULL DEFAULT 'Active',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`State_Id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `states`
--

LOCK TABLES `states` WRITE;
/*!40000 ALTER TABLE `states` DISABLE KEYS */;
INSERT INTO `states` VALUES (1,'Maharashtra','Active','2026-09-28 11:52:11');
/*!40000 ALTER TABLE `states` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `subcontractors`
--

DROP TABLE IF EXISTS `subcontractors`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `subcontractors` (
  `Contractor_Id` int NOT NULL AUTO_INCREMENT,
  `Contractor_Name` varchar(255) NOT NULL,
  `Address` varchar(500) DEFAULT NULL,
  `Mobile_No` varchar(100) DEFAULT NULL,
  `PAN_No` varchar(100) DEFAULT NULL,
  `Email` varchar(200) DEFAULT NULL,
  `Gender` varchar(50) DEFAULT NULL,
  `GST_Registration_Type` varchar(50) DEFAULT NULL,
  `GST_No` varchar(100) DEFAULT NULL,
  `Contractor_password` varchar(250) DEFAULT NULL,
  PRIMARY KEY (`Contractor_Id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `subcontractors`
--

LOCK TABLES `subcontractors` WRITE;
/*!40000 ALTER TABLE `subcontractors` DISABLE KEYS */;
INSERT INTO `subcontractors` VALUES (1,'S K','','','','','','','',''),(2,'S K Construction',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL),(3,'sanket','','','','','','','',''),(4,'Sanket Vibhute',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
/*!40000 ALTER TABLE `subcontractors` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `uploaded_files`
--

DROP TABLE IF EXISTS `uploaded_files`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `uploaded_files` (
  `file_id` int NOT NULL AUTO_INCREMENT,
  `original_name` varchar(255) NOT NULL,
  `stored_name` varchar(255) NOT NULL,
  `total_rows` int DEFAULT '0',
  `uploaded_date` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_date` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`file_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `uploaded_files`
--

LOCK TABLES `uploaded_files` WRITE;
/*!40000 ALTER TABLE `uploaded_files` DISABLE KEYS */;
INSERT INTO `uploaded_files` VALUES (1,'67112 - SK Construction  (2).xlsx','67112 - SK Construction  (2).xlsx',22,'2026-09-28 11:51:33','2026-09-28 12:05:14'),(2,'73275 - Sanket Vibhute.xlsx','73275 - Sanket Vibhute.xlsx',7,'2026-09-30 05:04:54','2026-09-30 05:04:54');
/*!40000 ALTER TABLE `uploaded_files` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Temporary view structure for view `view_invoice_details`
--

DROP TABLE IF EXISTS `view_invoice_details`;
/*!50001 DROP VIEW IF EXISTS `view_invoice_details`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `view_invoice_details` AS SELECT 
 1 AS `Invoice_Id`,
 1 AS `Contractor_Name`,
 1 AS `PMC_No`,
 1 AS `Village_Name`,
 1 AS `Work_Type`,
 1 AS `Invoice_Details`,
 1 AS `Invoice_Date`,
 1 AS `Invoice_No`,
 1 AS `Basic_Amount`,
 1 AS `Debit_Amount`,
 1 AS `After_Debit_Amount`,
 1 AS `Amount`,
 1 AS `GST_Amount`,
 1 AS `TDS_Amount`,
 1 AS `SD_Amount`,
 1 AS `On_Commission`,
 1 AS `Hydro_Testing`,
 1 AS `GST_SD_Amount`,
 1 AS `Final_Amount`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `villages`
--

DROP TABLE IF EXISTS `villages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `villages` (
  `Village_Id` int NOT NULL AUTO_INCREMENT,
  `Village_Name` varchar(255) DEFAULT NULL,
  `Block_Id` int DEFAULT NULL,
  `status` varchar(20) NOT NULL DEFAULT 'Active',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`Village_Id`),
  KEY `Block_Id` (`Block_Id`),
  CONSTRAINT `villages_ibfk_1` FOREIGN KEY (`Block_Id`) REFERENCES `blocks` (`Block_Id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `villages`
--

LOCK TABLES `villages` WRITE;
/*!40000 ALTER TABLE `villages` DISABLE KEYS */;
INSERT INTO `villages` VALUES (1,'solapur',1,'Active','2026-09-28 11:52:45');
/*!40000 ALTER TABLE `villages` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Final view structure for view `view_invoice_details`
--

/*!50001 DROP VIEW IF EXISTS `view_invoice_details`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `view_invoice_details` AS select distinct `i`.`Invoice_Id` AS `Invoice_Id`,`s`.`Contractor_Name` AS `Contractor_Name`,`i`.`PMC_No` AS `PMC_No`,`v`.`Village_Name` AS `Village_Name`,`i`.`Work_Type` AS `Work_Type`,`i`.`Invoice_Details` AS `Invoice_Details`,`i`.`Invoice_Date` AS `Invoice_Date`,`i`.`invoice_no` AS `Invoice_No`,`i`.`Basic_Amount` AS `Basic_Amount`,`i`.`Debit_Amount` AS `Debit_Amount`,`i`.`After_Debit_Amount` AS `After_Debit_Amount`,`i`.`Amount` AS `Amount`,`i`.`GST_Amount` AS `GST_Amount`,`i`.`TDS_Amount` AS `TDS_Amount`,`i`.`SD_Amount` AS `SD_Amount`,`i`.`On_Commission` AS `On_Commission`,`i`.`Hydro_Testing` AS `Hydro_Testing`,`i`.`GST_SD_Amount` AS `GST_SD_Amount`,`i`.`Final_Amount` AS `Final_Amount` from (((`invoice` `i` left join `assign_subcontractors` `a` on(((`i`.`PMC_No` = `a`.`PMC_no`) and (`i`.`Village_Id` = `a`.`Village_Id`)))) left join `subcontractors` `s` on((`a`.`Contractor_Id` = `s`.`Contractor_Id`))) left join `villages` `v` on((`i`.`Village_Id` = `v`.`Village_Id`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-09-30  5:17:53
