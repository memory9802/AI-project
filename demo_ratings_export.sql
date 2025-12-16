-- MySQL dump 10.13  Distrib 8.0.44, for Linux (aarch64)
--
-- Host: localhost    Database: outfit_db
-- ------------------------------------------------------
-- Server version	8.0.44

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
-- Dumping data for table `rating`
--
-- WHERE:  item_source='items'

LOCK TABLES `rating` WRITE;
/*!40000 ALTER TABLE `rating` DISABLE KEYS */;
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (143,1,'items',5092,5,'å®Œç¾Ž!','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (144,1,'items',5093,5,'è¶…è®š','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (145,2,'items',5093,5,'å¾ˆå¥½','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (146,3,'items',5093,5,'æŽ¨è–¦','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (147,4,'items',5093,5,'å¥½è©•','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (148,5,'items',5093,5,'æ»¿æ„','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (149,6,'items',5093,5,'å„ªè³ª','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (150,7,'items',5093,5,'å–œæ­¡','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (151,8,'items',5093,5,'æ£’','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (152,9,'items',5093,5,'è®š','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (153,10,'items',5093,5,'å®Œç¾Ž','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (154,11,'items',5093,5,'å¥½','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (155,12,'items',5093,5,'æŽ¨','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (156,13,'items',5093,5,'å„ª','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (157,14,'items',5093,5,'ä½³','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (158,15,'items',5093,5,'æ„›','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (159,68,'items',5093,5,'å¥½è©• 68','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (160,69,'items',5093,5,'å¥½è©• 69','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (161,70,'items',5093,5,'å¥½è©• 70','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (162,71,'items',5093,5,'å¥½è©• 71','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (163,72,'items',5093,5,'å¥½è©• 72','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (166,73,'items',5093,4,'ä¸éŒ¯ 73','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (167,74,'items',5093,4,'ä¸éŒ¯ 74','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (168,75,'items',5093,4,'ä¸éŒ¯ 75','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (169,76,'items',5093,4,'ä¸éŒ¯ 76','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (170,77,'items',5093,4,'ä¸éŒ¯ 77','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (171,78,'items',5093,4,'ä¸éŒ¯ 78','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (172,79,'items',5093,4,'ä¸éŒ¯ 79','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (173,80,'items',5093,4,'ä¸éŒ¯ 80','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (181,1,'items',5094,5,'æŽ¨','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (182,2,'items',5094,5,'å¥½','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (183,3,'items',5094,5,'è®š','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (184,4,'items',5094,5,'æ£’','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (185,5,'items',5094,5,'å„ª','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (186,6,'items',5094,5,'ä½³','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (187,7,'items',5094,5,'æ„›','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (188,8,'items',5094,5,'å–œæ­¡','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (189,9,'items',5094,5,'æ»¿æ„','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (190,10,'items',5094,5,'å¥½è©•','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (191,11,'items',5094,5,'æŽ¨è–¦','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (192,12,'items',5094,5,'å¾ˆå¥½','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (193,13,'items',5094,5,'è¶…è®š','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (194,14,'items',5094,5,'å®Œç¾Ž','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (195,15,'items',5094,5,'å„ªè³ª','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (196,68,'items',5094,4,'ä¸éŒ¯ 68','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (197,69,'items',5094,4,'ä¸éŒ¯ 69','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (198,70,'items',5094,4,'ä¸éŒ¯ 70','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (199,71,'items',5094,4,'ä¸éŒ¯ 71','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (200,72,'items',5094,4,'ä¸éŒ¯ 72','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (201,73,'items',5094,4,'ä¸éŒ¯ 73','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (202,74,'items',5094,4,'ä¸éŒ¯ 74','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (203,75,'items',5094,4,'ä¸éŒ¯ 75','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (211,1,'items',5095,5,'è¶…ç´šå¥½','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (212,2,'items',5095,5,'éžå¸¸æ»¿æ„','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (213,3,'items',5095,5,'å¼·çƒˆæŽ¨è–¦','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (214,4,'items',5095,5,'å¾ˆå–œæ­¡','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (215,5,'items',5095,5,'å¤ªæ£’äº†','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (216,6,'items',5095,5,'å®Œç¾Ž','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (217,7,'items',5095,4,'ä¸éŒ¯','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (218,1,'items',5096,5,'æŽ¨è–¦','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (219,2,'items',5096,5,'å¥½è©•','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (220,3,'items',5096,5,'å¾ˆå¥½','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (221,4,'items',5096,5,'æ»¿æ„','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (222,5,'items',5096,5,'å„ªè³ª','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (223,6,'items',5096,5,'å–œæ­¡','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (224,7,'items',5096,5,'æ£’','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (225,8,'items',5096,5,'è®š','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (226,9,'items',5096,5,'å¥½','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (227,10,'items',5096,5,'æŽ¨','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (228,18,'items',5096,4,'ä¸éŒ¯ 18','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (229,19,'items',5096,4,'ä¸éŒ¯ 19','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (230,20,'items',5096,4,'ä¸éŒ¯ 20','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (231,21,'items',5096,4,'ä¸éŒ¯ 21','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (232,22,'items',5096,4,'ä¸éŒ¯ 22','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (233,33,'items',5096,4,'ä¸éŒ¯ 33','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (234,34,'items',5096,4,'ä¸éŒ¯ 34','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (235,35,'items',5096,4,'ä¸éŒ¯ 35','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (236,36,'items',5096,4,'ä¸éŒ¯ 36','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (237,37,'items',5096,4,'ä¸éŒ¯ 37','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (238,48,'items',5096,4,'ä¸éŒ¯ 48','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (239,49,'items',5096,4,'ä¸éŒ¯ 49','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (240,50,'items',5096,4,'ä¸éŒ¯ 50','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (241,51,'items',5096,4,'ä¸éŒ¯ 51','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (242,52,'items',5096,4,'ä¸éŒ¯ 52','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (243,63,'items',5096,4,'ä¸éŒ¯ 63','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (244,64,'items',5096,4,'ä¸éŒ¯ 64','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (245,65,'items',5096,4,'ä¸éŒ¯ 65','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (246,66,'items',5096,4,'ä¸éŒ¯ 66','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (247,67,'items',5096,4,'ä¸éŒ¯ 67','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (248,68,'items',5096,4,'ä¸éŒ¯ 68','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (249,69,'items',5096,4,'ä¸éŒ¯ 69','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (259,1,'items',5097,5,'å®Œç¾Ž','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (260,2,'items',5097,5,'è¶…è®š','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (261,3,'items',5097,5,'å¤ªå¥½äº†','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (262,4,'items',5097,5,'éžå¸¸æ£’','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (263,1,'items',5098,5,'å¥½','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (264,2,'items',5098,5,'ä¸éŒ¯','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (265,3,'items',5098,5,'å¯ä»¥','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (266,4,'items',5098,4,'ok','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (267,5,'items',5098,4,'é‚„è¡Œ','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (268,6,'items',5098,4,'å°šå¯','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (269,7,'items',5098,4,'å¯','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (270,8,'items',5098,3,'æ™®é€š','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (271,9,'items',5098,3,'ä¸€èˆ¬','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (272,10,'items',5098,3,'é‚„å¥½','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (273,11,'items',5098,3,'soso','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (274,12,'items',5098,3,'ä¸­ç­‰','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (275,13,'items',5098,2,'ä¸å¤ªå¥½','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (276,1,'items',5099,5,'å¥½','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (277,2,'items',5099,5,'æŽ¨','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (278,3,'items',5099,5,'è®š','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (279,4,'items',5099,5,'æ£’','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (280,5,'items',5099,5,'å„ª','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (281,6,'items',5099,5,'ä½³','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (282,7,'items',5099,5,'æ„›','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (283,8,'items',5099,5,'å–œæ­¡','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (284,9,'items',5099,5,'æ»¿æ„','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (285,10,'items',5099,5,'å¥½è©•','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (286,18,'items',5099,4,'ä¸éŒ¯ 18','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (287,19,'items',5099,4,'ä¸éŒ¯ 19','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (288,20,'items',5099,4,'ä¸éŒ¯ 20','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (289,21,'items',5099,4,'ä¸éŒ¯ 21','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (290,22,'items',5099,4,'ä¸éŒ¯ 22','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (291,33,'items',5099,4,'ä¸éŒ¯ 33','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (292,34,'items',5099,4,'ä¸éŒ¯ 34','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (293,35,'items',5099,4,'ä¸éŒ¯ 35','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (294,36,'items',5099,4,'ä¸éŒ¯ 36','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (295,37,'items',5099,4,'ä¸éŒ¯ 37','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (296,48,'items',5099,4,'ä¸éŒ¯ 48','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (297,49,'items',5099,4,'ä¸éŒ¯ 49','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (298,50,'items',5099,4,'ä¸éŒ¯ 50','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (299,51,'items',5099,4,'ä¸éŒ¯ 51','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (300,52,'items',5099,4,'ä¸éŒ¯ 52','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (301,63,'items',5099,4,'ä¸éŒ¯ 63','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (302,64,'items',5099,4,'ä¸éŒ¯ 64','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (303,65,'items',5099,4,'ä¸éŒ¯ 65','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (304,66,'items',5099,4,'ä¸éŒ¯ 66','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (305,67,'items',5099,4,'ä¸éŒ¯ 67','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (306,68,'items',5099,4,'ä¸éŒ¯ 68','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (307,69,'items',5099,4,'ä¸éŒ¯ 69','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (308,70,'items',5099,4,'ä¸éŒ¯ 70','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (309,71,'items',5099,4,'ä¸éŒ¯ 71','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (310,72,'items',5099,4,'ä¸éŒ¯ 72','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (311,73,'items',5099,4,'ä¸éŒ¯ 73','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (312,74,'items',5099,4,'ä¸éŒ¯ 74','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (313,75,'items',5099,4,'ä¸éŒ¯ 75','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (314,76,'items',5099,4,'ä¸éŒ¯ 76','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (315,77,'items',5099,4,'ä¸éŒ¯ 77','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (317,78,'items',5099,3,'æ™®é€š 78','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (318,79,'items',5099,3,'æ™®é€š 79','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (319,80,'items',5099,3,'æ™®é€š 80','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (320,81,'items',5099,3,'æ™®é€š 81','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (321,82,'items',5099,3,'æ™®é€š 82','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (322,83,'items',5099,3,'æ™®é€š 83','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (323,84,'items',5099,3,'æ™®é€š 84','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (324,1,'items',5100,5,'å¥½','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (325,2,'items',5100,5,'ä¸éŒ¯','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (326,3,'items',5100,5,'å¯ä»¥','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (327,4,'items',5100,4,'ok','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (328,5,'items',5100,4,'é‚„è¡Œ','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (329,6,'items',5100,4,'å°šå¯','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (330,7,'items',5100,4,'å¯','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (331,8,'items',5100,3,'æ™®é€š','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (332,9,'items',5100,3,'ä¸€èˆ¬','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (333,10,'items',5100,3,'é‚„å¥½','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (334,11,'items',5100,2,'ä¸å¤ªå¥½','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (335,1,'items',5101,4,'é‚„å¯ä»¥','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (336,2,'items',5101,3,'ä¸€èˆ¬','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (337,3,'items',5101,3,'æ™®é€š','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (338,4,'items',5101,2,'ä¸å¤ªå¥½','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (339,5,'items',5101,2,'ä¸æŽ¨è–¦','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (340,6,'items',5101,2,'å¤±æœ›','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (341,7,'items',5101,2,'ä¸ä½³','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (342,8,'items',5101,1,'å¾ˆå·®','2025-12-16 03:10:34','2025-12-16 03:10:34');
INSERT INTO `rating` (`id`, `user_id`, `item_source`, `item_id`, `rating_value`, `review_text`, `created_at`, `updated_at`) VALUES (343,9,'items',5101,1,'ç³Ÿç³•','2025-12-16 03:10:34','2025-12-16 03:10:34');
/*!40000 ALTER TABLE `rating` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'NO_AUTO_VALUE_ON_ZERO' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `after_rating_insert` AFTER INSERT ON `rating` FOR EACH ROW BEGIN
  -- 更新或插入統計表
  INSERT INTO item_stats (item_source, item_id, avg_rating, rating_count, rating_sum,
    rating_5_count, rating_4_count, rating_3_count, rating_2_count, rating_1_count,
    high_rating_count, high_rating_ratio)
  SELECT 
    NEW.item_source,
    NEW.item_id,
    AVG(rating_value),
    COUNT(*),
    SUM(rating_value),
    SUM(CASE WHEN rating_value = 5 THEN 1 ELSE 0 END),
    SUM(CASE WHEN rating_value = 4 THEN 1 ELSE 0 END),
    SUM(CASE WHEN rating_value = 3 THEN 1 ELSE 0 END),
    SUM(CASE WHEN rating_value = 2 THEN 1 ELSE 0 END),
    SUM(CASE WHEN rating_value = 1 THEN 1 ELSE 0 END),
    SUM(CASE WHEN rating_value >= 4 THEN 1 ELSE 0 END),
    SUM(CASE WHEN rating_value >= 4 THEN 1 ELSE 0 END) / COUNT(*)
  FROM rating
  WHERE item_source = NEW.item_source AND item_id = NEW.item_id
  GROUP BY item_source, item_id
  ON DUPLICATE KEY UPDATE 
    avg_rating = VALUES(avg_rating),
    rating_count = VALUES(rating_count),
    rating_sum = VALUES(rating_sum),
    rating_5_count = VALUES(rating_5_count),
    rating_4_count = VALUES(rating_4_count),
    rating_3_count = VALUES(rating_3_count),
    rating_2_count = VALUES(rating_2_count),
    rating_1_count = VALUES(rating_1_count),
    high_rating_count = VALUES(high_rating_count),
    high_rating_ratio = VALUES(high_rating_ratio),
    last_updated = CURRENT_TIMESTAMP;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'NO_AUTO_VALUE_ON_ZERO' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `after_rating_update` AFTER UPDATE ON `rating` FOR EACH ROW BEGIN
  -- 更新統計表
  INSERT INTO item_stats (item_source, item_id, avg_rating, rating_count, rating_sum,
    rating_5_count, rating_4_count, rating_3_count, rating_2_count, rating_1_count,
    high_rating_count, high_rating_ratio)
  SELECT 
    NEW.item_source,
    NEW.item_id,
    AVG(rating_value),
    COUNT(*),
    SUM(rating_value),
    SUM(CASE WHEN rating_value = 5 THEN 1 ELSE 0 END),
    SUM(CASE WHEN rating_value = 4 THEN 1 ELSE 0 END),
    SUM(CASE WHEN rating_value = 3 THEN 1 ELSE 0 END),
    SUM(CASE WHEN rating_value = 2 THEN 1 ELSE 0 END),
    SUM(CASE WHEN rating_value = 1 THEN 1 ELSE 0 END),
    SUM(CASE WHEN rating_value >= 4 THEN 1 ELSE 0 END),
    SUM(CASE WHEN rating_value >= 4 THEN 1 ELSE 0 END) / COUNT(*)
  FROM rating
  WHERE item_source = NEW.item_source AND item_id = NEW.item_id
  GROUP BY item_source, item_id
  ON DUPLICATE KEY UPDATE 
    avg_rating = VALUES(avg_rating),
    rating_count = VALUES(rating_count),
    rating_sum = VALUES(rating_sum),
    rating_5_count = VALUES(rating_5_count),
    rating_4_count = VALUES(rating_4_count),
    rating_3_count = VALUES(rating_3_count),
    rating_2_count = VALUES(rating_2_count),
    rating_1_count = VALUES(rating_1_count),
    high_rating_count = VALUES(high_rating_count),
    high_rating_ratio = VALUES(high_rating_ratio),
    last_updated = CURRENT_TIMESTAMP;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'NO_AUTO_VALUE_ON_ZERO' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `after_rating_delete` AFTER DELETE ON `rating` FOR EACH ROW BEGIN
  -- 檢查是否還有其他評分
  IF (SELECT COUNT(*) FROM rating WHERE item_source = OLD.item_source AND item_id = OLD.item_id) = 0 THEN
    -- 沒有評分了,刪除統計記錄
    DELETE FROM item_stats WHERE item_source = OLD.item_source AND item_id = OLD.item_id;
  ELSE
    -- 還有評分,更新統計
    INSERT INTO item_stats (item_source, item_id, avg_rating, rating_count, rating_sum,
      rating_5_count, rating_4_count, rating_3_count, rating_2_count, rating_1_count,
      high_rating_count, high_rating_ratio)
    SELECT 
      OLD.item_source,
      OLD.item_id,
      AVG(rating_value),
      COUNT(*),
      SUM(rating_value),
      SUM(CASE WHEN rating_value = 5 THEN 1 ELSE 0 END),
      SUM(CASE WHEN rating_value = 4 THEN 1 ELSE 0 END),
      SUM(CASE WHEN rating_value = 3 THEN 1 ELSE 0 END),
      SUM(CASE WHEN rating_value = 2 THEN 1 ELSE 0 END),
      SUM(CASE WHEN rating_value = 1 THEN 1 ELSE 0 END),
      SUM(CASE WHEN rating_value >= 4 THEN 1 ELSE 0 END),
      SUM(CASE WHEN rating_value >= 4 THEN 1 ELSE 0 END) / COUNT(*)
    FROM rating
    WHERE item_source = OLD.item_source AND item_id = OLD.item_id
    GROUP BY item_source, item_id
    ON DUPLICATE KEY UPDATE 
      avg_rating = VALUES(avg_rating),
      rating_count = VALUES(rating_count),
      rating_sum = VALUES(rating_sum),
      rating_5_count = VALUES(rating_5_count),
      rating_4_count = VALUES(rating_4_count),
      rating_3_count = VALUES(rating_3_count),
      rating_2_count = VALUES(rating_2_count),
      rating_1_count = VALUES(rating_1_count),
      high_rating_count = VALUES(high_rating_count),
      high_rating_ratio = VALUES(high_rating_ratio),
      last_updated = CURRENT_TIMESTAMP;
  END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-12-16  3:34:55
