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
-- Dumping data for table `users`
--
-- WHERE:  username LIKE 'demo_user_%'

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `favorite_style`, `created_at`) VALUES (8,'demo_user_1','demo1@test.com','hash1','休閒','2025-12-15 08:56:26');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `favorite_style`, `created_at`) VALUES (9,'demo_user_2','demo2@test.com','hash2','正式','2025-12-15 08:56:26');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `favorite_style`, `created_at`) VALUES (10,'demo_user_3','demo3@test.com','hash3','運動','2025-12-15 08:56:26');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `favorite_style`, `created_at`) VALUES (11,'demo_user_4','demo4@test.com','hash4','街頭','2025-12-15 08:56:26');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `favorite_style`, `created_at`) VALUES (12,'demo_user_5','demo5@test.com','hash5','復古','2025-12-15 08:56:26');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `favorite_style`, `created_at`) VALUES (13,'demo_user_6','demo6@test.com','hash6','極簡','2025-12-15 08:56:26');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `favorite_style`, `created_at`) VALUES (14,'demo_user_7','demo7@test.com','hash7','學院','2025-12-15 08:56:26');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `favorite_style`, `created_at`) VALUES (15,'demo_user_8','demo8@test.com','hash8','浪漫','2025-12-15 08:56:26');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `favorite_style`, `created_at`) VALUES (16,'demo_user_9','demo9@test.com','hash9','搖滾','2025-12-15 08:56:26');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `favorite_style`, `created_at`) VALUES (17,'demo_user_10','demo10@test.com','hash10','韓風','2025-12-15 08:56:26');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `favorite_style`, `created_at`) VALUES (18,'demo_user_11','demo11@test.com','hash11','日系','2025-12-15 08:56:26');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `favorite_style`, `created_at`) VALUES (19,'demo_user_12','demo12@test.com','hash12','歐美','2025-12-15 08:56:26');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `favorite_style`, `created_at`) VALUES (20,'demo_user_13','demo13@test.com','hash13','商務','2025-12-15 08:56:26');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `favorite_style`, `created_at`) VALUES (21,'demo_user_14','demo14@test.com','hash14','休閒','2025-12-15 08:56:26');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `favorite_style`, `created_at`) VALUES (22,'demo_user_15','demo15@test.com','hash15','運動','2025-12-15 08:56:26');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `favorite_style`, `created_at`) VALUES (23,'demo_user_1','demo1@test.com','hash1','休閒','2025-12-15 09:02:19');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `favorite_style`, `created_at`) VALUES (24,'demo_user_2','demo2@test.com','hash2','正式','2025-12-15 09:02:19');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `favorite_style`, `created_at`) VALUES (25,'demo_user_3','demo3@test.com','hash3','運動','2025-12-15 09:02:19');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `favorite_style`, `created_at`) VALUES (26,'demo_user_4','demo4@test.com','hash4','街頭','2025-12-15 09:02:19');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `favorite_style`, `created_at`) VALUES (27,'demo_user_5','demo5@test.com','hash5','復古','2025-12-15 09:02:19');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `favorite_style`, `created_at`) VALUES (28,'demo_user_6','demo6@test.com','hash6','極簡','2025-12-15 09:02:19');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `favorite_style`, `created_at`) VALUES (29,'demo_user_7','demo7@test.com','hash7','學院','2025-12-15 09:02:19');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `favorite_style`, `created_at`) VALUES (30,'demo_user_8','demo8@test.com','hash8','浪漫','2025-12-15 09:02:19');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `favorite_style`, `created_at`) VALUES (31,'demo_user_9','demo9@test.com','hash9','搖滾','2025-12-15 09:02:19');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `favorite_style`, `created_at`) VALUES (32,'demo_user_10','demo10@test.com','hash10','韓風','2025-12-15 09:02:19');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `favorite_style`, `created_at`) VALUES (33,'demo_user_11','demo11@test.com','hash11','日系','2025-12-15 09:02:19');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `favorite_style`, `created_at`) VALUES (34,'demo_user_12','demo12@test.com','hash12','歐美','2025-12-15 09:02:19');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `favorite_style`, `created_at`) VALUES (35,'demo_user_13','demo13@test.com','hash13','商務','2025-12-15 09:02:19');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `favorite_style`, `created_at`) VALUES (36,'demo_user_14','demo14@test.com','hash14','休閒','2025-12-15 09:02:19');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `favorite_style`, `created_at`) VALUES (37,'demo_user_15','demo15@test.com','hash15','運動','2025-12-15 09:02:19');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `favorite_style`, `created_at`) VALUES (38,'demo_user_1','demo1@test.com','hash1','ä¼‘é–’','2025-12-16 03:06:09');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `favorite_style`, `created_at`) VALUES (39,'demo_user_2','demo2@test.com','hash2','æ­£å¼','2025-12-16 03:06:09');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `favorite_style`, `created_at`) VALUES (40,'demo_user_3','demo3@test.com','hash3','é‹å‹•','2025-12-16 03:06:09');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `favorite_style`, `created_at`) VALUES (41,'demo_user_4','demo4@test.com','hash4','è¡—é ­','2025-12-16 03:06:09');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `favorite_style`, `created_at`) VALUES (42,'demo_user_5','demo5@test.com','hash5','å¾©å¤','2025-12-16 03:06:09');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `favorite_style`, `created_at`) VALUES (43,'demo_user_6','demo6@test.com','hash6','æ¥µç°¡','2025-12-16 03:06:09');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `favorite_style`, `created_at`) VALUES (44,'demo_user_7','demo7@test.com','hash7','å­¸é™¢','2025-12-16 03:06:09');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `favorite_style`, `created_at`) VALUES (45,'demo_user_8','demo8@test.com','hash8','æµªæ¼«','2025-12-16 03:06:09');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `favorite_style`, `created_at`) VALUES (46,'demo_user_9','demo9@test.com','hash9','æ–æ»¾','2025-12-16 03:06:09');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `favorite_style`, `created_at`) VALUES (47,'demo_user_10','demo10@test.com','hash10','éŸ“é¢¨','2025-12-16 03:06:09');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `favorite_style`, `created_at`) VALUES (48,'demo_user_11','demo11@test.com','hash11','æ—¥ç³»','2025-12-16 03:06:09');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `favorite_style`, `created_at`) VALUES (49,'demo_user_12','demo12@test.com','hash12','æ­ç¾Ž','2025-12-16 03:06:09');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `favorite_style`, `created_at`) VALUES (50,'demo_user_13','demo13@test.com','hash13','å•†å‹™','2025-12-16 03:06:09');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `favorite_style`, `created_at`) VALUES (51,'demo_user_14','demo14@test.com','hash14','ä¼‘é–’','2025-12-16 03:06:09');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `favorite_style`, `created_at`) VALUES (52,'demo_user_15','demo15@test.com','hash15','é‹å‹•','2025-12-16 03:06:09');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `favorite_style`, `created_at`) VALUES (53,'demo_user_1','demo1@test.com','hash1','ä¼‘é–’','2025-12-16 03:10:34');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `favorite_style`, `created_at`) VALUES (54,'demo_user_2','demo2@test.com','hash2','æ­£å¼','2025-12-16 03:10:34');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `favorite_style`, `created_at`) VALUES (55,'demo_user_3','demo3@test.com','hash3','é‹å‹•','2025-12-16 03:10:34');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `favorite_style`, `created_at`) VALUES (56,'demo_user_4','demo4@test.com','hash4','è¡—é ­','2025-12-16 03:10:34');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `favorite_style`, `created_at`) VALUES (57,'demo_user_5','demo5@test.com','hash5','å¾©å¤','2025-12-16 03:10:34');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `favorite_style`, `created_at`) VALUES (58,'demo_user_6','demo6@test.com','hash6','æ¥µç°¡','2025-12-16 03:10:34');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `favorite_style`, `created_at`) VALUES (59,'demo_user_7','demo7@test.com','hash7','å­¸é™¢','2025-12-16 03:10:34');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `favorite_style`, `created_at`) VALUES (60,'demo_user_8','demo8@test.com','hash8','æµªæ¼«','2025-12-16 03:10:34');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `favorite_style`, `created_at`) VALUES (61,'demo_user_9','demo9@test.com','hash9','æ–æ»¾','2025-12-16 03:10:34');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `favorite_style`, `created_at`) VALUES (62,'demo_user_10','demo10@test.com','hash10','éŸ“é¢¨','2025-12-16 03:10:34');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `favorite_style`, `created_at`) VALUES (63,'demo_user_11','demo11@test.com','hash11','æ—¥ç³»','2025-12-16 03:10:34');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `favorite_style`, `created_at`) VALUES (64,'demo_user_12','demo12@test.com','hash12','æ­ç¾Ž','2025-12-16 03:10:34');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `favorite_style`, `created_at`) VALUES (65,'demo_user_13','demo13@test.com','hash13','å•†å‹™','2025-12-16 03:10:34');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `favorite_style`, `created_at`) VALUES (66,'demo_user_14','demo14@test.com','hash14','ä¼‘é–’','2025-12-16 03:10:34');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `favorite_style`, `created_at`) VALUES (67,'demo_user_15','demo15@test.com','hash15','é‹å‹•','2025-12-16 03:10:34');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `favorite_style`, `created_at`) VALUES (68,'demo_user_16','demo16@test.com','hash16','ä¼‘é–’','2025-12-16 03:10:34');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `favorite_style`, `created_at`) VALUES (69,'demo_user_17','demo17@test.com','hash17','æ­£å¼','2025-12-16 03:10:34');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `favorite_style`, `created_at`) VALUES (70,'demo_user_18','demo18@test.com','hash18','é‹å‹•','2025-12-16 03:10:34');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `favorite_style`, `created_at`) VALUES (71,'demo_user_19','demo19@test.com','hash19','è¡—é ­','2025-12-16 03:10:34');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `favorite_style`, `created_at`) VALUES (72,'demo_user_20','demo20@test.com','hash20','å¾©å¤','2025-12-16 03:10:34');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `favorite_style`, `created_at`) VALUES (73,'demo_user_21','demo21@test.com','hash21','æ¥µç°¡','2025-12-16 03:10:34');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `favorite_style`, `created_at`) VALUES (74,'demo_user_22','demo22@test.com','hash22','å­¸é™¢','2025-12-16 03:10:34');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `favorite_style`, `created_at`) VALUES (75,'demo_user_23','demo23@test.com','hash23','æµªæ¼«','2025-12-16 03:10:34');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `favorite_style`, `created_at`) VALUES (76,'demo_user_24','demo24@test.com','hash24','æ–æ»¾','2025-12-16 03:10:34');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `favorite_style`, `created_at`) VALUES (77,'demo_user_25','demo25@test.com','hash25','éŸ“é¢¨','2025-12-16 03:10:34');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `favorite_style`, `created_at`) VALUES (78,'demo_user_26','demo26@test.com','hash26','æ—¥ç³»','2025-12-16 03:10:34');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `favorite_style`, `created_at`) VALUES (79,'demo_user_27','demo27@test.com','hash27','æ­ç¾Ž','2025-12-16 03:10:34');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `favorite_style`, `created_at`) VALUES (80,'demo_user_28','demo28@test.com','hash28','å•†å‹™','2025-12-16 03:10:34');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `favorite_style`, `created_at`) VALUES (81,'demo_user_29','demo29@test.com','hash29','ä¼‘é–’','2025-12-16 03:10:34');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `favorite_style`, `created_at`) VALUES (82,'demo_user_30','demo30@test.com','hash30','æ­£å¼','2025-12-16 03:10:34');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `favorite_style`, `created_at`) VALUES (83,'demo_user_31','demo31@test.com','hash31','é‹å‹•','2025-12-16 03:10:34');
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `favorite_style`, `created_at`) VALUES (84,'demo_user_32','demo32@test.com','hash32','è¡—é ­','2025-12-16 03:10:34');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-12-16  3:34:47
